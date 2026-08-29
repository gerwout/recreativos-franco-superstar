# Super Star (Recreativos Franco, 1986) — PinMAME keyboard reference

Which keys close which switch in **standalone PinMAME** (`xpinmame` / `pinmame`),
so the machine can be exercised by hand without a front end.

For the switch numbering itself, what each contact is and where it sits on the
playfield, see `vpx-table-reference.md` §1. This document only answers "what do I
press".

Sets: `supstarf1` through `supstarf4` (revs. 1-4). The keyboard map is identical
for all four — it comes from the driver's input ports and PinMAME's own
manual-switch handler, neither of which differs between the sets.

> Everything in the tables below was measured on a running `supstarf1`: real X key
> events were delivered to the emulator and `coreGlobals.swMatrix` was read back
> over the debug HTTP API after each one. See §7 for exactly what was checked.

## 0. Launching

```bash
cd /code/superstar/pinmame
./xpinmamed.x11 supstarf1 -s 3 -skip_disclaimer -skip_gameinfo -rp roms
```

`-s 3` scales the 256×256 render to a 768×768 window; `-skip_disclaimer` drops
the "type OK" screen. Add `-nosound` if the audio stutters, and `-httpport 8931`
if you want the debug API and its web UI at `/ui`.

**If the window renders transparent**, that is not the driver. `x11_find_best_visual`
(`src/unix/video-drivers/x11_window.c:359`) asks for a depth-32 TrueColor visual
first and nothing in the codebase ever writes the alpha byte, so under a
compositing WM every pixel is alpha 0. Either turn compositing off
(`xfconf-query -c xfwm4 -p /general/use_compositing -s false` on Xfce) or drop
that depth-32 branch so the search starts at 24.

---

## 1. The two kinds of key

**Cabinet inputs have a key of their own.** They are declared in the driver's
input ports (`RFRANCO_COMPORTS` in `src/wpc/rfranco.h`), so one key = one contact
and the contact follows the key — except the two coin slots, which the driver
deliberately turns into pulses (§4).

**Playfield contacts have no key of their own.** They are reached through
PinMAME's generic manual-switch handler (`CORE_PORTS` in `src/wpc/core.h`,
handled in `core_updateSw`): you hold a **column** key and a **row** key together,
and the pair names one switch.

    column keys   Q W E R T Y U I   = columns 1..8   (this game uses 1-4)
    row keys      A S D F G H J K   = rows    1..8

The switch number is just the two digits: **column key = the tens digit, row key
= the units digit**. Switch 34 is `E`+`F`, switch 47 is `R`+`J`.

> **It is a toggle, not a button.** `coreGlobals.swMatrix[col] ^= 1 << (row-1)` —
> one press of the chord *closes* the contact and it stays closed after you let
> go; press the same chord again to open it. This is the single most surprising
> thing about driving the machine from the keyboard, and it matters here more
> than on most games: this ROM faults on contacts that stay closed (§4).
>
> Press both keys together, release both, press again. The handler only acts when
> the (column, row) pair *changes*, so mashing one key while holding the other
> does nothing extra.

---

## 2. Playfield contacts — the chords

### Column 1 — connector JG, read at `0x4000` (the scoring contacts)

| Switch | Chord | Contact | Note |
|---|---|---|---|
| 11 | `Q`+`A` | 10 PUNTOS — both slingshots | momentary; also fires synthetic solenoids 19 + 20 |
| 12 | `Q`+`S` | BUMPER DERECHO — right pop bumper | momentary; also fires synthetic solenoid 18 |
| 13 | `Q`+`D` | DIANA IZQUIERDA — left target bank, "any target" | pulse this *as well as* the individual target |
| 14 | `Q`+`F` | RAMPA ESPECIAL IZQUIERDA — left special lane | rollover; collects the special when lamp 52 is lit |
| 15 | `Q`+`G` | DIANA DERECHA — right target bank, "any target" | pulse this as well as the individual target |
| 16 | `Q`+`H` | RAMPA ESPECIAL DERECHA — right special lane | rollover; collects the special when lamp 42 is lit |
| 17 | `Q`+`J` | 100 PUNTOS lane | momentary |
| 18 | `Q`+`K` | BUMPER IZQUIERDO — left pop bumper | momentary; also fires synthetic solenoid 17 |

### Column 2 — cabinet inputs

These also have dedicated keys — see §3, which is what you normally want.

| Switch | Chord | Dedicated key | Contact |
|---|---|---|---|
| 21 | `W`+`A` | `Insert` | FALTA (tilt) |
| 22 | `W`+`S` | — | not wired, does nothing |
| 23 | `W`+`D` | — | not wired, does nothing |
| 24 | `W`+`F` | — | not wired, does nothing |
| 25 | `W`+`G` | `5` | MONEDERO 25 PTS. — 25 pta coin |
| 26 | `W`+`H` | `3` | MONEDERO 100 PTS. — 100 pta coin |
| 27 | `W`+`J` | `Backspace` | CAIDA DE BOLAS — ball drain / outhole |
| 28 | `W`+`K` | `1` | PULSADOR PARTIDAS — start button |

**Use the dedicated keys for 25–28.** The chord for a coin latches the contact
closed, which is exactly what wedges the machine (§4); the chord for 27
desynchronises the driver's trough model from the matrix bit; and a latched start
button auto-repeats inside the operator menus.

### Column 3 — serial 74165 chain, left half (connector JM)

| Switch | Chord | Contact |
|---|---|---|
| 31 | `E`+`A` | PASILLO INFERIOR DERECHO — lower right lane |
| 32 | `E`+`S` | PASILLO INFERIOR IZQUIERDO — lower left lane |
| 33 | `E`+`D` | DIANA IZQUIERDA 1ª — left drop target 1 |
| 34 | `E`+`F` | DIANA IZQUIERDA 3ª — left drop target 3 |
| 35 | `E`+`G` | DIANA IZQUIERDA 2ª — left drop target 2 |
| 36 | `E`+`H` | DIANA IZQUIERDA 4ª — left drop target 4 |
| 37 | `E`+`J` | DIANA IZQUIERDA 5ª — left drop target 5 |
| 38 | `E`+`K` | DIANA DERECHA 5ª — right drop target 5 |

Targets 34 and 35 are the one place the ROM and the manual disagree about the
wiring; the ROM's order is used. See `vpx-table-reference.md` §1.3.

### Column 4 — serial chain, right half (connector JN)

| Switch | Chord | Contact |
|---|---|---|
| 41 | `R`+`A` | DIANA DERECHA 4ª — right drop target 4 |
| 42 | `R`+`S` | DIANA DERECHA 3ª — right drop target 3 |
| 43 | `R`+`D` | DIANA DERECHA 2ª — right drop target 2 |
| 44 | `R`+`F` | DIANA DERECHA 1ª — right drop target 1 |
| 45 | `R`+`G` | PASILLO SUPERIOR DERECHO — upper right lane |
| 46 | `R`+`H` | PASILLO SUPERIOR IZQUIERDO — upper left lane |
| 47 | `R`+`J` | PICABOLAS — spinner |
| 48 | `R`+`K` | **do not use** — IC5's floating serial input |

Switch 48 is not a contact. It is the sixteenth position of the shift chain, tied
to nothing on the real board, and it must read open: closed, the ROM's own contact
test reports a phantom contact.

**Drop targets are level, not momentary.** Closed = target *down*, and a bank is
complete when all five of its targets are closed. So the toggle behaviour is
right for 33–38 and 41–44: chord once to knock the target down, chord again when
the bank resets. Everything else in columns 1, 3 and 4 is momentary and wants a
second chord to release it.

---

## 3. Cabinet keys

| Key | Switch | What it is |
|---|---|---|
| `5` | 25 | 25 pta coin. The driver turns the key press into a one-shot pulse, which is what the ROM demands. |
| `3` | 26 | 100 pta coin. Same one-shot. (`3`, not the usual `6` — the driver binds it explicitly.) |
| `1` | 28 | Start button. Also the "advance" button inside every operator menu. |
| `Backspace` | 27 | Drain — puts the ball back in the trough and ends the ball. Deliberately **not** `Home`, which is Slam Tilt in ~35 other drivers. |
| `Insert` | — | Falta (tilt). Not a matrix switch: it raises RST 6.5 on the CPU. Level-triggered, so hold it. |
| `7` | 1 | **Interruptor de ajuste** — the left operator switch on the door (§5). |
| `8` | 2 | **Interruptor de test** — the right operator switch on the door (§5). |
| `Left Shift` / `Right Shift` | — | Flipper buttons. Not CPU-driven on this machine — they only drive the synthesised flipper solenoids. |

**The two door keys are toggles, and the only ones in this table.** One press
puts the switch *up* and it stays up; press again to put it back down. That is
what the physical switches do, and Williams System 4–11 binds its coin-door
Auto/Manual switch to `7` in exactly the same way. Both start **down**, which is
the resting position — a machine nobody has touched boots into *juego*.

Their position is shown on screen, in the text area to the right, as
`Ajuste arriba` / `Ajuste abajo` and the same for `Test`. That is the only way
to see where a toggle is sitting, so check there rather than counting presses.

Standard MAME keys that matter here: `Tab` opens the config menu, `F3` resets
the machine, `P` pauses, `Esc` quits. On first launch the emulator shows the
copyright screen and waits for you to type **OK**.

> **The machine has no DIP switches.** There used to be two in the driver,
> standing in for the door switches; they are gone, and the operator's real
> settings live in NVRAM, reached through the ajustes menu (§5).
>
> *Dip Switches* in the `Tab` menu is **not** empty, though: it still lists
> *Balls*, *Spinner time* and *Return to menu*. Those are not this machine's.
> They come from `SIM_PORTS` in `src/wpc/sim.h`, which every driver using the
> simulator harness pulls in, and they were always there alongside the old
> *Door switches* entry. Nothing on this machine reads them.

---

## 4. Four things that will make the machine look broken

These are properties of the ROM, not of the driver, and each one is easy to hit
by hand. They are covered at length in `vpx-table-reference.md` §6.1; this is the
keyboard-specific version.

1. **Never leave a coin contact closed.** `0x0545` latches the coin and then waits
   for the contact to *open* within ~200 ms; still closed, it jumps to the fault
   handler and the machine is wedged for good. Use `5` and `3`, which pulse. Do
   not use the `W`+`G` / `W`+`H` chords.

2. **Switch 27 must be closed at rest.** *Caída de bolas* is closed whenever a
   ball is sitting in the trough, and both the game-start path and the fault
   recovery require it. The driver sets it at power-on and manages it from there:
   firing SALIDA BOLAS opens it, `Backspace` closes it. Toggling it with `W`+`J` writes
   the matrix bit behind the driver's back and the two states drift apart.

3. **Release momentary contacts.** Because the chords latch, a bumper or rollover
   you close and forget stays closed. On `supstarf4` that faults the machine:
   its watchdog at `0x3ABF` watches switches 11, 12, 18 and 47 and calls the falta
   handler after ~128 consecutive game-loop passes — around 7 s. Every digit then
   shows the 7447's pattern for 14 and stays there, which looks like a display
   bug. Read `C01C`: `0xFF` means the ROM faulted. `supstarf1` tolerates the same
   stuck contact indefinitely.

4. **A ball that has not scored is not counted.** Draining a ball that has touched
   nothing since it was served does not advance the ball number — the game serves
   the same ball again. Score something before pressing `Backspace`.

---

## 5. Getting into the operator menus, and the ROM's own contact test

The two door switches choose the mode. The ROM picks the mode **once**, in the
boot dispatch at `0x00BB`, so changing them mid-game does nothing until the next
reset — but inside the menus it re-reads them on every pass to decide what the
start button does:

| Door switches | Mode |
|---|---|
| both down | JUEGO — normal play |
| test up | TEST DE LUCES Y VISUALIZACION DE RAM — lamp test and the RAM audit zones |
| ajuste up | BORRADO — clears the stored credits |
| both up | AJUSTES DE TANTEO Y TEST DE CONTACTOS — the adjustment zones and the contact test |

`7` is the *ajuste* switch and `8` is the *test* switch. Both are toggles that
stay where you put them, and both rest **down**, so an untouched machine is in
*juego*. They have to be switches rather than a setting because the menus need a
door switch to move **while the machine runs**.

> **Needs the driver's reset handler.** Until `MACHINE_RESET(RFRANCO)` was added,
> a soft reset left the driver's power-on state stale — the ball-trough model
> most damagingly — so the ROM's startup never completed and the boot dispatch at
> `0x00BB` was never reached. `F3` therefore could not take a running machine
> into a menu, and it looked as though the mode were fixed at power-on. It is
> not. See `driver-notes.md` §7C.

### Getting in

1. Press `7` and `8` — both door switches up. Check the on-screen readout says
   `Ajuste arriba` and `Test arriba`.
2. `F3`.

You land in zone 1 within about 20 s, with the **zone number in the units digit
of the credit display** and the zone's value on player 1.

Then, inside the menu, the start button is the only control and what it does
depends on where the door switches are at that moment:

* **`8`** (test switch back down), then **`1`** — steps to the **next zone**.
  Repeat `1` to walk 1 → 2 → … → 9.
* **`8`** again (both up), then **`1`** — steps the **current zone's value**.

### Zone 9 — TEST DE CONTACTOS

This is the machine's own switch test and the fastest way to check a whole
wiring map. Close the contacts you want to test, then **press `1` to run a scan
pass**: player 1's units digit shows *how many* contacts are closed, and player 3
shows *which one*, one per press, cycling through them.

The numbers player 3 reports are the **manual's contact numbers (1–29)**, not
PinMAME switch numbers. `vpx-table-reference.md` has the translation table in its
appendix. Measured examples:

| Chord | PinMAME switch | Zone 9 reports |
|---|---|---|
| `Q`+`K` | 18 — bumper izquierdo | `04` |
| `R`+`H` | 46 — pasillo superior izquierdo | `01` |
| `R`+`H` and `E`+`D` | 46 + 33 | count `2`, cycling `01`, `11` |

The test covers only the 23 playfield contacts. The four cabinet inputs are not
in it, and neither are the contacts wired in parallel with another one — closing
either half of a pair reports the pair's higher number.

`supstarf1` has 9 zones; `supstarf4` has 19, and its extra ten are tabulated in
`vpx-table-reference.md` §5.1.1.

### Getting back to a game

`F3` again with the door switches back where you want them. To leave the menus
for good, press `7` and `8` until the readout says `Ajuste abajo` and
`Test abajo`, then reset.

**A toggle's position survives quitting**, exactly as the old DIP setting did.
Pressing a toggle flips `in->default_value` (`src/inptport.c:2550`), and that is
the field MAME writes to `~/.xpinmame/cfg/supstarf1.cfg` on `Esc` and reads back
at the next launch. So a machine left with both switches up comes back up in
AJUSTES. Put them down before quitting, or delete that file.

---

## 6. A minimal game from a cold start

```
  type OK          dismiss the copyright screen
  5                insert a 25 pta coin           -> credit display goes to 1
  1                start                          -> the game serves a ball,
                                                     switch 27 opens
  Q+A   Q+A        slingshot: close, then release -> 10 points
  Q+S   Q+S        right bumper
  E+D              left drop target 1 down        (level - leave it closed)
  Q+D   Q+D        ... and pulse the bank contact
  Backspace        drain                          -> bonus paid, next ball
```

`tools/rfranco_game.py` plays this sequence and asserts on it for both ROM sets,
driving the switches over the debug API instead of the keyboard.

---

## 7. How this was verified

Measured on `supstarf1` running under `xpinmamed.x11` on a virtual X server. Key
events were delivered to the emulator window with `xdotool` and the resulting
switch matrix read back from `/api/info`, whose `switches` field is a straight hex
dump of `coreGlobals.swMatrix`.

* **All 32 chords, one at a time.** Each of `Q W E R` × `A S D F G H J K` was
  pressed, the matrix sampled, the chord pressed again and the matrix sampled
  once more. Every chord set exactly the one expected bit in exactly the expected
  row, changed no other row, and restored the original value on the second press.
  That is the toggle behaviour and the whole switch table in one pass.
* **`5`, `3`, `1`.** Sampled continuously across the key press: `5` raised bit
  `0x10` of row 2 (switch 25) and took the credit display from 0 to 1; `3` raised
  `0x20` (switch 26); `1` raised `0x80` (switch 28). All three fell again on their
  own, confirming the coin one-shot.
* **`Backspace`.** With the ball in play and the trough reading open, the drain key closed
  switch 27.
* **`Insert` and `W`+`A`.** Either one latched `C01C` to `0xFF`, lit lamp 11
  (*luz falta*) and filled all thirty digits with the 7447's pattern for 14 —
  the documented signature of the falta handler.
* **The operator menu route (§5), end to end.** Both door switches up then `F3`
  brought the machine up in AJUSTES zone 1; putting the test switch back down
  and pressing `1` eight times walked it to zone 9; and in zone 9 the contacts
  closed by chord were reported back under the manual's numbering, one scan pass
  per press of `1`.
* **The reset handler that route depends on.** Before the fix in
  `driver-notes.md` §7C, door switches held up across an `F3` left the machine
  in normal play for the whole of a 300 s observation. After it, the same
  sequence reaches AJUSTES zone 1 within 10 s. Both ROM sets still pass
  `tools/rfranco_check.py` and `tools/rfranco_game.py`.

> **What changed when the door switches became toggles.** The two bullets above
> were originally measured with the controls of the time: a DIP for the mode and
> chords `W`+`D` / `W`+`F` on switches 23/24 to lift each switch. The route
> itself is unchanged — same bits reaching the ROM by the same path, only
> renumbered to switches 1 and 2 — and `tools/rfranco_zones.py` walks it on both
> sets over the debug API after the change. What has **not** been re-measured
> with `xdotool` is the two new keys, `7` and `8`; that is a keyboard check and
> is outstanding.

Not verified here: the contents of the individual adjustment zones — those come
from `tools/rfranco_zones.py`, which walks the menu over the debug API.

---

## Related documents

* `vpx-table-reference.md` — the switch, lamp, solenoid and display tables, and
  the manual-contact ↔ PinMAME-switch translation for the zone 9 test.
* `hardware-findings.md` — where the switch map comes from and how it was pinned
  down.
* `driver-notes.md` — the driver's architecture and known gaps.
