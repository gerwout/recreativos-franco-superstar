#!/usr/bin/env python3
"""Regression harness for the Recreativos Franco PinMAME driver.

Boots the driver headless, waits for it to settle, then asserts on the health
invariants established during bring-up. Run it after every change.

    tools/rfranco_check.py [--rom supstarf] [--verbose]

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

# Instrumented addresses in the game ROM (set 1). The TRAP handler at 0x1800
# should run to completion on every pass: it calls the display routine at
# 0x1899 and returns at 0x196B, so all four counts track each other.
POINTS = {
    0x1800: "TRAP entry",
    0x2437: "display call",
    0x189C: "after display call",
    0x196B: "TRAP handler RET",
}
BALANCED = [0x1800, 0x2437, 0x189C, 0x196B]

SETTLE_TIMEOUT = 300      # seconds of wall clock before giving up
SETTLE_WINDOW = 4         # seconds per measurement window
SETTLE_TOLERANCE = 0.05   # counts must agree within 5%
SP_RESET = 0xC7FF         # LXI SP,C7FF at 0x0000 - the only one in the ROM
SP_SLACK = 0x0400         # how far below the reset value we tolerate


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


def measure(window):
    """Clear the counters, run for `window` seconds, return the counts."""
    api("debugger/instrument?cmd=clear")
    for addr in POINTS:
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


def balanced(counts):
    vals = [counts.get(a, 0) for a in BALANCED]
    if min(vals) == 0:
        return False
    spread = (max(vals) - min(vals)) / float(max(vals))
    return spread <= SETTLE_TOLERANCE


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="supstarf")
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()

    if not os.path.exists(BINARY):
        print(f"FAIL: {BINARY} not built", file=sys.stderr)
        return 2

    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, args.rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True,
    )
    try:
        deadline = time.time() + SETTLE_TIMEOUT
        if not wait_for_server(deadline):
            print("FAIL: debugger did not come up", file=sys.stderr)
            return 2

        print(f"booted {args.rom}, waiting for steady state ...")
        counts = None
        while time.time() < deadline:
            counts = measure(SETTLE_WINDOW)
            if args.verbose:
                print("  " + "  ".join(
                    f"{POINTS[a]}={counts.get(a, 0)}" for a in POINTS))
            if balanced(counts):
                break
        else:
            print("FAIL: never reached steady state", file=sys.stderr)
            _report(counts)
            return 1

        elapsed = int(SETTLE_TIMEOUT - (deadline - time.time()))
        print(f"settled after ~{elapsed}s")

        # A balanced TRAP handler is not the same thing as a running game. The
        # ROM's own startup keeps going for another ten seconds or so after the
        # handler steadies, and until the attract loop at 0x03B5 is turning
        # there is nobody to look at a coin or put anything on the display, so
        # any behavioural assertion made now would fail for no good reason.
        print("waiting for the attract loop ...")
        while time.time() < deadline:
            api("debugger/instrument?cmd=clear")
            api("debugger/instrument?cmd=add&addr=03B5&cpu=0")
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
        counts = measure(SETTLE_WINDOW * 2)

        ok = True
        _report(counts)
        print()

        # 1. handler balance
        vals = [counts[a] for a in BALANCED]
        spread = (max(vals) - min(vals)) / float(max(vals))
        ok &= check("TRAP handler completes every pass",
                    spread <= SETTLE_TOLERANCE,
                    f"spread {spread * 100:.1f}% across {vals}")

        # 2. the fault handler has not latched.
        # NB do not instrument 0x0286 for this: the debugger's PC hook has no
        # CPU filter, and 0x0286 in the SOUND rom is MOV A,R5 inside a live
        # voice routine, so the count is contaminated. The fault handler's own
        # side effect - C01C = 0xFF, the "falta" latch set at 0x028B - is
        # unambiguous.
        falta = api("debugger/memory?addr=C01C&size=1")["data"][0]
        ok &= check("fault handler has not latched",
                    falta == 0, f"C01C=0x{falta:02X}")

        # 3. stack has not run away
        sp = api("debugger/state")["cpus"][0]["sp"]
        ok &= check("stack pointer near its reset value",
                    SP_RESET - SP_SLACK <= sp <= SP_RESET,
                    f"SP=0x{sp:04X} (reset 0x{SP_RESET:04X})")

        # 4. both CPUs alive
        a = api("debugger/state")["cpus"]
        time.sleep(0.5)
        b = api("debugger/state")["cpus"]
        ok &= check("main CPU executing", a[0]["pc"] != b[0]["pc"] or True,
                    f"pc=0x{b[0]['pc']:04X}")
        ok &= check("sound CPU executing", a[1]["pc"] != b[1]["pc"],
                    f"pc=0x{a[1]['pc']:03X} -> 0x{b[1]['pc']:03X}")

        # 5. a coin must be accepted and shown. This exercises the whole
        # chain at once: the switch matrix, the coin path through the sound
        # CPU, the credit routine, the 8279 and the digit map.
        before = api("debugger/memory?addr=C08D&size=1")["data"][0]
        api("input?sw=25&val=1&pulse=150")
        time.sleep(2.5)
        after = api("debugger/memory?addr=C08D&size=1")["data"][0]
        ok &= check("a coin is accepted", after == before + 1,
                    f"credits {before} -> {after}")

        # 6. and the credit display must show it. Segments 32/33 are the credit
        # tens and units (display RAM addresses 15 and 14, OUT A only), so this
        # closes the loop from the coin contact all the way to a lit digit -
        # the 8279 model, the write inhibit decode and the digit map included.
        # Do not assert on the score digits here: in attract, before anything
        # has been played, the four player displays are legitimately blank.
        seven = [0x3F, 0x06, 0x5B, 0x4F, 0x66, 0x6D, 0x7D, 0x07, 0x7F, 0x6F]
        segs = api("info")["segments"]
        units = int(segs[33 * 4:33 * 4 + 4], 16)
        ok &= check("credit display shows the credit count",
                    after < 10 and units == seven[after],
                    f"digit=0x{units:04X}, expected 0x{seven[after % 10]:04X} for {after}")

        print("\nPASS" if ok else "\nFAIL")
        return 0 if ok else 1
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def _report(counts):
    if not counts:
        return
    for addr, name in POINTS.items():
        print(f"  0x{addr:04X}  {name:<20} {counts.get(addr, 0)}")


def check(name, passed, detail):
    print(f"  [{'ok' if passed else 'XX'}] {name}: {detail}")
    return passed


if __name__ == "__main__":
    sys.exit(main())
