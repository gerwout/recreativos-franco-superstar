#!/usr/bin/env python3
"""Walk the AJUSTES DE TANTEO operator menu and record every zone.

The manual documents nine zones, which is what `supstarf` has. `supstarfa`
carries more, and they are not documented anywhere; this walks the menu on a
running machine and writes down what the displays actually show, plus the
NVRAM the ROM reads back for each zone.

    tools/rfranco_zones.py [--rom supstarf|supstarfa|all] [--steps N] [--json]

How the menu is driven. The two door switches are the mode; the start button
(switch 28) is the only other control, and what it does depends on where the
door switches are *at the time*:

  * both up   -> the button steps the current zone's VALUE
  * either one back down -> the button steps to the NEXT ZONE

so the switches have to move while the machine runs. The driver models them as
two ordinary switches in its pseudo coin-door column, the way Williams System
4-11 does: switch 1 is the ajuste switch and switch 2 is the test switch,
closed meaning up. Both are open by default, which is the resting position and
boots the machine into juego.

The zone number itself is shown in the credit display; the value is shown on
the player displays, which zone is which decides.
"""
import argparse
import json
import os
import signal
import subprocess
import sys
import tempfile
import time
import urllib.error
import urllib.request

PINMAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pinmame")
BINARY = os.path.join(PINMAME, "xpinmamed.x11")
ROMPATH = os.path.join(PINMAME, "roms")

# Keep the harness out of ~/.xpinmame. MAME saves input port state there on a
# clean exit, and that includes the position of the two operator door switches
# (they are toggles - see docs/pinmame-keyboard-reference.md). A switch left up
# in an interactive session would boot the machine straight into an operator
# mode on the next launch, failing every check here for a reason that has
# nothing to do with the driver. Give the emulator a scratch directory instead,
# so a run neither reads nor writes the user's settings.
CFGDIR = os.path.join(tempfile.gettempdir(), "rfranco-harness-cfg")
os.makedirs(CFGDIR, exist_ok=True)
PORT = 8935

SW_START = 28
SW_AJUSTE_UP = 1
SW_TEST_UP = 2

SEVEN = {0x3F: '0', 0x06: '1', 0x5B: '2', 0x4F: '3', 0x66: '4', 0x6D: '5',
         0x7D: '6', 0x07: '7', 0x7F: '8', 0x6F: '9', 0x00: ' ', 0x79: 'E'}

# Where each ROM keeps the zone number the menu is showing, and the NVRAM
# window the extra zones live in. Both established from the menu dispatcher
# rather than assumed. It is at 0x3255 in BOTH sets - the menu entry loads the
# zone counter with 1 at 0x3262 and the dispatcher reads it back at 0x3272,
# where set 1 bounds it with CP 0x0A and set 2 with CP 0x1A. That bound is where
# set 2's extra zones come from; how many of them the counter actually reaches
# is a question for this script.
SETS = {
    "supstarf":  {"zone": 0xC01D, "nv": (0xC1E9, 0x30), "extra": None},
    "supstarfa": {"zone": 0xC01D, "nv": (0xC1EA, 0x30), "extra": (0xC7F0, 0x10)},
}


def api(path, timeout=10):
    with urllib.request.urlopen("http://localhost:%d/api/%s" % (PORT, path),
                                timeout=timeout) as r:
        body = r.read().decode()
    try:
        return json.loads(body)
    except json.JSONDecodeError:
        return body


def segments():
    s = api("info")["segments"]
    return [int(s[i * 4:i * 4 + 4], 16) for i in range(len(s) // 4)]


def display():
    s = segments()

    def grp(o, n):
        return ''.join(SEVEN.get(s[o + i], '?') for i in range(n))
    return {"p1": grp(0, 7), "p2": grp(8, 7), "p3": grp(16, 7),
            "p4": grp(24, 7), "cr": grp(32, 2)}


def mem(addr, size=1):
    return api("debugger/memory?addr=%04X&size=%d&cpu=0" % (addr, size))["data"]


def sw(num, val):
    api("input?sw=%d&val=%d" % (num, val))


def press_start(hold=1.2, gap=1.5):
    # Headless, this runs at roughly a third of real time, so a press has to be
    # held for over a second of wall clock to be a press at all.
    sw(SW_START, 1)
    time.sleep(hold)
    sw(SW_START, 0)
    time.sleep(gap)


def next_zone(zone_addr, timeout=40):
    """Put a door switch back down, press start until the zone moves, lift it.

    Closed loop rather than a fixed number of presses: redrawing thirty digits
    through the serial display chain takes the ROM a while, and how long
    depends on how fast the host happens to be running the emulation.
    """
    was = mem(zone_addr)[0]
    sw(SW_TEST_UP, 0)      # test switch down -> the button steps the zone
    time.sleep(1.5)
    end = time.time() + timeout
    while time.time() < end:
        press_start()
        if mem(zone_addr)[0] != was:
            break
    sw(SW_TEST_UP, 1)      # both up again -> the button steps the value
    time.sleep(1.5)
    return mem(zone_addr)[0] != was


def snapshot(s):
    d = display()
    out = {"zone_nvram": "0x%02X" % mem(s["zone"])[0], "display": d}
    return out


def run(rom, steps, as_json):
    s = SETS[rom]
    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, "-cfg_directory", CFGDIR, rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        end = time.time() + 240
        while time.time() < end:
            try:
                api("info", timeout=2)
                break
            except (urllib.error.URLError, OSError, TimeoutError):
                time.sleep(1)
        else:
            print("FAIL: debugger did not come up", file=sys.stderr)
            return 2

        # The menu is entered from the boot dispatch - set 1 0x00BB, set 2
        # 0x00BF, the ANI 0xC0 on the cabinet byte the ROM has just fetched with
        # sound command 0xEE - so both door switches have to be up before the
        # ROM gets there. The debugger comes up long before that in wall clock
        # terms - the machine needs tens of seconds of it to finish starting -
        # so just hold them from now on.
        for _ in range(20):
            sw(SW_AJUSTE_UP, 1)
            sw(SW_TEST_UP, 1)
            time.sleep(0.1)

        # Wait for the menu to be on the DISPLAY, not merely for the zone
        # counter to be set: C01D holds 1 within a second of the reset, tens of
        # seconds before the ROM has finished starting and drawn anything, and
        # buttons pressed before then go nowhere.
        deadline = time.time() + 240
        while time.time() < deadline:
            d = display()
            if d["cr"].strip().isdigit() and d["p1"].strip():
                break
            time.sleep(1)
        else:
            print("FAIL: never reached the ajustes menu", file=sys.stderr)
            return 1
        time.sleep(2)

        rows = []
        seen = set()
        for i in range(steps):
            z = mem(s["zone"])[0]
            if z in seen:
                break
            seen.add(z)
            row = {"n": i + 1, "zone": "0x%02X" % z}
            row.update(snapshot(s))
            if s["extra"]:
                row["C7F0_FF"] = ' '.join("%02X" % b for b in mem(*s["extra"]))
            row["nv"] = ' '.join("%02X" % b for b in mem(*s["nv"]))
            rows.append(row)
            if not next_zone(s["zone"]):
                print("  (the zone stopped advancing after 0x%02X)" % z,
                      file=sys.stderr)
                break

        if as_json:
            print(json.dumps({"rom": rom, "zones": rows}, indent=1))
        else:
            print("\n%s - %d zones reached" % (rom, len(rows)))
            print("  %-4s %-8s %-8s %-8s %-8s %-4s" %
                  ("zone", "p1", "p2", "p3", "p4", "cr"))
            for r in rows:
                d = r["display"]
                print("  %-4s %-8s %-8s %-8s %-8s %-4s" %
                      (r["zone"], d["p1"].strip(), d["p2"].strip(),
                       d["p3"].strip(), d["p4"].strip(), d["cr"].strip()))
            if s["extra"]:
                print("\n  C7F0..C7FF per zone:")
                for r in rows:
                    print("    %-5s %s" % (r["zone"], r["C7F0_FF"]))
        return 0
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="supstarfa", choices=sorted(SETS) + ["all"])
    ap.add_argument("--steps", type=int, default=30)
    ap.add_argument("--json", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(BINARY):
        print("FAIL: %s not built" % BINARY, file=sys.stderr)
        return 2
    worst = 0
    for rom in (sorted(SETS) if args.rom == "all" else (args.rom,)):
        worst = max(worst, run(rom, args.steps, args.json))
    return worst


if __name__ == "__main__":
    sys.exit(main())
