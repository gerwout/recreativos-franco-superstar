# `rfranco.c` — notes for a PinMAME reviewer

Recreativos Franco (Spain), *Super Star*, 1986. New driver plus five fixes to the
shared Intel 8085 CPU core.

Files: `src/wpc/rfranco.c`, `src/wpc/rfranco.h`, `src/wpc/rfrancogames.c`,
`src/cpu/i8085/i8085.c`, `src/cpu/i8085/i8085.h`, plus two lines each in
`src/pinmame.mak` (`rfranco.o` in `DRVLIBS`, `rfrancogames.o` in `PINGAMES`) and
`src/wpc/driver.c` (`DRIVERNV(supstarf)`, `DRIVERNV(supstarfa)`), and the same
three source names in the per-file build lists under `vcproj/` and `cmake/`. The
`vcproj/` half is commit `4e8283e1`: `src/wpc/driver.c` is in every project, so
without it the MSVC builds compiled everything and then failed to link
`driver_supstarf` / `driver_supstarfa`.

Companion documents: `hardware-findings.md` (the full derivation and its audit
trail), `vpx-table-reference.md` (switch/lamp/solenoid tables),
`rom-provenance.md` (ROM sets and the MAME `BAD_DUMP` case).

---

## 1. The hardware in brief

Two processors, four boards, and serial I/O for everything.

| | |
|---|---|
| Main CPU | Intel 8085A, 5.0688 MHz crystal (the core is given 2 534 400 — the 8085 divides by two internally) |
| Program ROM | 27128 at IC19, `0x0000`–`0x3FFF`. IC14, a second socket, is unpopulated on every known board |
| RAM | 5517 2K×8 at IC11, `0xC000`–`0xC7FF`, battery-backed |
| Sound CPU | Intel 8035, clocked from the 8085's CLK OUT (pin 37) = XTAL/2; PinMAME's MCS-48 core is given the machine-cycle rate, XTAL/2/15 |
| Sound ROM | 2532 at IC4, 4 KB, **data bus bit-reversed** — see §4 |
| Sound | 2 × AY-3-8910 clocked from the 8035's T0 (XTAL/6 = 844 800 Hz), LM380 output |
| Inter-CPU | 4 × Intel 8212; two of them form the bidirectional command/ack path at `0x8000` |

### Memory and I/O map

| Range | Contents |
|---|---|
| `0x0000`–`0x3FFF` | program ROM |
| `0x4000` | eight playfield contacts on connector JG (74S138 CS1), active low, read once per scan pass |
| `0x8000` | 8212 latch pair: write = command to the sound CPU, read = reply (and clears RST 5.5) |
| `0xC000`–`0xC7FF` | NVRAM |
| `OUT` to any port | the shared serial shift clock — the whole I/O space is one decode |

MAME's skeleton (`supstarf.cpp`) does not map `0x4000` at all; the ROM reads it
on every scan pass. That is one of the two functional differences from the
skeleton (the other is the sound ROM scramble).

### Serial I/O

There is no parallel I/O port on this machine at all.

* **SOD** drives a 74164 on the display board, which feeds an 8279.
* **SID** reads two cascaded 74165s on the driver board carrying the playfield
  contacts.
* **Any `OUT` instruction** is the shift clock for *both* chains — the port number
  is irrelevant.
* The lamps and coils are not on the 8085 at all: they hang off the AY-3-8910 I/O
  ports on the sound board, and the 8085 ships a 20-byte frame to the 8035 which
  forwards it to the PSG.

### Interrupts

| Vector | Source | Rate |
|---|---|---|
| TRAP | mains zero cross, full-wave rectified from an 11-0-11 V winding on the PSU board | 100 Hz on 50 Hz Spanish mains |
| RST 5.5 | 8212, raised when the sound CPU answers | on demand |
| RST 6.5 | *falta* (tilt) pendulum on JD1 | on demand |
| RST 7.5 | **power fail / emergency stop** — deliberately never driven | never |

RST 7.5 deserves a note because it looks like a refresh tick and is not one. Its
handler at `0x0244` blanks the display, lights the *falta* lamp, sends sound
command `0xCC` and then spins forever at `0x026A`; it never returns. The ROM opens
a one-instruction window for it on every TRAP pass (`SIM #$0B` / `EI` / `NOP` /
`DI` at `0x182F`) and resets its latch with `SIM #$1D` at `0x194C`. Asserting it
kills the machine, so the driver does not.

**TRAP is load-bearing at boot.** With invalid NVRAM the reset path tests `C000`
for the magic byte `0x55` and executes `RST 0` when it fails, which lands back on
the reset vector. Nothing in that loop writes the magic — it is the TRAP handler
that detects it, sends a sound command, seeds `C000` and cold-resets. Without
TRAP running the machine never comes up at all. This matters because it is what
made bug (5) in §3 fatal rather than cosmetic.

### Lamp and coil multiplexing

Four CD4028 BCD-to-decimal decoders on the driver board, each output gating a
BT106 thyristor. A fired thyristor conducts to the end of the mains half-cycle,
so **each decoder output serves two loads** — one on FASE A, one on FASE B —
picked by which half-cycle it was gated in. The sound CPU samples the half-cycle
on T1 and reports it to the 8085 (sound command `0xDD` returns the T1 state), and
the 8085 selects between two copies of the lamp tables accordingly.

The 20-byte frame is ten time slots for PSG port A (`0x0E`: high nibble → IC1
backbox lamps, low nibble → IC2 playfield lamps) followed by ten for port B
(`0x0F`: high nibble → IC7 coils, low nibble → IC3 playfield lamps). Slot *n*
emits decoder code *n*, or 0xF for "none".

The driver therefore accumulates selects into `lampAcc[8]` / `solAcc` and commits
them at each TRAP rather than sampling instantaneously — an ~85 µs select window
means nothing on its own. Each (decoder, phase) pair gets a lamp matrix column of
its own, with bit *n* = decoder code *n*; codes 8 and 9, which only IC2 uses, go
in two spare columns. Coils are additionally accumulated across video frames,
because TRAP runs at 100 Hz against a 60 Hz vblank.

The phase the arriving bytes were selected for is one TRAP behind the current one:
`0x19E6` sends `0xDD`, stores the reply in `C04F`, and immediately ships the buffer
that was prepared on the *previous* pass.

One quirk worth knowing when reading the ROM: before shipping the frame the game
scans the ten coil slots for the first active code and copies it into the **last**
slot, so the 4028 is left selecting that coil for the rest of the half-cycle.
Only one coil is sustained at a time.

### Coils the CPU never sees

The two pop bumpers and the two slingshots (the manual's *expulsores*, board
53/3311's own name for the *rechazador* mechanism) are fired on that board
straight from their own playfield contacts, through an RC one-shot into a BDX53C
at +48 V. The 8085 reads those contacts for scoring and nothing else. The driver
synthesises solenoids 17–20 from the rising edge of the `0x4000` bits so a front
end has something to hang effects on; they are derived from the switch, so they
carry no information a table did not already have. Both slingshot contacts are
wired in parallel onto one bus bit, so solenoids 19 and 20 necessarily fire
together — see §7A.

---

## 2. Why this needed CPU-core work at all

PinMAME's `src/cpu/i8085/i8085.c` is used by `bingo.c`, `micropin.c` and
`regama.c` as well, so it is not dead code. But none of those three exercises the
8085's *serial and interrupt-latch* features, and the core's own comments admitted
as much:

```c
case 0x20:
    if( I.cputype ) { //!! misses fixes from newer MAME
                /* RIM */
        I.AF.b.h = I.IM;
...
case 0x30: //!! misses new port from MAME
```

and, in the reset routine:

```c
memset(&I, 0, sizeof(i8085_Regs)); //AT: this also resets I.cputype so 8085 features were never ever used!
```

Super Star reads its entire switch matrix through `RIM`/SID, uses `SIM` bit 4 to
clear the RST 7.5 latch, and takes a non-maskable TRAP 100 times a second whose
handler returns with interrupts disabled. It is the first driver to touch any of
that.

---

## 3. The five 8085 core fixes

Commits `8317f095` (1, 2, 3) and `2858c42b` (4, 5).

### (1) `RIM` never sampled SID, and reported the wrong pending flags

`RIM` returned `I.IM` raw. `I.IM` happens to hold the three interrupt masks, `IE`
and `SID` in the positions the RIM byte expects — but it holds `IM_TRAP` (0x10)
where the RST 5.5 *pending* flag belongs and `IM_SOD` (0x40) where RST 7.5
pending belongs, so bits 4–6 of the result were meaningless. The pending flags
live in `I.IREQ`.

Worse for this driver, SID was only ever reported if a driver had pushed a value
in beforehand with `i8085_set_SID()`. Super Star clocks the switch data in one
bit at a time (`RIM` / `CMA` / `ANI 80` / `ORA M` / `RRC` / `OUT`), so the value
must be sampled at the instant `RIM` executes; a pushed value is stale by
definition.

Fix: compose the RIM byte properly from `I.IM` and `I.IREQ`, and add a pull-style
`i8085_set_SID_callback(int (*)(void))`. `i8085_set_SID()` still works for drivers
that prefer to push — `regama.c` does, and is unaffected.

### (2) `SIM` ignored bit 4 (reset RST 7.5)

RST 7.5 is edge-triggered and latches. Unlike RST 5.5/6.5 it is *not* cleared by
the line going low — only by `SIM` with bit 4 set, or by the interrupt being
taken. The old core did not implement bit 4 at all, so the latch stuck and the
handler re-entered forever. The game ROM uses it: `SIM #$1D` at `0x194C`
(R7.5 = 1, MSE = 1, M6.5 = 0).

Fix: honour bit 4 — clear `IM_M75` in `I.IREQ`, and also drop the interrupt if it
was scheduled but not yet taken.

### (3) `i8085_reset()` wiped the driver's callbacks

`i8085_reset()` `memset`s the whole register struct. That is correct for CPU state
and wrong for the irq / SOD (and now SID) callbacks, which are board wiring the
driver installs once. They were being silently dropped on every reset.

Fix: save and restore them across the `memset`, alongside the `cputype` restore
that was already there for the same reason.

This one bites hard here because the sound CPU asserts the main CPU's reset line
during its own ~1.94 s power-up delay, so the main CPU is reset *after* the driver
has installed its callbacks.

### (4) `EI` took effect immediately

On real hardware an interrupt is not recognised until the instruction *after* `EI`
has completed. Service routines lean on it — an ISR ending

```
EI / POP PSW / RET
```

needs the `POP` to run before anything else can be taken, or the frame is left
half unwound.

Fix: swallow exactly one instruction's worth of interrupt latency after `EI`, the
way newer MAME does with `m_after_ei`.

### (5) TRAP could only ever fire once

`i8085_set_TRAP()` gated on `I.ISRV`:

```c
I.IREQ |= IM_TRAP;
if( I.ISRV & IM_TRAP ) return;   /* already servicing TRAP ? */
```

`I.ISRV` is an "in service" lock that only `EI` clears — but a TRAP handler is
under no obligation to `EI` on the way out. Running with interrupts disabled and
simply `RET`ing is perfectly legal, and this ROM does exactly that at boot. The
lock then stayed set forever, blocking not only further TRAPs but RST 5.5/6.5/7.5
as well.

Fix: gate on the pending flag instead. `Interrupt()` clears it as it takes the
interrupt, so a new edge re-arms TRAP while a second edge arriving before the
first is taken is still ignored. `I.ISRV` is deliberately left alone so it keeps
masking the maskable interrupts for the duration of the handler.

Of the other three 8085 drivers only `micropin.c` touches `IRQ_LINE_NMI`, and it
drives it as a level from a tilt switch rather than pulsing it 100 times a second
from a mains reference, so the stuck lock was never visible there.

**Regression risk.** Fixes (1)–(3) and (5) change behaviour only for code that
reads RIM's pending bits, uses SIM bit 4, resets the CPU after installing
callbacks, or takes more than one TRAP. Fix (4) changes interrupt timing for every
8085/8080 driver by one instruction, which is the correct behaviour and matches
current MAME, but it is the one worth a second look from anyone who owns
`bingo.c`, `micropin.c`, `regama.c` or `taito.c`.

---

## 4. The sound ROM's data bus is bit-reversed

The 2532 at IC4 has its data pins wired to the 8035's AD0–AD7 in reverse order:
EPROM D7 lands on AD0 and D0 on AD7 (CPU board schematic, manual sheet 1 of
ref. 53/3291).

Read straight off the chip the image is not MCS-48 code at all. Reversing each
byte turns it into an ordinary program:

| variant | JMP | CALL | RET | MOV A,# | OUTL | first bytes |
|---|---|---|---|---|---|---|
| as dumped | 119 | 35 | **5** | 10 | 8 | `a8 20 f9 a3 f5 20 14 a6` |
| **bit reversed** | **172** | **88** | **28** | **59** | **48** | `15 04 9f c5 af 04 28 65` |

Five `RET` opcodes in 2 KB of program is not credible. Reversed, the vector
layout is textbook:

```
000: 15        DIS I
001: 04 9F     JMP $09F
003: C5 AF     SEL RB0 / MOV R7,A     <- external interrupt
005: 04 28     JMP $028
007: 65        STOP TCNT              <- timer
```

Six independent dumps across five manufacturer device profiles agree on the chip
contents (see `rom-provenance.md`), so the reversal is in the board wiring, not
in the dump.

This is almost certainly why MAME's driver is marked `MACHINE_NO_SOUND`: it loads
the image unmodified, so its 8035 executes noise.

The driver undoes the reversal once, after ROM load. **See §7 — the current
placement of that call has a latent bug.**

---

## 5. The 8212 READY handshake

Writing `0x8000` sends a command to the sound CPU and raises its interrupt;
reading takes the reply and clears RST 5.5 on the main CPU.

The 8212 also holds the 8085 in wait states through its READY output until the
sound CPU has taken the byte, and **that flow control is not optional**. The lamp
and coil frame at `0x19E6` sends command `0xDD` and then pushes 20 bytes back to
back with no handshake of its own:

```
19E6: MVI A,$DD / CALL $196C
19EB: STA (C04F)
19EE: MVI D,$13
19F0: LXI HL,$C034
19F3: MOV A,(HL) / STA ($8000) / INX HL / DCR D / JP $19F3
19FC: MVI A,$FF / STA ($8000)
```

The 8035 does not take an interrupt for those bytes — it **polls** the INT pin
with `JNI` at `0x00FB` and consumes one byte per pass, forwarding each to the PSG.
It is far too slow to keep up with the 8085. Without READY the 8085 simply
overwrites the latch and most of the transfer is lost, which is what produced the
original symptom: a stack that leaked 0x1C bytes on every TRAP because the display
call at `0x1899` never returned.

MAME's skeleton has the same wiring noted but commented out:

```cpp
//m_soundlatch[1]->int_wr_callback().append_inputline(m_maincpu, I8085_READY_LINE);
```

PinMAME's 8085 core has no READY input, so the driver stalls the main CPU on a
trigger (`cpu_spinuntil_trigger`) and lets the sound CPU release it
(`cpu_trigger`) when it reads the latch, with `cpu_triggertime` as a deadlock
guard for the case where the sound CPU has masked its interrupt and will never
read.

Before/after over the same 5 s window:

| addr | meaning | before | after |
|---|---|---|---|
| `0x1800` | TRAP entry | 853 | 176 |
| `0x189C` | after the display call | 0 | 176 |
| `0x198E` | echo check | 0 | 176 |
| `0x196B` | TRAP handler RET | 34 | 176 |
| `0x0286` | error path | 67 | 0 |

**The guard timeout is derived from the sound ROM.** It is 4000 µs
(`RFRANCO_SOUND_GUARD_US`; 1000 µs before the derivation existed, and a literal
100 µs until commit `a655aa50`). The bound it must exceed is the worst case the
8035 can legitimately take between the 8085's write (INT asserted) and its
`MOVX` read of the latch at `0x02B`: the interrupt is recognised at the first
instruction boundary with no interrupt in progress and `EN I` in effect, plus a
fixed 12 machine cycles from recognition to the read. The longest blocked
stretch the ROM can produce — computed by cycle-accurate emulation of the sound
ROM over every command's complete run — is one timer-ISR pass of the
three-voice player at a chord boundary where all three voice countdowns expire
in the same tick and voice A also consumes the envelope re-arm event (tune
`0x7CA`, commands `0x01`/`0xB0`): 468 cycles at 5.92 µs = **2770 µs** (computed).
Runners-up `0x11` 2243 µs and `0x00` 2089 µs; every non-tune path is ≤ 953 µs.
Guard = 2770 µs × 1.44 ≈ 4000 µs. It must also stay below the span of any 32
consecutive latch writes, because the guard timers cannot be cancelled and the
trigger numbers rotate through `RFRANCO_SOUND_TRIGGERS` = 32: the longest burst
is 23 writes (`0xDD` + 20 frame bytes + `0xAA` + `0x99` per TRAP pass, ~2 ms),
so 32 consecutive writes always straddle a full 10 ms TRAP period — 4000 µs
passes with ≥ 2× headroom, and stays far below the 50 ms that was measured to
distort game timing when the sound CPU never answers.

Measured against the running driver (exec-trace on both CPUs, 238 425
handshakes over attract, a played game and repeated faults): every latency
matches the computed path within 3 cycles, max observed 971 µs on the 953 µs
tune-end path, and the `0x00` tune's boundary pass shows exactly the computed
blocked-cycle count. The old 1000 µs sat inside the chord windows but was never
caught misbehaving, for two measured reasons: the TRAP-burst commands are
phase-locked away from the long passes (a tick pending during the burst's
in-ISR chain is postponed past it, and the `MOV T,#EB` reload inside the ISR
drags the tick phase with it every frame), and a prematurely released 8085 on
the `0x196C` path still `HLT`s for the RST 5.5 reply before writing again.
Neither mechanism covers the main-loop bare `STA (8000)` sends, which were
measured landing inside blocked passes (up to 840 µs), so the computed bound is
the one that holds. If the guard ever fires before the 8035 has collected a
byte, the main CPU is released early and reads a stale reply — which shows up
as the echo check at `0x198E` failing. See `hardware-findings.md` §11.

---

## 6. Measurement caveats

Two of these cost this project real time. Anyone re-measuring the driver should
read them first.

### The instrumentation hook counts both processors by default

`remote_debug_breakpoint_hook()` reads `activecpu_get_reg(REG_PC)` and matches it
against every instrumented address whose `cpu` field is `-1`, which is the default
when `/api/debugger/instrument?cmd=add` is called without a `cpu=` parameter. On
this board the 8035's address space is `0x000`–`0xFFF` and overlaps the bottom of
the 8085's, so **any instrumented address below `0x1000` counts hits from both
processors**.

This is not hypothetical. `0x0102` in the sound ROM is `ORL P2,#0FFH` and fires
once per TRAP, which made the 8085's main loop look like it was running when it
was in fact wedged.

It cost the harness a false failure, and that one is now closed.
`tools/rfranco_check.py` used to instrument `0x0286` (the "error path") with no
`cpu` filter, and `0x0286` in the sound ROM is `MOV A,R5` inside a live
voice-setup routine, so its "error path never taken" check reported ~3 hits per
8 s against a main CPU that had never been there. The debugger endpoints now
take `&cpu=N`, every request the tools make passes `&cpu=0`
(`tools/rfranco_check.py:125` and `:211`), and the harness no longer instruments
`0x0286` at all — it asserts on machine state instead. The four points it does
instrument (`0x1800`, `0x2437`, `0x189C`, `0x196B` on set 1) are all above
`0x1000` and were unambiguous either way.

### Do not sample before the machine has settled

The 8035 spends ~1.94 s in a timer delay at power-on and holds the *rest of the
machine in reset* while it does (P2.4 is the system `/RESET` net, reaching both
AYs, the 8212s and the main board). The game's own startup runs well past that.
Readings taken during that window look alarming and mean nothing — an entire
phantom regression was chased on the strength of one.

`tools/rfranco_check.py` detects the settle programmatically rather than sleeping,
and then deliberately takes a *fresh* window, because the window that detects the
settle straddles the transition and still carries startup counts. Typical settle
is **~25 s** of wall clock; it was 75–80 s until the harness learned to wait on
the credit display before enabling the PC hook — see the Update at the end of
this document.

---

## 7. Open items and known gaps

Ordered by how much they would matter to a reviewer. Several entries that were
here before are now closed; they are listed at the end with what closed them.

### 7.1 Solenoid 2 is what the ROM drives, not necessarily what the coil is

The ROM gates 4028 output 1 when it awards a replay. That is a measurement, not
a reading: award a special on a running machine and the coil select taken off
PSG1 port B is output 1, on both ROM sets. Nothing anywhere gates output 0.

Whether output 1 is physically the knocker is the open part. The driver
schematic (manual page 17, `manual-images/page-23.jpg`) prints the 4028 output
pin number against every row - bottom to top 3, 14, 2, 15, 1, 6, 7, 4, 9, 5,
which is exactly Q0…Q9 - and by those numbers **Q0 goes to JL6 TACA and Q1 to
JL10 N.C.** The JL connector table on the previous sheet
(`manual-images/page-22.jpg`, manual page 16) agrees about JL10: it is the one
pin on that connector with no wire colour against it.

Read literally, the machine never knocks and the one coil output the program
drives is not connected. The driver assumes instead that the sheet's bottom two
rows have their JL destinations transposed. Codes 2-9 all match the ROM exactly,
the same manual's *fe de erratas* already corrects two transpositions of exactly
this kind (connector JA reversed, IC5 pins 10 and 11 swapped), and a machine
whose replay never bangs is not credible. **Only a physical board settles it.**

The reading itself is no longer in doubt. The same sheet draws the three lamp
decoders in the identical style, and their true mappings are ROM-verified: read
by the printed pin numbers, every verifiable row - all ten of IC2's, including
codes 8 and 9, the five wired rows of IC3 and the wired rows of IC1 - lands
exactly on the measured lamp map. Twenty-five rows calibrate the convention; the
two IC7 rows are the sheet's only outliers against the ROM. Note also that the
*fe de erratas* revisits this very page (it moves the falta lamp onto IC1 pin 3)
without touching IC7 - and that its other entries are board-revision notes, not
drawing fixes, so a late TACA move from Q0 to Q1 that never made the errata is
exactly the kind of change it records elsewhere. What to ask someone with a
machine is written up in `questions-for-a-real-machine.md` Q1/Q2.

### 7.2 The READY guard timeout — closed, now derived

See §5. It is now 4000 µs, derived: worst-case INT-to-latch-read latency
2770 µs (computed from the sound ROM, the `0x01`/`0xB0` chord-boundary
timer-ISR pass) × 1.44 margin, bounded above by the 32-trigger rotation
(longest write burst is 23, so trigger reuse always spans a full TRAP period)
and by the 50 ms figure that measurably distorts game timing. Verified live
against 238 425 traced handshakes; agreement within 3 cycles. The symptom to
watch for if it is ever changed is still the echo check at `0x198E` failing.

### 7.3 `MDRV_INTERLEAVE` retested since READY was modelled: 500 comes down to 250

It was raised for the sound handshake before the trigger-based READY model
existed. Retested empirically (2026-08-11) on a scratch copy of the tree with
`RFRANCO_SOUND_GUARD_US 4000` in place: one rebuild per rung, and for every
rung `rfranco_check.py --rom all`, plus `rfranco_game.py --rom all` where the
check passed, plus `rfranco_sound.py --rom supstarf` at the surviving rungs,
all from a cold NVRAM in a private `-nvram_directory` (see the caveats below).

| Interleave | check sf | check fa | game sf | game fa | sound sf |
|---|---|---|---|---|---|
| 500 | pass | pass | pass | pass | pass |
| 250 | pass x2 | pass x2 | pass x2 | pass x2 | pass |
| 150 | pass | pass | pass | pass | pass |
| 100 | pass | pass | **fail** | pass | - |
| 50 | pass | **fail x2** | - | - | - |
| 20, 10, 5, 1 | **boot wedge** | **boot wedge** | - | - | - |

The failure modes, lowest first:

* **1-20: both sets wedge at power-on.** Blank display for ever, the 8085
  circling the boot delay at `0x19F4-0x19FC` (set 1; the `0x1A7D` region on
  set 2) and the 8035 stuck in its `0x0D8-0x0EF` init. The READY trigger only
  covers the per-byte stall in `rfranco_sound_w`; the power-on handshake is
  still interleave-carried, so the constant cannot go anywhere near 1.
* **50: supstarfa never settles.** TRAP entries outnumber completed display
  passes ~4x (935 entries vs 248 display calls in one window) - handler passes
  start but do not finish. Genuine, reproduced twice.
* **100: supstarf's end-of-ball bonus assert fails.** The avance ladder is
  consumed in-play instead of surviving to the drain, so `rfranco_game` sees
  per-turn bonus `[0, 0, 0]`. The total final score is identical to the 500
  run (292330), every other check passes, `C01C` stays clear - so this is the
  wall-clock harness stimuli landing at different emulated phases (headless
  the machine runs ~0.35x real time at 500 but ~0.87x at 100, measured against
  the 100 Hz TRAP), not a corrupted transfer. Scaling the pulse widths to
  match emulated closure width did not change it, so it is phase, not width.
  By the harness bar it is a fail all the same.

**Conclusion: `MDRV_INTERLEAVE(250)`**, applied to the driver. Lowest
fully-passing rung (150) x 1.7, 5x the highest `rfranco_check` failure (50).
Passes check, game and sound repeatedly on both sets. What it buys, measured
headless on supstarf in steady attract (30 s `/proc` utime+stime samples, two
runs each, spread < 0.001):

| Interleave | emulated speed (vs wall) | host CPU fraction | CPU per emulated second |
|---|---|---|---|
| 500 | 0.35x | 0.091 | 0.26 |
| 250 | 0.57x | 0.098 | 0.17 |
| 150 | 0.73x | 0.102 | 0.14 |
| 100 | 0.87x | 0.107 | 0.12 |

At 500 the headless machine cannot even hold real time - the per-slice
overhead is paid in scheduler sleeps, not CPU - so 250 also cuts the wall
time of the harness suite by ~30-40% (`check --rom all` 91 s -> 73 s,
`game --rom all` 169 s -> 131 s). The slice quantum at 250 is ~67 us, still
far inside the 4000 us sound guard's 1230 us margin (§5). If it is ever
lowered again the symptoms appear in this order: `rfranco_game`'s bonus
attribution (~100), supstarfa's settle (~50), a power-on wedge (~20).

Two caveats earned the hard way during this retest, worth keeping:

* **NVRAM is global.** Every run of any harness shares
  `~/.xpinmame/nvram/<set>.nv`, and a machine killed while wedged mid-boot
  saves garbage there, which then wedges every later boot of the same set in
  every tree - it looks exactly like a driver regression ("the credit display
  never came up" / "attract loop never started") and it survives rebuilds.
  Concurrent harness runs also collide on the fixed HTTP ports (8931-8933).
  Experiments on a copy of the tree should pass `-nvram_directory` somewhere
  private and move the harness ports.
* The check/game harnesses drive switches in wall-clock milliseconds while
  the headless machine's emulated speed varies with interleave (and with host
  load), so gameplay-attribution assertions are speed-sensitive. The bonus
  check at 100 above is the example: same total score, different attribution.

### 7.4 Smaller things

* `MDRV_DIPS(16)` declares sixteen DIP bits for two used ones. Harmless -
  `core_updateSw` reads `(coreDips+31)/16` ports either way - but untidy.
* `core_bcd2seg7[]` only initialises entries 0-9 outside `MAME_DEBUG` builds, so
  the driver's use of index `0x0F` to blank a digit works by falling into the
  zero-initialised tail. Correct in both build types (index 15 is zero either
  way), but in a `MAME_DEBUG` build nibbles `0x0A`-`0x0E` render as letters
  where a 7447 would not.
* `supstarfa`'s zone 13 (`C7F4`) is now settled behaviourally — it is the
  extra-ball cap per *ball in play*, not per game: `0x0CBC`'s refusal (`RC` at
  `0x0CC4`) happens before `C006` is even loaded, `C006`'s sign only selects
  which side's BOLA EXTRA lamp arms, and a drain without the earned lamp zeroes
  `C7F7`. Isolated with PC hit counters and forced NVRAM on the running
  machine — `hardware-findings.md` §15.9 has the trials.
* `supstarfa`'s zone 19 (`C7FD`) is the end-of-ball bonus collect: at 1 the
  drain pays out the avance ladder through the countdown at `0x0F9E`
  (measured: +10 000 and +30 000 from the matching rungs, the last ball
  included), at 0 the call at `0x11E6` is skipped and the value is lost.
  The ladder opens the next ball on 10 000 either way — that reset belongs
  to the serve path, not the zone. See `hardware-findings.md` §15.10.

### 7.5 Closed since the last revision of this document

| Was | Now |
|---|---|
| `SWITCH_UPDATE` is dead code under VPinMAME, so the trough model, the coin one-shot and tilt never run | All three moved outside `if (inports)`. The trough is driven from events, the coin one-shot is run down from either path, and *falta* is read off switch 21 unconditionally |
| The sound-ROM descramble is guarded by a process-lifetime static, so a second game start in one process runs a scrambled image | Moved into `DRIVER_INIT`, which runs once per game start after the ROMs load |
| The lamp-map comment documents a numbering the driver does not install | `MDRV_LAMP_CONV(rfranco_lamp2m, rfranco_m2lamp)` added; lamp numbers are now `col*10 + row + 1`, matching both the comment and the switch numbering |
| `locals.simSinceClock` written and never read | Removed |
| `PORT_READ_START` closed with `MEMORY_END` | Closed with `PORT_END` |
| The file header still says "work in progress … display, lamps and solenoids not yet mapped" | Rewritten; it now says what has been played through and on which sets |
| The harness instruments `0x0286` with no CPU filter, so its "error path" result is contaminated by the sound ROM | The debugger endpoints take `&cpu=N` and the harness asserts on machine state (`C01C`, credits, lit segments) instead |

---

## 7A. Two corrections this revision makes to earlier conclusions

Both were stated as settled in earlier notes and were wrong.

### The switch matrix was being overwritten every frame

`SWITCH_UPDATE(RFRANCO)` rebuilt the whole cabinet row from the keyboard input
port on every vblank:

```c
if (inp & 0x0080) v |= 0x80;      /* pulsador partidas */
if (locals.coinPulse) v |= locals.coinBits;
mask |= 0xb0;                     /* coins and start button */
...
if (mask) CORE_SETKEYSW(v, mask, 2);
```

`CORE_SETKEYSW` writes every bit in the mask, so switches 25, 26 and 28 were
stamped back to whatever the keyboard said 60 times a second. Anything else that
set them - a front end, or the debugger's `/api/input` - survived less than one
frame, and the ROM reads that row through a sound-command round trip rather than
directly, so whether it ever saw the switch was luck. In practice "insert coin,
press start" worked about half the time from outside the keyboard, which is
exactly the kind of flakiness that gets blamed on the emulation.

Fixed by making every write edge-driven: the start bit is only written when the
key level changes, and the coin bits only when the one-shot's own output
changes. Nothing writes a bit it is not currently changing, so an external
writer keeps control of everything in between. This is the same rule the trough
contact already followed.

### The two ball "ejectors" are the slingshots, and they share one contact

Pseudo-solenoids 19 and 20 were wired to switches 14 and 16, *rampa especial
izquierda/derecha*, on the reading that "EXPULSOR" on board 53/3311 meant a
kickout hole. This playfield has no holes. The manual's contact drawing (page 3)
puts contacts 24 and 25 - both named *10 PUNTOS* - inside the two triangular
bodies at the bottom corners, and the parts list calls that mechanism the
*rechazador*, the only coil-bearing mechanism in the manual that the driver
board's JL connector does not account for. Contacts 3 and 7 are plain rollover
wires in the outer lanes with the ESPECIAL lamps beside them.

Contacts 24 and 25 are wired in parallel onto AD0 - the ROM's own contact-test
table flags that bit as a paralleled pair - so both slingshots reach the CPU as
switch 11 and it cannot tell them apart. Both pseudo-solenoids now fire from
switch 11, together, because there is no information in the machine that
separates them.

---

## 7B. The operator door switches are now reachable as switches

The two door switches were only settable through `core_getDip`, which is fine
for choosing a mode at power-on and useless for anything else: inside the
AJUSTES menu the ROM re-reads them on every pass and uses them to decide what
the start button does - both up steps the current zone's *value*, either one
down steps to the next *zone*. Walking the menu means moving a switch while the
machine runs, and a DIP setting cannot do that.

The ROM never looks at bits 0-3 of the cabinet byte (every read masks
`0x10`/`0x20`/`0x40`/`0x80`), which is what already lets the driver borrow bit 0
for *falta*. Bits 2 and 3 - switches 23 and 24 - now lift the *ajuste* and
*test* door switches respectively, ANDed into whatever the DIP says, so with
both open nothing changes. `tools/rfranco_zones.py` uses them to walk the whole
menu on either set.

## 7C. The driver had no reset handler, so a soft reset did almost nothing

The driver declared `MDRV_CORE_INIT_RESET_STOP(RFRANCO, NULL, NULL)` and put all
of its power-on state — the `memset` of `locals`, `ballInTrough = 1`,
`troughEdge = 1`, the SID/SOD callback installs — in the **init** hook. That is
the wrong hook. `core.c` calls them from two different places:

```c
2435:  if (!coreData) {                             // first time only
2609:    if (coreData->init) coreData->init();      //   <- init lives in here
         ...
       }
2629:  if (coreData->reset) coreData->reset();      // every reset, including F3
```

So `MACHINE_INIT(RFRANCO)` ran once per game start and never again. A soft reset
— `F3`, or *Reset Game* in the Tab menu — reset both CPUs and left every byte of
`locals` exactly as the running machine had left it: the 8279 display RAM, the
8212 latch state, `scpuP2`, the shift-chain position, the coin and start edge
detectors, and most damagingly the two-state trough model.

The visible symptom was that resetting into an operator mode did nothing at all.
With the trough model stale, `caída de bolas` was not re-seeded closed, and §4.4
of `hardware-findings.md` already records what that does to this ROM: `0x030F`
and `0x0331` ping-pong for ever and the foreground program never completes its
startup. The boot dispatch at `0x00BB` — the only place in the whole program
where the operator door switches are read — was therefore never reached, so no
combination of door switches or DIP setting could take a *running* machine into a
menu. It looked like a ROM property ("the mode is chosen at power-on and a reset
does not redo it") and it was not; it was this.

Fixed by making it a `MACHINE_RESET(RFRANCO)` and declaring
`MDRV_CORE_INIT_RESET_STOP(NULL, RFRANCO, NULL)`, which is what the comparable
drivers do — `idsa.c` (also Spanish, also 8085-era), `mac.c`, `jeutel.c`. Nothing
in the handler is once-only, so there is no init hook left to keep. `coreData->reset()`
also runs on the first pass, so cold boot behaviour is unchanged.

Measured, on `supstarf` with the DIP at its default (*juego*):

| | Before | After |
|---|---|---|
| Cold boot, switches 23/24 open | normal play | normal play |
| Close switches 23/24, press `F3` | still normal play after 300 s | **AJUSTES zone 1 within 10 s** |
| Trough bit (row 2, `0x40`) after `F3` | left as the last game left it | re-seeded closed |

Both ROM sets still pass `tools/rfranco_check.py` and `tools/rfranco_game.py`.

## 7D. The trough model is gated on `g_fHandleMechanics`

*CAIDA DE BOLAS* is an ordinary trough contact — manual contact 28, connector
JO3, debounced on the driver board with the AR3 pull-ups like every other input.
The machine senses a ball in the outhole exactly the way any pinball does, and
the driver does not model the sensing.

What the driver models is the ball **movement** that works the contact, because
standalone PinMAME has no ball: SALIDA BOLAS firing stands in for "the ball
left", and the DRAIN key for "the ball came back". That is mechanical simulation,
and it used to run unconditionally — including under VPinMAME, where a table has
its own ball physics driving the same switch. Two writers, one bit.

Now gated on `g_fHandleMechanics`, which is the convention core.c already applies
to the generic mech handler (`core.c:1783`) and `mech.c` to its own updates
(`mech.c:93`). VPinMAME exposes it to the table as `Controller.HandleMechanics`
(default `0xFF`), libpinmame defaults it to `0`, and the standalone build to
`0xff` — so keyboard play is unchanged and a table can take the trough over
completely by setting it to `0`.

Measured on `supstarf` with the flag forced to `0`:

| | Result |
|---|---|
| Trough at power-on | left **open** — the driver no longer forces a ball into it |
| Game started with an empty trough | credit taken, game starts, and **SALIDA BOLAS never fires** — no ball served, no fault (`C01C = 0x00`) across 45 s |
| Front end closes switch 27, then plays | entirely normal — kicker, scoring, drain |

The middle row is the machine's own ball-missing behaviour. There is no "ball
missing" message because there is nowhere to display one — the machine has only
7-segment score displays — so waiting is the whole of the indication.

With the flag at its default, standalone behaviour is byte-for-byte what it was:
both sets still pass `tools/rfranco_check.py` and `tools/rfranco_game.py`.

## 8. What is verified, and how

| Claim | Evidence |
|---|---|
| Column-1 switch order (11–18) | CPU-board JG connector table gives the bus bit per contact; the ROM's own switch-test table at `0x34A2` lists the same order independently |
| Serial chain order (31–48) | manual's IC5/IC6 wiring tables + the errata; 15 of 16 positions match the ROM's switch-test table (the 16th is documented in `vpx-table-reference.md` §1.3) |
| Cabinet inputs (25–28) | CPU-board JC table (`PA4`…`PA7`) and the driver-board JC table agree |
| Lamp decoder/phase assignment | manual's IC1/IC2/IC3 schematic tables, cross-checked against the ROM: the four score-threshold blocks flash IC1 FASE B codes 1/2 and FASE A codes 1/2 for players 1–4, which pins both the code order and which phase is which |
| Coil decoder codes | every write to the coil bit-field is an immediate `MVI A,<bit>`; there are exactly eight in set 1 and their contexts (coin paths, bank resets, replay award) identify each one |
| Coil codes 0 and 5 unused | exhaustive: those two bits are never written. Code 5 is the `FLIPPER` supply relay, so the ROM genuinely never energises it |
| The *falta* lamp is on FASE B | every write that sets or preserves IC1 code 0 targets the FASE B table (`C21C`); the FASE A table (`C219`) is repeatedly masked with `ANI 0x1F`, which clears code 0 unconditionally. The errata does not say which phase; the ROM does |
| RST 7.5 is a terminal input | the handler at `0x0244` blanks the display, sends sound command `0xCC` and spins forever at `0x026A`. It never returns, so it cannot be a refresh tick |
| Display digit map | 8279 RAM layout from the display-board schematic (74159 + two 7447s, 30 HDSP-3400s); 4 × 7 + 2 = exactly 30 |
| TRAP at 100 Hz | PSU board 53/3309 takes an 11-0-11 V centre-tapped winding into D3/D4 — full-wave, so 100 Hz on 50 Hz mains. This is also the rate the two-phase lamp multiplexing needs |
| 8035 clock | PinMAME's MCS-48 core has no internal divider, so the machine-cycle rate is what it wants. The sound ROM's tone table corroborates the resulting PSG clock: at 844.8 kHz the entries give A3 = 220.000, A4 = 440.000, A5 = 880.000, A6 = 1760.000 Hz exactly |

| A complete game plays on both sets | `tools/rfranco_game.py --rom all`: coin → credit → start button lamp → start → SALIDA BOLAS → JUGADOR 1 and BOLA 1 lamps → eight playfield contacts each scoring → both drop-target banks lighting their ESPECIAL lamps → collecting one awards a credit and gates the knocker → ball 1/2/3 each ending with its bonus and each being re-served → FIN DE JUEGO → the final score held into attract, with `C01C` still 0 |
| Solenoid 2 fires on a replay award | Observed rather than inferred: the coil select taken off PSG1 port B reads 4028 output 1 at the same moment the credit appears, on both sets. Which coil is on that output is §7.1 |
| The two *expulsores* are the slingshots | Manual page 3's contact drawing places contacts 24 and 25 inside the two bottom-corner triangles; the parts list names that mechanism *rechazador*; it is the only coil mechanism the driver board's JL connector does not account for, and there are two of them. The ROM's own contact test independently says 24+25 are paralleled onto AD0 |
| `supstarfa` has ten extra operator zones, not sixteen | Walked on the machine: the BCD zone counter steps 9 → 10 and stops at 19, so six of the jump table's 25 entries are unreachable. Each new zone's NVRAM byte and displayed range were read off the machine while walking the menu, and all ten effects were then established by changing the value and measuring the difference — zones 13 and 19 last, isolated with PC hit counters and forced NVRAM after plain replay trials could not separate them; see `hardware-findings.md` §15.9 and §15.10 |

Not verified against real hardware: nothing here has been checked on a physical
machine. Everything is derived from the factory manual, the two ROM images and the
running emulation.


---

## Update: harness and sound verification

Superseding the harness description earlier in this document.

There are now four tools, all under `tools/`:

| Tool | What it does |
|---|---|
| `rfranco_check.py` | Boots headless, waits for steady state, asserts eight health invariants. Run it after every change |
| `rfranco_game.py` | Plays a complete game on either set and asserts on lamps, coils and digits at every step |
| `rfranco_soak.py` | Many games with randomised switch traffic, watching for the fault handler latching, the display sticking, the stack walking or a CPU stopping |
| `rfranco_zones.py` | Walks the AJUSTES menu and prints every zone with its display and its NVRAM |


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
command; every note in the three decoded commands lands within 25 cents of equal
temperament, the worst being the ROM's own integer-period rounding. That is
**not** true of the whole 64-entry table: index 63 is +47.7 cents (see
`sound-rom-map.md`).

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

Sound `0xB1`'s handler at `0x6D8` calls three tune launchers in turn - `0x585`,
`0x598`, `0x535`. Only the first ever plays. The tune terminator at `0x28B`
(`MOV A,PSW / ANL A,#F8 / MOV PSW,A`, not a single `ANL PSW` opcode - there is no
such instruction in MCS-48) zeroes the PSW's stack-pointer field, so the return
address the `CALL` at `0x6D8` pushed is discarded and `0x6DA` onwards is never
reached.

Settled rather than inferred, by static tracing and by cycle-accurate emulation:
command `0xB1` runs 48 186 machine cycles against the 48 184 that sub-tune 1
alone takes in isolation, and the executed-PC set contains `0x6D8` but never
`0x6DA`. Since the discard is the ROM's own instruction sequence, a real 8035
does the same - this is a ROM bug, not an emulation artefact, and "fixing" it
would make the driver wrong.

Two details in the earlier wording were off. The discarded call is **at** `0x6D8`
and **targets** `0x585`; there is no `CALL` instruction at `0x585`. And `0x535`
is **not** dead - it is reachable through commands `0x31` and `0xF0`. Only
`0x598` is unreachable. Full derivation in `sound-rom-map.md` §6.
