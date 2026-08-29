#!/usr/bin/env python3
"""Exercise the front-end-owned trough path: g_fHandleMechanics == 0.

The driver models the ball movement that works CAIDA DE BOLAS (switch 27) -
SALIDA BOLAS firing opens the contact, the drain event closes it - and gates
that model on g_fHandleMechanics, PinMAME's standard "who owns the mechanics"
flag (rfranco.c, rfranco_ownsBall). A front end that owns its own ball physics
sets the flag to 0 and drives the contact itself; VPinMAME exposes it as
Controller.HandleMechanics, libpinmame defaults it to 0.

The standalone build pins the flag at 0xff, so this path used to be untestable
from the harnesses and was recorded as a known gap. The debug API now exposes
the flag (/api/mechanics), which is what this harness uses: it plays the front
end's role by hand and asserts the driver keeps its hands off.

What is asserted, in order:
  1. the flag defaults to 0xff and the endpoint can set it;
  2. with the flag 0, an opened switch 27 STAYS open - the driver never
     reasserts the trough;
  3. a game started with an empty trough takes the credit and never fires
     SALIDA BOLAS, without faulting (C01C stays 0) - the machine's own
     ball-missing behaviour;
  4. closing 27 (the ball arrives) makes the pending serve fire;
  5. a full front-end-driven ball works: open on serve, score, close to drain,
     and the next serve follows;
  6. the driver did not touch the contact anywhere in (4)-(5): every edge on
     switch 27 in that window is one this harness wrote.

Run tools/rfranco_mech.py [--rom supstarf1|supstarf4|all] [--verbose].
Exit code 0 = pass, 1 = fail, 2 = could not run.
"""
import argparse
import os
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfranco_game import (Machine, Report, BINARY, ROMPATH, ROMS, CFGDIR,   # noqa: E402
                          S_BALLREL, SW_COIN25, SW_DRAIN, SW_START,
                          BOOT_TIMEOUT)
from rfranco_check import FALTA   # noqa: E402

PORT = 8938

# The serve decision is polled by the game loop through a sound-command round
# trip, and headless runs well under real time; a window shorter than this
# risks calling "did not serve" on a machine that merely had not got there yet.
NO_SERVE_WINDOW = 25   # seconds we require SALIDA BOLAS to stay quiet
SERVE_WINDOW = 45      # seconds we allow a legitimate serve to take


def run(rom, verbose):
    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, "-cfg_directory", CFGDIR, rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
        start_new_session=True)
    m = Machine(PORT, verbose)
    rep = Report()
    try:
        end = time.time() + BOOT_TIMEOUT
        while time.time() < end:
            try:
                m.api("info", timeout=2)
                break
            except Exception:
                time.sleep(1)
        else:
            print("FAIL: debugger did not come up", file=sys.stderr)
            return 2

        # -- 1. the flag itself --------------------------------------------
        v = m.api("mechanics")["handleMechanics"]
        rep.check("flag defaults to 0xff", v == 0xff, "handleMechanics=%d" % v)
        v = m.api("mechanics?val=0")["handleMechanics"]
        rep.check("endpoint sets it to 0", v == 0, "handleMechanics=%d" % v)

        # Boot ran with the flag at its default, so the driver has already
        # seeded the trough closed. From here on it is ours. Empty it.
        m.sw(SW_DRAIN, 0)

        # Let the machine finish coming up with the trough open. Attract does
        # not need a ball; only serving one does.
        if not m.wait(lambda: m.credits() is not None, timeout=BOOT_TIMEOUT):
            print("FAIL: machine never reached attract", file=sys.stderr)
            return 2
        time.sleep(3)
        v27 = m.switch(SW_DRAIN)
        rep.check("switch 27 stays open (driver hands off)",
                  v27 is not None and not v27,
                  "switch 27 reads %s" % v27)

        # -- 3. start with an empty trough ---------------------------------
        m.watch_solenoids()
        before = m.credits() or 0
        m.pulse(SW_COIN25, 150)
        m.wait(lambda: (m.credits() or 0) > before, timeout=20)
        m.hold(SW_START)
        quiet_until = time.time() + NO_SERVE_WINDOW
        served_early = None
        while time.time() < quiet_until:
            if S_BALLREL in m.fired(clear=False):
                served_early = True
                break
            time.sleep(1)
        rep.check("no serve with an empty trough", not served_early,
                  "SALIDA BOLAS quiet for %ds" % NO_SERVE_WINDOW
                  if not served_early else "SALIDA BOLAS fired")
        falta = m.mem(FALTA)[0]
        rep.check("no fault while waiting", falta == 0, "C01C=0x%02X" % falta)
        v27 = m.switch(SW_DRAIN)
        rep.check("driver still not touching 27",
                  v27 is not None and not v27,
                  "switch 27 reads %s" % v27)

        # -- 4. the ball arrives -------------------------------------------
        m.fired()                      # clear the log
        m.sw(SW_DRAIN, 1)
        served = m.wait(lambda: S_BALLREL in m.fired(clear=False),
                        timeout=SERVE_WINDOW)
        rep.check("closing 27 releases the pending serve", served,
                  "SALIDA BOLAS %s" % ("fired" if served else
                                       "never fired in %ds" % SERVE_WINDOW))

        # -- 5. one front-end-driven ball ----------------------------------
        # The kicker threw the ball out; the front end opens the contact.
        m.sw(SW_DRAIN, 0)
        time.sleep(4)
        v27 = m.switch(SW_DRAIN)
        rep.check("driver left 27 open after the serve",
                  v27 is not None and not v27,
                  "switch 27 reads %s" % v27)
        m.pulse(11, 200)               # score once so the drain counts
        time.sleep(4)
        m.fired()
        m.sw(SW_DRAIN, 1)              # ball drains into the trough
        next_serve = m.wait(lambda: S_BALLREL in m.fired(clear=False),
                            timeout=SERVE_WINDOW)
        rep.check("drain ends the ball, next ball serves", next_serve,
                  "SALIDA BOLAS %s" % ("fired again" if next_serve else
                                       "never fired in %ds" % SERVE_WINDOW))
        falta = m.mem(FALTA)[0]
        rep.check("no fault across the whole ball", falta == 0,
                  "C01C=0x%02X" % falta)

        # -- flag restore, as a last sanity of the endpoint ----------------
        v = m.api("mechanics?val=255")["handleMechanics"]
        rep.check("endpoint restores 0xff", v == 0xff, "handleMechanics=%d" % v)

        print("\n%s: %s" % (rom, "PASS" if rep.ok else "FAIL"))
        return 0 if rep.ok else 1
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="supstarf1", choices=ROMS + ("all",))
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(BINARY):
        print("FAIL: %s not built" % BINARY, file=sys.stderr)
        return 2
    worst = 0
    for rom in (ROMS if args.rom == "all" else (args.rom,)):
        print("== %s ==" % rom)
        worst = max(worst, run(rom, args.verbose))
    return worst


if __name__ == "__main__":
    sys.exit(main())
