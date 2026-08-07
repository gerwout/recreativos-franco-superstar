# Super Star (Recreativos Franco, 1986) — Visual Pinball table-author reference

PinMAME driver: `src/wpc/rfranco.c` / `rfranco.h` / `rfrancogames.c`
ROM sets: `supstarf` (set 1, 9 operator adjustment zones — the revision the factory
manual documents), `supstarfa` (set 2, newer firmware, 25 zones)

Boards: CPU 53/3291 (8085A + 8035 sound + 2 x AY-3-8910), driver 53/3308,
display 53/3307, PSU 53/3309, interconnect 53/3310, bumper/eject 53/3311.

Everything below is derived from the driver source, the factory manual
(`../super-star-pinball-manual.md`, including its *Fe de erratas*) and a
disassembly of the game ROM. Where the three disagree the ROM wins and the
disagreement is called out. Statements that are inferred rather than measured
are marked.

> **Read §6 before wiring anything.** Two things will leave you with a machine
> that looks alive but never starts a game: *caída de bolas* (switch 27) must
> read **closed** whenever a ball is in the trough, and the coin switches must be
> **pulsed**, never held.

> **Lamp numbers are not final.** The driver is still under active development
> and does not yet declare a lamp-number conversion, so it inherits PinMAME's
> sequential 1–64. Its own source comments describe the same lamps on a 10-based
> scheme (`1`–`8`, `11`–`18`, … `71`–`74`). Confirm with the driver author before
> committing a table to the numbers in §2.

---

## 0. Quick orientation

| Thing | Count | VPX numbers |
|---|---|---|
| Playfield / cabinet switches | 4 hardware bytes, 27 real contacts | `11`–`18`, `21`–`28`, `31`–`38`, `41`–`48` |
| Tilt (*falta*) | 1 | **not a switch and not reachable from VPX** — see §1.5 |
| Lamps | 8 matrix columns, 44 that can light | `1`–`64` (see §2) |
| Solenoids, CPU-driven | 8 of 10 decoder outputs actually used | `2`–`5`, `7`–`10` |
| Solenoids, synthesised by the driver | 4 (bumpers and ejects) | `17`–`20` |
| Flippers | 2, not CPU-controlled | buttons `112` / `114` in, solenoids `45`–`48` out |
| Display segments | 30 HDSP-3400 digits | LED indices `0`–`33` (see §4) |
| DIP switches | 2 used of 16 | door switches, see §1.6 |

Absences that will trip up a table author:

* **No ball-in-play display.** The ball number is shown by playfield lamps
  *BOLA 1*…*BOLA 5* (lamps 25–29).
* **No match, no game-over reel.** *FINAL PARTIDA* is a lamp (30).
* **No flipper switches and no CPU flipper control.** The flipper buttons feed
  the coils directly through the interconnect board.
* **No coin-door slam switch and no ball-shooter switch.**
* **The two pop bumpers and the two eject holes fire on their own board**
  (53/3311), straight from their playfield switches. The CPU never commands
  them; the driver synthesises solenoids 17–20 so you have something to hang a
  sound and a flasher on — see §3.2.

---

## 1. Switches

The driver declares its own numbering with
`MDRV_SWITCH_CONV(rfranco_sw2m, rfranco_m2sw)`, giving the conventional
`column*10 + row + 1`. In VPX: `Controller.Switch(nn) = True/False`.

**Polarity.** PinMAME's normal convention applies throughout: `True` = contact
closed. The driver handles all the hardware's active-low inversions internally.

### 1.1 Column 1 — connector JG, read directly at `0x4000`

Eight playfield contacts run from the playfield into the CPU board on connector
JG and are read as a single byte at `0x4000` (74S138 chip select CS1). These are
the *scoring* contacts — and four of them also fire a coil locally.

Corroborated twice over: the CPU-board JG table gives the bus bit for each
contact, and the ROM's own switch-test table at `0x34A2` lists the same order.

| # | Bus | Spanish name | English name | Playfield location | Notes |
|---|---|---|---|---|---|
| 11 | AD0 | 10 PUNTOS | 10-point rollover | lower playfield | **Paralleled pair**: manual contacts 24 + 25. Either bulb-switch closes 11. Momentary. |
| 12 | AD1 | BUMPER DERECHO | Right pop bumper | upper right | Also triggers synthetic solenoid **18**. Momentary. |
| 13 | AD2 | DIANA IZQUIERDA | Left drop-target bank, "any target" | left bank | Bank-level contact. The individual targets are 33–37. **Pulse this as well as closing the individual target.** |
| 14 | AD3 | RAMPA ESPECIAL IZQUIERDA | Left special ramp / eject hole | upper left | Also triggers synthetic solenoid **19**. |
| 15 | AD4 | DIANA DERECHA | Right drop-target bank, "any target" | right bank | Bank-level contact. Individual targets 38, 41–44. |
| 16 | AD5 | RAMPA ESPECIAL DERECHA | Right special ramp / eject hole | upper right | Also triggers synthetic solenoid **20**. |
| 17 | AD6 | 100 PUNTOS | 100-point rollover | mid playfield | **Paralleled pair**: manual contacts 10 + 21. Momentary. |
| 18 | AD7 | BUMPER IZQUIERDO | Left pop bumper | upper left | Also triggers synthetic solenoid **17**. Momentary. |

### 1.2 Column 2 — cabinet inputs, read through the sound CPU

The 8085 cannot read these directly. It asks the 8035 with sound command `0x99`;
the 8035 selects PSG2 (IC2) and reads AY register `0x0E`, and the answer comes
back through the 8212 latch. Driver-board connector JO; CPU-board connector JC.

| # | Port bit | Spanish name | English name | Location | Notes |
|---|---|---|---|---|---|
| 21 | PA0 | — | — | — | **Not wired, and never read by the ROM.** Leave it alone. |
| 22 | PA1 | — | — | — | **Not wired, never read.** |
| 23 | PA2 | — | — | — | **Not wired, never read.** |
| 24 | PA3 | — | — | — | **Not wired, never read.** |
| 25 | PA4 | MONEDERO 25 PTS. | 25 pta coin slot | coin door | **Required.** Must be a short pulse — see §6.1. |
| 26 | PA5 | MONEDERO 100 PTS. | 100 pta coin slot | coin door | **Required.** Must be a short pulse — see §6.1. |
| 27 | PA6 | CAIDA DE BOLAS | Ball drain / outhole | trough | **Required, and must read CLOSED at rest** — see §6.1. Manual contact 28; the driver board also labels this net *contacto final partidas*. |
| 28 | PA7 | PULSADOR PARTIDAS | Start button | cabinet front | **Required.** Manual contact 29. Also the "advance" button inside every operator menu. |

Only bits 4–7 are ever tested by the game program (verified by exhaustive search
of the reads of `C027`). Switches 21–24 have no effect whatsoever.

### 1.3 Column 3 — the serial 74165 chain, left half (driver-board IC6, connector JM)

Driver-board IC6 and IC5 are two cascaded 74165 shift registers clocked out into
the 8085's SID pin one bit at a time. IC6's contents leave first, and its H input
(JM3) is shifted past before the firmware's first `RIM`, so it is invisible to the
game — which is exactly why the manual's errata moves the *picabolas* contact off
JM3 and onto JN2.

| # | 74165 in | Conn. | Spanish name | English name | Location | Notes |
|---|---|---|---|---|---|---|
| 31 | IC6 G | JM4 | PASILLO INFERIOR DERECHO | Lower right lane | lower right | **Paralleled pair**: manual contacts 23 + 27 |
| 32 | IC6 F | JM5 | PASILLO INFERIOR IZQUIERDO | Lower left lane | lower left | **Paralleled pair**: manual contacts 22 + 26 |
| 33 | IC6 E | JM6 | DIANA IZQUIERDA 1ª | Left drop target 1 | left bank | closed = target **down** |
| 34 | IC6 D | JM7 | DIANA IZQUIERDA 3ª | Left drop target 3 | left bank | see the discrepancy note below |
| 35 | IC6 C | JM8 | DIANA IZQUIERDA 2ª | Left drop target 2 | left bank | see the discrepancy note below |
| 36 | IC6 B | JM1 | DIANA IZQUIERDA 4ª | Left drop target 4 | left bank | |
| 37 | IC6 A | JM2 | DIANA IZQUIERDA 5ª | Left drop target 5 | left bank | |
| 38 | IC5 H | JN3 | DIANA DERECHA 5ª | Right drop target 5 | right bank | first bit of the IC5 half |

> **Discrepancy on switches 34 / 35.** The manual's IC6 wiring table labels JM7
> *diana izquierda 2* and JM8 *diana izquierda 3*. The game ROM's own switch-test
> table (byte-identical in both ROM revisions) reports contact **13** for the JM7
> position and contact **12** for JM8 — i.e. targets 3 and 2, the other way round.
> Fifteen of the sixteen serial positions agree between the two sources; this is
> the only one that does not. The ROM is what the machine actually displays in
> zone 9, so it is treated as authoritative here. In practice it only matters if
> your target bank awards differ per target position.

### 1.4 Column 4 — the serial chain, right half (driver-board IC5, connector JN)

| # | 74165 in | Conn. | Spanish name | English name | Location | Notes |
|---|---|---|---|---|---|---|
| 41 | IC5 G | JN4 | DIANA DERECHA 4ª | Right drop target 4 | right bank | |
| 42 | IC5 F | JN5 | DIANA DERECHA 3ª | Right drop target 3 | right bank | |
| 43 | IC5 E | JN6 | DIANA DERECHA 2ª | Right drop target 2 | right bank | |
| 44 | IC5 D | JN9 | DIANA DERECHA 1ª | Right drop target 1 | right bank | |
| 45 | IC5 C | JN8 | PASILLO SUPERIOR DERECHO | Upper right lane | upper right | manual contact 2 |
| 46 | IC5 B | JN7 | PASILLO SUPERIOR IZQUIERDO | Upper left lane | upper left | manual contact 1 |
| 47 | IC5 A | JN2 | PICABOLAS | Spinner / ball chopper | centre playfield | Moved here by the *Fe de erratas* (JM3 → JN2). Awards the *especial picabolas*. |
| 48 | IC5 SER | JN1 | — | — | — | **Unused — leave open.** This is IC5's floating serial input. If it reads closed, the zone-9 contact test reports a phantom contact. |

**Drop targets.** Contact closed = target **down**. A completed bank is "all five
closed". The bank-level contacts (13 / 15) are separate wires from the individual
target contacts, so a VPX drop target must close its own switch *and* pulse the
bank switch. At the start of every ball the game fires the bank-reset coil for any
bank that is not fully standing.

### 1.5 Falta (tilt) — not a matrix switch

The tilt pendulum reaches the CPU on JD1 and pulses **RST 6.5** (vector `0x0034`
→ handler at `0x0286` in set 1). There is no switch number.

In standalone PinMAME it is bit `0x0100` of the common input port
("Falta (Tilt)", default key `INSERT`).

> **Under VPX there is currently no way to trigger it at all.** The driver raises
> RST 6.5 from inside `SWITCH_UPDATE`, which only runs when PinMAME is handling
> the keyboard — and VPinMAME turns that off. See `driver-notes.md`; this needs a
> driver change before a table can tilt.

### 1.6 Operator door switches — DIP 1 and 2

The two door switches (*interruptor de ajuste*, *interruptor de test*) are not
matrix switches either. They arrive as PSG2 port B bits 7/6 and the driver models
them as DIP switches 1–2 (`core_getDip(0) & 0x03`). In VPX: `Controller.Dip(0)`.

| DIP value | Manual position | Mode entered at power-on |
|---|---|---|
| 0 | both down | **JUEGO** (normal play) |
| 1 | test up only | **TEST DE LUCES Y VISUALIZACION DE RAM** |
| 2 | ajuste up only | **BORRADO DE DISPLAY Y CREDITOS** |
| 3 | both up | **AJUSTES DE TANTEO Y TEST DE CONTACTOS** |

The ROM chooses the mode at boot (dispatch at `0x00BB`), so entering a menu needs
a **reset** with the DIP already set. Once inside a menu the DIP is re-read live,
which is what makes the "lower the adjust switch, press start" navigation work.

---

## 2. Lamps

Three CD4028 BCD-to-decimal decoders on the driver board (IC1, IC2, IC3) each gate
a BT106 thyristor per output. A fired thyristor conducts until the end of the
mains half-cycle, so **each decoder output serves two lamps** — one on **FASE A**,
one on **FASE B** — selected by which half-cycle it was gated in. The sound CPU
reports the current half-cycle on its T1 pin and the 8085 uses it to pick between
two copies of the lamp tables.

The driver gives each (decoder, phase) pair a matrix column of its own:

| Col | Decoder | Phase | Decoder codes | Connector | VPX lamps |
|---|---|---|---|---|---|
| 0 | IC1 | FASE A | 0–7 | JA → display board | 1–8 |
| 1 | IC1 | FASE B | 0–7 | JA → display board | 9–16 |
| 2 | IC2 | FASE A | 0–7 | JQ odd pins | 17–24 |
| 3 | IC2 | FASE B | 0–7 | JQ even pins | 25–32 |
| 4 | IC3 | FASE A | 0–7 | JP odd pins | 33–40 |
| 5 | IC3 | FASE B | 0–7 | JP even pins | 41–48 |
| 6 | IC1 and IC2 | both | 8–9 | JQ | 49–56 |
| 7 | IC3 | both | 8–9 | — | 57–64 |

Within columns 0–5, **bit *n* is decoder code *n***, so the lamp number is
`col*8 + code + 1`.

**Lamp numbers.** The driver installs no lamp conversion of its own, so it
inherits the base PinMAME machine driver's sequential scheme — see the warning at
the top of this document.

The game does its own flashing (it keeps separate "force on" and "force off"
overlay tables and merges them on alternate frames), so a table should follow the
lamp state and not add blink logic.

### 2.1 Column 0 — IC1, FASE A (lamps 1–8): backbox

| Lamp | Code | Pin | Spanish name | English name |
|---|---|---|---|---|
| 1 | 0 | JA8 | LUZ FALTA | Tilt — **never lit**, see §2.9 |
| 2 | 1 | JA20/21 | JUGADOR 3º | Player 3 up |
| 3 | 2 | JA7 | JUGADOR 4º | Player 4 up |
| 4 | 3 | JA9 | LOTERIA 90 | Lottery 90 |
| 5 | 4 | JA10 | LOTERIA 80 | Lottery 80 |
| 6 | 5 | JA11 | LOTERIA 70 | Lottery 70 |
| 7 | 6 | JA12 | LOTERIA 60 | Lottery 60 |
| 8 | 7 | JA13 | LOTERIA 50 | Lottery 50 |

### 2.2 Column 1 — IC1, FASE B (lamps 9–16): backbox

| Lamp | Code | Pin | Spanish name | English name |
|---|---|---|---|---|
| **9** | 0 | JA8 | LUZ FALTA | **Tilt — this is the one that lights** |
| 10 | 1 | JA20/21 | JUGADOR 1º | Player 1 up |
| 11 | 2 | JA7 | JUGADOR 2º | Player 2 up |
| 12 | 3 | JA9 | LOTERIA 00 | Lottery 00 |
| 13 | 4 | JA10 | LOTERIA 10 | Lottery 10 |
| 14 | 5 | JA11 | LOTERIA 20 | Lottery 20 |
| 15 | 6 | JA12 | LOTERIA 30 | Lottery 30 |
| 16 | 7 | JA13 | LOTERIA 40 | Lottery 40 |

The *lotería* lamps are the 0…90 lottery wheel in the backbox. Each JA pin carries
two bulbs, one per phase: `JA9` = 00/90, `JA10` = 10/80, `JA11` = 20/70,
`JA12` = 30/60, `JA13` = 40/50. (The manual's parts list is missing part
`01-2339 Pantallas Luces Loteria`, flagged in its own errata.)

### 2.3 Column 2 — IC2, FASE A (lamps 17–24): the *avance* ladder

| Lamp | Code | Pin | Spanish name | English name | Manual luz # |
|---|---|---|---|---|---|
| 17 | 0 | JQ11 | LUZ 10000 PUNTOS | Advance 10,000 | 19 |
| 18 | 1 | JQ19 | LUZ 20000 PUNTOS | Advance 20,000 | 18 |
| 19 | 2 | JQ13 | LUZ 30000 PUNTOS | Advance 30,000 | 17 |
| 20 | 3 | JQ17 | LUZ 40000 PUNTOS | Advance 40,000 | 16 |
| 21 | 4 | JQ15 | LUZ 50000 PUNTOS | Advance 50,000 | 15 |
| 22 | 5 | JQ5 | LUZ 60000 PUNTOS | Advance 60,000 | 14 |
| 23 | 6 | JQ3 | LUZ 70000 PUNTOS | Advance 70,000 | 13 |
| 24 | 7 | JQ9 | LUZ 80000 PUNTOS | Advance 80,000 | 12 |

The 90,000 and 100,000 rungs are on codes 8 and 9 — lamps 53 and 54, §2.7.

### 2.4 Column 3 — IC2, FASE B (lamps 25–32)

| Lamp | Code | Pin | Spanish name | English name | Manual luz # |
|---|---|---|---|---|---|
| 25 | 0 | JQ12 | LUZ BOLA 1ª | Ball 1 | 27 |
| 26 | 1 | JQ20 | LUZ BOLA 2ª | Ball 2 | 28 |
| 27 | 2 | JQ14 | LUZ BOLA 3ª | Ball 3 | 29 |
| 28 | 3 | JQ18 | LUZ BOLA 4ª | Ball 4 | 30 |
| 29 | 4 | JQ16 | LUZ BOLA 5ª | Ball 5 | 31 |
| 30 | 5 | JQ6 | LUZ FINAL PARTIDA | Game over | 32 |
| 31 | 6 | JQ4 | LUZ BOLA EXTRA (CONSEGUIDA) | Extra ball earned | 26 |
| 32 | 7 | JQ10 | LUZ ESPECIAL PICABOLAS | Spinner special | 3 |

**Lamps 25–29 are the only ball-in-play indication the machine has.**

### 2.5 Column 4 — IC3, FASE A (lamps 33–40)

| Lamp | Code | Pin | Spanish name | English name | Manual luz # |
|---|---|---|---|---|---|
| 33 | 0 | JP1 | BUMPER DERECHO | Right bumper | 5 |
| 34 | 1 | JP9 | ESPECIAL DERECHA | Right special | 9 |
| 35 | 2 | JP3 | BOLA EXTRA DIANA DERECHA | Extra ball, right target bank | 8 |
| 36 | 3 | JP7 | PASILLO DERECHO INF. Y SUPERIOR | Right lanes | 2, 23, 25 — **three bulbs on one output** |
| 37 | 4 | JP5 | PULSADOR PARTIDAS | Start-button lamp | 33 |
| 38–40 | 5–7 | — | — | *(decoder codes 5–7 unwired)* | — |

### 2.6 Column 5 — IC3, FASE B (lamps 41–48)

| Lamp | Code | Pin | Spanish name | English name | Manual luz # |
|---|---|---|---|---|---|
| 41 | 0 | JP2 | BUMPER IZQUIERDO | Left bumper | 4 |
| 42 | 1 | JP10 | ESPECIAL IZQUIERDA | Left special | 6 |
| 43 | 2 | JP4 | BOLA EXTRA DIANA IZQUIERDA | Extra ball, left target bank | 7 |
| 44 | 3 | JP8 | PASILLO IZQUIERDO INF. Y SUPERIOR | Left lanes | 1, 22, 24 — **three bulbs on one output** |
| 45 | 4 | JP6 | — | *(N.C. on the connector)* | — |
| 46–48 | 5–7 | — | — | *(unwired)* | — |

### 2.7 Column 6 — decoder codes 8 and 9 for IC1 and IC2 (lamps 49–56)

| Lamp | Decoder | Phase | Code | Pin | Spanish name | English name | Manual luz # |
|---|---|---|---|---|---|---|---|
| 49–52 | IC1 | A, A, B, B | 8, 9, 8, 9 | — | — | *(N.U. on the schematic — never light)* | — |
| 53 | IC2 | A | 8 | JQ1 | LUZ 90000 PUNTOS | Advance 90,000 | 11 |
| 54 | IC2 | A | 9 | JQ7 | LUZ 100000 PUNTOS | Advance 100,000 | 10 |
| 55 | IC2 | B | 8 | JQ2 | LUZ AVANZE DOBLE | Double advance | 20 |
| 56 | IC2 | B | 9 | JQ8 | LUZ AVANZE TRIPLE | Triple advance | 21 |

*Double* lights when one target bank is completed while the other still has
targets standing; *triple* when both banks are down.

### 2.8 Column 7 — decoder codes 8 and 9 for IC3 (lamps 57–64)

Nothing is wired to IC3's codes 8 and 9, so lamps 57–60 never light and 61–64 do
not exist. The column is present only to keep the layout regular.

### 2.9 The tilt lamp

The errata puts the *falta* lamp on IC1 pin 3, which is decoder output 0, with
connector pin JA8. It does not say which of the two mains phases it sits on — but
the ROM does: every write that sets or preserves code 0 targets the **FASE B**
copy of the IC1 table (`C21C`), and the FASE A copy (`C219`) is repeatedly masked
with `ANI 0x1F`, which clears code 0 unconditionally. The power-fail handler at
`0x0244` lights it the same way.

**Bind lamp 9. Lamp 1 will never light.**

### 2.10 Coverage check against the manual

The manual's *LUCES DE TABLERO* lists 33 playfield bulbs; the driver board has 29
playfield outputs (9 usable on IC3, 20 on IC2). The difference is the two lane
groups — the left lane (manual luces 1, 22, 24) is three bulbs on `JP8` and the
right lane (2, 23, 25) three bulbs on `JP7`. All 33 are accounted for above.
IC1 adds 15 backbox bulbs (falta ×1, jugador ×4, lotería ×10).

29 + 15 = **44 lamp numbers that can light**, one per physical output.

Connector pin numbers on JA are given as printed on the driver-board sheet. The
errata reverses the whole JA connector and the display-board sheet numbers it the
other way round; the signal names are reliable, the JA pin numbers are not.

---

## 3. Solenoids

### 3.1 CPU-driven coils — driver-board IC7 (a fourth CD4028), connector JL

The 8035 writes a byte to PSG1 register `0x0F`; its **high nibble** is a 4028
select code. Codes 0–9 pick an output, 10–15 select none. **VPX solenoid number =
decoder code + 1.**

In VPX: `SolCallback(n) = "SubName"`.

| # | Code | Pin | Spanish name | English name | Function | Used by the ROM? |
|---|---|---|---|---|---|---|
| 1 | 0 | JL10 | — | *(unwired)* | Connector pin is N.C. | never asserted |
| 2 | 1 | JL6 | TACA / PARTIDA ESPECIAL | Knocker | Bangs on every *especial* (replay) award | yes |
| 3 | 2 | JL7 | BOBINA MONEDERO | Coin-mechanism coil | Coin lockout / diverter actuator | yes |
| 4 | 3 | JL9 | CONTADOR 25 PTS. | 25 pta coin meter | Mechanical audit meter, pulsed on a 25 pta coin | yes |
| 5 | 4 | JL8 | CONTADOR 100 PTS. | 100 pta coin meter | Mechanical audit meter, pulsed on a 100 pta coin | yes |
| 6 | 5 | JL3 | FLIPPER | Coil-supply relay (RL1 on the interconnect board, labelled *relé alimentación bobinas*) | **Never energised by the game program.** The flippers are live whenever the machine is on. Ignore it. | never asserted |
| 7 | 6 | JL2 | BANCADA IZQUIERDA | Left bank reset | Raises the 5 left drop targets | yes |
| 8 | 7 | JL5 | PICA-BOLAS | Spinner / ball-chopper coil | Drives the picabolas mechanism | yes |
| 9 | 8 | JL1 | BANCADA DERECHA | Right bank reset | Raises the 5 right drop targets | yes |
| 10 | 9 | JL4 | SALIDA BOLAS | Ball release / outhole kicker | **Required** — serves the ball into the shooter lane | yes |

The "used by the ROM" column is not a guess: every write to the coil bit-field is
an immediate `MVI A,<bit>` and there are exactly eight of them in set 1. Codes 0
and 5 are never set.

Two hardware facts worth knowing:

* **Only one coil is sustained at a time.** The firmware emits ten decoder-select
  time slots per half-cycle; before sending them it scans for the first active
  coil code and copies it into the *last* slot, so the 4028 is left selecting that
  coil for the remainder of the half-cycle. If two coils were requested at once,
  the lower-numbered one gets the sustained slot.
* Coils are re-gated on every mains half-cycle (the thyristors need it). The
  driver accumulates everything gated since the previous video frame, so expect a
  coil to be reported for whole frames.

### 3.2 Synthesised coils — the bumpers and the ejects

The two pop bumpers and the two eject holes (*expulsores*, the "rampa especial"
kickouts) are fired on board 53/3311 directly from their own playfield switches,
through a thyristor block, **with no CPU involvement at all**. The 8085 only ever
learns that the switch closed.

The driver therefore invents four solenoids and pulses each one for six video
frames on the rising edge of the corresponding column-1 switch:

| # | Fired by switch | Spanish name | English name |
|---|---|---|---|
| 17 | 18 (BUMPER IZQUIERDO) | BOBINA BUMPER IZQUIERDO | Left pop bumper coil |
| 18 | 12 (BUMPER DERECHO) | BOBINA BUMPER DERECHO | Right pop bumper coil |
| 19 | 14 (RAMPA ESPECIAL IZQUIERDA) | EXPULSOR IZQUIERDO | Left eject/kickout coil |
| 20 | 16 (RAMPA ESPECIAL DERECHA) | EXPULSOR DERECHO | Right eject/kickout coil |

These are useful for sound and lighting, but **do not use them to drive the ball**:
they are generated *from* your switch, one frame or more after it, so they cannot
tell you anything you did not already know. Do the bumper and kickout physics in
the table on the switch hit, and use the callback for the effects.

### 3.3 Flippers

Not CPU-controlled. The buttons reach the coils through the interconnect board
(J1-18 / J1-19), and the game program never even sees them. There is no EOS
switch and no flipper-button contact anywhere in this machine's own matrix.

PinMAME's core synthesises the standard flipper solenoids anyway, from its own
cabinet flipper column (internal switch column 11). Under VPX — where PinMAME is
not handling the keyboard — that column is what your table drives:

| Input | Number | Meaning |
|---|---|---|
| switch | **112** | Lower **right** flipper button |
| switch | **114** | Lower **left** flipper button |

| Output | Constant | Meaning |
|---|---|---|
| 45 | `sLRFlipPow` | Lower right flipper, power winding |
| 46 | `sLRFlip` | Lower right flipper, hold winding |
| 47 | `sLLFlipPow` | Lower left flipper, power winding |
| 48 | `sLLFlip` | Lower left flipper, hold winding |

112 and 114 are the same numbers WPC Fliptronic tables use, because the driver's
`column*10 + row + 1` numbering happens to land on them for column 11. If you
would rather not route the flippers through PinMAME at all, drive them directly
from the table — the game does not care either way.

---

## 4. Display

Display board 53/3307 carries **30 HDSP-3400 digits** behind an Intel 8279, a
74159 digit select and two 7447 BCD-to-seven-segment decoders. There is no ball
display and no match display: 4 players × 7 digits + 2 credit digits = exactly 30.

The 8279 has 16 display-RAM addresses and each byte holds **two** digits. The high
nibble goes to the 7447 driving D15–D30, the low nibble to the one driving D1–D14.
Digits are raw BCD; `0x0F` blanks a digit.

In VPX these are read with `Controller.ChangedLEDs(&HFFFFFFFF, &HFFFFFFFF)` and
indexed by the segment ("LED") numbers below. The driver refreshes
`coreGlobals.segments` every second VBLANK.

### 4.1 Segment index map

| Player | Segment indices | Order |
|---|---|---|
| Player 1 | 0–6 | `0` = millions … `6` = the trailing zero |
| Player 2 | 8–14 | `8` = millions … `14` = the trailing zero |
| Player 3 | 16–22 | `16` = millions … `22` = the trailing zero |
| Player 4 | 24–30 | `24` = millions … `30` = the trailing zero |
| Credits | 32–33 | `32` = tens, `33` = units |

Indices 7, 15, 23 and 31 are not wired; they exist only to keep each player on an
8-index boundary.

**The least significant digit of every score is a trailing zero** — the smallest
playfield award is 10 points. `0123450` on the display means 123,450 points and
the maximum displayable score is 9,999,990. *(Inferred from the award structure;
the digit is a real 8279 position and the ROM writes 0 to it.)*

### 4.2 8279 RAM address → segment index

Only needed if you are debugging the driver.

| 8279 addr | High nibble → | Low nibble → | Digit position |
|---|---|---|---|
| 0 | 14 (P2) | 6 (P1) | least significant (trailing 0) |
| 1 | 30 (P4) | 22 (P3) | least significant (trailing 0) |
| 2 | 13 (P2) | 5 (P1) | tens |
| 3 | 29 (P4) | 21 (P3) | tens |
| 4 | 12 (P2) | 4 (P1) | hundreds |
| 5 | 28 (P4) | 20 (P3) | hundreds |
| 6 | 11 (P2) | 3 (P1) | thousands |
| 7 | 27 (P4) | 19 (P3) | thousands |
| 8 | 10 (P2) | 2 (P1) | ten-thousands |
| 9 | 26 (P4) | 18 (P3) | ten-thousands |
| 10 | 9 (P2) | 1 (P1) | hundred-thousands |
| 11 | 25 (P4) | 17 (P3) | hundred-thousands |
| 12 | 8 (P2) | 0 (P1) | millions |
| 13 | 24 (P4) | 16 (P3) | millions |
| 14 | 33 | — | credits units |
| 15 | 32 | — | credits tens |

Players 1 and 3 take the low nibble, players 2 and 4 the high one; players 1–2 use
even RAM addresses, players 3–4 odd ones. The game uses the 8279's *display write
inhibit* command (`0xA8` for the odd players, `0xA4` for the even ones) so the two
players sharing an address can be written independently, and its auto-increment
mode for the 16-byte block fills.

### 4.3 On-screen layout the driver uses

```
player 1 (0-6)                       player 3 (16-22)
player 2 (8-14)   credits (32-33)    player 4 (24-30)
```

---

## 5. Operator adjustments, tests and audits

Reached with the two door switches (§1.6 — DIP 1–2). The **start button
(switch 28)** is the only control inside every menu.

### 5.1 AJUSTES DE TANTEO Y TEST DE CONTACTOS (DIP = 3)

Nine zones in `supstarf`. **The zone number is shown in the units digit of the
credits display** (segment index 33).

Procedure from the manual:

1. Switch the machine off.
2. Set both door switches up and power on — you land in zone 1 with its current
   value.
3. To move to another zone: put the *ajuste* switch **down** (DIP = 1) and press
   start; each press advances one zone.
4. To change the value of the current zone: put the *ajuste* switch **up**
   (DIP = 3) and press start; each press steps the value.

| Zone | Spanish | English | Range |
|---|---|---|---|
| 1 | NUMERO DE BOLAS POR PARTIDA | Balls per game | 1–5 |
| 2 | AJUSTE DE TANTEO BOLA EXTRA | Extra-ball score threshold | 10,000–100,000 |
| 3 | NUMERO DE PARTIDAS POR MONEDA DE 25 PTAS. | Games per 25 pta coin | — |
| 4 | NUMERO DE PARTIDAS POR MONEDA DE 100 PTAS. | Games per 100 pta coin | — |
| 5 | NUMERO DE ESPECIALES POR TANTEO | Number of score specials | 1–3 |
| 6 | TANTEO PRIMER ESPECIAL | 1st replay score | — |
| 7 | TANTEO SEGUNDO ESPECIAL | 2nd replay score | — |
| 8 | TANTEO TERCER ESPECIAL | 3rd replay score | — |
| 9 | TEST DE CONTACTOS | Switch test | see below |

**Zone 9 — switch test.** The **units end of player 1's display** shows *how many*
contacts are currently closed; the **player 3 display** shows *which* ones, using
the manual's contact numbers (1–29 from *CONTACTOS DE TABLERO*, not the PinMAME
switch numbers). This is the fastest way to validate a table's switch wiring:
close one switch at a time and check that exactly one contact is reported.

The test covers only the 23 playfield contacts read through `0x4000` and the
74165 chain. The four cabinet inputs (25–28) are not part of it, and neither are
the four contacts wired in parallel with another one — closing either half of a
pair reports the pair's higher number (see the appendix).

> The `supstarfa` ROM extends this menu to **25 zones** — set 1's nine unchanged
> plus sixteen more — and reserves an extra `0x30` bytes of NVRAM (its stack base
> drops from `C7FF` to `C7CF`). The extra sixteen are not documented in the manual.

### 5.2 TEST DE LUCES Y VISUALIZACION DE RAM (DIP = 1)

Power on with the *test* switch up and the machine goes straight into the lamp
test: every playfield and backbox bulb lights alternately. This exercises both
mains phases, so it is a good end-to-end check that a table has all 44 usable lamp
numbers wired.

Pressing **start** from inside the lamp test steps through the RAM-visualisation
(audit) zones. Each zone shows four counters, one per player display.

**ZONA 1**

| Display | Spanish | English |
|---|---|---|
| Player 1 | TOTAL PARTIDAS | Total games played |
| Player 2 | TOTAL ESPECIALES PRIMER TANTEO | Specials awarded at threshold 1 |
| Player 3 | TOTAL ESPECIALES SEGUNDO TANTEO | Specials awarded at threshold 2 |
| Player 4 | TOTAL ESPECIAL TERCER TANTEO | Specials awarded at threshold 3 |

**ZONA 2**

| Display | Spanish | English |
|---|---|---|
| Player 1 | TOTAL ESPECIAL POR LOTERIA | Specials awarded by the lottery |
| Player 2 | TOTAL ESPECIALES POR PICABOLAS | Specials awarded by the spinner |
| Player 3 | TOTAL ESPECIALES POR RAMPAS | Specials awarded by the ramps |
| Player 4 | TOTAL BOLAS EXTRAS | Extra balls awarded |

**ZONA 3**

| Display | Spanish | English |
|---|---|---|
| Player 1 | TOTAL MONEDAS DE 25 PTS. | 25 pta coins taken |
| Player 2 | TOTAL MONEDAS DE 100 PTS. | 100 pta coins taken |
| Player 3 | TOTAL PARTIDAS GRATIS MONEDAS DE 25 PTS. | Free games from the 25 pta slot |
| Player 4 | TOTAL PARTIDAS GRATIS MONEDAS DE 100 PTS. | Free games from the 100 pta slot |

### 5.3 BORRADO DE DISPLAY Y CREDITOS (DIP = 2)

Powering on in this position clears all stored credits.

---

## 6. Getting started

### 6.1 The two things that will kill your table

**(1) Switch 27 (*caída de bolas*) must read CLOSED whenever a ball is in the
trough — which is the rest state, including at power-on.**

Both the game-start path and the fault-recovery path require it. Left open, the
recovery loop ping-pongs forever: the interrupt handlers keep running so the
machine *looks* alive — display refresh ticking, sound handshake completing,
attract lamps sensible — while the foreground program is dead and nothing you do
has any effect.

It must also **open** once the ball has been served, or the game ends every ball
the instant it starts one. The correct model is a two-state trough:

* closed at power-on, and whenever a ball is sitting in the outhole;
* opened when solenoid **10** (SALIDA BOLAS) fires;
* closed again when the ball drains.

The driver contains exactly that model, driven by the `HOME` key — but **it only
runs when PinMAME is handling the keyboard, which VPinMAME turns off.** Under VPX
your table owns switch 27 completely:

```vbscript
Sub Table1_Init
    Controller.Switch(27) = True    ' a ball rests in the outhole
End Sub

Sub SolBallRelease(enabled)
    If enabled Then
        Controller.Switch(27) = False   ' trough is now empty
        ' ...kick the ball into the shooter lane
    End If
End Sub

Sub Drain_Hit
    Controller.Switch(27) = True
End Sub
```

**(2) Coin switches must be pulsed, not held.**

The coin routine latches the coin and then waits for the contact to **open**
within 20 mains half-cycles (≈200 ms). If it is still closed it falls through to
the fault handler, which wedges the machine permanently — no reset short of
restarting the emulation gets it back.

```vbscript
Sub AddCoin25
    Controller.Switch(25) = True
    vpmTimer.AddTimer 60, "Controller.Switch(25) = False'"   ' well under 200 ms
End Sub
```

The driver's one-shot for this is, again, keyboard-mode only.

### 6.2 The absolute minimum to get a game going

| Item | Number | Why |
|---|---|---|
| Ball drain / outhole | switch **27** | Must be closed at rest, or nothing runs at all |
| Coin slot 25 pta | switch **25** | One of only two routes to a credit; pulse it |
| Coin slot 100 pta | switch **26** | Ditto |
| Start button | switch **28** | Starts a game *and* drives every operator menu |
| Ball release | solenoid **10** (SALIDA BOLAS) | Serves the ball, and empties the trough |

Also:

* **Leave switch 48 open.** It is a floating shift-register input; setting it
  makes the zone-9 contact test report a phantom contact.
* Switches 21–24 do nothing at all — the ROM never reads them.
* **Do not look for a ball-in-play display** — use lamps 25–29 (*BOLA 1*–*BOLA 5*).
* **The knocker is solenoid 2**, fired on every *especial*.
* Solenoid 1 and solenoid 6 never fire. That is correct, not a bug.
* **Bind lamp 9 for tilt, not lamp 1** (§2.9).

### 6.3 First boot: the NVRAM starts zeroed

The driver uses `MDRV_NVRAM_HANDLER(generic_0fill)`, so a fresh install starts
with 2 KB of zeros at `0xC000`–`0xC7FF`.

The reset path tests `C000` for the magic byte `0x55` and, failing it, executes
`RST 0` — which lands back on the reset vector. Nothing in that loop writes the
magic. It is the **TRAP handler** (the mains zero-cross interrupt) that notices
the bad magic, seeds `C000` with `0x55` and resets. So the first power-up takes a
moment and then comes up with **every adjustment at zero**.

**Practical consequence: zero games per coin. The machine will appear to swallow
coins without crediting.** Before shipping a table, or on your own first run:

1. Set DIP 1–2 to `3` (both door switches up) and reset.
2. You land in zone 1 (balls per game). DIP = `3` + start changes the value;
   DIP = `1` + start advances to the next zone.
3. Walk zones 1–8 and give each a sane value — in particular **zone 3** and
   **zone 4** (games per coin).
4. Optionally use zone 9 to verify every switch the table drives.
5. Set DIP back to `0` and reset.

The values persist in the `.nv` file from then on. Shipping a pre-adjusted `.nv`
with the table is the friendliest option.

### 6.4 Plumbing sketch

```vbscript
' ---- solenoids -------------------------------------------------
SolCallback(2)  = "SolKnocker"          ' TACA - especial awarded
SolCallback(3)  = "SolCoinLockout"
SolCallback(4)  = "SolCoinMeter25"
SolCallback(5)  = "SolCoinMeter100"
SolCallback(7)  = "SolResetLeftBank"    ' BANCADA IZQUIERDA
SolCallback(8)  = "SolPicabolas"
SolCallback(9)  = "SolResetRightBank"   ' BANCADA DERECHA
SolCallback(10) = "SolBallRelease"      ' SALIDA BOLAS - also opens switch 27
SolCallback(17) = "SndLeftBumper"       ' synthesised from switch 18
SolCallback(18) = "SndRightBumper"      ' synthesised from switch 12
SolCallback(19) = "SndLeftEject"        ' synthesised from switch 14
SolCallback(20) = "SndRightEject"       ' synthesised from switch 16
SolCallback(45) = "SolRFlipper"         ' synthesised by the PinMAME core
SolCallback(47) = "SolLFlipper"
' 1 and 6 are never asserted - do not bind them

' ---- flipper buttons (PinMAME's own cabinet column, not the game matrix) ----
' Controller.Switch(112) = right button, Controller.Switch(114) = left button

' ---- switches --------------------------------------------------
Sub Table1_Init
    Controller.Switch(27) = True        ' ball in the trough: MUST be closed
End Sub

' bumpers and ejects: solenoids 17-20 are for effects only, do the physics here
Sub LeftBumper_Hit
    vpmTimer.PulseSw 18                 ' scoring contact
    ' ...and kick the ball with your own mechanics
End Sub

' drop targets: close the individual switch AND pulse the bank contact
Sub LeftTarget1_Hit
    Controller.Switch(33) = True        ' stays closed while the target is down
    vpmTimer.PulseSw 13                 ' DIANA IZQUIERDA, bank-level contact
End Sub
```

---

## Appendix — the manual's contact numbers ↔ PinMAME switch numbers

Zone 9 reports the manual's numbering. Use this to translate.

| Manual contact | PinMAME switch |
|---|---|
| 1 PASILLO SUPERIOR IZQUIERDO | 46 |
| 2 PASILLO SUPERIOR DERECHO | 45 |
| 3 RAMPA ESPECIAL IZQUIERDA | 14 |
| 4 BUMPER IZQUIERDO | 18 |
| 5 PICABOLAS | 47 |
| 6 BUMPER DERECHO | 12 |
| 7 RAMPA ESPECIAL DERECHA | 16 |
| 8 DIANA IZQUIERDA (bank) | 13 |
| 9 DIANA DERECHA (bank) | 15 |
| 10 100 PUNTOS | 17 (paralleled with 21; reported as 21) |
| 11 DIANA 1 IZQUIERDA | 33 |
| 12 DIANA 2 IZQUIERDA | 35 |
| 13 DIANA 3 IZQUIERDA | 34 |
| 14 DIANA 4 IZQUIERDA | 36 |
| 15 DIANA 5 IZQUIERDA | 37 |
| 16 DIANA 1 DERECHA | 44 |
| 17 DIANA 2 DERECHA | 43 |
| 18 DIANA 3 DERECHA | 42 |
| 19 DIANA 4 DERECHA | 41 |
| 20 DIANA 5 DERECHA | 38 |
| 21 100 PUNTOS | 17 (paralleled with 10) |
| 22 PASILLO INFERIOR IZQUIERDO | 32 (paralleled with 26; reported as 26) |
| 23 PASILLO INFERIOR DERECHO | 31 (paralleled with 27; reported as 27) |
| 24 10 PUNTOS | 11 (paralleled with 25; reported as 25) |
| 25 10 PUNTOS | 11 (paralleled with 24) |
| 26 PASILLO INFERIOR IZQUIERDO | 32 (paralleled with 22) |
| 27 PASILLO INFERIOR DERECHO | 31 (paralleled with 23) |
| 28 CAIDA DE BOLA | 27 (not covered by zone 9) |
| 29 PULSADOR PARTIDA | 28 (not covered by zone 9) |
| — FALTA | none — RST 6.5, see §1.5 |

Note the collision of names: manual contact 27 is *pasillo inferior derecho*,
PinMAME switch 27 is *caída de bolas*. They are different things.

The ROM's table stores contacts 21, 25, 26 and 27 with bit 7 set, which is how it
marks the four paralleled pairs; that flag is why contacts 10, 22, 23 and 24 never
appear in the test on their own.

---

## Related documents

* `driver-notes.md` — for PinMAME reviewers: architecture, the 8085 core fixes,
  known driver gaps.
* `hardware-findings.md` — the full hardware analysis and its audit trail.
* `rom-provenance.md` — ROM sets, hashes, and the `supstarfa` BAD_DUMP case.
