# Questions for someone with a real Super Star

Everything in this project was derived from the ROM, the factory manual and the
emulation. A handful of things cannot be settled that way, and a few more would
be settled far more cheaply by ten seconds with the machine than by any amount
of further analysis.

The questions are ordered by value. **Q1 is the one that matters** — it is the
only place the driver ships an inference rather than a measurement, and it has
been open since the driver was written.

Where a photo or a phone video would answer better than words, that is said.
Video is genuinely useful: pitch survives a phone microphone intact, so a
recording is enough to settle anything about *which notes* play and *when*.

---

## Q1. Does the knocker fire when the machine awards a replay? ★

**Why it matters.** The ROM demonstrably drives 4028 output 1 when it awards a
replay — measured, on both firmware revisions, and nothing anywhere drives
output 0. But the manual's driver-board schematic, read by the output pin
numbers printed on it, puts **TACA (the knocker) on output 0** and an **unwired
pin on output 1**. Taken literally the machine would never knock, and the one
output the program does drive would go nowhere.

The driver assumes the manual transposed two adjacent rows — plausible, because
the same manual's own *fe de erratas* already corrects two transpositions of
exactly that kind (connector JA reversed, IC5 pins 10 and 11 swapped). But it is
an assumption, and it is the only one in the driver.

**What to ask:**

1. When the machine awards a *especial* (a replay — the credit counter goes up),
   **is there an audible mechanical bang**, distinct from the playfield sounds?
2. If yes: does it also bang when the machine is already at maximum credits and
   refuses the credit?
3. If no bang ever: is there a knocker coil fitted at all? It would be a solenoid
   on the cabinet or backbox, positioned to strike a plate or the cabinet wall.

**Easiest way to trigger one:** complete either drop-target bank so the ESPECIAL
lamp beside the corresponding outer lane lights, then send the ball up that lane.
Alternatively play past the replay score on the apron card.

**A phone video would settle it outright** if it catches the credit display at
the moment of the award. A knocker is a broadband bang and is trivially
distinguishable from the sound board's tones.

---

## Q2. Which decoder output does the replay coil hang off?

Only worth asking if Q1 says the machine *does* knock. Re-reading the manual
narrows this a long way, so the question is sharper than it first looks.

The manual's JL connector table (page 16) gives **JL6** the wire colour
*Am. Gr.* and names it **PARTIDA ESPECIAL**, and gives **JL10** no wire at all.
So the replay coil is real, and it is on JL6 — that much both manual tables
agree on, and it is not in doubt.

What is in doubt is only which of the CD4028's ten outputs JL6 hangs off. The
manual's IC7 table, read bottom-to-top as Q0…Q9, gives:

| | manual says | driver assumes |
|---|---|---|
| Q0 | JL6 TACA | (nothing — never driven) |
| Q1 | JL10 N.C. | JL6 TACA |
| Q2…Q9 | monedero, contadores, flipper, bancadas, picabolas, salida bolas | **identical** |

**Eight of the ten rows match the driver exactly** — only the bottom two are
swapped. That is the same single-transposition error the manual's own
*fe de erratas* already corrects twice elsewhere, which is why the driver assumes
it. But the ROM drives Q1, so if the table is right as printed the machine
cannot knock, and Q1 above will show that immediately.

Two things are worth knowing about how solid each side of this is. The
schematic reading is calibrated: the same sheet draws the three lamp decoders
in the same style, their true mappings are known from the ROM, and all
twenty-five verifiable rows agree with the printed pin numbers — so nobody has
misread the drawing; either the drawing is wrong in exactly those two rows, or
the machine really never knocks. And the errata's other entries are largely
*board-revision* notes, so a late rewire of TACA that never made the errata
would be in character for this manual.

**What to ask, if someone is willing to open the machine:** with the power off,
on the driver board (ref. 53/3308), does JL6's wire trace back to **pin 3** of
IC7 (that is Q0) or **pin 14** (Q1)? A photo of the board around IC7 and JL may
be enough for someone else to read it off.

---

## Q3. What happens when a game is started with no ball in the trough?

**Why it matters.** The emulation's behaviour here was recently changed and is
now: the machine takes the credit, starts the game, and then simply never fires
the ball-release coil — no fault, no error, it just waits. That is what the ROM
does, and it looks correct, but it has never been checked against the machine.

**What to ask:** with the ball removed from the outhole (or held out of it),
insert a credit and press start.

1. Does the machine take the credit and start?
2. Does it try to kick — a click or thump from the outhole kicker — repeatedly,
   once, or not at all?
3. Does anything appear on the displays, or any lamp indicate a problem?
4. When the ball is then returned to the trough, does it serve normally?

---

## Q4. Two drop-target positions the ROM and the manual disagree about

**Why it matters.** The manual's IC6 wiring table labels connector **JM7** as
*diana izquierda 2ª* and **JM8** as *diana izquierda 3ª*. The game ROM's own
contact test reports them the other way round. Fifteen of the sixteen positions
in that chain agree between the two sources; this is the only one that does not.
The ROM was taken as authoritative, since it is what the machine's own test
displays — but that is reasoning, not evidence.

**What to ask:** enter the operator contact test (both door switches up at
power-on, then step to zone 9 — see Q8) and press the **second** and **third**
drop targets of the **left** bank individually, counting from whichever end the
manual numbers them. Which contact number does the display report for each?

Expected if the ROM is right: 2nd target → **12**, 3rd target → **13**. If the
manual is right they are swapped.

---

## Q5. Does the sound board play more than one phrase for the ball-start sound?

*A confirmation rather than an open question — but a cheap one, and the only
thing that could overturn the analysis.*

**Why it matters.** The ball-start handler calls three tune launchers in turn,
but the tune terminator zeroes the 8035's stack-pointer field, so the return
from the first call is discarded and the second and third never play. That is
now established from the ROM itself, twice over — by tracing and by
cycle-accurate emulation, which measures the command running 48 186 machine
cycles against the 48 184 the first phrase alone takes.

Since the discard is the ROM's own instruction sequence, a real 8035 must behave
the same way. If the machine turns out to play a longer sound, then something
about the emulation of the MCS-48 stack is wrong and the conclusion collapses —
which is why it is worth thirty seconds to check.

**What to ask:** when a ball is served at the start of a game, is the sound a
**single short phrase**, or does it continue into a second and third part?

**A phone video of a ball being served answers this directly.**

---

## Q6. Two operator settings on the newer firmware — settled in emulation, cheap to confirm

Only relevant if the machine has the **newer** firmware — it has **19**
adjustment zones rather than 9. (Count them in the operator menu; see Q8.)

Both were open for a long time and have now been isolated on the emulated
machine with debugger instrumentation, so these are confirmations rather than
questions:

- **Zone 13** is the extra-ball cap **per ball in play** (not per game): with it
  at 1, a second extra ball cannot be earned until the earned one has been
  played, and draining without an earned extra ball resets the count. Confirm:
  set zone 13 to 1, earn and play an extra ball, and see whether the next ball
  can earn one again (it should).
- **Zone 19** is the **end-of-ball bonus collect**: at 1 the *avance* ladder
  value (with doble/triple multiplier) is counted down and paid when the ball
  drains; at 0 the drain pays nothing. Confirm: set it to 0 and check that no
  bonus countdown happens at the end of a ball.

---

## Q7. Confirmations that would take seconds

Each of these is believed correct but rests on a single source.

1. **The tilt lamp.** When the machine tilts, does the *FALTA* lamp light, and
   do all the score digits change to a single repeated character? (The emulation
   shows every digit displaying the same shape.)
2. **Solenoid 1 and 6.** The program never drives two of the ten coil outputs.
   One is believed to be a flipper-supply relay that this machine does not use —
   are the **flippers live as soon as the machine is switched on**, before any
   game is started?
3. **The two "expulsores".** The manual's parts list calls them *rechazadores*
   and the driver takes them to be the two slingshots at the bottom corners, not
   kickout holes. Is that right — **are there any holes on the playfield at all**?
4. **The 100 puntos lane.** On the newer firmware this is believed to score
   1,000 rather than 100. Which does the machine show?
5. **Ball count.** Does a game give 3 or 5 balls as the machine is currently set?

---

## Q8. How to reach the operator menus (for whoever is at the machine)

Included so the questions above can be answered without hunting.

The two switches inside the coin door select the mode **at power-on** — set them
first, then switch on.

| Door switches | Mode |
|---|---|
| both down | normal play |
| test up | lamp test, and the RAM audit counters |
| ajuste up | clears the credits |
| **both up** | **adjustments, and the contact test** |

Inside the adjustments menu the **start button** is the only control:

- with a door switch **down**, each press steps to the **next zone**
- with both **up**, each press steps the **value** of the current zone

The zone number shows in the **units digit of the credit display**. Zone 9 is
the contact test: player 1's display shows how many contacts are closed and
player 3's shows which one, using the numbers from the *CONTACTOS DE TABLERO*
list in the manual.

---

## What a decisive video would contain

If the owner is willing to record one pass, the most valuable single clip is:

1. Start with the **credit display in frame** alongside the playfield.
2. Complete a drop-target bank until an **ESPECIAL** lamp lights.
3. Send the ball up that outer lane to collect it.
4. Keep recording for a few seconds afterwards.

That one clip answers Q1 and Q2 together, and confirms the special-collection
behaviour at the same time. A previous 115-second video of the machine was
analysed for exactly this and could not settle it — no replay was awarded during
it, and the game ended at 1,051,150 points against a replay threshold of
2,500,000 on that machine's settings.
