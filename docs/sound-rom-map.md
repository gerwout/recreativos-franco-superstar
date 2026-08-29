# Recreativos Franco "Super Star" — 2532 sound ROM (IC4), complete byte map

Image: `supstarf1.zip::2532.ic4`, 4096 bytes, **bit-reversed** on the board.
All addresses below are in the de-reversed image
(`bytes(int('{:08b}'.format(b)[::-1],2) for b in raw)`), which is what the 8035
actually executes.

```
raw sha1   (2532.ic4)      : see rom-provenance.md
reversed image             : ic4_rev.bin (in this directory)
```

## 0. Method, and what is measured vs. inferred

Three independent passes were used, and every claim below is tagged with which
one supports it.

1. **A hand-written MCS-48 disassembler** (`mcs48.py`) with a full 8035 opcode
   table, correct 3-bit page fields on `JMP`/`CALL`, correct page-of-`PC+2`
   behaviour for the conditional jumps, and `MOVP`/`MOVP3`/`JMPP` page rules.
2. **A recursive-descent static tracer** (`trace2.py`) from the three hardware
   vectors, with the three `JMPP` tables and the four *manufactured returns*
   resolved by hand (each justified in §5). This is an **over-approximation** of
   reachability: it follows every branch regardless of feasibility.
3. **A cycle-approximate 8035 emulator** (`emu.py`) — internal RAM, both register
   banks, the real stack layout, the timer with its 32-cycle prescaler, both
   interrupts, and a `MOVX` decode that follows the documented P2 chip selects
   (P2.7 low = 8212 latch, P2.6 low = PSG1, P2.5 low = PSG2). The ROM is booted
   from reset (through the real ~1.94 s power-on delay) and then **all 256
   command values are injected**, logging every executed PC, every `MOVP`/`MOVP3`
   data read, and every AY register write. This is a **lower bound** on
   reachability.

The two bounds meet almost exactly: static tracing finds 708 instruction starts,
the 256-command emulation sweep executes 692 of them, and every one of the 16
differences is explained in §5 (two are the cold-boot path, three need a T1/INT
input state the sweep did not produce, and eleven are provably dead).

**Byte-count check** (`map.py`, over all 4096 addresses, no address unclassified):

| class | bytes |
|---|---|
| reachable code | 1071 |
| provably dead code | 60 |
| tables (jump tables, tone table, opcode map) | 188 |
| tune / sequence data | 679 |
| tune padding (terminator operand bytes) | 3 |
| unused table slack | 1 |
| page filler | 2094 |
| **total** | **4096** |

The previous Ghidra pass reported 43.4 % / 19.5 % disassembled; the gap was
entirely the three `JMPP` tables, the four manufactured returns, and 2094 bytes
of deliberate filler that is not code at all.

---

## 1. Complete byte map

`code` = statically reachable and (except where noted) executed in the emulation
sweep. `deadcode` = decodes as instructions but cannot be reached — reason given.

| range | class | n | contents |
|---|---|---|---|
| `000`–`002` | code | 3 | RESET vector: `DIS I / JMP $09F` |
| `003`–`006` | code | 4 | external-interrupt vector: `SEL RB0 / MOV R7,A / JMP $028` |
| `007`–`027` | code | 33 | timer ISR: reload `T=#EB`, then the F0-selected voice/sweep tick |
| `028`–`053` | code | 44 | command dispatcher: `MOVX A,@R1 / INC A`, cumulative XOR chain |
| `054`–`061` | code | 14 | "no chain match": builds a fake stack frame → `RETR` into `$062` |
| `062`–`066` | code | 5 | low-nibble re-dispatch: `MOV A,@R1 / ANL A,#0F / ADD A,#67 / JMPP @A` |
| `067`–`076` | **table** | 16 | JMPP table for `$067`. Index = `((cmd+1)&0x0F)+0x67`; slot 0 is the `JMPP` opcode byte itself (`B3`) |
| `077` | unused | 1 | one byte past the end of that table (value `9B`) |
| `078`–`07D` | code | 6 | cmd `AA`: pulse the display strobe on P1, load `A = cmd` |
| `07E`–`082` | code | 5 | shared "reply through the 8212 latch" tail (`ORL P2,#FF / ANL P2,#7F / MOVX @R1,A`) |
| `083`–`088` | code | 6 | ISR exit: restore P2 from RAM `29`, `MOV A,R7`, `RETR` |
| `089`–`08A` | code | 2 | `JMP $1D0` (cmd `88`) |
| `08B`–`08C` | code | 2 | `JMP $617` (cmd `69`) |
| `08D`–`08E` | code | 2 | `JMP $61B` (cmd `96`) |
| `08F`–`090` | code | 2 | `JMP $1E1` (cmd `77`) |
| `091`–`092` | code | 2 | `JMP $403` (low nibble `B`) |
| `093`–`094` | code | 2 | `JMP $60F` (cmd `99`) |
| `095`–`098` | code | 4 | cmd `EE`: `MOV R1,#0F / JMP $5E5` |
| `099`–`09A` | code | 2 | `JMP $1E6` (low nibble `0` or `1` → sound effect) |
| `09B`–`09C` | code | 2 | `JMP $000` (full CPU reset) |
| `09D`–`09E` | **deadcode** | 2 | `JMP $1DA`; no slot of the `$067` table selects `09D` |
| `09F`–`0CA` | code | 44 | power-on init: P1/P2, PSG2 reg 7 = `38`, assert `/RESET` on P2.4, 40 × timer delay (≈1.94 s), release, `CALL $1DA` |
| `0CB`–`0D4` | code | 10 | idle scan: RAM `3A` ≠ 0 → `$0F2`; RAM `39` ≠ 0 → `$0F0` |
| `0D5`–`0EF` | code | 27 | idle loop body: clear the busy flag, PSG1 reg 7 = `F8`, PSW SP←1, `RETR` back into `$0D7` |
| `0F0`–`0F3` | code | 4 | `JMP $1BC` / `JMP $1C5` |
| `0F4`–`0FA` | code | 7 | cmd `DD`: `A = T1` (mains phase), reply through the latch |
| `0FB`–`0FE` | code | 4 | `JNI` spin waiting for the next latched byte |
| `0FF`–`1BB` | code | 189 | the 20-byte lamp/coil frame, fully unrolled: 10 bytes → PSG1 reg `0E`, `FF` to reg `0E`, 10 bytes → PSG1 reg `0F`, `ORL A,#0F` on the last |
| `1BC`–`1C4` | code | 9 | queue a repeat: stack ← `0567` |
| `1C5`–`1CF` | code | 11 | queue the sweep: stack ← `0626`, PSW SP←1, `RETR` |
| `1D0`–`1D9` | code | 10 | cmd `88`: `CALL $1DA`, reply `88`, `JMP $0D5` |
| `1DA`–`1E0` | code | 7 | clear RAM `39` and `3A` (cancel queued sounds) |
| `1E1`–`1E5` | code | 5 | cmd `77`: reply with RAM `3F` (the busy flag) |
| `1E6`–`213` | code | 46 | sound-effect entry: clear F0, RAM `39`←0, RAM `3F`←1, PSG1 reg 6←0, regs 8/9/10←`FF`, RAM `30`/`31`/`32`←`FF`, then `MOV A,R1 / SWAP A / ADD A,#15` |
| `214` | code | 1 | `JMPP @A` |
| `215`–`234` | **table** | 32 | sound-effect jump table. Index = `SWAP(cmd)+0x15`; the 32 slots are exactly the commands `$X0` and `$X1` |
| `235`–`250` | code | 28 | second-level `JMP` instructions (`$235`,`$237`,…) plus cmd `00`'s `EN I / CALL $5C9` |
| `251`–`252` | **deadcode** | 2 | `JMP $0CB` after `CALL $5C9`, which never returns |
| `253`–`266` | code | 20 | more second-level `JMP` instructions |
| `267`–`28A` | code | 36 | **sequencer core**: fetch one event pair, decode it, program the AY |
| `28B`–`293` | code | 9 | tune terminator: `DIS I / DIS TCNTI / MOV A,PSW / ANL A,#F8 / MOV PSW,A / EN I / JMP $0CB` (SP ← 0) |
| `294`–`2A2` | code | 15 | opcode `04` handler (envelope) |
| `2A3`–`2A9` | code | 7 | opcode `07` handler (rest — saves the AY volume register first) |
| `2AA`–`2DB` | code | 50 | the **single-voice sweep player** |
| `2DC`–`2E2` | code | 7 | the **three-voice player** entry (`CPL F0`, prime all three voices) |
| `2E3`–`2EE` | code | 12 | player wait loop and end handling |
| `2EF`–`2F9` | code | 11 | opcode `01` handler (fixed channel-A volume) |
| `2FA`–`2FF` | filler | 6 | page-2 tail pad: `EN I / SEL MB0` pairs, then `JMP $000` |
| `300`–`307` | **table** | 8 | `MOVP3` opcode map: `00 01 02 03 04 05 06 08` |
| `308`–`387` | **table** | 128 | **tone table**: 64 little-endian AY periods (see §4.1) |
| `388`–`39A` | **deadcode** | 19 | `CALL $39B`, then PSG1 reg 11 (envelope fine period) ← `FF` and RAM `30`/`31`/`32` ← `1F`. No `CALL`/`JMP` anywhere in the 4 KB image targets `388`; consequently reg 11 is never written by reachable code and stays 0 |
| `39B`–`3A8` | code | 14 | silence both PSGs (`P2 = 9F` pulls both selects low, regs 8/9/10 ← 0) |
| `3A9`–`3BC` | code | 20 | fetch one **event pair** into `A` (byte 1) and RAM `20` (byte 2); sets F1 |
| `3BD`–`3C0` | code | 4 | page fetcher: `MOV A,R6 / ADD A,#BD / JMPP @A` |
| `3C1`–`3C4` | **table** | 4 | JMPP table for `$3C0`. Index = `R6+0xBD`, `R6 ∈ 4..7` |
| `3C5`–`3CC` | code | 8 | `JMP $410 / $500 / $600 / $700` — the four page fetchers |
| `3CD`–`3D5` | code | 9 | voice base → AY volume register (8/9/10) and RAM slot (`30`/`31`/`32`) |
| `3D6`–`3DD` | code | 8 | step voice A (`R0=0`), duration → R4 |
| `3DE`–`3E5` | code | 8 | step voice B (`R0=2`), duration → R3 |
| `3E6`–`3ED` | code | 8 | step voice C (`R0=4`), duration → R2 |
| `3EE`–`3EF` | code | 2 | `JMP $28B` |
| `3F0`–`3FE` | code | 15 | sweep step: reload R3 from R2, fetch one raw byte → AY reg 0; byte `00` → terminator |
| `3FF`–`402` | code | 4 | `MOV R1,#20 / MOV A,@R1 / RET` (re-read the event's second byte) |
| `403`–`40F` | code | 13 | low-nibble-`B` handler: 3 × (`ANL P1,#40 / ORL P1,#A1 / ORL P1,#AA`), then `JMP $0CB` |
| `410`–`413` | code | 4 | page-4 data fetcher: `MOV A,R7 / MOVP A,@A / EN I / RET` |
| `414`–`41A` | code | 7 | tune launcher → data `41B` |
| `41B`–`469` | **tune** | 79 | tune data (cmd `E0`) |
| `46A`–`470` | code | 7 | tune launcher → data `471` |
| `471`–`4BF` | **tune** | 79 | tune data (cmd `D0`) |
| `4C0`–`4FA` | **tune** | 59 | tune data (cmd `10`, `20`, `D1`) |
| `4FB`–`4FF` | filler | 5 | page-4 tail pad: `EN I / SEL MB0 / EN I`, then `JMP $0CB` |
| `500`–`503` | code | 4 | page-5 data fetcher |
| `504`–`50A` | code | 7 | launcher → data `50B` |
| `50B`–`513` | **tune** | 9 | tune data (cmd `A1`) |
| `514`–`51A` | code | 7 | launcher → data `51B` |
| `51B`–`523` | **tune** | 9 | tune data (cmd `F1`) |
| `524`–`52A` | **deadcode** | 7 | tune launcher; nothing in the image targets `524` |
| `52B`–`533` | **tune (dead)** | 9 | its tune data |
| `534`–`53B` | code | 8 | `00` pad + launcher → data `53C` (jumped to as `$534`) |
| `53C`–`548` | **tune** | 13 | tune data (cmd `31`, `F0`) |
| `549`–`54F` | code | 7 | launcher → data `550` |
| `550`–`562` | **tune** | 19 | tune data (cmd `51`) |
| `563`–`579` | code | 23 | `563`: set repeat count RAM `39` ← 12; `567`: repeat entry, decrement RAM `39`, launcher → data `57A` |
| `57A`–`584` | **tune** | 11 | tune data (cmd `41` = 255 repeats, cmd `61` = 12 repeats) |
| `585`–`58B` | code | 7 | launcher → data `58C` |
| `58C`–`596` | **tune** | 11 | tune data (cmd `B1`, `C1`) |
| `597` | tunepad | 1 | operand byte of the `596` END pair (read, ignored) |
| `598`–`59E` | **deadcode** | 7 | launcher reached only by the dead `CALL` at `6DB` |
| `59F`–`5AF` | **tune (dead)** | 17 | its tune data |
| `5B0` | tunepad | 1 | operand byte of the `5AF` END pair |
| `5B1`–`5B7` | **deadcode** | 7 | tune launcher; nothing in the image targets `5B1` |
| `5B8`–`5C8` | **tune (dead)** | 17 | its tune data |
| `5C9`–`5CF` | code | 7 | launcher → data `5D0` |
| `5D0`–`5E4` | **tune** | 21 | tune data (cmd `00`) |
| `5E5`–`5F9` | code | 21 | cmd `EE`: read PSG2 port B bits 7/6 and port A bit 7, reply |
| `5FA`–`5FF` | filler | 6 | page-5 tail pad, ends `JMP $000` |
| `600`–`603` | code | 4 | page-6 data fetcher |
| `604`–`60E` | code | 11 | idle housekeeping: RAM `3F`←0, `CALL $39B`, RAM `29`←`FF` |
| `60F`–`616` | code | 8 | cmd `99`: read PSG2 port A (cabinet inputs), reply |
| `617`–`61A` | code | 4 | cmd `69`: `ANL P1,#BF` (clear P1.6) |
| `61B`–`61E` | code | 4 | cmd `96`: `ORL P1,#40` (set P1.6) |
| `61F`–`625` | code | 7 | launcher → data `4C0` |
| `626`–`634` | code | 15 | sweep launcher: RAM `3A`←0, `P2=BF`, → data `635`, player `$2AA` |
| `635`–`675` | **tune (sweep)** | 65 | sweep data (cmd `A0`, and queued by cmd `01`/`B0`) |
| `676`–`67C` | code | 7 | sweep launcher → data `67D` |
| `67D`–`6AA` | **tune (sweep)** | 46 | sweep data (cmd `90`) |
| `6AB`–`6B1` | code | 7 | launcher → data `6B2` |
| `6B2`–`6BC` | **tune** | 11 | tune data (cmd `E1`, the coin sound) |
| `6BD`–`6D7` | **tune** | 27 | tune data (cmd `11`) |
| `6D8`–`6D9` | code | 2 | cmd `B1`/`C1`: `CALL $585` |
| `6DA`–`6E2` | **deadcode** | 9 | `STRT T / CALL $598 / STRT T / CALL $535 / STRT T / JMP $0CB` — see §6 |
| `6E3`–`6FF` | filler | 29 | page-6 tail pad, ends `JMP $000` |
| `700`–`703` | code | 4 | page-7 data fetcher |
| `704`–`70A` | **deadcode** | 7 | tune launcher; nothing in the image targets `704` |
| `70B`–`747` | **tune (dead)** | 61 | its tune data |
| `748`–`74E` | code | 7 | launcher → data `74F` |
| `74F`–`757` | **tune** | 9 | tune data (cmd `30`) |
| `758`–`75E` | code | 7 | launcher → data `75F` |
| `75F`–`767` | **tune** | 9 | tune data (cmd `40`) |
| `768`–`76E` | code | 7 | launcher → data `76F` |
| `76F`–`777` | **tune** | 9 | tune data (cmd `50`) |
| `778`–`77E` | code | 7 | launcher → data `77F` |
| `77F`–`787` | **tune** | 9 | tune data (cmd `C0`) |
| `788`–`78E` | code | 7 | launcher → data `78F` |
| `78F`–`797` | **tune** | 9 | tune data (cmd `60`) |
| `798`–`79E` | code | 7 | launcher → data `79F` |
| `79F`–`7A7` | **tune** | 9 | tune data (cmd `70`) |
| `7A8`–`7AE` | code | 7 | launcher → data `7AF` |
| `7AF`–`7B7` | **tune** | 9 | tune data (cmd `21`, `71`, `80`, `81`, `91`) |
| `7B8`–`7C2` | code | 11 | launcher → data `7CA`, and sets RAM `3A`←1 so the `635` sweep follows |
| `7C3`–`7C9` | code | 7 | launcher → data `6BD` |
| `7CA`–`7FE` | **tune** | 53 | tune data (cmd `B0`, and cmd `01`) |
| `7FF` | tunepad | 1 | operand byte of the `7FE` END pair |
| `800`–`FFF` | filler | 2048 | `05 E5` (`EN I / SEL MB0`) repeated, with `04 00` (`JMP $000`) at every `$xFE` |

### 1.1 About the filler

The pads are not erased-EPROM bytes; they are a deliberate slide. `05 E5` decodes
as `EN I / SEL MB0`, so a runaway PC walks harmlessly to the end of the page and
hits `JMP $000` (`JMP $0CB` in page 4). The upper 2 KB is *doubly* unreachable:
there is **no `SEL MB1` (`F5`) anywhere in the image** (verified by byte count),
so no `JMP`/`CALL` can ever set A11; the only way in would be falling off `7FF`,
and the byte at `7FF` is the last tune's terminator operand.

---

## 2. The sound command map

### 2.1 How dispatch works

The 8085 writes one byte to the 8212 latch, which raises INT on the 8035.

```
003:  SEL RB0 / MOV R7,A / JMP $028      ; R7 saves A across the ISR
028:  MOV A,#7F / OUTL P2,A              ; P2.7 low = select the latch
02B:  MOVX A,@R1                         ; read the command (clears INT)
02C:  INC A
02D:  JZ  $083                           ; cmd == FF -> plain ISR return
02F:  MOV R1,#21 / MOV @R1,A             ; RAM[21] = cmd+1
032:  XRL A,#AB / JZ $078                ; ... cumulative XOR chain ...
054:  <no match> build the fake return frame, RETR into $062
```

The chain constants `AB 75 44 13 66 85 FD EF` accumulate to
`AB DE 9A 89 EF 6A 97 78`, so the eight matched commands are one less:
**`AA DD 99 88 EE 69 96 77`** — confirming the existing docs.

Everything that does *not* match runs a **second dispatch on the low nibble**:

```
062:  MOV A,@R1 / ANL A,#0F / ADD A,#67 / JMPP @A     ; A = ((cmd+1)&0x0F)+0x67
```

and everything that reaches `$099` runs a **third dispatch on the whole byte**:

```
1E6:  ... / MOV A,R1 / SWAP A / ADD A,#15 / JMPP @A   ; A = SWAP(cmd)+0x15
```

`SWAP(cmd)+0x15` only lands inside the 32-entry table at `215`–`234` when
`SWAP(cmd) ≤ 0x1F`, i.e. when the command's **low nibble is 0 or 1** — which is
exactly the set of commands the low-nibble dispatch routes to `$099`. The two
levels are consistent by construction; the table has no unreachable slots and no
out-of-range index is possible.

### 2.2 Level 1 — the XOR chain (8 commands)

| cmd | entry | what it does | reply |
|---|---|---|---|
| `AA` | `078` | pulse the display LOAD strobe (`ANL P1,#C0 / ORL P1,#3F`), echo the command back | `AA` |
| `DD` | `0F7` | reply with the T1 mains-phase bit, then `JNI`-wait and forward 20 latched bytes to PSG1 regs `0E`/`0F` (the lamp/coil frame) | `00`/`01` |
| `99` | `60F` | select PSG2, read register `0E` (port A = cabinet inputs), reply | port A |
| `88` | `1D0` | `CALL $1DA` (clear both queued-sound flags), reply `88`, drop into the idle loop — **the "stop all sound" command** | `88` |
| `EE` | `095`→`5E5` | read PSG2 port B bits 7/6 (door switches) and port A bit 7, merge, reply | e.g. `C8` |
| `69` | `617` | `ANL P1,#BF` — clear the latched P1.6 output | none |
| `96` | `61B` | `ORL P1,#40` — set the latched P1.6 output | none |
| `77` | `1E1` | reply with RAM `3F`, the **sound-busy flag** (1 while a tune is playing, 0 when idle) | `00`/`01` |

`77` as a busy poll is new relative to the existing notes: RAM `3F` is set to 1
at `1EE` when any sound effect starts, and cleared at `605`–`607` by the idle
loop.

### 2.3 Level 2 — the low nibble (all other commands)

| low nibble of cmd | slot | target | effect |
|---|---|---|---|
| `0` or `1` | `068`,`069` | `$099` → `JMP $1E6` | sound effect, see §2.4 |
| `2,3,4,5,6,7,8,9,A,D,E` | `06A`..`072`, `075`,`076` | `$09B` → `JMP $000` | **full CPU reset** (≈1.94 s of silence) |
| `B` | `073` | `$091` → `JMP $403` | three write bursts on P1 (`&40 → \|A1 → \|AA`), then idle. This is where the main CPU's `0xBB` "invalid NVRAM" command lands. What the bursts do on the display board is *not established here* — P1 drives the 74S138 and the 7438 strobe gates, so a display blank/refresh is the natural reading, but that is an inference |
| `C` | `074` | `$0A0` | re-run the power-on init from `0A0` (≈1.94 s) |
| `F` | slot 0 = `067` | `$0B3` | re-run the init from `0B3`: assert `/RESET` on P2.4, hold ≈1.94 s, release |

`0F,1F,…,EF` (15 values) take the `F` row; `FF` never gets here because it is
caught by the `JZ` at `02D`.

**So: which commands "fall through to the idle path"?** Strictly, only `FF`.
`FF` is answered at `083` — restore P2 from RAM `29`, `MOV A,R7`, `RETR` — i.e. a
plain interrupt return with no side effect. Every other one of the 255 values
does something: 8 go through the XOR chain, 32 play a sound effect, 16 go to
`$403`, 16 re-init from `0A0`, 15 re-init from `0B3`, and the remaining **168
values hard-reset the CPU**.

### 2.4 Level 3 — the 32 sound-effect commands

Table at `215`–`234`, index `SWAP(cmd)+0x15`. Verified byte-for-byte and
re-verified by running each command in the emulator.

| cmd(s) | slot | 2nd-level | launcher | player | tune data | length |
|---|---|---|---|---|---|---|
| `00` | `215` | `24E` | `5C9` | 3-voice | `5D0`–`5E4` | 3.11 s |
| `01`, `B0` | `225`,`220` | `239` | `7B8` | 3-voice | `7CA`–`7FE`, **then** `635` sweep | 1.20 s |
| `10`, `20` | `216`,`217` | `240` | `61F` | 3-voice | `4C0`–`4FA` | 0.32 s |
| `11` | `226` | `23B` | `7C3` | 3-voice | `6BD`–`6D7` | 2.05 s |
| `21`, `71`, `80`, `81`, `91` | `227`,`22C`,`21D`,`22D`,`22E` | `261` | `7A8` | 3-voice | `7AF`–`7B7` | 0.08 s |
| `30` | `218` | `255` | `748` | 3-voice | `74F`–`757` | 0.08 s |
| `31`, `F0` | `228`,`224` | `246` | `534`→`535` | 3-voice | `53C`–`548` | 0.37 s |
| `40` | `219` | `257` | `758` | 3-voice | `75F`–`767` | 0.08 s |
| `41` | `229` | `248` | `567` | 3-voice | `57A`–`584` × **255** | 31.7 s |
| `50` | `21A` | `259` | `768` | 3-voice | `76F`–`777` | 0.08 s |
| `51` | `22A` | `24A` | `549` | 3-voice | `550`–`562` | 0.43 s |
| `60` | `21B` | `25D` | `788` | 3-voice | `78F`–`797` | 0.08 s |
| `61` | `22B` | `24C` | `563`→`567` | 3-voice | `57A`–`584` × **12** | 1.48 s |
| `70` | `21C` | `25F` | `798` | 3-voice | `79F`–`7A7` | 0.08 s |
| `90` | `21E` | `242` | `676` | sweep | `67D`–`6AA` | 0.31 s |
| `A0` | `21F` | `237` | `626` | sweep | `635`–`675` | 0.27 s |
| `A1` | `22F` | `23D` | `504` | 3-voice | `50B`–`513` | 0.14 s |
| `B1`, `C1` | `230`,`231` | `253` | `6D8`→`585` | 3-voice | `58C`–`596` | 0.29 s |
| `C0` | `221` | `25B` | `778` | 3-voice | `77F`–`787` | 0.08 s |
| `D0` | `222` | `244` | `46A` | 3-voice | `471`–`4BF` | 0.17 s |
| `D1` | `232` | `23F`→`240` | `61F` | 3-voice | `4C0`–`4FA` | 0.32 s |
| `E0` | `223` | `235` | `414` | 3-voice | `41B`–`469` | 0.17 s |
| `E1` | `233` | `265` | `6AB` | 3-voice | `6B2`–`6BC` | 0.42 s |
| `F1` | `234` | `263` | `514` | 3-voice | `51B`–`523` | 0.20 s |

Note `23F`: the slot value is `3F`, and `23F` holds a `00` (`NOP`) which falls
into the `JMP $61F` at `240`. Same trick at `246`: `JMP $534`, where `534` is a
`00` pad before the real launcher at `535`.

**Command `41` is worth flagging.** `248` jumps straight to `567`, the *repeat*
entry, without first setting the repeat count. RAM `39` is 0 at that point
(cleared at `1EA`), and `567` does `MOV A,@R0 / DEC A / MOV @R0,A`, so the count
underflows to `FF` and the two-note figure at `57A` plays **255 times, ≈31.7 s**.
Command `61` reaches the same tune through `563`, which sets the count to 12
first, so it plays 12 times. Whether the 255 repeats are intentional is not
determinable from the ROM; the asymmetry is a fact, the intent is not.

---

## 3. The tune data format

Two players share one byte stream format at the fetch level and diverge at the
opcode level.

### 3.1 The pointer and the fetcher

`R6`/`R7` of **register bank 1** hold a 12-bit ROM pointer: `R6` = page (4–7),
`R7` = offset. There is exactly **one** pointer, shared by all three voices.

```
3BD:  MOV A,R6 / ADD A,#BD / JMPP @A      ; table 3C1..3C4 -> JMP $410/$500/$600/$700
410:  MOV A,R7 / MOVP A,@A / EN I / RET   ; MOVP reads within page 4
```

`MOVP A,@A` is page-relative, which is why the four one-line fetchers exist —
one per data page. Data therefore cannot cross a page boundary, and all tune data
lives in `400`–`7FF`.

`3A9` fetches an **event pair** and sets F1:

```
3A9:  CLR F1 / CPL F1        ; F1 = 1  ("keep going")
      SEL RB1 / DIS I / CALL $3BD / SEL MB0 / INC R7
      MOV R1,#20 / MOV @R1,A          ; RAM[20] = byte 1 (temporarily)
      SEL RB1 / DIS I / CALL $3BD / SEL MB0 / INC R7
      XCH A,@R1 / MOV R1,A / RET      ; A = R1 = byte 1, RAM[20] = byte 2
```

So **every event is exactly two bytes**: `b1` = opcode, `b2` = operand.

### 3.2 The three-voice player (`$2DC`)

Entry:

```
2DC:  CPL F0                 ; F0 = 1 selects the 3-voice tick in the timer ISR
      CALL $3D6              ; voice A: R0=0, first event, duration -> R4
      CALL $3DE              ; voice B: R0=2,                        -> R3
      CALL $3E6              ; voice C: R0=4,                        -> R2
2E3:  EN I / EN TCNTI / JZ $2E9 / JMP $2E3     ; spin until the ISR leaves A == 0
```

The timer ISR reloads `T = #EB` (21 counts × 32 machine cycles = 672 cycles, plus
the ISR itself ≈ 676 cycles ≈ **4.00 ms** at the measured 168 960 machine
cycles/s) and then:

```
018:  DJNZ R4,$01E / CALL $3D6 / JZ $026    ; voice A countdown
01E:  DJNZ R3,$022 / CALL $3DE
022:  DJNZ R2,$026 / CALL $3E6
026:  STRT T / RETR
```

Each voice has its own countdown (`R4`,`R3`,`R2` = A, B, C) but they all pull
from the **same stream pointer**, in the order their countdowns expire. The
stream is therefore *demand-interleaved*, not per-voice — which is why decoding
by hand needs the timing, and why the tables in §4 were produced by running it.

`3D6`/`3DE`/`3E6` loop on F1: control opcodes leave F1 = 1 and are re-fetched
immediately; note and rest opcodes clear F1 and return a duration.

**Opcode decode** (`267`): `v = ROM[0x300 + b1]`.
Because `ROM[300..307] = 00 01 02 03 04 05 06 08` and the tone table starts at
`308`, the same `MOVP3` serves both as the opcode map (for `b1 < 8`) and as the
tone lookup (for `b1 ≥ 8`).

| `b1` | `v` | meaning |
|---|---|---|
| `00` | 0 | **END** — `JMP $28B`. `b2` is still fetched and discarded |
| `01` | 1 | **VOL A** — `handler 2EF`: PSG1 reg 8 ← `b2 & 0x0F`, and RAM `30` ← same. *Fixed* level, envelope bit cleared. Note this is hard-wired to channel A (`MOV R0,#08`) regardless of which voice consumed the event; in every tune present it is only ever used by voice A |
| `04` | 4 | **ENVELOPE** — `handler 294`: PSG1 reg 12 (envelope coarse period) ← `b2 & 0x0F`; `R5` ← `b2 >> 4` (envelope shape, written to reg 13 on every subsequent note). Reg 11 (fine) is never written and stays 0, so the envelope period is `b2&0x0F` × 256 |
| `07` | 8 | **REST** — `handler 2A3`: read back this voice's PSG1 volume register, save it to RAM `30`/`31`/`32`, write 0, duration = `b2` |
| `02,03,05,06` | 2,3,5,6 | not decoded as opcodes — they would fall through into the note path and read a bogus period from `302`–`307`. **No tune in the ROM uses them** |
| `08,0A,0C,…,86` (even, ≥ 8) | period byte | **NOTE**, tone-table index `(b1 - 8) / 2`, duration = `b2` |

The NOTE path:

```
277:  MOV A,R1 / MOVP3 A,@A / MOVX @R0,A     ; period low  -> AY reg R0
27A:  INC R1 / MOV A,R1 / MOVP3 A,@A / INC R0 / MOVX @R0,A   ; period high -> reg R0+1
27F:  DEC R0 / CALL $3CD                     ; R0 -> 8/9/10, R1 -> RAM 30/31/32
282:  MOV A,@R1 / MOVX @R0,A                 ; restore this voice's volume
284:  MOV R0,#0D / MOV A,R5 / MOVX @R0,A     ; AY reg 13 = envelope shape
288:  CLR F1 / JMP $3FF                      ; return b2 as the duration
```

Writing reg 13 on **every** note re-triggers the AY envelope generator, which is
how these tunes get their per-note decay.

**Duration** is in timer ticks of ≈4.00 ms, range 1–255 (`b2 = 0` would wrap the
`DJNZ` to 256).

**Steady state at tune start** (set by `1E6` before any launcher runs): PSG1
reg 6 (noise) = 0, reg 7 = `F8` (tone on for A/B/C, noise off, both ports out),
regs 8/9/10 = `FF` (level 15 **plus the envelope-mode bit**), RAM `30`/`31`/`32`
= `FF`. So by default all three channels follow the envelope; opcode `01`
switches channel A to a fixed level.

### 3.3 The sweep player (`$2AA`)

Reached only by `JMP $2AA` from `633` and `67B`. It leaves F0 = 0, which selects
the other half of the timer ISR, and it silences channels B and C.

```
2AA:  MOV R5,#00                     ; envelope shape 0
      MOV R0,#3E / CLR A / MOV @R0,A ; RAM 3E = 0 (written, never read anywhere)
      AY reg 10 = 0, reg 9 = 0       ; mute B and C
      AY reg 1 = 0                   ; channel A coarse period = 0
2B9:  STRT T
2BA:  CALL $3A9                      ; fetch a pair
2BC:  XRL A,#01 / JZ $2D8            ; b1 == 1
2C0:  XRL A,#03 / JZ $2D0            ; b1 == 2
2C4:  XRL A,#07                      ; *** dead: A is overwritten on the next line
2C6:  CALL $3FF / JZ $2A0            ; A = b2 ; b2 == 0 -> RET
2CA:  MOV R4,A / CALL $3F0 / STRT T / JMP $2E3
```

Note this player compares `b1` **directly**; it does not use the `MOVP3` opcode
map. Its opcodes are therefore a different set:

| `b1` | meaning |
|---|---|
| `01` | channel-A volume ← `b2 & 0x0F` (shares handler `2EF` with the other player) |
| `02` | tick divider: `R2 = R3 = b2` — one raw byte is consumed every `b2` timer ticks |
| anything else (`03` in practice) | play the next `b2` bytes as raw channel-A **fine period** values |
| — | a pair whose `b2` is `00` exits via `RET` (see below) |

The run itself is `3F0`:

```
3F0:  DIS TCNTI / MOV A,R2 / MOV R3,A      ; reload the divider
      SEL RB1 / DIS I / CALL $3BD / SEL MB0 / INC R7
3F9:  JZ $3EE                              ; a raw byte of 00 -> JMP $28B, hard end
3FB:  MOV R0,#00 / MOVX @R0,A / RET        ; AY reg 0 = the byte
```

and the F0 = 0 half of the ISR:

```
00D:  DJNZ R3,$026                          ; divider
00F:  DJNZ R4,$014                          ; bytes remaining
011:  CLR A / JMP $026                      ; run finished -> wake the main loop
014:  CALL $3F0 / JMP $026                  ; next byte
```

Because coarse period is pinned to 0, a sweep byte `p` produces
`844800 / (16 × p)` Hz, i.e. 3.3 kHz at `p = 16` down to 207 Hz at `p = 255`.

Both real sweeps end with a raw `00` byte, so the `b2 == 0` exit at `2A0` is
never taken by any data in this ROM — which is fortunate, because `2A0` ends in
`RET` while `2AA` was entered by `JMP`; the return address would be garbage.

### 3.4 Termination, and the manufactured-return idiom

```
28B:  DIS I / DIS TCNTI / MOV A,PSW / ANL A,#F8 / MOV PSW,A / EN I / JMP $0CB
```

`ANL A,#F8` zeroes the PSW's 3-bit stack pointer, so **every pending return is
discarded**. That is the single most consequential fact in this ROM, and §6
turns on it.

The complement of that idiom is used all over the ROM as a *jump that also drops
the interrupt context*: write a target into RAM `08`/`09`, set `PSW = 1` (SP = 1),
and `RETR`. Four sites do it:

| site | RAM `08`,`09` | lands at | purpose |
|---|---|---|---|
| `054` | `62`,`00` | `062` | unmatched command → low-nibble dispatch |
| `0EA` | `D7`,`00` | `0D7` | the idle loop's own back-edge |
| `1BC` | `67`,`05` | `567` | replay the `57A` tune |
| `1C5` | `26`,`06` | `626` | play the queued `635` sweep |

The high byte doubles as the restored PSW nibble, so every one of these also
clears F0, CY, AC and selects RB0 — which is exactly why the repeat path at `567`
works: `2DC` does `CPL F0`, and the previous tune left F0 = 1, so without the
`RETR` clearing it the second pass would run the wrong ISR half.

### 3.5 Worked example — decoding a tune by hand

Command `E1`, data at `6B2`: `04 02 | 38 34 | 40 6A | 46 6A | 50 34 | 00 04`

| pair | voice | decode |
|---|---|---|
| `04 02` | A (first) | ENVELOPE: shape 0, coarse period 2 → 2×256/844800 = 0.61 s decay |
| `38 34` | A | NOTE index `(0x38-8)/2 = 24` = C4, period 201, 262.687 Hz, 52 ticks = 208 ms |
| `40 6A` | B | NOTE index 28 = E4, 330.000 Hz, 106 ticks = 424 ms |
| `46 6A` | C | NOTE index 31 = G4, 394.030 Hz, 106 ticks |
| `50 34` | A (its 52 ticks expired first) | NOTE index 36 = C5, 522.772 Hz, 52 ticks |
| `00 04` | A | END |

A C-major triad with the lower voice stepping C4 → C5 — which is the coin sound
the existing docs describe.

---

## 4. Tune catalogue

### 4.1 The tone table (`308`–`387`)

64 little-endian 16-bit AY periods. Event byte `b1` **is** the byte offset into
page 3, so index `n` is addressed as `b1 = 8 + 2n`.

* indices 0–59: chromatic **C2 … B6** (`b1 = 08 … 7E`)
* indices 60–63: `16, 15, 14, 13` = **G#7, A7, A#7, B7** — an octave above indices
  56–59, *not* a continuation of the chromatic run.

At 844 800 Hz, index 33 (`b1 = 4A`) is period 120 = **exactly 440.000 Hz**, and
A3/A5/A6 are exact too. Full listing with cents error in `tonetable.txt`.

One correction to the existing notes: the claim that "every note lands within
25 cents" does not hold across the whole table. Nine entries exceed 15 cents and
index 63 (period 13, 4061.5 Hz vs B7 = 3951.1) is **+47.7 cents**. It is used —
it is the first note of command `D0`'s cascade. The three commands the docs
actually measured (`E1`, `B1`, `E0`) do stay within 25 cents.

### 4.2 The tunes

Full event-by-event decodes with cycle timestamps, voice assignment, tone index,
period and frequency are in **`tunes.txt`**. Summary:

| data | played by | voices | decoded content |
|---|---|---|---|
| `41B`–`469` | `E0` | env + C | 36-note falling cascade, tone indices 47,46,45,44 / 31…24 / 35…32 / 19…12 / 23…20 / 7…0. 33 of the 35 steps descend; the two ascents (24→35 and 12→23) are in the data, not an artefact. Matches the documented bumper sound |
| `471`–`4BF` | `D0` | env + C | the same shape one register higher: 63,62,61,60 / 55…48 / 59…56 / 43…36 / 47…44 / 31…24. B7 down to C4 |
| `4C0`–`4FA` | `10`, `20`, `D1` | A only, fixed volume | D5 (index 38) repeated 12 times in four groups of three, volumes 15,13,11 / 9,11,9 / 7,7,7 / 3,7,3, each group followed by a 9-tick rest — a decaying rattle |
| `50B`–`513` | `A1` | A + 2 rests | single F3 (index 17), 35 ticks, envelope period 2 |
| `51B`–`523` | `F1` | A,B,C | one chord: G4 (31) + A#5 (46) + E4 (28), 50 ticks, envelope period 8 |
| `52B`–`533` | **none — dead** | A + 2 rests | single C4 (index 24), 35 ticks, envelope period 2 |
| `53C`–`548` | `31`, `F0` | env + C | D4 (26), F#4 (30), A5 (45), 30 ticks each |
| `550`–`562` | `51` | env + C | A5 (45), D5 (38), F#5 (42), 30 ticks each with 5-tick rests between |
| `57A`–`584` | `41` (×255), `61` (×12) | A | A6 (57) then C6 (48), 15 ticks each |
| `58C`–`596` | `B1`, `C1` | A + 2 rests | **D4 (index 26, 294.972 Hz) twice**, 35 ticks each — the documented ball-start sound |
| `59F`–`5AF` | **none — dead** | A,B,C | E4, E4, then the chord B5 (47) + E5 (40) + G#6 (56) |
| `5B8`–`5C8` | **none — dead** | A,B,C | F#4, F#4, then the chord C#5 (37) + F#5 (42) + A#6 (58) |
| `5D0`–`5E4` | `00` | A + 2 rests | A#5 (46) three times, 255 ticks (≈1.02 s) each, envelope shape 8 (the repeating saw) with period 1 — a slow pulsing tone, 3.11 s total |
| `635`–`675` | `A0`; queued after `01`/`B0` | **sweep** | vol 15, then six runs: divider 3 × `80 7A 76`; divider 2 × `70 6C 66 62 5C`; divider 1 × `52 4E 3E 34 2A 20 16 0C 02 01`; divider 3 × `01 01 01 80 7A 76`; divider 2 × `70 6C 66 62 5C`; divider 1 × `52 4E 3E 34 2A 20 16 0C 02 00`. Period 128 → 1 twice, i.e. two rising zaps from 413 Hz up through the top of the audible band (the tail is ultrasonic); the final `00` ends the tune |
| `67D`–`6AA` | `90` | **sweep** | vol 15, divider 2, then a run of 37 bytes `FF A3 68 43 2B 1B 11 13 15 … E9 FF` — period falls 255→17 then climbs back to 255: one full siren up-and-down — then a 1-byte run whose byte is `00`, ending it |
| `6B2`–`6BC` | `E1` | A,B,C | C4 + E4 + G4 triad, voice A then stepping to C5 — the coin sound |
| `6BD`–`6D7` | `11` | A,B,C | D4+G4 held 252 ticks while C plays D5,D5,D5,B4; then D4+A4 while C plays C5,C5,C5,C4. 2.05 s |
| `70B`–`747` | **none — dead** | A only, fixed volume | the `4C0` rattle transposed to F3 (index 17), with 20-tick rests and a longer tail |
| `74F`–`757` | `30` | A | single F3 (17), 20 ticks |
| `75F`–`767` | `40` | A | single C4 (24), 20 ticks |
| `76F`–`777` | `50` | A | single F4 (29), 20 ticks |
| `77F`–`787` | `C0` | A | single C5 (36), 20 ticks |
| `78F`–`797` | `60` | A | single F5 (41), 20 ticks |
| `79F`–`7A7` | `70` | A | single C6 (48), 20 ticks |
| `7AF`–`7B7` | `21`,`71`,`80`,`81`,`91` | A | single F6 (53), 20 ticks |
| `7CA`–`7FE` | `B0`, `01` | A,B,C | eight three-note chords, 28 ticks each: (D5,F#4,A4) (E5,G4,B4) (F#5,A4,C#4) (G5,B4,D4) (A6,C#5,E4) — envelope re-armed — (B6,D5,F#4) (C#6,E5,G#4) (D6,F#5,A5). Followed automatically by the `635` sweep, because `7B8` sets RAM `3A` = 1 |

`74F`,`75F`,`76F`,`77F`,`78F`,`79F`,`7AF` are a deliberate seven-step ladder —
F3, C4, F4, C5, F5, C6, F6 — one command per rung (`30`,`40`,`50`,`C0`,`60`,`70`,
and the five aliases of `7AF`). Almost certainly the score/chime ladder.

### 4.3 Tunes unreachable from the dispatcher

| data | launcher | why it cannot be reached |
|---|---|---|
| `52B`–`533` | `524` | no `JMP`/`CALL` in the whole 4 KB image targets `524`, and no jump-table slot holds a value that resolves there |
| `59F`–`5AF` | `598` | reached only by `CALL $598` at `6DB`, which is itself dead (§6) |
| `5B8`–`5C8` | `5B1` | nothing targets `5B1` |
| `70B`–`747` | `704` | nothing targets `704` |

Searching the image for both encodings of every possible reference
(`JMP` = `04\|page<<5`, `CALL` = `14\|page<<5`, plus every jump-table byte value)
returns nothing for `524`, `5B1` and `704`. All four were also never executed in
the 256-command emulation sweep.

---

## 5. Static vs. emulated coverage — the 16 differences

Static tracing reaches 708 instruction starts; the 256-command sweep executed
692. The 16 not executed:

| addresses | why |
|---|---|
| `001`, `09F` | the cold-boot path. Reached — the sweep just starts *after* boot |
| `0F4`, `0F5` | the `JT1` = 1 branch of cmd `DD`. Needs T1 (mains phase) high; the emulator held it low. Reachable on hardware |
| `0FD` | the `JMP $0FB` back-edge of the `JNI` spin. Needs the 8085 to be slower than the 8035 at that moment. Reachable |
| `251`–`252` | `JMP $0CB` placed after `CALL $5C9` (cmd `00`). The tune terminator zeroes SP, so the call never returns. **Dead** |
| `598`,`599`,`59B`,`59D` | the second sub-tune launcher — §6. **Dead** |
| `6DA`,`6DB`,`6DD`,`6DE`,`6E0`,`6E1` | the tail of the `B1` handler — §6. **Dead** |

Plus three regions the static tracer never reached at all and which nothing in
the image references: `09D` (`JMP $1DA`), `388`–`39A` (a volume-reset subroutine
that would set RAM `30`/`31`/`32` and PSG1 reg 9 — an orphan), and the three dead
launchers of §4.3.

---

## 6. Settling the `0xB1` question

**The docs' premise is correct in substance, and slightly imprecise in wording.**

Command `B1` (and `C1`, which shares the slot) resolves through
`SWAP(0xB1)+0x15 = 0x230` → value `53` → `$253` → `JMP $6D8`. The handler is:

```
6D8  B4 85    CALL $585      ; sub-tune 1, data at 58C
6DA  55       STRT T
6DB  B4 98    CALL $598      ; sub-tune 2, data at 59F
6DD  55       STRT T
6DE  B4 35    CALL $535      ; sub-tune 3, data at 53C
6E0  55       STRT T
6E1  04 CB    JMP  $0CB
```

and each `CALL` target is a launcher that ends in `JMP $2DC`:

```
585  05       EN   I
586  BF 8C    MOV  R7,#8C
588  BE 05    MOV  R6,#05
58A  44 DC    JMP  $2DC          ; three-voice player; data begins at 58C
58C  04 04 | 3C 23 | 07 46 | 07 46 | 3C 23 | 00 00
```

### Are `598` and `535` sub-tune entry points?

**Yes.** Both are ordinary tune launchers, byte-identical in form to the other
24 in the ROM:

```
598  05 BF 9F BE 05 44 DC     EN I / MOV R7,#9F / MOV R6,#05 / JMP $2DC   ; data 59F
535  05 BF 3C BE 05 44 DC     EN I / MOV R7,#3C / MOV R6,#05 / JMP $2DC   ; data 53C
```

### Is the discarded call "at 0x585"?

**The call is at `6D8`; `585` is its target.** The docs' phrase "the `CALL 0x585`
return" is right if read as "the return from the call to `0x585`" — that return
address (`6DA`) is what gets thrown away. There is no `CALL` instruction located
at `585`; `585` is `EN I`.

### Why the return is discarded

The chain is:

1. `6D8 CALL $585` pushes `6DA` and PSW-high into RAM `08`/`09` and sets SP = 1.
2. `585` → `JMP $2DC` → the three-voice player. `2DC` is entered by `JMP`, so it
   inherits SP = 1 with `6DA` sitting in slot 0.
3. The tune's first voice to reach a `00` opcode lands in `267`'s
   `MOVP3 A,@A / JZ $28B`.
4. `28B` runs `MOV A,PSW / ANL A,#F8 / MOV PSW,A` — SP becomes 0 — and then
   `JMP $0CB`, the idle loop.

Control never returns to `6DA`, so `6DA`–`6E2` (nine bytes) is dead, and `598` is
dead with it. Emulation confirms it: command `B1` runs 48 186 machine cycles,
against the 48 184 that sub-tune 1 alone takes when launched in isolation, and
the executed-PC set contains `6D8`/`6D9` but not `6DA` or anything at `598`.

### So: genuinely unreachable?

* `598` and its data `59F`–`5AF`: **yes, genuinely unreachable.** `CALL $598` at
  `6DB` is the only reference in the image, and `6DB` is dead.
* `535` and its data `53C`–`548`: **no — the docs' implication is wrong here.**
  `535` is *also* the target of jump-table slot `246` (`JMP $534`, a `00` pad
  falling into `535`), which serves commands `31` and `F0`. It is reachable and
  it does play; only its *third-sub-tune role* under `B1` is lost. Emulation
  confirms: commands `31` and `F0` both read `53C`–`548`.

The same bug pattern appears once more, unremarked in the existing notes:
command `00` at `24E` is `EN I / CALL $5C9 / JMP $0CB`, and `5C9` is another
launcher, so the `JMP $0CB` at `251` is equally dead. There it is harmless —
`28B` jumps to `0CB` anyway.

### Checked against real-hardware audio

The 115 s phone recording of a working machine
(`video/Pinball super star [OFmSN9UxXuo].mkv`) confirms the conclusion on
hardware. Video frames put the game start at t ≈ 2.0–2.25 s (attract scores
933090 and CREDIT 9 still shown at 1.75 s, displays blanked at 2.0 s, score 0
and CREDIT 8 by 2.25 s), and the only sound the machine makes there is
sub-tune 1 and nothing else: two square-wave notes measured at 294.80 and
295.53 Hz (D4 = 294.972 Hz predicted — within 4 cents), odd harmonics only,
measured through the 13th (887.7 / 1474.4 / 2065.4 / 2655.8 / 3246.5 /
3835.0 Hz against an ideal 884.9 / 1474.9 / 2064.8 / 2654.7 / 3244.7 /
3834.6), onsets at t = 2.128 and 2.351 s. Nothing of sub-tune 2 follows: for
a full second after the second note the E4 (330.000 Hz) band never leaves its
−49 dBFS noise floor — ≥ 16 dB below the level the two played notes reached
in their band — and the `59F` chord bands (660.0 / 996.2 / 1650.0 Hz) stay at
the floor too. As a control, the same recording *does* contain tune `53C` —
the would-have-been third sub-tune, reachable on its own through commands
`31`/`F0` — played twice mid-game (t ≈ 53.6 s and 72.1 s) as the full
D4→F#4→A5 arpeggio, identified to the cent by its harmonics (1115.5 Hz =
3 × 371.83, 2639.7 Hz = 3 × 880.00). The third phrase is therefore loud and
identifiable whenever it actually plays; its absence at ball start is real,
not a detection failure.

One calibration falls out of the same measurement. Pitch confirms the
844 800 Hz PSG clock to within a few cents, but the ball-start notes' onset
spacing is 220 ± 10 ms against the 147 ms the ≈ 4.00 ms tick of §3.2
predicts — a factor of ≈ 1.5, and the `53C` arpeggio's note spacing
(≈ 145–190 ms against a predicted 118 ms) is consistent with the same
factor. This rescales tick-derived durations in §4 and changes nothing
else — no pitch, no note sequence, no reachability result.

The cause is NOT settled, and a first hypothesis died on measurement. "The
8035 machine-cycle rate is ⅔ of the assumed 168 960/s" would explain the
video, but the live PinMAME machine — same cycle table as the datasheet,
verified opcode-by-opcode — was then measured directly: instrument counters
on the timer ISR against the 100 Hz TRAP give a **5.000 ms** tick during
command `0x41`'s tune, and an injected `0xB1` plays its two notes
**306 ms** apart (offline model 147 ms, real machine 220 ± 10 ms). Three
implementations of the same ROM, three different tempi. What that pattern
does establish is that the tick is not the bare 672-cycle reload: the
prescaler is cleared by the `STRT T` at the ISR's end (`0x026`), so each
period is 672 cycles *plus the ISR pass that preceded it*, and the tempo
therefore depends on per-pass ISR cycle accounting — which is where the
three diverge. Pitch is unaffected (the PSG clock is independent), and the
`0xB1` single-phrase conclusion is unaffected (confirmed on hardware above).
A close-mic recording of one coin sound and one ball start would give the
real tick to a millisecond and settle which accounting is right; asked for
in `questions-for-a-real-machine.md`.

---

## 7. Corrections and additions to the existing project notes

| existing note | status |
|---|---|
| Reset/INT/timer vectors, `0x028` dispatcher, the eight chain commands | confirmed byte-for-byte |
| `0x0078` handles `0xAA`; `0x00B1`/`0x00DB` program the PSG register 7s; `0x060F` reads the cabinet inputs; `0x0BA`/`0x0C7` drive P2.4 | confirmed |
| `0x00F8` is the only `JT1` | confirmed — one `56` opcode in the whole image |
| Tone table `0x308`–`0x387`, A4 = period 120 = 440.000 Hz | confirmed |
| "chromatic … plus four an octave up" | confirmed; the four are indices 60–63 = G#7 A7 A#7 B7, an octave above 56–59 |
| "every note within 25 cents" | **not true of the whole table** — index 63 is +47.7 cents. True of the three commands measured |
| `0x28B` terminator zeroes SP | confirmed |
| `0x2A5` is the REST handler saving a voice's volume | confirmed; the handler starts at `2A3`, and `2A5` is the `MOVX A,@R0` read-back inside it |
| `0xE1` coin, `0xB1` ball start, `0xE0` bumper decodes | all three reproduced exactly, including "33 of 35 steps descending" |
| `0x598`/`0x535` unreachable, `CALL 0x585` discarded | **half right** — `598` is unreachable, `535` is reachable via commands `31`/`F0`; the discarded call is *at* `6D8`, *to* `585` |
| — | **new:** command `0x77` is a sound-busy poll (returns RAM `3F`) |
| — | **new:** command `0x88` is "stop all sound" (clears both queued-sound flags) |
| — | **new:** 168 of the 256 command values hard-reset the sound CPU |
| — | **new:** command `0x41` plays its tune 255 times (≈31.7 s) because it enters the repeat path with the counter at 0 |
| — | **new:** three further tunes are dead (`52B`, `5B8`, `70B`) plus a dead subroutine at `388` and dead code at `09D` and `251` |
| — | **new:** the whole upper 2 KB is `EN I / SEL MB0` filler with `JMP $000` at each `$xFE`; there is no `SEL MB1` in the image, so it is unreachable |

---

## 8. Files in this directory

| file | what it is |
|---|---|
| `SOUNDMAP.md` | this report |
| `ic4_rev.bin` | the bit-reversed 4 KB image everything below is keyed to |
| `mcs48.py` | MCS-48 opcode table and disassembler |
| `trace2.py` / `trace2_listing.txt` | recursive-descent static trace and the full annotated listing |
| `emu.py` | the 8035 emulator |
| `analyze.py` / `emu_full.json` | the 256-command sweep: per-command coverage, data reads, AY writes |
| `cmdscan.py` | the earlier, simpler sweep (kept because it prints the per-command summary) |
| `tunes.py` / `tunes.txt` / `tunes.json` | per-tune event decode with voice assignment and timing |
| `map.py` / `bytemap.txt` | the 4096-byte classification |
| `cmdmap.txt` | all 256 commands with dispatch path, target, run length, and tunes played |
| `tonetable.txt` | the 64 tone-table entries with frequency and cents error |
| `run.py` | boot helper |
