#!/usr/bin/env python3
"""Sound check for the Recreativos Franco PinMAME driver.

Boots the driver, triggers the coin, ball-start and bumper sounds, and reports
what the 8035 actually programmed into the AY-3-8910 - decoded to frequencies
and note names - then asserts the result is musically sensible.

    tools/rfranco_sound.py [--rom supstarf|supstarfa|all] [--verbose]

How the capture works, since it needs no changes to the driver: the remote
debugger's tracepoint log snapshots CPU registers by M6809 register id, and on
PinMAME's MCS-48 core those ids land on

    a  (M6809_A  = 4) -> I8039_A    the accumulator, i.e. the byte being written
    x  (M6809_X  = 7) -> I8039_P2   the port that selects which chip
    y  (M6809_Y  = 8) -> I8039_R0   the MOVX address, i.e. the AY register
    dp (M6809_DP = 9) -> I8039_R1

The snapshot is taken before the instruction runs, so at each MOVX @R0,A in the
sound engine the pair (R0, A) is exactly (AY register, value). P2 bit 6 low
selects PSG1 (board IC3), which is the only chip the sound engine ever uses.

The sound ROM's tone table at 0x308 is a 64 entry chromatic scale of 16 bit AY
periods, C2 to B6 plus four entries an octave above. A = 440 is exact at the
844800 Hz PSG clock (period 120 -> 52800/440 with no remainder), so decoding a
period back to a frequency and comparing it against equal temperament is a
strong check that the whole chain is right.

Exit code 0 = all checks passed, 1 = a check failed, 2 = could not run.
"""
import argparse
import json
import math
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

PINMAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pinmame")
BINARY = os.path.join(PINMAME, "xpinmamed.x11")
ROMPATH = os.path.join(PINMAME, "roms")
PORT = 8932

PSG_CLOCK = 5068800.0 / 6.0     # the 8035's T0 pin, XTAL/6 = 844800 Hz
NOTES = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]

# Where the command byte can be read. 0x0210 is inside the sound engine
# prologue, after "SEL RB1 / MOV R1,A" has stashed it in bank 1's R1, and it is
# reached only for commands the ROM has decided are sounds - so it does not bury
# the 512 entry log under the 0xAA / 0xDD / 0x99 / 0x69 housekeeping traffic the
# 8085 sends several hundred times a second.
CMD_PC = 0x0210

# The MOVX writes inside the sound engine. 0x0101-0x01B9 is deliberately absent:
# that is the 20 byte lamp and coil frame the 8085 ships on every TRAP pass, and
# tracing it would fill the log in a quarter of a second.
SOUND_MOVX = [0x01D7,                          # 0x1D0, stop everything
              0x0200, 0x0204, 0x0206, 0x0208,  # prologue: r6, r8/r9/r10
              0x0279, 0x027E, 0x0283, 0x0287,  # NOTE: period, volume, r13
              0x029A,                          # ENV: r12
              0x02B2, 0x02B4, 0x02B7,          # effect mode
              0x02F5,                          # VOL: r8
              0x03FD]                          # effect sweep -> r0

SEG_CREDIT_UNITS = 33
SEG_ZERO = 0x3F
CENTS_TOLERANCE = 25    # the ROM's periods are integers, so a few cents is normal


def api(path, timeout=10):
    url = f"http://localhost:{PORT}/api/{path}"
    with urllib.request.urlopen(url, timeout=timeout) as r:
        body = r.read().decode()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def note_of(hz):
    n = 12 * math.log(hz / 440.0, 2) + 57       # 57 = A4 in semitones above C0
    k = int(round(n))
    return "%s%d" % (NOTES[k % 12], k // 12), (n - k) * 100.0


def sw(num, pulse=150):
    api(f"input?sw={num}&val=1&pulse={pulse}")


def _arm():
    api("debugger/tracepoints?cmd=clear")
    for a in SOUND_MOVX + [CMD_PC]:
        api(f"debugger/tracepoints?cmd=add&addr={a:04X}&cpu=1")


def _drain():
    """Read the log back and split it into one record per sound command."""
    log = api("debugger/tracepoints")["log"]
    events, cur = [], None
    for e in log:
        if e["pc"] == CMD_PC:
            cur = {"cmd": e["dp"] & 0xff, "writes": []}
            events.append(cur)
        elif cur is not None:
            cur["writes"].append((e["pc"], e["y"], e["a"], e["x"]))
    return events


def capture_sounds(verbose):
    """Provoke each sound in turn, draining the log between them.

    The log holds 512 records and one bumper cascade is 36 notes, four writes
    each, so reading only at the end loses whatever came first."""
    events = []

    def phase(action, settle):
        _arm()
        time.sleep(0.3)
        action()
        time.sleep(settle)
        events.extend(_drain())

    # Coins first: the game loop does not poll them, so this only works from
    # attract.
    phase(lambda: sw(25), 2.5)
    phase(lambda: sw(25), 2.5)
    phase(lambda: sw(28, 200), 5.0)          # start: serves the ball
    for contact in (18, 12, 11, 17, 13, 15):  # find the bumper cascade
        phase(lambda c=contact: sw(c, 120), 1.8)
    return events


def analyse(ev, verbose):
    """Decode one command's writes into notes. Returns a summary dict."""
    per, notes, cents, chans, env = {}, [], [], set(), None
    lines = []
    for pc, reg, data, p2 in ev["writes"]:
        psg1 = (p2 & 0x80) and not (p2 & 0x40)
        if not psg1:
            continue
        if reg in (0, 2, 4):
            per[reg] = data
        elif reg in (1, 3, 5):
            p = per.get(reg - 1, 0) | ((data & 0x0f) << 8)
            if p:
                hz = PSG_CLOCK / (16.0 * p)
                name, c = note_of(hz)
                notes.append((reg // 2, p, hz, name, c))
                cents.append(c)
                chans.add(reg // 2)
                lines.append("      ch%s period %4d = %8.3f Hz  %-4s %+5.1f cent"
                             % ("ABC"[reg // 2], p, hz, name, c))
        elif reg == 12:
            env = data << 8
    if verbose:
        for ln in lines:
            print(ln)
    return {"cmd": ev["cmd"], "notes": notes, "cents": cents,
            "channels": chans, "env": env}


def run(rom, verbose):
    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    try:
        deadline = time.time() + 300
        while time.time() < deadline:
            try:
                s = api("info", timeout=2)["segments"]
                if int(s[SEG_CREDIT_UNITS * 4:SEG_CREDIT_UNITS * 4 + 4], 16) == SEG_ZERO:
                    break
            except (urllib.error.URLError, OSError, TimeoutError, ValueError):
                pass
            time.sleep(1)
        else:
            print("FAIL: %s never reached attract" % rom, file=sys.stderr)
            return 2
        time.sleep(20)
        print("booted %s, provoking sounds ..." % rom)

        events = capture_sounds(verbose)
        by_cmd = {}
        for ev in events:
            print("\n  sound command 0x%02X, %d PSG writes"
                  % (ev["cmd"], len(ev["writes"])))
            a = analyse(ev, verbose)
            if a["notes"]:
                print("      %d notes on channel(s) %s, %s"
                      % (len(a["notes"]), "".join(sorted("ABC"[c] for c in a["channels"])),
                         "envelope period %d" % a["env"] if a["env"] else "no envelope"))
                print("      " + " ".join(n[3] for n in a["notes"][:40]))
            by_cmd.setdefault(ev["cmd"], a)
        print()

        ok = True
        ok &= check("three or more distinct sounds were provoked",
                    len(by_cmd) >= 3, "commands " +
                    " ".join("0x%02X" % c for c in sorted(by_cmd)))

        # 0xE1, the coin. Three voices at once, and the ROM's own triad.
        coin = by_cmd.get(0xE1)
        ok &= check("coin (0xE1) programmes a three voice chord",
                    bool(coin) and len(coin["channels"]) == 3,
                    "channels %s" % (sorted(coin["channels"]) if coin else "-"))
        if coin:
            first = [n[3] for n in coin["notes"][:3]]
            ok &= check("coin chord is C4 E4 G4", first == ["C4", "E4", "G4"],
                        " ".join(first))

        # 0xB1, ball start. One voice, one note, repeated.
        start = by_cmd.get(0xB1)
        ok &= check("ball start (0xB1) is a single voice",
                    bool(start) and len(start["channels"]) == 1,
                    "channels %s" % (sorted(start["channels"]) if start else "-"))
        if start:
            names = set(n[3] for n in start["notes"])
            ok &= check("ball start note is D4", names == {"D4"}, " ".join(sorted(names)))

        # 0xE0, the bumper: a fast falling cascade on one voice.
        bump = by_cmd.get(0xE0)
        ok &= check("bumper (0xE0) is a falling cascade on one voice",
                    bool(bump) and len(bump["channels"]) == 1 and len(bump["notes"]) >= 8,
                    "%d notes on %s" % (len(bump["notes"]), sorted(bump["channels"]))
                    if bump else "not seen")
        if bump:
            hz = [n[2] for n in bump["notes"]]
            falls = sum(1 for a, b in zip(hz, hz[1:]) if b < a)
            ok &= check("bumper cascade descends", falls >= len(hz) * 0.7,
                        "%d of %d steps fall" % (falls, len(hz) - 1))

        # and every note the machine played is a real tempered pitch
        allc = [c for a in by_cmd.values() for c in a["cents"]]
        worst = max((abs(c) for c in allc), default=99)
        ok &= check("every note is within %d cent of equal temperament"
                    % CENTS_TOLERANCE, allc and worst <= CENTS_TOLERANCE,
                    "%d notes, worst %+.1f cent" % (len(allc), worst))

        print(f"\n{rom}: PASS" if ok else f"\n{rom}: FAIL")
        return 0 if ok else 1
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def check(name, passed, detail):
    print(f"  [{'ok' if passed else 'XX'}] {name}: {detail}")
    return bool(passed)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="supstarf",
                    choices=["supstarf", "supstarfa", "all"])
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(BINARY):
        print(f"FAIL: {BINARY} not built", file=sys.stderr)
        return 2
    roms = ["supstarf", "supstarfa"] if args.rom == "all" else [args.rom]
    worst = 0
    for rom in roms:
        worst = max(worst, run(rom, args.verbose))
        if len(roms) > 1:
            print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
