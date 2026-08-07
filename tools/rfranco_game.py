#!/usr/bin/env python3
"""Play a complete game of Super Star through the driver and assert on it.

`rfranco_check.py` proves the machine boots, takes a coin and lights a digit.
This goes further: it plays a whole game on either ROM set and asserts on the
things a player would see - the ball is served, playfield contacts score, the
ball number advances, the bonus is paid, the game ends and the final score is
held. Everything it asserts on is read back out of the running machine, either
from the segment map or from the lamp/solenoid matrices, so a pass means the
driver really produced it.

    tools/rfranco_game.py [--rom supstarf|supstarfa|all] [--players N] [--verbose]

Exit code 0 = all checks passed, 1 = a check failed, 2 = could not run.

Notes on the two things that are easy to get wrong when driving this machine
from outside:

  * A coin contact must be a pulse. Held closed for more than ~200 ms it trips
    the fault path (set 1: 0x055C) and wedges the machine for good.
  * The ball trough (caida de bolas, switch 27) is a level, not a pulse. Close
    it to drain; the driver opens it again by itself when the game fires SALIDA
    BOLAS, because that is what the real outhole kicker does.
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

PINMAME = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "pinmame")
BINARY = os.path.join(PINMAME, "xpinmamed.x11")
ROMPATH = os.path.join(PINMAME, "roms")
PORT = 8933

ROMS = ("supstarf", "supstarfa")

# Segment indices, from the 8279 RAM map in rfrancogames.c.
PLAYER = [(0, 7), (8, 7), (16, 7), (24, 7)]
CREDIT = (32, 2)

# Lamp numbers, col*10 + row + 1 (the driver installs this scheme explicitly).
L_FALTA_B   = 11          # IC1 FASE B code 0
L_PLAYER    = {1: 12, 2: 13, 3: 2, 4: 3}   # jugador 1..4
L_BALL      = {1: 31, 2: 32, 3: 33, 4: 34, 5: 35}
L_GAMEOVER  = 36          # fin de juego
L_START     = 45          # pulsador partidas (IC3 FASE A code 4, lit on a credit)
L_AVANCE1   = 21          # avance 10000, the bottom of the bonus ladder

# Solenoids, IC7 decoder code + 1.
S_KNOCKER   = 2
S_COINCOIL  = 3
S_METER25   = 4
S_BANK_L    = 7
S_BANK_R    = 9
S_BALLREL   = 10

SW_COIN25   = 25
SW_DRAIN    = 27
SW_START    = 28

SEVEN = {0x3F: '0', 0x06: '1', 0x5B: '2', 0x4F: '3', 0x66: '4', 0x6D: '5',
         0x7D: '6', 0x07: '7', 0x7F: '8', 0x6F: '9', 0x00: ' ', 0x79: 'E'}

BOOT_TIMEOUT = 240
STEP_TIMEOUT = 90


class Machine(object):
    def __init__(self, port, verbose=False):
        self.port = port
        self.verbose = verbose

    def api(self, path, timeout=10):
        url = "http://localhost:%d/api/%s" % (self.port, path)
        with urllib.request.urlopen(url, timeout=timeout) as r:
            body = r.read().decode()
        try:
            return json.loads(body)
        except json.JSONDecodeError:
            return body

    # -- reading the machine ------------------------------------------------
    def segments(self):
        s = self.api("info")["segments"]
        return [int(s[i * 4:i * 4 + 4], 16) for i in range(len(s) // 4)]

    def display(self):
        s = self.segments()

        def grp(off, n):
            return ''.join(SEVEN.get(s[off + i], '?') for i in range(n))
        return {
            "p1": grp(*PLAYER[0]), "p2": grp(*PLAYER[1]),
            "p3": grp(*PLAYER[2]), "p4": grp(*PLAYER[3]),
            "cr": grp(*CREDIT),
        }

    def score(self, player=1):
        t = self.display()["p%d" % player].strip()
        return int(t) if t.isdigit() else None

    def credits(self):
        t = self.display()["cr"].strip()
        return int(t) if t.isdigit() else None

    def lamps(self):
        return set(l["num"] for l in self.api("lamps")["lamps"] if l["active"])

    def mem(self, addr, size=1):
        return self.api("debugger/memory?addr=%04X&size=%d&cpu=0" % (addr, size))["data"]

    # -- driving it ---------------------------------------------------------
    def sw(self, num, val, pulse=None):
        q = "input?sw=%d&val=%d" % (num, val)
        if pulse:
            q += "&pulse=%d" % pulse
        self.api(q)

    def pulse(self, num, ms=250):
        self.sw(num, 1, ms)

    def hold(self, num, secs=1.2, gap=1.0):
        """A press long enough for the ROM to see it.

        Headless this runs at well under real time, and the cabinet row is
        polled through a sound-command round trip rather than read directly,
        so a couple of hundred milliseconds of wall clock is not reliably a
        press at all. Coins are the exception - they must NOT be held, see the
        module docstring - so this is for the start button only.
        """
        self.sw(num, 1)
        time.sleep(secs)
        self.sw(num, 0)
        time.sleep(gap)

    def press_until(self, num, pred, timeout=60, settle=8):
        """Press, then give the ROM time to react before pressing again.

        Pressing again too soon is not harmless on the start button: a second
        press while a game is starting adds a second player, which is a
        perfectly good machine behaviour and doubles how long everything takes.
        """
        end = time.time() + timeout
        while time.time() < end:
            self.hold(num)
            if self.wait(pred, timeout=settle, poll=0.5):
                return True
        return False

    # -- the solenoid action log -------------------------------------------
    def watch_solenoids(self, lo=1, hi=20):
        self.api("monitor?cmd=clear")
        for i in range(lo, hi + 1):
            self.api("monitor?cmd=add&type=sol&id=%d" % i)
        self.api("monitor/log?cmd=clear")

    def fired(self, clear=True):
        """Solenoid numbers seen going active since the last call."""
        acts = self.api("monitor/log")["actions"]
        if clear:
            self.api("monitor/log?cmd=clear")
        return [a["id"] for a in acts if a["type"] == "sol" and a["val"]]

    def wait(self, pred, timeout=STEP_TIMEOUT, poll=0.5):
        end = time.time() + timeout
        while time.time() < end:
            v = pred()
            if v:
                return v
            time.sleep(poll)
        return None


class Report(object):
    def __init__(self):
        self.ok = True
        self.rows = []

    def check(self, name, passed, detail):
        self.ok &= bool(passed)
        self.rows.append((name, bool(passed), detail))
        print("  [%s] %-46s %s" % ("ok" if passed else "XX", name, detail))
        return bool(passed)

    def note(self, text):
        print("      %s" % text)


def play(m, rep, balls_expected, verbose):
    """One complete game: coin, start, score, drain each ball, game over."""
    fired = []

    # --- attract -----------------------------------------------------------
    lamps = m.lamps()
    rep.check("attract: FIN DE JUEGO lit", L_GAMEOVER in lamps,
              "lamps %s" % sorted(lamps))

    # --- coin --------------------------------------------------------------
    m.watch_solenoids()
    before = m.credits()
    m.pulse(SW_COIN25, 150)
    got = m.wait(lambda: m.credits() == (before or 0) + 1, timeout=20)
    after = m.credits()
    rep.check("coin gives a credit", got, "credits %s -> %s" % (before, after))
    f = m.fired()
    rep.check("coin fires the 25 pta meter (sol %d)" % S_METER25,
              S_METER25 in f, "solenoids %s" % sorted(set(f)))
    lit = m.wait(lambda: L_START in m.lamps(), timeout=30)
    rep.check("start button lamp lit with a credit (lamp %d)" % L_START,
              lit, "lamps %s" % sorted(m.lamps()))

    # --- start -------------------------------------------------------------
    got = m.press_until(SW_START, lambda: m.display()["p1"].strip() == "0")
    rep.check("start button starts a game", got, "player 1 display %r" % m.display()["p1"])
    rep.check("the credit is taken", m.credits() == (after - 1),
              "credits %s -> %s" % (after, m.credits()))

    got = m.wait(lambda: S_BALLREL in m.fired(clear=False), timeout=60)
    f = m.fired()
    rep.check("ball served: SALIDA BOLAS (sol %d) fires" % S_BALLREL,
              S_BALLREL in f, "solenoids %s" % sorted(set(f)))

    lamps = m.wait(lambda: (L_PLAYER[1] in m.lamps() and L_BALL[1] in m.lamps())
                   and m.lamps(), timeout=30)
    lamps = lamps or m.lamps()
    rep.check("JUGADOR 1 lamp (%d) lit" % L_PLAYER[1], L_PLAYER[1] in lamps,
              "lamps %s" % sorted(lamps))
    rep.check("BOLA 1 lamp (%d) lit" % L_BALL[1], L_BALL[1] in lamps,
              "lamps %s" % sorted(lamps))
    rep.check("FIN DE JUEGO lamp (%d) out during play" % L_GAMEOVER,
              L_GAMEOVER not in lamps, "lamps %s" % sorted(lamps))

    # --- score -------------------------------------------------------------
    # Contacts that score without needing the ball anywhere in particular:
    #   11 10 puntos, 17 100 puntos, 12/18 bumpers, 31/32 pasillos inferiores,
    #   45/46 pasillos superiores.
    prev = m.score(1)
    steps = []
    for sw in (11, 17, 12, 18, 31, 32, 45, 46):
        m.pulse(sw, 300)
        got = m.wait(lambda: m.score(1) != prev, timeout=15)
        now = m.score(1)
        steps.append((sw, prev, now))
        if verbose:
            rep.note("switch %-2d  %s -> %s" % (sw, prev, now))
        prev = now
    rose = [s for s in steps if s[2] is not None and s[1] is not None and s[2] > s[1]]
    rep.check("playfield contacts score", len(rose) == len(steps),
              "%d of %d contacts scored, %s -> %s" %
              (len(rose), len(steps), steps[0][1], prev))

    # --- the drop target banks --------------------------------------------
    # The five left drop targets have to be held down together; the game then
    # lights ESPECIAL IZQUIERDA. Same on the right.
    for bank, targets, lamp, sol in (("left", (33, 34, 35, 36, 37), 52, S_BANK_L),
                                     ("right", (38, 41, 42, 43, 44), 42, S_BANK_R)):
        for sw in targets:
            m.sw(sw, 1)
            time.sleep(0.6)
        lit = m.wait(lambda: lamp in m.lamps(), timeout=20)
        rep.check("%s drop target bank lights ESPECIAL (lamp %d)" % (bank, lamp),
                  lit, "lamps %s" % sorted(m.lamps()))
        for sw in targets:
            m.sw(sw, 0)
        time.sleep(0.5)

    # --- collect a special: the knocker ------------------------------------
    m.fired()
    cr = m.credits()
    m.pulse(14, 300)          # rampa especial izquierda
    got = m.wait(lambda: m.credits() != cr, timeout=20)
    f = m.fired()
    rep.check("collecting a special awards a replay", got,
              "credits %s -> %s" % (cr, m.credits()))
    rep.check("... and bangs the knocker (sol %d)" % S_KNOCKER,
              S_KNOCKER in f, "solenoids %s" % sorted(set(f)))

    # --- play the balls out ------------------------------------------------
    # The end-of-ball bonus is the avance ladder, so build some of it up on
    # each ball before draining: the two lower rollovers step it.
    bonuses = []
    before_drain = m.score(1)
    for ball in range(1, balls_expected):
        m.fired()
        m.sw(SW_DRAIN, 1)
        nxt = ball + 1
        got = m.wait(lambda: L_BALL.get(nxt) in m.lamps(), timeout=STEP_TIMEOUT)
        rep.check("ball %d ends, BOLA %d lamp (%d) lights" % (ball, nxt, L_BALL[nxt]),
                  got, "lamps %s" % sorted(m.lamps()))
        f = m.fired()
        rep.check("ball %d served (sol %d)" % (nxt, S_BALLREL), S_BALLREL in f,
                  "solenoids %s" % sorted(set(f)))
        s = m.score(1)
        bonuses.append(None if (s is None or before_drain is None) else s - before_drain)
        rep.check("score does not go backwards across ball %d -> %d" % (ball, nxt),
                  s is not None and before_drain is not None and s >= before_drain,
                  "score %s -> %s (end of ball bonus %s)" % (before_drain, s, bonuses[-1]))
        # play the new ball a little, and step the avance ladder
        for sw in (11, 17, 31, 32, 45, 46):
            m.pulse(sw, 300)
            time.sleep(0.6)
        before_drain = m.score(1)

    # --- last ball, game over ---------------------------------------------
    m.fired()
    m.sw(SW_DRAIN, 1)
    got = m.wait(lambda: L_GAMEOVER in m.lamps(), timeout=STEP_TIMEOUT)
    rep.check("last ball ends the game (FIN DE JUEGO, lamp %d)" % L_GAMEOVER,
              got, "lamps %s" % sorted(m.lamps()))
    final = m.score(1)
    bonuses.append(None if (final is None or before_drain is None)
                   else final - before_drain)
    rep.check("final score is held on the display",
              final is not None and before_drain is not None and final >= before_drain,
              "score %s (last bonus %s)" % (final, bonuses[-1]))
    rep.check("an end-of-ball bonus was paid",
              any(b for b in bonuses if b), "per-ball bonus %s" % bonuses)
    lamps = m.lamps()
    rep.check("no BOLA lamp left lit after the game",
              not (set(L_BALL.values()) & lamps), "lamps %s" % sorted(lamps))
    time.sleep(3)
    rep.check("the score survives into attract", m.score(1) == final,
              "score %s" % m.score(1))
    rep.check("the fault handler never latched", m.mem(0xC01C)[0] == 0,
              "C01C=0x%02X" % m.mem(0xC01C)[0])
    return final


def run(rom, players, verbose):
    proc = subprocess.Popen(
        [BINARY, "-headless", "-nosound", "-httpport", str(PORT),
         "-rompath", ROMPATH, rom],
        stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL, start_new_session=True)
    try:
        m = Machine(PORT, verbose)
        end = time.time() + BOOT_TIMEOUT
        while time.time() < end:
            try:
                m.api("info", timeout=2)
                break
            except (urllib.error.URLError, OSError, TimeoutError):
                time.sleep(1)
        else:
            print("FAIL: debugger did not come up", file=sys.stderr)
            return 2

        print("booted %s, waiting for attract ..." % rom)
        if not m.wait(lambda: m.credits() == 0, timeout=BOOT_TIMEOUT, poll=1):
            print("FAIL: never reached attract", file=sys.stderr)
            return 1
        # The credit digit comes up a little before the attract loop is really
        # turning; give the ROM's own startup the last few seconds it wants.
        time.sleep(5)

        # Balls per game is an operator adjustment, zone 1, and the ROM has
        # already written its default by now. Read it rather than assuming.
        balls_addr = {"supstarf": 0xC1E9, "supstarfa": 0xC1EA}[rom]
        balls = m.mem(balls_addr)[0]
        if not 1 <= balls <= 5:
            balls = 3
        print("balls per game (zone 1, %04X) = %d\n" % (balls_addr, balls))

        rep = Report()
        play(m, rep, balls, verbose)
        print("\n%s: %s" % (rom, "PASS" if rep.ok else "FAIL"))
        return 0 if rep.ok else 1
    finally:
        try:
            os.killpg(os.getpgid(proc.pid), signal.SIGTERM)
        except OSError:
            pass


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--rom", default="supstarf", choices=list(ROMS) + ["all"])
    ap.add_argument("--players", type=int, default=1)
    ap.add_argument("--verbose", action="store_true")
    args = ap.parse_args()
    if not os.path.exists(BINARY):
        print("FAIL: %s not built" % BINARY, file=sys.stderr)
        return 2
    worst = 0
    for rom in (ROMS if args.rom == "all" else (args.rom,)):
        worst = max(worst, run(rom, args.players, args.verbose))
        print()
    return worst


if __name__ == "__main__":
    sys.exit(main())
