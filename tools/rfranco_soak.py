#!/usr/bin/env python3
"""Long soak: play games with randomised switch traffic and watch for trouble.

`rfranco_check.py` proves the machine is healthy at rest and `rfranco_game.py`
proves one scripted game plays through. This is the third leg: many games, with
the playfield contacts pulsed in a random order and at random times, looking for
the failures that only turn up after a while - the ROM's fault handler latching,
the display sticking on the fault fill, the stack walking away, a CPU stopping,
or the game simply refusing to start another game.

    tools/rfranco_soak.py [--rom supstarf|supstarfa|all] [--games N] [--seed N]

Exit code 0 = clean, 1 = something went wrong, 2 = could not run.

Contacts are pulsed, never held. Two reasons: a coin held closed for more than
~200 ms wedges the machine by design, and on `supstarfa` a playfield contact held
closed for about 128 game-loop passes trips the stuck-contact watchdog, which is
also by design. Both are real machine behaviour and neither is what this is
looking for.
"""
import argparse
import os
import random
import signal
import subprocess
import sys
import time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from rfranco_game import (Machine, Report, BINARY, ROMPATH, ROMS,   # noqa: E402
                          SW_COIN25, SW_DRAIN, SW_START, L_BALL, L_GAMEOVER,
                          L_START, S_BALLREL)

PORT = 8937
FALTA = 0xC01C
EE_FILL = 0x0079
SP_SLACK = 0x0400
SP_RESET = {"supstarf": 0xC7FF, "supstarfa": 0xC7CF}

# Everything the playfield can present. The drop targets are pulsed rather than
# held, so the banks rarely complete - that is fine, this is looking for
# robustness rather than for a particular rule firing.
PLAYFIELD = [11, 12, 13, 14, 15, 16, 17, 18,
             31, 32, 33, 34, 35, 36, 37, 38,
             41, 42, 43, 44, 45, 46, 47]


def health(m, rom, rep, tag):
    ok = True
    falta = m.mem(FALTA)[0]
    ok &= rep.check("%s: fault handler not latched" % tag, falta == 0,
                    "C01C=0x%02X" % falta)
    segs = m.segments()
    ee = sum(1 for v in segs[:34] if v == EE_FILL)
    ok &= rep.check("%s: display not on the fault fill" % tag, ee == 0,
                    "%d of 34 digits" % ee)
    sp = m.api("debugger/state")["cpus"][0]["sp"]
    base = SP_RESET[rom]
    ok &= rep.check("%s: stack near its reset value" % tag,
                    base - SP_SLACK <= sp <= base, "SP=0x%04X" % sp)
    a = m.api("debugger/state")["cpus"]
    time.sleep(0.4)
    b = m.api("debugger/state")["cpus"]
    ok &= rep.check("%s: sound CPU executing" % tag, a[1]["pc"] != b[1]["pc"],
                    "pc 0x%03X -> 0x%03X" % (a[1]["pc"], b[1]["pc"]))
    return ok


def play_out(m, balls, tries=12):
    """Drain until the game is over. Returns True if it got there."""
    for _ in range(tries):
        if L_GAMEOVER in m.lamps():
            return True
        # Score at least once first. A ball that has not scored since it was
        # served is not counted: the ROM simply serves it again, for ever. That
        # is the machine's own rule, not a driver quirk - measured by draining
        # the same ball twice with nothing touched (no advance either time) and
        # then once after a single 10-point contact (advanced immediately).
        m.pulse(11, 300)
        time.sleep(1.0)
        # Clear the solenoid log BEFORE closing the trough. Leaving the serve
        # that started this ball in the log makes the wait below return at once
        # and burns every retry in a couple of seconds without the ROM ever
        # having been given time to end the ball.
        m.fired()
        m.sw(SW_DRAIN, 1)
        m.wait(lambda: (L_GAMEOVER in m.lamps()) or
               (S_BALLREL in m.fired(clear=False)), timeout=90)
        lamps = m.lamps()
        for n, l in L_BALL.items():
            if l in lamps:
                balls.add(n)
    return L_GAMEOVER in m.lamps()


def one_game(m, rng, pulses):
    """Coin, start, random traffic, drain out. Returns (started, balls_seen)."""
    balls = set()
    # Whatever state the last game left behind, get back to attract first.
    if L_GAMEOVER not in m.lamps():
        play_out(m, balls)
    m.pulse(SW_COIN25, 150)
    if not m.wait(lambda: L_START in m.lamps(), timeout=40):
        return False, len(balls)
    if not m.press_until(SW_START, lambda: L_BALL[1] in m.lamps(), timeout=60):
        return False, len(balls)

    balls.add(1)
    fired = 0
    end = time.time() + 90
    while time.time() < end and L_GAMEOVER not in m.lamps():
        for _ in range(rng.randint(1, 4)):
            m.pulse(rng.choice(PLAYFIELD), rng.choice((120, 200, 300)))
            fired += 1
            time.sleep(rng.uniform(0.05, 0.35))
        lamps = m.lamps()
        for n, l in L_BALL.items():
            if l in lamps:
                balls.add(n)
        if fired >= pulses:
            break
    play_out(m, balls)
    return True, len(balls)


def run(rom, games, seed, verbose):
    rng = random.Random(seed)
    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        m = Machine(PORT)
        end = time.time() + 240
        while time.time() < end:
            try:
                m.api("info", timeout=2)
                break
            except Exception:
                time.sleep(1)
        else:
            print("FAIL: debugger did not come up", file=sys.stderr)
            return 2
        if not m.wait(lambda: m.credits() == 0, timeout=240, poll=1):
            print("FAIL: never reached attract", file=sys.stderr)
            return 1
        time.sleep(5)
        m.watch_solenoids()

        rep = Report()
        print("soaking %s: %d games, seed %d" % (rom, games, seed))
        health(m, rom, rep, "before")
        started = 0
        ballsum = 0
        t0 = time.time()
        for g in range(games):
            ok, balls = one_game(m, rng, pulses=40)
            started += 1 if ok else 0
            ballsum += balls
            if verbose or not ok:
                print("  game %2d: started=%s balls seen=%d score=%s falta=0x%02X"
                      % (g + 1, ok, balls, m.display()["p1"].strip(),
                         m.mem(FALTA)[0]))
            if m.mem(FALTA)[0] != 0:
                rep.check("game %d: fault handler latched mid-soak" % (g + 1),
                          False, "C01C=0x%02X" % m.mem(FALTA)[0])
                break
        elapsed = time.time() - t0
        print("  %d of %d games started, %d ball changes seen, %.0fs"
              % (started, games, ballsum, elapsed))
        rep.check("every game started", started == games,
                  "%d/%d" % (started, games))
        rep.check("balls advanced during the soak", ballsum > games,
                  "%d ball numbers seen across %d games" % (ballsum, games))
        health(m, rom, rep, "after")
        print("\n%s: %s" % (rom, "PASS" if rep.ok else "FAIL"))
        return 0 if rep.ok else 1
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="all", choices=list(ROMS) + ["all"])
    ap.add_argument("--games", type=int, default=6)
    ap.add_argument("--seed", type=int, default=1986)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(BINARY):
        print("FAIL: %s not built" % BINARY, file=sys.stderr)
        return 2
    worst = 0
    for rom in (ROMS if args.rom == "all" else (args.rom,)):
        worst = max(worst, run(rom, args.games, args.seed, args.verbose))
        print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
