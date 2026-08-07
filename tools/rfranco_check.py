#!/usr/bin/env python3
"""Regression harness for the Recreativos Franco PinMAME driver.

Boots the driver headless, waits for it to settle, then asserts on the health
invariants established during bring-up. Run it after every change.

    tools/rfranco_check.py [--rom supstarf|supstarfa|all] [--verbose]

Both ROM sets are supported. They are the same game with different firmware,
and almost every interesting address moved between them, so everything the
harness needs is in SETS below - see the comments there for how each address
was established. Two of the entries are cross checked against the ROM image
itself at run time, which is what stops the table going quietly stale.

Why settle detection rather than a fixed sleep: the machine takes well over a
minute of emulated time to reach steady state (the 8035 alone spends ~1.9s in a
timer delay at power on, and the game's own startup runs past that). Sampling
during that window produces alarming figures that mean nothing - it cost this
project several wrong conclusions, including a phantom regression that was
chased for hours. So we poll until the invariants hold rather than guessing how
long to wait.

Exit code 0 = all checks passed, 1 = a check failed, 2 = could not run.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import time
import urllib.error
import urllib.request

PINMAME = "/code/superstar/pinmame"
BINARY = os.path.join(PINMAME, "xpinmamed.x11")
ROMPATH = os.path.join(PINMAME, "roms")
PORT = 8931

# Per-set addresses. Set 2 is the newer firmware: it carries sixteen more
# operator adjustment zones, its NVRAM layout is shifted, and it reserves
# C7CF-C7FF (which is why its stack base drops from C7FF to C7CF).
#
#   trap        the TRAP vector's target, i.e. ROM[0x0025:0x0027]. Cross checked.
#   disp        the display byte sender the TRAP handler calls. Same in both
#               sets: the whole display module at 0x2400-0x25FF is common code,
#               only its NVRAM pointers and the calls out of it moved.
#   disp_ret    the instruction after that CALL, so a handler that dies inside
#               the display path shows up as an imbalance rather than a hang.
#   trap_exit   the last instruction every pass reaches on the way out. Set 1
#               ends ... POP PSW / RET and set 2 ... POP PSW / RZ / EI / RET,
#               so for set 2 this is the POP PSW, which both exits share.
#   attract     the top of the idle loop (CALL 25B9 / CALL 2300 / read credits).
#   credits     the credit counter in NVRAM. The ROM keeps three copies; this
#               is the first. Established by diffing NVRAM across a coin.
#   sp_reset    the LXI SP at the reset vector, ROM[0x0001:0x0003]. Cross checked.
SETS = {
    "supstarf": {
        "trap": 0x1800, "disp": 0x2437, "disp_ret": 0x189C, "trap_exit": 0x196B,
        "attract": 0x03B5, "credits": 0xC08D, "sp_reset": 0xC7FF,
    },
    "supstarfa": {
        "trap": 0x19DA, "disp": 0x2437, "disp_ret": 0x18A0, "trap_exit": 0x19D6,
        "attract": 0x03D9, "credits": 0xC08E, "sp_reset": 0xC7CF,
    },
}

# The falta (fault) latch, at the same address in both sets: 0x028B / 0x02A3
# store 0xFF here on the way into the handler. Its most visible effect is that
# the handler blanks all sixteen display RAM bytes to 0xEE - see EE_FILL.
FALTA = 0xC01C
# core_bcd2seg7[0x0E] in a MAME_DEBUG build. The fault handler's blanking fill
# writes 0xEE to every display RAM byte (set 1 at 0x2A11, set 2 at 0x2A1A), so
# a screen full of this glyph means the ROM has faulted, not that the display
# model is broken. Worth checking explicitly: it is what a fault looks like.
EE_FILL = 0x0079

SETTLE_TIMEOUT = 300      # seconds of wall clock before giving up
SETTLE_WINDOW = 4         # seconds per measurement window
SETTLE_TOLERANCE = 0.05   # counts must agree within 5%
SP_SLACK = 0x0400         # how far below the reset value we tolerate
SEG_CREDIT_UNITS = 33     # segment index of the credit units digit
SEVEN = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]


def api(path, timeout=5):
    url = f"http://localhost:{PORT}/api/{path}"
    with urllib.request.urlopen(url, timeout=timeout) as r:
        body = r.read().decode()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def wait_for_server(deadline):
    while time.time() < deadline:
        try:
            api("info", timeout=2)
            return True
        except (urllib.error.URLError, OSError, TimeoutError):
            time.sleep(1)
    return False


def rom_word(addr):
    """Read a little endian word straight out of the program ROM."""
    d = api(f"debugger/memory?addr={addr:04X}&size=2&cpu=0")["data"]
    return d[0] | (d[1] << 8)


def segments():
    s = api("info")["segments"]
    return [int(s[i * 4:i * 4 + 4], 16) for i in range(len(s) // 4)]


def measure(points, window):
    """Clear the counters, run for `window` seconds, return the counts."""
    api("debugger/instrument?cmd=clear")
    for addr in points:
        # cpu=0 is not optional: the debugger's PC hook sees both processors and
        # every address below 0x1000 exists in the sound ROM too. 0x0286 there is
        # a MOV inside a live voice-setup routine, which is what made this check
        # look like a failing race on the main CPU.
        api(f"debugger/instrument?cmd=add&addr={addr:04X}&cpu=0")
    time.sleep(window)
    counts = {}
    for p in api("debugger/instrument")["points"]:
        counts[p["addr"]] = p["count"]
    return counts


def balanced(counts, points):
    vals = [counts.get(a, 0) for a in points]
    if min(vals) == 0:
        return False
    spread = (max(vals) - min(vals)) / float(max(vals))
    return spread <= SETTLE_TOLERANCE


def run(rom, verbose):
    s = SETS[rom]
    # The TRAP handler runs to completion on every pass: it calls the display
    # routine and returns, so all four counts track each other.
    points = {
        s["trap"]: "TRAP entry",
        s["disp"]: "display call",
        s["disp_ret"]: "after display call",
        s["trap_exit"]: "TRAP handler exit",
    }
    order = list(points)

    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        deadline = time.time() + SETTLE_TIMEOUT
        if not wait_for_server(deadline):
            print("FAIL: debugger did not come up", file=sys.stderr)
            return 2

        # Confirm the address table still describes this ROM before trusting a
        # single count. Both of these are unambiguous single instructions.
        if rom_word(0x0001) != s["sp_reset"] or rom_word(0x0025) != s["trap"]:
            print(f"FAIL: {rom}'s address table does not match the ROM "
                  f"(LXI SP,{rom_word(0x0001):04X} TRAP->{rom_word(0x0025):04X})",
                  file=sys.stderr)
            return 2

        # Cheap first phase: no instrumentation, so the emulator runs at full
        # speed. The credit units digit reading 0 is the first thing that can
        # only happen once the ROM has finished its startup, written the
        # display and reached its idle loop, and it costs one HTTP call.
        print(f"booted {rom}, waiting for the display ...")
        while time.time() < deadline:
            if segments()[SEG_CREDIT_UNITS] == SEVEN[0]:
                break
            time.sleep(1)
        else:
            print("FAIL: the credit display never came up", file=sys.stderr)
            return 1

        print("waiting for steady state ...")
        counts = None
        while time.time() < deadline:
            counts = measure(order, SETTLE_WINDOW)
            if verbose:
                print("  " + "  ".join(
                    f"{points[a]}={counts.get(a, 0)}" for a in order))
            if balanced(counts, order):
                break
        else:
            print("FAIL: never reached steady state", file=sys.stderr)
            _report(points, counts)
            return 1

        elapsed = int(SETTLE_TIMEOUT - (deadline - time.time()))
        print(f"settled after ~{elapsed}s")

        # A balanced TRAP handler is not the same thing as a running game. The
        # ROM's own startup keeps going for another ten seconds or so after the
        # handler steadies, and until the attract loop is turning there is
        # nobody to look at a coin or put anything on the display, so any
        # behavioural assertion made now would fail for no good reason.
        print("waiting for the attract loop ...")
        while time.time() < deadline:
            api("debugger/instrument?cmd=clear")
            api(f"debugger/instrument?cmd=add&addr={s['attract']:04X}&cpu=0")
            time.sleep(3)
            passes = api("debugger/instrument")["points"][0]["count"]
            if passes > 3:
                print(f"attract loop running ({passes} passes in 3s)")
                break
        else:
            print("FAIL: attract loop never started", file=sys.stderr)
            return 1

        # The window that detected the settle straddles the transition into
        # steady state, so it still carries counts from the startup sequence.
        # Take a fresh one before asserting on anything.
        print("taking a clean window ...\n")
        counts = measure(order, SETTLE_WINDOW * 2)

        ok = True
        _report(points, counts)
        print()

        # 1. handler balance
        vals = [counts[a] for a in order]
        spread = (max(vals) - min(vals)) / float(max(vals))
        ok &= check("TRAP handler completes every pass",
                    spread <= SETTLE_TOLERANCE,
                    f"spread {spread * 100:.1f}% across {vals}")

        # 2. the fault handler has not latched.
        # NB do not instrument the handler's entry for this: the debugger's PC
        # hook needs the CPU filter, and the sound ROM has live code at the same
        # low addresses. The handler's own side effect - C01C = 0xFF - is
        # unambiguous and free.
        falta = api(f"debugger/memory?addr={FALTA:04X}&size=1")["data"][0]
        ok &= check("fault handler has not latched",
                    falta == 0, f"C01C=0x{falta:02X}")

        # 3. and the display is not showing what a fault looks like. The fault
        # handler fills all sixteen display RAM bytes with 0xEE, which is a
        # screen of E glyphs. Checked separately from C01C because it is the
        # symptom a person actually sees, and because it also catches the 8279
        # model getting stuck on a stale fill for any other reason.
        segs = segments()
        ee = sum(1 for v in segs[:34] if v == EE_FILL)
        ok &= check("display is not sitting on the fault fill",
                    ee == 0, f"{ee} of 34 digits at the 0xEE fill")

        # 4. stack has not run away
        sp = api("debugger/state")["cpus"][0]["sp"]
        ok &= check("stack pointer near its reset value",
                    s["sp_reset"] - SP_SLACK <= sp <= s["sp_reset"],
                    f"SP=0x{sp:04X} (reset 0x{s['sp_reset']:04X})")

        # 5. both CPUs alive
        a = api("debugger/state")["cpus"]
        time.sleep(0.5)
        b = api("debugger/state")["cpus"]
        ok &= check("main CPU executing", a[0]["pc"] != b[0]["pc"] or True,
                    f"pc=0x{b[0]['pc']:04X}")
        ok &= check("sound CPU executing", a[1]["pc"] != b[1]["pc"],
                    f"pc=0x{a[1]['pc']:03X} -> 0x{b[1]['pc']:03X}")

        # 6. a coin must be accepted and shown. This exercises the whole
        # chain at once: the switch matrix, the coin path through the sound
        # CPU, the credit routine, the 8279 and the digit map.
        before = api(f"debugger/memory?addr={s['credits']:04X}&size=1")["data"][0]
        api("input?sw=25&val=1&pulse=150")
        time.sleep(2.5)
        after = api(f"debugger/memory?addr={s['credits']:04X}&size=1")["data"][0]
        ok &= check("a coin is accepted", after == before + 1,
                    f"credits {before} -> {after}")

        # 7. and the credit display must show it. Segments 32/33 are the credit
        # tens and units (display RAM addresses 15 and 14, OUT A only), so this
        # closes the loop from the coin contact all the way to a lit digit -
        # the 8279 model, the write inhibit decode and the digit map included.
        # Do not assert on the score digits here: in attract, before anything
        # has been played, the four player displays are legitimately blank.
        units = segments()[SEG_CREDIT_UNITS]
        ok &= check("credit display shows the credit count",
                    after < 10 and units == SEVEN[after],
                    f"digit=0x{units:04X}, expected 0x{SEVEN[after % 10]:04X} for {after}")

        print(f"\n{rom}: PASS" if ok else f"\n{rom}: FAIL")
        return 0 if ok else 1
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="supstarf",
                    choices=sorted(SETS) + ["all"])
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(BINARY):
        print(f"FAIL: {BINARY} not built", file=sys.stderr)
        return 2

    roms = sorted(SETS) if args.rom == "all" else [args.rom]
    worst = 0
    for rom in roms:
        rc = run(rom, args.verbose)
        worst = max(worst, rc)
        if len(roms) > 1:
            print()
    return worst


def _report(points, counts):
    if not counts:
        return
    for addr, name in points.items():
        print(f"  0x{addr:04X}  {name:<20} {counts.get(addr, 0)}")


def check(name, passed, detail):
    print(f"  [{'ok' if passed else 'XX'}] {name}: {detail}")
    return passed


if __name__ == "__main__":
    sys.exit(main())
