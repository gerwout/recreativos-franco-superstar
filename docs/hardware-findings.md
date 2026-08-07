# Super Star (Recreativos Franco, 1986) — hardware findings

Reference for the machine and for the PinMAME driver that emulates it. Everything
here was derived by analysis and is reproducible; nothing has been checked against
a physical machine.

**Sources.** The game ROM disassembly (Ghidra, 8085 module), the sound ROM
disassembly (Ghidra, 8048 module, after de-scrambling), the factory manual
(`../super-star-pinball-manual.md`, including its *Fe de erratas*) and MAME's
`supstarf.cpp` skeleton. Where the manual and the ROM disagree, the ROM wins and
the disagreement is called out.

**Companion documents.**

| Document | For |
|---|---|
| `vpx-table-reference.md` | Visual Pinball table authors — the switch, lamp, solenoid and display tables |
| `driver-notes.md` | PinMAME reviewers — architecture summary, the 8085 core fixes, open items |
| `rom-provenance.md` | ROM sets, hashes, revision order, the MAME `BAD_DUMP` case |

Analysis artifacts live in `../ghidra/out/`. Regenerate with:

```bash
cd /code/superstar/ghidra
GHIDRA_INSTALL_DIR=/usr/share/ghidra ./venv/bin/python scripts/deep_analyze.py
GHIDRA_INSTALL_DIR=/usr/share/ghidra ./venv/bin/python scripts/export_analysis.py /ic19_game.bin
```

Addresses are set 1 (`supstarf`) unless stated otherwise.

**A note on how to read this document.** Part V records findings that were later
disproved. They are kept deliberately: several of them looked convincing for
hours, and knowing what the wrong answer looked like — and what finally settled
it — is worth more than a clean document.

---

# Part I — The machine

## 1. Boards and parts

Five boards. Everything the CPU touches is serial.

| Board | Ref. | Contents |
|---|---|---|
| C.P.U. | 53/3291 | 8085A main CPU, program ROM, NVRAM, **and the whole sound section** (8035, sound ROM, 2 × AY-3-8910, LM380, four 8212s) |
| Fuente de alimentación | 53/3309 | supplies, and the mains phase detector that feeds TRAP |
| Driver | 53/3308 | four CD4028 decoders + BT106 thyristors for lamps and coils, two 74165s for the switch chain |
| Displays | 53/3307 | 74164 → 8279 → 74159 + two 7447 → 30 × HDSP-3400 |
| Conexión intermedia | 53/3310 | interconnect; carries the flipper buttons, the knocker, and RL1, the coil-supply relay |
| Control bumper y expulsor | 53/3311 | fires the two bumpers and the two slingshots locally, with no CPU involvement |

| Function | Part | Socket |
|---|---|---|
| Main CPU | Intel 8085A @ 5.0688 MHz (X1) | IC9 |
| Game ROM | 27128, 16 KB → `0x0000`–`0x3FFF` | IC19 |
| Second game ROM socket | unpopulated on every known board | IC14 |
| NVRAM | 5517 2K×8, battery-backed → `0xC000`–`0xC7FF` | IC11 |
| Sound CPU | Intel 8035 @ XTAL/2 (8085 CLK OUT, pin 37) | IC7 |
| Sound ROM | 2532, 4 KB, **bit-reversed data bus** (§9) | IC4 |
| PSGs | 2 × AY-3-8910 @ XTAL/6 (8035 T0, pin 1) | IC2 = PSG2 (inputs), IC3 = PSG1 (outputs) |
| Latches | 4 × Intel 8212 | IC1, IC5, IC6, IC10 |
| Audio | LM380 | IC20 |

The manual settles two of MAME's open TODOs: the display controller is an
**8279** (MAME guesses "i8259"), and **IC7 is the 8035**.

## 2. Memory map and I/O

Verified from the disassembly. The 74S138 (IC8) decodes A14/A15 into CS0–CS3.

| Range | Width | Contents | Evidence |
|---|---|---|---|
| `0x0000`–`0x3FFF` | 16K | program ROM, IC19 | reset vector, all code |
| `0x4000` | 1 | **eight playfield contacts on connector JG**, active low | `LDA (0x4000)` at `0x18BD` → `STA (0xC026)` |
| `0x8000` | 1 | 8212 latch pair: read = reply from the sound CPU, write = command | `STA (0x8000)` at `0x1810`, `0x196C`; `LDA (0x8000)` at `0x0044` |
| `0xC000`–`0xC7FF` | 2K | 5517 battery-backed NVRAM, IC11 | throughout |

I/O space (8085 `OUT`) — only two ports are ever used, and the port number is
irrelevant because the whole space is one decode:

| Port | Purpose | Site |
|---|---|---|
| `OUT (0x00)` | shift clock, inside the SID switch-read loop | `0x18B3` |
| `OUT (0xFF)` | shift clock, inside the SOD display-write loop | `0x241C` |

This matches MAME's `main_io_map` (`map.global_mask(0xff); map(0x00,0xff).w(driver_clk_w)`).

> **Difference from MAME.** MAME's `main_map` does not map `0x4000` and would
> return open bus. Both ROM revisions read it, once per scan pass. See §4.1.

## 3. Interrupts and the boot path

| Vector | Addr | Set 1 target | Role |
|---|---|---|---|
| RESET | `0x0000` | `LXI SP,C7FF` → NVRAM magic test → `JZ 0186`, else `RST 0` | cold/warm boot |
| TRAP | `0x0024` | `JMP 0x1800` | mains zero cross, non-maskable, 100 Hz |
| RST 5.5 | `0x002C` | `JMP 0x003F` | 8212 sound-latch ack |
| RST 6.5 | `0x0034` | `JMP 0x0286` (set 2: `0x028E`) | *falta* (tilt), and the general fault/error path |
| RST 7.5 | `0x003C` | `JMP 0x0244` | **power fail / emergency stop** — see below |

RST 7.5 looks like a refresh tick and is not one. Its handler blanks the display
(`CALL 0x2400`), lights the *falta* lamp, clears `C001`, sends sound command
`0xCC` and then spins forever at `0x026A`:

```
0244: CALL 0x2400          ; blank the display
0247: LXI H,C21C / ORI 80  ; IC1 FASE B code 0 = luz falta ON
0250: LXI H,C228 / ANI 03  ; drop most of the IC2 FASE B lamps
0258: LXI H,C23D / ANI F7  ; drop the start-button lamp
0261: XRA A / STA (C001)
0265: MVI A,CC / STA (8000)
026A: XRA A / STA (C001) / JMP 026A   ; never returns
```

The ROM still opens a one-instruction window for it on every TRAP pass
(`SIM #$0B` / `EI` / `NOP` / `DI` at `0x182F`) and resets its latch with
`SIM #$1D` at `0x194C` — which is what makes the `SIM` bit 4 core fix necessary
even though the interrupt is never taken. An emulation must **not** drive it.

The `RST 0`–`RST 7` software vectors are all `0xFF` fill except `RST 0`, which is
used as a cold reset (`RST 0` at `0x000C` and `0x1822`).

```
0000: 31 FF C7   LXI SP,C7FF
0003: F3         DI
0004: 3A 00 C0   LDA (C000)
0007: EE 55      XRI 55        ; NVRAM magic byte
0009: CA 86 01   JZ 0186       ; warm boot
000C: C7         RST 0         ; else cold reset -> back to 0000
```

**TRAP is load-bearing at boot.** Nothing in that reset loop ever writes the
magic byte. The TRAP handler re-checks it and, if invalid, sends sound command
`0xBB`, spins a delay, writes `0x55` to `C000` and cold-resets
(`0x1806`–`0x1822`). Without TRAP running the machine never comes up at all.

### TRAP rate: 100 Hz, derived not assumed

The phase detector on the power-supply board (53/3309) takes an 11 V / 0 V / 11 V
centre-tapped winding into D3 and D4 (with R4, C1, R3) — full-wave rectification,
so 100 Hz on 50 Hz Spanish mains. That is also the rate the FASE A / FASE B lamp
multiplexing needs, since the two phases light on alternate half-cycles.

### The sound CPU holds the rest of the machine in reset

P2.4 on the 8035 is the system `/RESET` net: it reaches both AY-3-8910s (pin 23),
the 8212 latches and the main board. The sound CPU asserts it at `0x0BA`, holds it
across its power-up timer delay (40 iterations of a full 256-count timer overflow
at `0x00BF`–`0x00C5`, ≈1.94 s) and releases it at `0x0C7`. So the 8035 deliberately
holds the 8085 in reset while it starts up. This delay is genuine, not an
emulation artefact, and it is the first reason not to measure anything early
(§13).

---

# Part II — Subsystems

## 4. Switch input

Four hardware bytes reach the game, from three different places.

### 4.1 The `0x4000` port — eight playfield contacts, connector JG

Read once per scan pass at `0x18BD` and stored to `C026`. The bus is active low
and the ROM applies no `CMA`, so `0` = closed.

The CPU-board JG connector table gives the bus bit for each contact directly, and
the ROM's own switch-test table (§4.5) lists the same order independently:

| Bit | Conn. | Contact | Manual contact # |
|---|---|---|---|
| AD0 | JG8 | 10 PUNTOS | 24 + 25 (paralleled) |
| AD1 | JG6 | BUMPER DERECHO | 6 |
| AD2 | JG3 | DIANA IZQUIERDA (bank) | 8 |
| AD3 | JG2 | RAMPA ESPECIAL IZQUIERDA | 3 |
| AD4 | JG1 | DIANA DERECHA (bank) | 9 |
| AD5 | JG4 | RAMPA ESPECIAL DERECHA | 7 |
| AD6 | JG5 | 100 PUNTOS | 10 + 21 (paralleled) |
| AD7 | JG7 | BUMPER IZQUIERDO | 4 |

Four of these eight also fire a coil locally on board 53/3311 (§7.4).

### 4.2 The serial chain — sixteen contacts on SID

Two 74165 shift registers on the driver board (IC6 = left/JM, IC5 = right/JN) are
cascaded and clocked out into the 8085's SID pin, through 7414 inverters, one bit
at a time. Routine at `0x18A6`, storing to `C028`/`C029`:

```
189C: LXI H,C029
189F: MVI M,00
18A1: DCX H          ; H = C028
18A2: MVI M,00
18A4: MVI E,01       ; 2 bytes
18A6: MVI D,07       ; 8 bits
18A8: RIM            ; SID -> bit 7
18A9: CMA
18AA: ANI 80
18AC: ORA M
18AD: DCR D
18AE: JM 0x18B2
18B1: RRC
18B2: MOV M,A
18B3: OUT (0x00)     ; clock the 74165s
18B5: JP 0x18A8
18B8: INX H
18B9: DCR E
18BA: JP 0x18A6
18BD: LDA (0x4000)
```

**Polarity.** The contacts are active low at the 74165 inputs, but the chain
output reaches the CPU as `/SID` — inverted by IC4 (7414) — so a closed contact
presents `1` at SID. The ROM's `CMA` then makes `0` = closed in `C028`/`C029`,
which is the same convention as the `0x4000` byte. The dispatch code confirms it:
it calls a handler with `CZ`, i.e. on a zero bit.

For the driver this means SID must be presented **as PinMAME has it** — 1 = closed
— with no inversion. That is what `rfranco_sid_r` does.

**Chain order.** IC6 clocks out first and its H input leaves before A, so the
firmware sees chain positions 2..17: IC6's H input (JM3) is shifted past before
the first `RIM` and is invisible to the ROM. That is exactly why the manual's
errata moves the *picabolas* contact from JM3 to JN2.

**IC6 — left, connector JM**

| 74165 in | Pin | JM | Contact |
|---|---|---|---|
| H | 6 | JM3 | PICABOLAS — **errata: becomes N.U.**, and is invisible to the ROM anyway |
| G | 5 | JM4 | PASILLO INFERIOR DERECHO |
| F | 4 | JM5 | PASILLO INFERIOR IZQUIERDO |
| E | 3 | JM6 | DIANA IZQUIERDA 1 |
| D | 14 | JM7 | DIANA IZQUIERDA 2 *(the ROM says 3 — see below)* |
| C | 13 | JM8 | DIANA IZQUIERDA 3 *(the ROM says 2 — see below)* |
| B | 12 | JM1 | DIANA IZQUIERDA 4 |
| A | 11 | JM2 | DIANA IZQUIERDA 5 |

**IC5 — right, connector JN**

| 74165 in | Pin | JN | Contact |
|---|---|---|---|
| H | 6 | JN3 | DIANA DERECHA 5 |
| G | 5 | JN4 | DIANA DERECHA 4 |
| F | 4 | JN5 | DIANA DERECHA 3 |
| E | 3 | JN6 | DIANA DERECHA 2 |
| D | 14 | JN9 | DIANA DERECHA 1 |
| C | 13 | JN8 | PASILLO SUPERIOR DERECHO |
| B | 12 | JN7 | PASILLO SUPERIOR IZQUIERDO |
| A | 11 | JN2 | **PICABOLAS** (errata; the schematic sheet shows N.U.) |
| SER | 10 | JN1 | floating — the sixteenth bit, must read open |

Both errata entries come from the manual's own *FE DE ERRATAS*: the picabolas
contact moves from JM3 to JN2, and IC5 pin 10 goes to JN1 while pin 11 goes to
JN2.

> **The one disagreement between the manual and the ROM.** The manual labels JM7
> *diana izquierda 2* and JM8 *diana izquierda 3*; the ROM's switch-test table
> reports contact 13 (target 3) for the JM7 position and contact 12 (target 2) for
> JM8. Fifteen of the sixteen serial positions agree; this is the only one that
> does not. The ROM is what the machine displays in zone 9, so it is taken as
> authoritative.

### 4.3 Cabinet inputs — through the sound CPU

The 8085 cannot read these directly. It asks the 8035 with sound command `0x99`
(`0x18C3`: `MVI A,99 / CALL 196C`); the 8035 answers from `0x060F` by selecting
PSG2 (IC2) and reading AY register `0x0E`, and the reply lands in `C027`.

| Bit | CPU-board JC | Driver-board JO | Contact |
|---|---|---|---|
| PA4 | JC1 | JO5 | MONEDERO 25 PTS. |
| PA5 | JC2 | JO4 | MONEDERO 100 PTS. |
| PA6 | JC3 | JO3 | CAIDA DE BOLAS (the driver board also calls this net *contacto final partidas*) |
| PA7 | JC4 | JO2 | PULSADOR PARTIDAS |
| PA0–PA3 | — | — | not wired |

**Bits 0–3 are never read by the game.** Every read of `C027` masks with `0x10`,
`0x20`, `0x40` or `0x80` and nothing else.

*Falta* (tilt) does not come through here at all: JO1 → JD1 → RST 6.5.

The two operator door switches arrive on PSG2 **port B** bits 7/6 (`0x0F`);
`0xC0` = both down = normal play, which is what the boot dispatch at `0x00BB`
decodes.

### 4.4 Three rules the firmware imposes

The first two were found the hard way, by a machine that booted, refreshed its
display and completed its sound handshake while the foreground program was dead.
The third was found the same way, by a soak that kept serving the same ball.

* **Caída de bolas must read closed at rest.** It is closed whenever a ball is
  sitting in the trough. Both the game-start path at `0x0508` and the fault
  recovery at `0x030F` require it. Left open, `0x030F` and `0x0331` ping-pong
  forever.
* **Coin contacts must pulse.** `0x0545` latches the coin, then waits for the
  contact to **open** within 20 TRAP ticks (≈200 ms). If it is still closed it
  falls through to `0x055C` and jumps to the fault handler, which wedges the
  machine permanently.
* **A ball that has not scored is not counted.** Closing the trough on a ball
  that has scored nothing since it was served does not advance the ball number;
  the game serves the same ball again, indefinitely. Measured: two consecutive
  drains of an untouched ball left the ball number unchanged, and a single
  10-point contact before the third drain made it advance at once. This is a
  sensible rule — it is what stops a ball that never left the shooter lane from
  being lost — but it costs time to rediscover from the outside, and it is why
  `tools/rfranco_soak.py` scores once before every drain.

### 4.5 The zone-9 switch-test table, decoded

Immediately after the adjustment jump table (set 1: `0x34A2`), byte-identical in
both ROM revisions:

```
A5 06 08 03 09 07 A1 04 | A7 A6 11 13 12 14 15 20 | 19 18 17 16 02 01 05 FF
```

24 entries: the eight `0x4000` bits (LSB first), then the sixteen serial-chain
positions in shift order. Each entry is the manual's contact number in BCD.
**Bit 7 marks a contact that is wired in parallel with another one**, and the
table stores the higher of the pair — which is why the manual's contacts 10, 22,
23 and 24 never appear in the test on their own. The four flagged entries
(`A5`=25, `A1`=21, `A7`=27, `A6`=26) are exactly the four paralleled contacts.

The final `FF` is IC5's floating SER input.

This table is what pins the whole switch map down without hardware, and it agrees
with the manual everywhere except JM7/JM8.

## 5. Display output

### 5.1 The serial path

`SOD → 74164 (IC1) → 8279 (IC2) → 74159 (IC6) digit select + 2 × 7447 (IC5/IC7)
segments → 30 × HDSP-3400`. Connector JA carries `CLK` (pin 10), `SOD` (11),
`LOAD` (12) on the display-board side.

Routine at `0x2417`. `E` holds the payload, `D` the trailing SOD level:

```
2417: MVI D,0xC0     ; D = SOE|SOD  -> line left HIGH after the frame
2419: PUSH BC
241A: MVI B,0x09     ; 9 bits
241C: OUT (0xFF)     ; clock pulse
241E: MOV A,E
241F: RAL            ; next payload bit -> carry
2420: MOV E,A
2421: MVI A,0x80
2423: RAR            ; A = (carry<<7) | 0x40  -> bit7 = data, bit6 = SOE
2424: SIM            ; drive SOD
2425: DCR B
2426: JNZ 0x241C
2429: MOV A,D
242A: SIM            ; final SOD level
242B: MVI B,0xAA
242D: CALL 0x1987    ; sound command 0xAA = LOAD strobe
```

Nine clocks per frame, each preceded by an `OUT`. The first clock has no `SIM`
before it and shifts in the stale trailing level from the previous frame, which
then falls off the end of the 8-bit 74164 — so dropping the leading bit lands the
payload byte exactly.

Entry points:

| Entry | `E` | `D` | Note |
|---|---|---|---|
| `0x2400` | `0xDD` | `0xC0` | |
| `0x2405` | `0xDD` | `0xC0` | via `CALL 0x1779` first |
| `0x240D` | `0x20` | `0xC0` | |
| `0x2415` | `0x08` | `0xC0` | |
| `0x2432` | caller | `0x40` | trailing SOD **low** |

### 5.2 The LOAD strobe and the 8279's A0

The byte in the 74164 is committed when `LOAD` pulses, which is the rising edge of
the 8279's `/WR`. `LOAD` comes from the sound CPU: **sound command `0xAA`** makes
the 8035's handler at `0x078` pulse P1, which drives the display strobe gates.
`0x242B` is the only place in the whole ROM that sends `0xAA`.

The 8279's A0 is whatever level SOD was left at: `0x2417` finishes with `D=0xC0`
(high = command) and `0x2432` with `D=0x40` (low = data). That is the entire
command/data distinction.

### 5.3 Digit map

The 8279 has 16 display-RAM addresses; each byte holds two digits. The high nibble
goes to the 7447 driving D15–D30, the low nibble to the one driving D1–D14, with
the 74159 selecting one anode pair per RAM address. Digits are raw BCD and `0x0F`
blanks.

Players 1 and 3 take the low nibble, 2 and 4 the high one; players 1–2 use even
RAM addresses and 3–4 odd ones. The 8279's *display write inhibit* command masks
one nibble so the two players sharing an address can be written independently.

Address 0/1 is the least significant digit and carries the score's fixed trailing
zero — the smallest playfield award is 10 points. 4 players × 7 digits + 2 credit
digits = exactly 30, which is why there is no ball-in-play display on this board.

The full address → segment-index table is in `vpx-table-reference.md` §4.2.

## 6. Lamps

### 6.1 Two lamps per decoder output

Three CD4028 BCD-to-decimal decoders on the driver board (IC1, IC2, IC3), each
output gating a BT106 thyristor. A fired thyristor conducts to the end of the mains
half-cycle, so **each output serves two lamps** — one wired to FASE A, one to
FASE B — selected by which half-cycle it was gated in.

| Decoder | Nibble | Connector | Contents |
|---|---|---|---|
| IC1 | PSG1 port A, high | JA → display board | falta, jugador 1–4, lotería 00–90 |
| IC2 | PSG1 port A, low | JQ | 20 playfield lamps |
| IC3 | PSG1 port B, low | JP | 9 playfield lamps |
| IC7 | PSG1 port B, high | JL | the coils (§7) |

Signal routing from the CPU board: JB1–4 = PA0–PA3 → IC2, JB5–8 = PA4–PA7 → IC1,
JC5–8 = PB0–PB3 → IC3, JD2/4/6/7 = PB4–PB7 → IC7.

### 6.2 Which phase is which

The 8035 samples the mains half-cycle on T1 (JD-8, *detección fase*). There is
exactly one `JT1` in the whole sound ROM, at `0x00F8`, inside the handler for
sound command `0xDD` — the command that opens every lamp frame. The 8035 replies
1 or 0, and the 8085 stores it in `C04F` and uses it to pick between two copies of
the lamp tables (`0x199C`–`0x19C7`).

The phase↔content assignment is settled by the ROM, not guessed: the four
score-threshold blocks at `0x1306` / `0x1343` / `0x1372` / `0x13A1` flash IC1
FASE B code 1, FASE B code 2, FASE A code 1 and FASE A code 2 for players 1, 2, 3
and 4 respectively. That matches the manual's IC1 table, where the FASE A column
carries *jugador 3º/4º* and FASE B carries *jugador 1º/2º*.

The ROM also settles something the manual leaves open. The errata puts the *falta*
lamp on IC1 pin 3 = decoder output 0, connector JA8, without saying which phase.
Every write that sets or preserves code 0 targets the **FASE B** copy of the table
(`C21C`, e.g. `ORI 0x80` at `0x008A` and at `0x024A`), while the FASE A copy
(`C219`) is repeatedly masked with `ANI 0x1F`, which clears code 0 unconditionally
(`0x0125`, `0x02B7`). **The tilt lamp is on FASE B only**, and IC1's FASE A
code 0 is a dead output.

Note the gating phase lags the reported one by a TRAP: `0x19E6` sends `0xDD`,
stores the reply in `C04F` and immediately ships the buffer that `0x1996` built on
the *previous* pass.

### 6.3 Decoder code order

The manual's IC1/IC2/IC3/IC7 schematic tables list ten rows each, **bottom row
first** in decoder-code order — i.e. the last row of each table is code 0. Three
independent checks:

* IC2 read that way gives the *avance* ladder ascending (code 0 = 10 000 … code 9
  = 100 000) and *bola 1*…*bola 5* on codes 0–4. Read the other way both run
  backwards.
* IC1 read that way puts *jugador 1º/3º* on code 1 and *jugador 2º/4º* on code 2,
  which is exactly what the ROM does (§6.2).
* The errata puts the *falta* lamp on "IC1 pin 3", and CD4028 pin 3 is Q0.

The one exception is IC7, whose last two rows are the other way round — see §7.2,
where the ROM settles it.

### 6.4 The lamp frame

The 8085 does not touch the PSGs. It builds a 20-byte frame in `C034`–`C047` and
ships it to the sound CPU, which forwards each byte to PSG1.

The builder is at `0x1A02` (one slot) / `0x1A2E` (a decoder's ten slots):

```
1A02: MOV A,(HL) / RAL / MOV (HL),A     ; next bit of the high-nibble table
      MVI D,FF
      (if carry) D = (E<<4) | 0x0F      ; select this decoder output
      LDAX (BC) / RAL / STAX (BC)       ; next bit of the low-nibble table
      (if carry) D = (D & 0xF0) | E
      store D at (C04D)++ ; INR E
```

so **slot *n* emits decoder code *n* in each nibble, or `0xF` for "none"**. Ten
slots for port A (`0x0E`: IC1 high, IC2 low), then ten for port B (`0x0F`: IC7
high, IC3 low).

`0x1A2E` runs eight slots from the first table byte, then skips both pointers
forward by 6 and runs two more, which is how codes 8 and 9 come from a second
byte.

Source tables, selected by phase:

| Decoder | FASE A bytes | FASE B bytes |
|---|---|---|
| IC1 | `C2A9`, `C2AF` | `C2AC`, `C2B2` |
| IC2 | `C2B5`, `C2BB` | `C2B8`, `C2BE` |
| IC7 (coils) | `C2C1`, `C2C7` | `C2C4`, `C2CA` |
| IC3 | `C2CD`, `C2D3` | `C2D0`, `C2D6` |

Within each byte, bit 7 = code 0 … bit 0 = code 7; in the second byte, bit 7 =
code 8 and bit 6 = code 9.

The `C2xx` block is itself rebuilt on every TRAP by the loop at `0x1844`–`0x186A`,
from three parallel tables at `C219` (steady state), `C249` (force on) and `C279`
(force off), merged on alternate frames of the `C006` counter:

```
1849: LDA (C006) / ANA A
184D: LXI H,C219 / DAD B / MOV A,(HL)
1852: JP 0x185F                        ; on the other half of the blink cycle:
1855: LXI H,C279 / DAD B / ANA (HL)    ;   A &= "force off"
185A: LXI H,C249 / DAD B / ORA (HL)    ;   A |= "force on"
185F: LXI H,C2A9 / DAD B / CALL 15EC
```

That is the machine's lamp flashing, and it is why a VPX table should follow lamp
state rather than add blink logic of its own.

**Emulation consequence.** A lamp is gated for an ~85 µs slot and then stays lit
for the rest of the half-cycle. Sampling instantaneously reports nothing useful;
the driver accumulates selects into `lampAcc[7]` and commits them at each TRAP.

## 7. Coils

### 7.1 IC7, the fourth CD4028

The high nibble of PSG1 port B (`0x0F`) is IC7's select code. Codes 0–9 pick an
output; 10–15 select none.

### 7.2 The map, settled by the ROM

Every write to the coil bit-field is an immediate `MVI A,<bit>` to `C231` (codes
0–7) or `C237` (codes 8–9). There are exactly eight in set 1, and their contexts
identify each coil:

| Code | Sol # | Pin | Coil | Bit written | Where, and why it is that coil |
|---|---|---|---|---|---|
| 0 | 1 | JL10 | *(unwired)* | never | connector pin is N.C. |
| 1 | 2 | JL6 | TACA (knocker) | `0x40` @ `0x175C` | called from the four score-threshold blocks after a special is awarded; the same routine adds a credit at `0x1727` |
| 2 | 3 | JL7 | BOBINA MONEDERO | `0x20` @ `0x15A6` | coin-mechanism actuator |
| 3 | 4 | JL9 | CONTADOR 25 PTS. | `0x10` @ `0x055F` | end of the 25 pta coin path (`C027` bit 4) |
| 4 | 5 | JL8 | CONTADOR 100 PTS. | `0x08` @ `0x05F4` | end of the 100 pta coin path (`C027` bit 5) |
| 5 | 6 | JL3 | FLIPPER supply relay | **never** | see below |
| 6 | 7 | JL2 | BANCADA IZQUIERDA | `0x02` @ `0x1656` | guarded by `(C028 & 0x7C) != 0x7C`, the five left drop targets |
| 7 | 8 | JL5 | PICA-BOLAS | `0x01` @ `0x1004` | |
| 8 | 9 | JL1 | BANCADA DERECHA | `0x80` @ `0x1639` | guarded by the right-bank target bits |
| 9 | 10 | JL4 | SALIDA BOLAS | `0x40` @ `0x1682` | ball release, in the ball-start sequence |

**Codes 0 and 1 are the one place the manual and the ROM cannot both be right.**
Read strictly bottom-up the manual puts TACA on code 0 and the N.C. on code 1 —
and that reading is not just a row-order guess: the schematic sheet
(`manual-images/page-23.jpg`) prints the 4028 output pin number against every
row, bottom to top 3, 14, 2, 15, 1, 6, 7, 4, 9, 5, which is Q0…Q9 exactly. The
JL connector table on the previous sheet agrees about the other half: JL10 is
the one pin on that connector with no wire colour listed. So by the manual, TACA
is on Q0 → JL6 and Q1 → JL10 is unwired.

The ROM gates code **1** on a replay award and never code 0, in both firmware
revisions. That is now measured rather than read: award a special on a running
machine and the coil select taken off PSG1 port B is output 1, together with the
credit. Codes 2–9 all match the manual's assignment exactly, so the disagreement
is confined to these two rows.

Taken literally the manual says the machine never knocks and the one coil output
the program drives goes nowhere. The driver assumes instead that the sheet's
bottom two rows have their JL destinations transposed — the same manual's own
*fe de erratas* already corrects two transpositions of exactly this kind
(connector JA reversed, IC5 pins 10 and 11 swapped) — and keeps TACA on code 1.
**This is an inference. Only a physical board settles it.**

**Code 5 — the `FLIPPER` relay — is never asserted.** The interconnect board
calls the relay it drives *relé alimentación bobinas* (RL1, 75 Ω, on J2-9), so the
name on JL3 is misleading. Since the ROM never energises it and the machine
plainly works, the relay must not gate anything the game needs; the flipper
buttons feed their coils directly through interconnect J1-18/19. Confidence:
the "never asserted" half is exhaustively verified; the interpretation of what the
relay does is inferred.

### 7.3 Only one coil is sustained at a time

Before shipping the frame, `0x19CA`–`0x19E5` scans the ten coil slots for the
first byte whose high nibble is < `0x0A` and copies that code into the **last**
slot:

```
19CA: MVI D,09 / LXI H,C03E
19CF: MOV A,(HL) / ANI F0 / CPI A0 / JC 19DC
      INX H / DCR D / JP 19CF
19DC: MOV D,A / LXI H,C047
      MOV A,(HL) / ANI 0F / ORA D / MOV (HL),A
```

The 4028 is a level device, so leaving it selecting a coil in the final slot is
what keeps the thyristor gated for the remainder of the half-cycle. If two coils
were requested at once, the lower-numbered one gets the sustained slot.

### 7.4 The four coils the CPU never sees

The two pop bumpers and the two *expulsores* are fired on board 53/3311 straight
from their playfield switches: +9 V through a 1N4007 and the switch into a
timing capacitor, then BDX53C to the coil at +48 V. The CPU only ever learns that
the switch closed, so there is no coil event to report. The board's 15-way
connector names all four (`manual-images/page-29.jpg`): ENTRADA/SALIDA BUMPER
IZQUIERDO on 1/2, BUMPER DERECHO on 4/5, EXPULSOR IZQUIERDO on 6/7, EXPULSOR
DERECHO on 10/11, with 12/13 at +48 V and the common emitter fused at 1.5 A.

**The *expulsores* are the slingshots, not kickout holes.** This playfield has no
holes at all. The contact drawing (`manual-images/page-07.jpg`, manual page 3)
puts contacts **24 and 25**, both named *10 PUNTOS*, inside the two triangular
bodies at the bottom corners; the parts list calls that mechanism the
*RECHAZADOR* and it is the only coil-bearing mechanism in the manual that the
driver board's JL connector does not account for. Contacts **3 and 7**, *rampa
especial izquierda/derecha*, are plain rollover wires in the upper outer lanes
with the ESPECIAL lamps (JP10/JP9) beside them, and drive nothing.

Contacts 24 and 25 are wired in parallel onto AD0, which the ROM's own contact
test states independently by flagging that bit as a paralleled pair (§4.5). So
one CPU input serves both slingshots and the program cannot tell left from
right.

The driver synthesises four pseudo-solenoids (17–20) from the rising edges of the
corresponding `0x4000` bits so that a front end has something to drive: 17 and 18
from the two bumper contacts, and **both** 19 and 20 from switch 11. They carry
no information the switch did not already carry.

## 8. Operator switches, adjustments and audits

Two switches on the door, reaching the CPU as PSG2 port B bits 7/6 (`1` = down):

| Position | Mode entered at power-on |
|---|---|
| both down | JUEGO (normal play) |
| test up | TEST DE LUCES Y VISUALIZACION DE RAM |
| ajuste up | BORRADO DE DISPLAY Y CREDITOS |
| both up | AJUSTES DE TANTEO Y TEST DE CONTACTOS |

The ROM dispatches on them at boot (`0x00BB`) **and re-reads them live inside the
menus**, which is the part that matters for driving the machine from outside: in
AJUSTES, both switches still up makes the start button step the current zone's
*value* and either one put back down makes it step to the next *zone* (set 1
`0x3380`/`0x33BC`, set 2 `0x3383`/`0x33BF`). A DIP setting cannot be moved while
the machine runs, so the driver also exposes the two switches on the spare
cabinet bits — switch 23 lifts *ajuste*, switch 24 lifts *test* — ANDed into the
DIP value so that both open changes nothing.

Set 1 has 9 adjustment zones; set 2 has **19**, numbered 1–9 and 10–19. Its jump
table at `0x349D` carries 25 entries, which is where the "25 zones" figure in
earlier notes came from, but the zone counter at `C01D` is BCD and the step at
`0x33DD` forces `0x0A` to `0x10`, so table entries 9–14 can never be selected;
they are filled with the address of the zone-9 handler. Walked on the running
machine with `tools/rfranco_zones.py`, set 1 reaches zones 1–9 and set 2 reaches
1–9 and 10–19, and stops.

The zone contents, including all ten of set 2's extra ones, and the three
RAM-visualisation audit zones are tabulated in `vpx-table-reference.md` §5.

## 9. The sound section

### 9.1 The data bus is bit-reversed

The 2532 at IC4 has its data pins wired to the 8035's AD0–AD7 in reverse order
(EPROM D7 → AD0, D0 → AD7). Straight off the chip the image is not MCS-48 code at
all; reversed byte by byte it is an ordinary program:

| variant | JMP | CALL | RET | MOV A,# | OUTL | first bytes |
|---|---|---|---|---|---|---|
| as dumped | 119 | 35 | **5** | 10 | 8 | `a8 20 f9 a3 f5 20 14 a6` |
| **bit reversed** | **172** | **88** | **28** | **59** | **48** | `15 04 9f c5 af 04 28 65` |

Five `RET` opcodes in 2 KB of program is not credible. Reversed, the vector layout
is textbook:

```
000: 15        DIS I
001: 04 9F     JMP $09F
003: C5 AF     SEL RB0 / MOV R7,A     <- external interrupt
005: 04 28     JMP $028
007: 65        STOP TCNT              <- timer
```

Six independent dumps across five manufacturer device profiles agree on the chip
contents, so the reversal is in the board wiring, not the dump. The driver undoes
it once after ROM load.

This is very likely why MAME's driver is marked `MACHINE_NO_SOUND`: it loads the
image unmodified, so its 8035 executes noise.

### 9.2 Command protocol

The 8035 reaches everything through `MOVX`, with **P2.7 low selecting the 8212
latch pair** and **P2.6 low selecting PSG1** / **P2.5 low selecting PSG2**. The
MOVX address comes from R0/R1 and, for the PSGs, is the AY register number.

```
0028: MOV A,#$7F / OUTL P2,A   ; P2.7 low
002B: MOVX A,@R1               ; read command, clears INT35
002C: INC A                    ; NOTE: the dispatch tests cmd+1
002D: JZ  $083                 ; 0xFF = idle
002F: MOV R1,#$21 / MOV @R1,A  ; stash cmd+1
0032: XRL A,#$AB / JZ $078     ; matches when cmd == 0xAA
      ... cumulative XOR chain ...
```

Because of the `INC A`, the handled commands are one less than the constants in
the chain: **`0xAA`, `0xDD`, `0x99`, `0x88`, `0xEE`, `0x69`, `0x96`, `0x77`**.

| Command | Purpose |
|---|---|
| `0xAA` | display LOAD strobe, and an echo/ping the main side verifies (§5.2) |
| `0xDD` | opens a lamp/coil frame; **replies with the T1 mains phase** |
| `0x99` | read the cabinet inputs (PSG2 port A) |
| `0xBB` | sent by the TRAP handler on invalid NVRAM (`0x1810`) |
| `0x88`, `0xEE`, `0x69`, `0x96`, `0x77` | sound effects / sequencer control; `0x96` and `0x69` also toggle the latched P1.6 output |

The `0xAA` echo path:

```
0078: ANL P1,#$C0 / ORL P1,#$3F    ; pulse the display strobe gates
007C: MOV A,@R1 / DEC A            ; A = 0xAA
007E: ORL P2,#$FF / ANL P2,#$7F    ; P2.7 low
0082: MOVX @R1,A                   ; reply -> raises RST5.5
```

and the main side, which verifies it:

```
1987: MOV A,B / STA (C033) / CALL $196C   ; arm C033, send
198E: XRA B / JNZ $0286                   ; reply must equal B
1992: STA (C033)                          ; disarm (A is 0 here)
```

`0x196C` writes the command, unmasks RST 5.5 with `SIM #$0E`, then either `HALT`s
or spins in the `EI`/`NOP` loop at `0x197D`. The RST 5.5 handler escapes that spin
by discarding its own return address:

```
003F: LDA (C033) / CPI $AA / LDA ($8000) / RNZ
0048: XTHL / LXI H,$1985 / PCHL
1985: POP H / RET            ; returns one level up, abandoning the spin
```

`C033` is the flag that tells the handler which of the two exits to take.

### 9.3 PSG access paths

* **PSG1 (chip 0, IC3) is the output device.** Its register 7 is programmed
  `0xF8` at sound ROM `0x00DB`, making both ports outputs. Registers `0x0E`/`0x0F`
  are the lamp/coil nibbles (§6, §7).
* **PSG2 (chip 1, IC2) is the input device.** Its register 7 is programmed `0x38`
  at `0x00B1`, making both ports inputs. Port A is the cabinet contacts, port B
  the two door switches.
* PSG1 is also **read back**: the sequencer's `REST` opcode saves a voice's volume
  register before muting it (sound ROM `0x2A5`).
* `P2 = 0x9F` pulls **both** chip selects low at once, which the sound ROM uses at
  `0x39B` to zero registers 8/9/10 on both chips. A driver must not treat the two
  selects as mutually exclusive.
* P1 does **not** carry BDIR/BC1 — those come from IC17 (7400) fed by `/WR35`,
  `/RD35` and ALE, which is why a single `MOVX` both latches the AY register
  number and writes it. P1 drives the 74S138 (IC8) and the 7438 (IC15) display
  strobe gates; P1.6 is an independent latched output.

### 9.4 Clock chain

The 8035 has no crystal of its own: it is fed from the 8085's CLK OUT (pin 37) =
XTAL/2, and its T0 output (XTAL1/3) clocks both AY-3-8910s, giving
5.0688 / 2 / 3 = 844 800 Hz = XTAL/6, as the manual says.

The sound ROM's tone table corroborates it exactly: at 844.8 kHz the entries give
A3 = 220.000, A4 = 440.000, A5 = 880.000 and A6 = 1760.000 Hz.

PinMAME's MCS-48 core has no internal divider — it decrements `i8039_ICount` by
machine cycles directly — so the value passed to `MDRV_CPU_ADD_TAG` must be the
machine-cycle rate, XTAL/2/15 = 168 960. PinMAME's 8085A core likewise takes the
internal clock rather than the crystal (compare `regama.c`, which passes
`6144000./2.`), so the main CPU gets 2 534 400.

---

# Part III — Firmware revisions

Summarised here; the full comparison and all hashes are in `rom-provenance.md`.

**Set 2 (`9A440461`) is the newer firmware**, despite MAME's parent/clone
ordering. It extends the operator menu from 9 adjustment zones to **19** (set 1's
nine unchanged, uniformly relocated by +`0x2D`, plus ten new handlers at
`0x3971`–`0x3A23` in what is `0xFF` fill in set 1) and reserves an extra `0x30`
bytes of NVRAM — its stack base drops from `C7FF` to `C7CF`, and the new
settings live at `C7F1`–`C7FD`.

Two of the new settings change how the game plays out of the box, so the two
sets do **not** score identically: set 2's 100 PUNTOS lane pays 1000 where set 1
pays 100 (zone 15, default `0x10`), and its zone 17 is on by default, so
completing a *diana* lights both bumper lamps and the bumpers go from 1000 to
10000. Everything else about the two is the same game.

**The manual documents exactly 9 zones, so the manual describes set 1.** Develop
and validate against set 1.

The playfield switch-test table (§4.5) is byte-identical in both: same machine,
same wiring, firmware revision only.

---

# Part IV — Emulation

## 10. The 8085 core

Five defects were fixed in `src/cpu/i8085/i8085.c`; they are described in
`driver-notes.md` §3. In short: `RIM` never sampled SID and reported the wrong
pending flags; `SIM` bit 4 (reset RST 7.5) was unimplemented; `i8085_reset()`
wiped the driver's callbacks; `EI` took effect immediately instead of one
instruction late; and `i8085_set_TRAP()` gated on `I.ISRV` so TRAP could fire only
once.

The features this ROM depends on, and where:

| Site | `A` | Bits | Effect |
|---|---|---|---|
| `0x1831` | `0x0B` | MSE=1, M7.5=0 | enable RST 7.5 only |
| `0x194C` | **`0x1D`** | **R7.5=1**, MSE=1, M6.5=0 | **reset the RST 7.5 latch** + enable 6.5 |
| `0x1962` | `(A&7)\|8` | MSE=1 | restore saved masks on ISR exit |
| `0x1971` | `0x0E` | MSE=1, M5.5=0 | unmask RST 5.5, then `HALT` |
| `0x2424` | `0x40`/`0xC0` | SOE=1 | drive SOD (display data) |
| `0x242A` | `D` | SOE=1 | final SOD level |

`RIM` sites: `0x1801` (TRAP entry), `0x18A8` (switch shift-in, SID), `0x34B1`.

## 11. The 8212 READY handshake

The lamp/coil frame at `0x19E6` sends command `0xDD` and then pushes 20 bytes
straight at the latch (`0x19F3`–`0x19F9`) with no handshake of its own. The 8035
does not take an interrupt for those bytes — it **polls** the INT pin with `JNI`
and consumes one byte per pass:

```
00F7: CLR A / JT1 $00F4
00FA: MOVX @R1,A
00FB: JNI $00FF      ; jump when INT is asserted
00FD: JMP $00FB      ; otherwise spin
00FF: MOV R1,#$0E / MOVX A,@R1   ; take the byte (clears INT)
0102: ORL P2,#$FF / ANL P2,#$BF  ; P2.6 low = PSG1 select
0106: MOVX @R1,A                 ; forward it to the PSG
```

The 8085 runs far ahead of the 8035 here, so without flow control it overwrites
the latch and most of the transfer is lost. The hardware holds the 8085 in wait
states through the 8212's READY output until the byte has been taken. MAME's
skeleton has that wiring present but commented out:

```cpp
//m_soundlatch[1]->int_wr_callback().append_inputline(m_maincpu, I8085_READY_LINE);
```

PinMAME's 8085 core has no READY input, so the driver stalls the main CPU on a
trigger (`cpu_spinuntil_trigger`) and lets the sound CPU release it
(`cpu_trigger`) when it reads the latch, with `cpu_triggertime` as a deadlock
guard.

Measured over the same 5 s window that previously showed 853 TRAP entries against
34 returns:

| addr | meaning | before | after |
|---|---|---|---|
| `0x1800` | TRAP entry | 853 | 176 |
| `0x189C` | after `CALL $2437` | 0 | 176 |
| `0x198E` | echo check | 0 | 176 |
| `0x1943` | handler pre-exit | 0 | 176 |
| `0x196B` | handler RET | 34 | 176 |
| `0x0286` | error path | 67 | 0 |

Every TRAP now completes, and SP holds a narrow band instead of walking down.

The guard timeout is sensitive and has no derivation: 500 µs was measured as
behaving correctly, 50 ms as much worse (the main CPU stalls long enough to
distort game timing). The driver currently uses 100 µs. See §15.

## 12. Timing constants and how each was established

| Constant | Value | Basis |
|---|---|---|
| Main CPU clock | 2 534 400 | 5.0688 MHz crystal, 8085 internal /2; PinMAME's core wants the internal clock |
| TRAP rate | 100 Hz | full-wave rectified 50 Hz mains, from the PSU schematic (§3) |
| 8035 clock | 168 960 | XTAL/2 pin frequency ÷ 15 machine cycles; MCS-48 core wants machine cycles |
| PSG clock | 844 800 | 8035 T0 = XTAL/6; corroborated by the ROM's tone table (§9.4) |
| Interleave | 500 | empirical, raised for the sound handshake before READY was modelled; re-test |
| READY guard | 100 µs | **not derived** — see §15 |
| RST 7.5 rate | 400 Hz | **a guess, and currently unused** — see §15 |

## 13. Measurement caveats

### The instrumentation hook counts both processors by default

`remote_debug_breakpoint_hook()` reads `activecpu_get_reg(REG_PC)` and matches it
against instrumented addresses whose `cpu` field is `-1`, which is the default
when `/api/debugger/instrument?cmd=add` is called without `&cpu=`. The 8035's
address space is `0x000`–`0xFFF` and overlaps the bottom of the 8085's, so **any
instrumented address below `0x1000` counts hits from both processors.**

Concrete example that cost real time: `0x0102` in the sound ROM is
`ORL P2,#0FFH` and fires once per TRAP, which made the 8085's main loop look like
it was running when it was in fact wedged.

It still affects the harness — see §14.

### Do not sample before the machine has settled

The 8035 spends ~1.94 s in a timer delay at power-on and holds the rest of the
machine in reset while it does; the game's own startup runs well past that.
Readings taken during that window look alarming and mean nothing. This produced
an entire phantom regression that was chased for hours (§18.2).

Typical settle is 75–80 s of wall clock.

## 14. Regression harness (`tools/rfranco_check.py`)

Boots the driver headless against the remote debugger, polls until it reaches
steady state, then asserts on the invariants established during bring-up.

```
tools/rfranco_check.py [--rom supstarf] [--verbose]
```

It detects the settle programmatically rather than sleeping a fixed time, and then
takes a *fresh* window, because the window that detects the settle straddles the
transition and still carries startup counts. `--verbose` prints each window so the
startup ramp is visible (display calls climb 0 → 3 → 8 → 21 → 143).

Checks: TRAP handler balance across the four per-set addresses; the fault latch
`C01C` clear; the display not sitting on the fault fill; stack pointer near its
reset value; both CPUs executing; a coin accepted; and the credit display showing
the count. Both sets pass all eight.

The earlier "known defect" note here — that the harness instrumented `0x0286`
without a CPU filter, and that `0x0286` in the sound ROM is live code — is
obsolete. The debugger's breakpoint, instrumentation and tracepoint endpoints now
take `&cpu=N`, and the harness asserts on machine state rather than on PC counts
wherever it can.

### Three more tools

| Tool | What it does |
|---|---|
| `rfranco_game.py` | Plays a complete game on either set — coin, credit, start, ball served, scoring, both drop-target banks, collecting a special, ball 1/2/3 with bonus, game over, final score held — and asserts on lamps, coils and digits at every step |
| `rfranco_soak.py` | Many games with randomised playfield traffic, checking after every game that the fault handler has not latched, the display is not on the fault fill, the stack has not walked and both CPUs are still running |
| `rfranco_zones.py` | Walks the AJUSTES menu on either set and prints each zone with its display and the NVRAM behind it. This is what established `supstarfa`'s ten extra zones |

`rfranco_zones.py` is also the reason the driver exposes the two door switches on
switches 23/24: the menu cannot be walked with a DIP setting, because the ROM
uses the switch *position at the time of the button press* to choose between
stepping the zone and stepping the value (§8).

## 15. Open questions

What is still genuinely unknown, after the second pass. Items that have been
closed are listed underneath with what closed them.

1. **Which 4028 output the knocker is actually on.** The ROM gates output 1 on a
   replay award, measured; the manual's IC7 sheet, read by the output pin
   numbers printed on it, puts TACA on output 0 and an unwired JL10 on output 1
   (§7.2). One of the two is wrong and only a physical board decides. The driver
   follows the ROM.
2. **The READY guard timeout.** 1000 µs, with a bound argued from the 8035's
   per-byte cost but not derived. The transfer no longer loses bytes and the
   echo check at `0x198E` tracks the TRAP count, but the number itself is still
   chosen rather than computed.
3. **PinMAME's 8085 core has no mask-reveal recheck.** `i8085_set_RST55()`
   returns early when the interrupt is masked, leaving `IREQ` set but never
   scheduling it, and nothing re-evaluates when a later `SIM` unmasks. The ROM
   does `SIM #$0E` then `EI` / `HALT` at `0x1971`. If the sound CPU's reply lands
   between the `STA` and the `SIM` the interrupt is lost and the `HALT` never
   wakes. Not observed in any soak so far, but structurally possible; newer MAME
   re-checks.
4. **Sound command semantics** beyond the six understood ones (§9.2). Sound ROM
   coverage is ~42% of the code region.
5. **The upper 2 KB of the sound ROM** (`0x800`–`0xFFF`) holds only four distinct
   byte values. Genuine, not a dump artefact; purpose unknown.
6. **The `FLIPPER` relay (IC7 code 5)** is never energised by the ROM, but the
   interconnect board calls the relay it drives *relé alimentación bobinas*. What
   it actually gates is inferred, not established.
7. **JM7 / JM8** — manual and ROM disagree on which is *diana izquierda 2* and
   which is 3 (§4.2). Only resolvable on hardware.
8. **Connector JA pin numbering.** The errata reverses the whole connector and the
   two boards' sheets number it in opposite directions. Signal names are reliable;
   pin numbers on JA are not.
9. **`supstarfa` zone 19 (`C7FD`).** The instruction it gates is not in doubt: at
   `0x11E6`, on the path between balls, it decides whether `0x0F70` runs, and
   `0x0F70` forces the saved avance ladder at `C094`/`C097` to its bottom rung
   and sets the `C7FE` flag. What has not been isolated is the visible
   consequence. `C094`/`C097` is read back at `0x1062` and written into the live
   ladder at `C226`/`C22C`, which reads as a ball-to-ball carry-over of the
   avance ladder — but with the setting off and a saved value deliberately
   different from the live one, the next ball still started at the bottom rung,
   so `0x1062` is evidently not on the ordinary new-ball path. The likely reading
   is that this is about the ball being held by the *picabolas* rather than about
   ball changes; that has not been tested.

### Closed since the first pass

| Question | What closed it |
|---|---|
| Whether solenoid 2 fires at all, or is only inferred from `0x1754` | Observed. Completing a drop-target bank lights the ESPECIAL lamp; collecting it at the *rampa especial* awards a credit and gates 4028 output 1, on both sets. What remains open is only which coil sits on that output — item 1 above |
| Which contacts fire the two EXPULSOR coils on 53/3311 | The contact drawing and the parts list: they are the two slingshots (*rechazadores*), contacts 24 and 25, both wired in parallel onto AD0 = switch 11 (§7.4). Not the *rampa especial* lanes |
| `supstarfa`'s extra adjustment zones | Ten of them, not sixteen; walked on the machine and each one's NVRAM byte, range and effect established (§8, `vpx-table-reference.md` §5.1.1) |
| Whether set 2 plays a complete game | It does, and so does set 1. `tools/rfranco_game.py` plays coin → credit → start → ball served → scoring → ball 1/2/3 → game over → final score held, and asserts on lamps, coils and digits at each step |
| Whether the harness's "error path" figure could be trusted | Superseded: the debugger endpoints take `&cpu=N` and the harness asserts on machine state instead |

# Part V — Superseded findings

Kept for the record. Each of these was believed at the time and is now known to be
wrong; what settled it is recorded with it.

## 16. "The `0x4000` read has an unknown purpose"

**Claimed:** that `LDA (0x4000)` at `0x18BD` might be a latched cabinet input or a
shift-register reload strobe whose *read* is the side effect.

**Actually:** it is a plain input port carrying eight playfield contacts on
connector JG, active low. Settled by the CPU-board JG connector table, which names
each contact against its bus bit, and independently by the ROM's own switch-test
table, which lists the same eight contacts in the same order (§4.1, §4.5).

## 17. "No existing PinMAME driver uses the 8085 core"

**Claimed** as the argument that the core fixes carry no regression risk.

**Actually:** `bingo.c`, `micropin.c` and `regama.c` all instantiate `8085A`, and
`taito.c` uses the same core as an 8080. `regama.c` even pushes SID with
`i8085_set_SID()`.

The narrower statement is the true one, and is what `driver-notes.md` argues:
none of them reads RIM's pending flags, uses `SIM` bit 4, or needs SID sampled per
instruction; and only `micropin.c` touches TRAP, as a level from a tilt switch
rather than as a 100 Hz pulse train. The `EI` timing fix does affect all of them
by one instruction, which is the part reviewers should look at.

## 18. The `CALL $2437` stack leak and its two wrong diagnoses

The original symptom was real and severe: the TRAP handler leaked a constant
`0x1C` bytes per pass, and the display call at `0x1899` never returned.

```
TRAP entry SP=0xC6B3, 0xC6A5, 0xC689, 0xC66D, 0xC651, 0xC635, ...
```

### 18.1 Wrong diagnosis: a self-sustaining `C033` race

**Claimed:** that `0x19E6` calls `0x196C` without touching `C033`, so a TRAP
arriving while the display path was spinning would unwind RST 5.5 against the
TRAP handler's frame, return to `0x1838` instead of `0x198E`, and leave `C033`
armed forever.

The reasoning was internally consistent and the observed return address (`0x1838`)
fitted it. Raising `MDRV_INTERLEAVE` from 50 to 500 did not fix it, which was read
as evidence that the problem was not scheduling granularity.

**Actually:** the root cause was the missing 8212 READY flow control (§11). The
bulk transfer at `0x19F3` was being lost, not mis-sequenced. Modelling READY made
every TRAP complete and drove the error path to zero; the `C033` behaviour is
normal and self-limiting once the transfers survive.

Ruled out along the way, and still true: the MCS-48 core's `anl_p2_n`/`orl_p2_n`
do call the port write handler, so the driver's `scpuP2` shadow is current; and
the `INC A`/`DEC A` pairing in the sound ROM means `0xAA` in gives `0xAA` back.

### 18.2 Wrong diagnosis: a regression after `3ff6b021`

**Claimed:** that the TRAP handler had stopped reaching the display call after the
serial-framing commit.

**Actually:** a sampling artefact. The original balanced figures were taken at
~2 minutes of uptime; every follow-up was taken at ~45 seconds, while the machine
is still working through its startup sequence. Measured again at matched uptime,
over a 10 s window at ~2 minutes:

| point | count |
|---|---|
| `0x1800` TRAP entry | 358 |
| `0x2437` display calls | 358 |
| `0x189C` after that call | 358 |
| `0x196B` handler RET | 358 |
| `0x0286` error path | 0 |

Exact balance, and `SP = 0xC7EB` against a reset value of `0xC7FF` — the
healthiest stack reading recorded.

Two sub-claims made during that chase and also disproved:

* That SID polarity caused the imbalance. It could not have: with `swMatrix` all
  zeros the pre-fix code returned 0 for every bit, identical to the uninstalled
  callback's `I.IM & IM_SID` fallback.
* That installing the callbacks caused it. Bisected by installing SOD alone — the
  same figures appeared, because the sampling point was still wrong.

This is the episode the harness's settle detection exists to prevent.

## 19. "The display stream is a digit scan ring"

**Claimed:** with the framing fixed, the byte stream clocked out through SOD was a
clean repeating 9-byte cycle captured at idle:

```
40 A0 50 28 14 0A 05 02 81  40 A0 50 28 14 0A 05 02 81  ...
```

Read as a ring every step is a right shift by one with a `1` injected at the MSB
at two points, which was interpreted as a digit scan ring for the 74159 digit
select.

**Actually:** a capture artefact of the trace point, not the machine's behaviour.
The 74159 digit select is driven by the **8279**, from its own internal scan
counter clocked by the 555 on the display board — it never appears on the serial
link at all. What crosses the link is 8279 command and data bytes, and the
command/data distinction is the SOD level left standing at the `LOAD` strobe
(§5.2), not anything in the byte pattern.

The three framing faults fixed on the way to that capture were real and remain
fixed:

1. **Callbacks were never installed.** `MACHINE_INIT` runs before the CPU cores
   are initialised, so `i8085_set_SOD_callback` / `i8085_set_SID_callback` calls
   made there were discarded. Installed on first use instead. (The core-level fix
   in `driver-notes.md` §3(3) — not wiping callbacks on reset — is the other half
   of this.)
2. **Chain aliasing.** `OUT` is the shared strobe for both serial chains and the
   port number cannot discriminate. This was worked around by gating the display
   shift on "a `SIM` happened since the last clock". **That workaround is itself
   now superseded**: the 74164 is reloaded from scratch every frame and only ever
   committed when `LOAD` pulses, so the switch scan's clocks disturb it
   harmlessly. `locals.simSinceClock` survives in the driver as dead state.
3. **Bit alignment.** Nine `OUT`/`RAL`/`SIM` per frame; the first `OUT` has no
   `SIM` before it and clocks in the stale trailing level from the previous frame.
   Dropping the leading bit lands the byte correctly.

## 20. "The switch-number convention does not line up"

**Claimed:** that injected switches were landing in the wrong `swMatrix` row
because a `sw2m` was being supplied from somewhere unknown, or because the
debugger's switch dump was not a straight dump of `swMatrix[]`.

**Actually:** the driver had no switch conversion of its own and was inheriting
`core.c`'s default. Installing `MDRV_SWITCH_CONV(rfranco_sw2m, rfranco_m2sw)`
made the numbering the driver's own choice and the confusion disappeared. Switches
are now `11`–`48` on the `column*10 + row + 1` scheme.

The related note remains true and is worth keeping: the driver's `SWITCH_UPDATE`
writes row 2 from the input port every frame, so cabinet switches injected by the
debugger are overwritten — drive those through the input port instead. (Under
VPinMAME the opposite applies, because `SWITCH_UPDATE` does not run at all there;
see `driver-notes.md` §7.1.)

## 21. The "remaining work" list

Superseded wholesale. Display decode, lamp mapping, switch mapping and solenoids
were all listed as not started; all four are implemented and documented in
Part II. The `0x4000` placeholder is gone (§16). Sound ROM coverage at ~42%
remains open and is carried forward as §15.4.


---

## Update: harness and sound verification

Superseding the harness description earlier in this document.

`tools/rfranco_check.py` now covers **both** ROM sets: `--rom supstarf`,
`--rom supstarfa` or `--rom all`. It carries a per-set address table (TRAP entry
0x1800 / 0x19DA, after-display-call 0x189C / 0x18A0, TRAP exit 0x196B / 0x19D6,
attract loop 0x03B5 / 0x03D9, credits C08D / C08E, stack base C7FF / C7CF), and
cross-checks two of those entries against the ROM at run time - the `LXI SP`
operand at 0x0001 and the TRAP vector at 0x0025 - so the table cannot rot
silently.

Eight checks, and **both sets pass all eight**: handler balance, fault handler
not latched, display not sitting on the fault fill, stack near its reset value,
both CPUs executing, a coin accepted, and the credit display showing the count.

Settling now waits on the credit display before enabling the PC hook, which cut
the wait from ~80s to **~25s**.

The earlier note about the harness instrumenting 0x0286 without a CPU filter is
obsolete: the debugger's breakpoint, instrumentation and tracepoint endpoints
now take an optional `&cpu=N`, and the harness asserts on machine state (C01C,
credits, lit segments) rather than on PC counts wherever it can.

### Set 2 has a stuck-contact watchdog that set 1 does not

Set 2 was reported as "the display breaks after scoring". It is not a display
fault and not a driver bug. The 0xE fill is `core_bcd2seg7[0x0E]`, written into
all sixteen 8279 RAM bytes by the ROM's own falta handler (set 2: 0x028E latches
C01C, 0x031F calls 0x2A1A; set 1 has the same mechanism at 0x0286 / 0x0317 /
0x2A11).

The trigger is a watchdog at **0x3ABF**, called from 0x0713, which set 1 does not
have. It watches switches 11, 12, 18 and 47 with counters at C7E0..C7E7 - inside
the C7CF..C7FF block that set 1 uses as stack. A contact left closed increments
its counter until it passes 0x7F, then jumps to the falta handler. Measured:
holding switch 11 closed on set 2, C7E2 climbed 0B → 21 → 38 → 4E → 64 → 7A and
faulted at 27 seconds from cold NVRAM (~7s once the counters hold their 0x60
idle value). Set 1 with the same contact held 16s: nothing.

A pulsed scoring switch was never made to fault: 38 games and 2221 randomised
pulses per set ended with `falta = 00` and zero hits on the falta entry. The
display module at 0x2400-0x25FF is common code and both ROMs emit byte-identical
attract streams, so the 8279 model is not implicated either way.

**Rule for anyone debugging this: read C01C before suspecting the 8279.**

### Sound is verified by listening, not only by register writes

Register capture (`tools/rfranco_sound.py`) decodes the AY programming for each
command; every note lands within 25 cents of equal temperament, the worst being
the ROM's own integer-period rounding.

| command | decoded |
|---|---|
| 0xE1 coin | C4 262.687 / E4 330.000 / G4 394.030 - a C major triad - bass stepping to C5 |
| 0xB1 ball start | D4 294.972 Hz, twice |
| 0xE0 bumper | B5 → C2 falling chromatic cascade, 33 of 35 steps descending |

Confirmed against real audio: rebuilt with `SOUND_WAVEOUT=1`, run on Xvfb with
`-dsp-plugin waveout`, four WAVs recorded. Ball start autocorrelates to
**295.4 Hz against 294.972 predicted (+2.5 cents)** with 3rd and 5th harmonics
dominant - a square wave, as expected. The bumper's pitch track walks the
predicted cascade. Note headless builds are silent (`video.c:787` returns before
`sound_stream_update`), so audio needs the waveout build and a real or virtual
display.

The tone table at 0x308-0x387 is 64 little-endian AY periods, chromatic C2-B6
plus four an octave up. A4 = period 120 = **exactly 440.000 Hz** at 844800 Hz.

### One ROM bug, faithfully emulated

Sound 0xB1's second and third sub-tunes (0x598, 0x535) are unreachable: the tune
terminator at 0x28B does `ANL PSW,#F8`, zeroing SP and discarding the
`CALL 0x585` return. Only the first sub-tune plays, and the capture confirms it.
Worth checking on hardware before anyone "fixes" it.
