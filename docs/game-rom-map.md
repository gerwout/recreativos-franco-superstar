# Recreativos Franco "Super Star" — game ROM (IC19), complete byte map

Four firmware revisions, one 27128 each, plain 8085 binaries (no scrambling):

```
rev. 1  supstarf   m31-a-01187.ic19  16384 bytes  sha1 496d3c9664386ae64e94462db2fdd36811a68a87
rev. 2  supstarfc  27128Prg.bin      16384 bytes  sha1 efdf60b53ac105985ca6d4eeb6ed48b893bb7ad8
rev. 3  supstarfb  super.dat         16384 bytes  sha1 d10c6456716ca49cce590996e7271b8cd7026f38
rev. 4  supstarfa  27c128.ic19       16384 bytes  sha1 e2f8dcf95084f755d3a34d77ba2649602687a610
```

**This document maps the first and last of the four**, which it calls set 1 and
set 2 throughout — the names they had when it was written, and still their MAME
names. Read "set 1" as rev. 1 and "set 2" as rev. 4.

Set 1 is mapped completely, byte by byte. Set 2 is mapped as a structured diff
against set 1 — the two are the same program with insertions — plus a full
classification of the set-2-only material. Addresses are set 1 unless marked.

Revs. 2 and 3 were dumped later and sit *between* those two. They are byte-
aligned to set 1's layout and inherit its map unchanged apart from the
insertions listed in `rom-revision-chain.md`, which also carries the evidence
for the ordering and a per-revision changelog. Two of the changes §6.2 and §6.3
below attribute to set 2 in fact entered the line earlier: the TRAP sentinel in
rev. 2 and the bounded sender spin in rev. 3. Set 2 inherited both.

## 0. Method, and what is measured vs. inferred

Three passes, mirroring `sound-rom-map.md`; every claim below is tagged by
which one supports it.

1. **A recursive-descent static tracer** (`trace85.py`, over the shared
   `dis85.py` 8085 disassembler) from the reset vector and all four hardware
   vectors (TRAP `0x0024`, RST5.5 `0x002C`, RST6.5 `0x0034`, RST7.5 `0x003C`).
   `RST 0` is modelled as a jump (this ROM uses it only as a cold reset; the
   first pass that modelled it as a call walked into the vector-area `0xFF`
   fill and decoded 23 phantom `RST 7`s). Three computed jumps exist per set
   and each is resolved by hand with its justification in §2. The trace is an
   **over-approximation**: it follows both sides of every branch.
2. **A dynamic lower bound** from the live emulator's code-coverage API
   (`/api/debugger/coverage`), driving the machine through boot (cold and
   warm), attract with the full display carousel, coined and played games on
   one and two players, both drop banks, a collected special, tilt and
   recovery, game over, and all four boot modes (JUEGO, BORRADO, TEST,
   AJUSTES with all nine zones walked and the contact test exercised). One
   measured caveat governs everything below `0x1000`: **the coverage bitmap is
   not CPU-filtered** (`remote_debug.c:756` marks whatever PC the active CPU
   has), and the 8035's address space overlaps the bottom of the 8085's, so a
   set bit below `0x1000` can be a sound-CPU hit. Handled two ways: positive
   claims below `0x1000` are only made for addresses outside the sound ROM's
   reachable-code ranges (transcribed from `sound-rom-map.md` §1 into
   `soundcode.py`), and 33 disputed region entries were re-measured with
   `cpu=0` instrument points, which are CPU-filtered (§7).
3. **A hand check of every unclassified residue**: each region the trace did
   not reach was either identified as a referenced data table (with the
   referencing instruction cited), proved dead by an exhaustive scan of the
   image for both encodings of every possible reference (immediate operands
   and table bytes — the same test the sound map used), or shown to be
   `0xFF` fill.

**Byte-count check** (`build_map.py`, over all 16384 addresses per set, no
address unclassified, every `code` byte trace-covered, every `fill` byte
verified `0xFF`):

| class | set 1 | set 2 |
|---|---|---|
| reachable code | 11 190 | 12 385 |
| data tables | 130 | 162 |
| provably dead code | 24 | 24 |
| filler (`0xFF`, plus set 2's one `0xD0` tail byte) | 5 040 | 3 813 |
| **total** | **16 384** | **16 384** |

Static instruction starts: 5 120 (set 1), 5 667 (set 2).

The old Ghidra pass reported 60.4 % coverage with `0x1A53`–`0x22FF` (2 221
bytes) undefined. **That range is `0xFF` fill, all of it** — measured, one
distinct byte value — as are all eleven other gaps it left. Nothing in either
image is unaccounted for.

---

## 1. Set 1 — complete byte map

`code` = statically reachable; §7 records which of it the dynamic pass also
executed and why the rest was not exercised. Functional labels are derived
from the disassembly and cross-checked against the measured behaviour in
`hardware-findings.md`; sub-boundaries inside contiguous code are routine
groupings, not gaps.

| range | class | n | contents |
|---|---|---|---|
| `0000`-`000C` | code | 13 | RESET: LXI SP,#C7FF / DI / NVRAM magic test (C000 xor 55) -> JZ 0186 warm boot, else RST 0 (cold spin until TRAP seeds the magic) |
| `000D`-`0023` | filler | 23 | FF fill between the software RST slots (RST1-RST4 unused) |
| `0024`-`0026` | code | 3 | TRAP vector: JMP 1800 |
| `0027`-`002B` | filler | 5 | FF fill |
| `002C`-`002E` | code | 3 | RST5.5 vector: JMP 003F |
| `002F`-`0033` | filler | 5 | FF fill |
| `0034`-`0036` | code | 3 | RST6.5 vector: JMP 0286 |
| `0037`-`003B` | filler | 5 | FF fill |
| `003C`-`004C` | code | 17 | RST7.5 vector (JMP 0244) + RST5.5 handler: verify echo when C033 armed, read 8000, RNZ; else XTHL / LXI H,#1985 / PCHL to abandon the senders spin |
| `004D`-`00B2` | code | 102 | warm-boot continuation: attract lamp init, display init (2405), settings-range validation (CALL 34BA), startup tone (CALL 0271 = sound 00 for 2.55 s then 88), display buffers (28BB), C01C prime/clear |
| `00B3`-`00C6` | code | 20 | boot mode dispatch: sound EE -> door switches, ANI C0; C0 -> 0102 (JUEGO), 40 -> 00C7 (BORRADO), 80 -> 312C (TEST), 00 -> 3255 (AJUSTES) |
| `00C7`-`00F7` | code | 49 | BORRADO mode: zero credits C08D (x2 triples), sound 96, zero player-1 score group C20A, display refresh, then re-poll EE until the door switch moves, JMP 00B3 |
| `00F8`-`0101` | code | 10 | mode fork for the 80/00 cases: JNZ 312C (TEST), else blink-table reset (15B9) and JMP 3255 (AJUSTES) |
| `0102`-`0185` | code | 132 | JUEGO boot: restore lamp state from the C219/C21C/C249 tables into C008-C00C, then dispatch on the C20A mode flag: 10 clears the force tables first, 40 resumes the interrupted game via CALL 115B, 30 re-enters attract at 03B5, anything else takes the game-over entry 0350 |
| `0186`-`01E8` | code | 99 | warm-boot NVRAM validation: majority-check every triple C08A-C372 (CALL 156A per triple, undocumented DSUB 08 at 0193 as the 16-bit loop compare), then six sentinels (C099=55 C0B1=AA C108=55 C15F=AA C207=55 C2D9=AA), credits sanity (C090, C08D), balls C1E3<6; pass -> C001=0, JMP 004D; fail -> fall into 01E9 |
| `01E9`-`0243` | code | 91 | cold init: C001=AA, clear C002-C372 (DSUB at 01F8 as loop compare), write the six sentinels, C001=0, sound 11, poll busy (77) until idle, factory defaults (CALL 3824), display refresh, RST 0 |
| `0244`-`0270` | code | 45 | RST7.5 power-fail handler: blank display (2400), luz falta on (C21C\|=80), drop lamps, C001=0, sound CC, spin forever at 026A |
| `0271`-`0285` | code | 21 | startup-tone helper (called from 009E and 030C): sound 00, wait 255 TRAP ticks (2.55 s), then B=88 -> 1987 stop-all |
| `0286`-`030B` | code | 134 | RST6.5 falta handler: RNZ if C01C already set, else latch FF, B=88 -> 1987 (stop sound), sound 96, drop the start lamp (C23D&F7), coils clear (1500), save masked lamp state to C008-C00C, blink reset (15B9), restore with luz falta ORed in (C21C\|80 at 02FB), fault display fill (CALL 2A19 at 0309) |
| `030C`-`033E` | code | 51 | fault recovery: startup tone (0271), then poll: trough open -> check the picabolas contact (C029 bit 6) and fire the PICA-BOLAS coil (CALL 1004 at 0339) if a ball sits on it; trough closed -> sound 69 when players were in game, C01C=0, RST 0 |
| `033F`-`034F` | filler | 17 | FF fill |
| `0350`-`03B4` | code | 101 | game-over -> attract entry: clear the per-player lamp groups (C20D+11 bytes), C1E3=1, C1B3=1, zero C051-C068 and C02A-C02C, sound 96, FIN DE JUEGO lamp (C228\|=04), C20A=30 |
| `03B5`-`0507` | code | 339 | attract loop: display update (25B9), LFSR tick (2300), credits fetch, attract carousel service (04EB/04F1 -> 2E1A/2E5F), coin arrival check (C027 bits 4/5), start-button check (bit 7) |
| `0508`-`0544` | code | 61 | game start: trough (caida de bolas) gate, credit decrement, player add on repeated presses, ball-serve arm, C20A=10 |
| `0545`-`055E` | code | 26 | coin-pulse validation: latch the coin, wait for the contact to open within 20 TRAP ticks (C005), still closed -> JMP the falta path (wedge) |
| `055F`-`05F3` | code | 149 | 25 pta path: CONTADOR 25 coil (C231=10), credit ladder (4th coin pays 2), coin audit (30EC), sound E1 |
| `05F4`-`0634` | code | 65 | 100 pta path: CONTADOR 100 coil (C231=08), 5 credits (+1 bonus), coin audit (30E5), sound E1 |
| `0635`-`06FF` | filler | 203 | FF fill |
| `0700`-`081B` | code | 284 | ball-start / serve: sound 69, ball lamp select, SALIDA BOLAS arming, switch-scan result dispatch top: C026 (0x4000 byte) bit walk with per-contact CZ handlers, C02D edge memory |
| `081C`-`0AFB` | code | 736 | playfield contact handlers: 10/100 puntos scoring, rampa especial (special collect check), diana bank target bits (C028/C029 -> lamp groups), pasillos, avance ladder stepping (0CBC offer logic called from here) |
| `0AFC`-`0C3C` | code | 321 | bumper handler: sound E0 + 1000 points; drop-target bank state machines, ESPECIAL lamp arming on bank completion |
| `0C3D`-`0C62` | code | 38 | extra-ball / especial collect: lamp 37, C7-area counters (set 2 only), sound F1 at 0C4B, credit or extra-ball award |
| `0C63`-`0DBB` | code | 345 | main in-play loop: per-TRAP service, avance ladder rung compare (0CBC offer, C006 sign picks the side), bola-extra lamp arming, bank reset requests, C007 countdown dispatch |
| `0DBC`-`0E10` | code | 85 | picabolas award: clear C023/C024 scratch, display, sound 90 (siren) at 0DCB/0DDB, C007=15 countdown start |
| `0E11`-`0EFB` | code | 235 | ball-end bookkeeping: bank/lamp resets, re-serve decision, sound B1 at 0E88 (ball re-serve), display refresh |
| `0EFC`-`0F35` | code | 58 | bonus-collect start: C1DA lamp, 100-tick guard (158D #64), sound A0 at 0F0C then busy-poll 77, C096 ladder save, sound B0 at 0F3B |
| `0F36`-`1003` | code | 206 | avance-ladder countdown: one rung per tick paying 10000 through 14C2 (x2/x3 under the C22F doble/triple bits), ladder save/restore slots C094/C097, epilogue restores the live ladder |
| `1004`-`1041` | code | 62 | picabolas coil fire (C237=01) and its one-shot timing |
| `1042`-`115A` | code | 281 | scoring commit and lamp maintenance: 10/100/1000-point adds via 2663/26E0, avance doble/triple lamps, C1DD score-mute flag handling |
| `115B`-`11AE` | code | 84 | mid-game resume (from boot when C20A=40): rebuild player state, ball lamp, re-serve |
| `11AF`-`120F` | code | 97 | drain handler: ball scored check (an unscored ball is re-served without advancing), bonus gate at 11E6, ball advance C1E3, next-player rotation C1B3, per-player lamp swap |
| `1210`-`1264` | code | 85 | game over: loteria draw (C=9 -> CALL 2346), sound 41 (repeats until the next command), player lamps off, FIN DE JUEGO |
| `1265`-`1305` | code | 161 | ball-number advance and turn epilogue: BOLA lamps, C7-audits (set 2), lamp group rotation |
| `1306`-`13F4` | code | 239 | score-threshold blocks, players 1-4: compare score against the two replay thresholds, flash the JUGADOR lamp (IC1 B1/B2/A1/A2), award at most one replay per threshold |
| `13F5`-`1431` | code | 61 | replay award: clear C023/24, display (2A55), score-add (262D), JMP 1754 (credit + knocker) |
| `1432`-`146D` | code | 60 | lamp flash helper: D-selected bit into the C249/C279 force tables with 1779 tick waits |
| `146E`-`14FF` | filler | 146 | FF fill |
| `1500`-`151A` | code | 27 | coil/force-table clear: C231/C261 zeroed, C291 = FF (force-off) |
| `151B`-`1569` | code | 79 | avance doble/triple lamp alternator (C23D bits 10/20, C240 phase) |
| `156A`-`1581` | code | 24 | triple-store majority read: 2-of-3 vote, repairs the odd byte in place; a 3-way disagreement jumps to cold init 01E9 |
| `1582`-`158C` | code | 11 | majority-read D+1 consecutive triples |
| `158D`-`1597` | code | 11 | wait A TRAP ticks (C003, decremented by the TRAP handler) |
| `1598`-`15B8` | code | 33 | coil release helper: 8 ticks then clear C231 x4 triples (15B1 = store-A-to-D-triples loop) |
| `15B9`-`15EB` | code | 51 | blink/force table reset: C219 x7 + C23D x3 steady kept, C249/C26D zeroed, C279/C29D = FF |
| `15EC`-`15F2` | code | 7 | triple store: A -> (HL),(HL+1),(HL+2) |
| `15F3`-`161D` | code | 43 | credits sanity + decrement: BCD borrow C090:C08D; malformed credits jump to the falta handler 0286 |
| `161E`-`1655` | code | 56 | turn-start refresh: display 240D, buffers 28BB, coil clear 1500, right-bank check (C028 bit 7 + C029 low nibble) |
| `1656`-`171F` | code | 202 | bank reset coils: BANCADA IZQ (C231=02) when C028&7C != 7C, BANCADA DER (C237=80), SALIDA BOLAS (C237=40) at 1682 with trough-open wait |
| `1720`-`1726` | code | 7 | block fill: B bytes of C at (HL) (LXI B = count/value) |
| `1727`-`1778` | code | 82 | credit add (BCD, cap 99) + start-button lamp; 1754: replay entry lighting; 175C: TACA knocker coil (C231=40) |
| `1779`-`1785` | code | 13 | wait one TRAP tick (C002 handshake with the TRAP handler) |
| `1786`-`17FF` | filler | 122 | FF fill |
| `1800`-`1843` | code | 68 | TRAP handler entry: RIM save, NVRAM magic recheck -> on invalid send BB, delay, seed C000=55, RST 0; tick C002/C003/C005/C006/C007 counters; RST7.5 one-instruction window (SIM 0B / EI / NOP / DI) |
| `1844`-`189B` | code | 88 | lamp-frame source rebuild: C219 steady x C249 force-on x C279 force-off per blink phase into C2A9-C2D8, then CALL 2437 (display byte service) |
| `189C`-`18C7` | code | 44 | switch scan: 74165 chain via RIM/SID x16 into C028/C029 (OUT 00 clocks), LDA 4000 -> C026, sound 99 -> C027 |
| `18C8`-`194B` | code | 132 | switch edge dispatch: C02A-C02C edge memories, per-bit CZ into the contact handlers, falta debounce, coin one-shot service |
| `194C`-`1984` | code | 57 | handler exit: SIM 1D (reset RST7.5 latch, unmask 6.5), C001 state check, restore masks (SIM at 1962), POP / RET at 196B; 196C: sound-command send (STA 8000, SIM 0E, EI, HALT or 197D EI/NOP spin) |
| `1985`-`1986` | code | 2 | POP H / RET - the RST5.5 escape landing (reached only via the 004C PCHL) |
| `1987`-`199B` | code | 21 | send-with-echo: arm C033, send B via 196C, reply must equal B else JMP 0286 (falta) |
| `199C`-`19C9` | code | 46 | phase select: C04F (T1 reply) picks FASE A/B copies of the four source-table pointers |
| `19CA`-`19E5` | code | 28 | coil sustain scan: first active coil code copied into the last frame slot |
| `19E6`-`1A01` | code | 28 | frame send: sound DD (reply -> C04F), 20 bytes C034-C047 raw to 8000, then FF terminator |
| `1A02`-`1A52` | code | 81 | lamp frame builder: one decoder slot per call (1A02), ten slots per decoder (1A2E), codes 8/9 from the second table byte |
| `1A53`-`22FF` | filler | 2221 | FF fill - 2221 bytes, the largest gap; the old Ghidra pass left it undefined and it is genuinely empty |
| `2300`-`2345` | code | 70 | pseudo-random generator: XOR/rotate LFSR over the four triple-stored bytes C1BC/C1BF/C1C2/C1C5, one step per call |
| `2346`-`2375` | code | 48 | game-over random draw (2346, C=9 from 1210): six LFSR steps, then a tiered compare (03/07/0F) selecting the award - read as the loteria 00-90 lamp draw, an inference from the call site and the lamp group it feeds |
| `2376`-`23FF` | filler | 138 | FF fill |
| `2400`-`2436` | code | 55 | display serial writer: 9 clocks x (OUT FF + RAL + SIM) per frame, trailing SOD level = 8279 A0; entries 2400/2405/240D/2415 (E=DD/20/08, D=C0) and 2432 (caller E, D=40); ends B=AA -> 1987 (LOAD strobe) |
| `2437`-`24A7` | code | 113 | per-TRAP display service: walks the C09C dirty flags and C0B4 shadow, writes one 8279 command/data pair per pass, final E=DD commit |
| `24A8`-`24B3` | **deadcode** | 12 | orphan routine: 16 x (E=FF -> 2432) - a display blanking loop nothing references (no CALL/JMP/table entry anywhere in the image) |
| `24B4`-`24BB` | code | 8 | fill (HL)=0F x C - display RAM blank helper |
| `24BC`-`2503` | code | 72 | score -> display transfer for the current player: clear shadow (2504), sentinel 55, player pointers via 2536, inhibit-nibble handling (B from C1B3), final 2432 commit |
| `2504`-`2514` | code | 17 | clear the 0x15-byte display shadow C09C-C0B0 |
| `2515`-`2535` | code | 33 | compare the player score triple-run (6 digits) against its display copy |
| `2536`-`254C` | code | 23 | player pointer fetch: HL = 254D table [2*(C1B3-1)] |
| `254D`-`2554` | **table** | 8 | 4 LE NVRAM pointers C10E C123 C138 C14D - per-player score storage (7 BCD digits, each digit a triple; 21 bytes apart) |
| `2555`-`255B` | code | 7 | stub: LXI H,#255C / JMP 253A (same fetch for the next table) |
| `255C`-`2563` | **table** | 8 | 4 LE NVRAM pointers C0B7 C0CC C0E1 C0F6 - per-player display copies |
| `2564`-`256A` | code | 7 | stub -> 256B table |
| `256B`-`2572` | **table** | 8 | 4 LE NVRAM pointers C162 C16B C174 C17D |
| `2573`-`2579` | code | 7 | stub -> 257A table |
| `257A`-`2581` | **table** | 8 | 4 LE NVRAM pointers C18F C198 C1A1 C1AA |
| `2582`-`258E` | code | 13 | two stubs: PUSH D variant (2582, F1/C9 tail at 2589) -> 258F table |
| `258F`-`2596` | **table** | 8 | 4 LE NVRAM pointers C1C8 C1CB C1CE C1D1 |
| `2597`-`259D` | code | 7 | stub -> 259E table |
| `259E`-`25A5` | **table** | 8 | 4 LE NVRAM pointers C20D C210 C213 C216 - per-player lamp-bit groups |
| `25A6`-`25AC` | **deadcode** | 7 | orphan stub: PUSH D / LXI H,#C01F / JMP 25AD - nothing references it |
| `25AD`-`25B8` | code | 12 | HL += A (25AD); swap nibbles A (25B4, RLC x4) |
| `25B9`-`262C` | code | 116 | display update dispatcher: per-mode (C078) selection of what the 30 digits show |
| `262D`-`26DF` | code | 179 | score add: BCD digit-position add into the current player triple-run, carry propagation, 100 000 lamp handling |
| `26E0`-`270C` | code | 45 | score commit + chime: mask digit, avance ladder step (28A9), unless C07C or C1DD mute -> sound = 273F table[C] to 8000 (2707) |
| `270D`-`273E` | code | 50 | score-add entry points per digit position (segment C from the contact handlers) |
| `273F`-`2744` | **table** | 6 | chime ladder: sound command per scored digit position = 10 10 30 40 50 60 (10/100 pts both 10; 1000 -> 30, 10 000 -> 40, 100 000 -> 50, 1 000 000 -> 60) |
| `2745`-`284C` | code | 264 | score display propagate: per-digit BCD compare/update into the display copy, 8279 write-inhibit nibble selection |
| `284D`-`284D` | **deadcode** | 1 | orphan RET byte between routines - unreferenced |
| `284E`-`28A8` | code | 91 | player-score display writer (285F): 4 players x 7 digits through 244F/2432, blanking inactive players |
| `28A9`-`28BA` | code | 18 | digit nibble writer: C1B3 parity picks raw or swapped nibble -> 2432 |
| `28BB`-`2996` | code | 220 | score/display buffer rebuild for all players (called at boot and turn start); high-score compare and update (C168 group via 2D00-area helpers) |
| `2997`-`2A10` | code | 122 | credit display writer: C08D -> the two credit digits, C162/C18F group maintenance |
| `2A11`-`2A54` | code | 68 | fault display: 2A11 shows C1B9 via 245C; 2A19 is the falta E-fill - 8279 command 90, inhibit A4/A8, 16 x 0xEE data twice (the fill the harness watches for) |
| `2A55`-`2BF9` | code | 421 | BCD value display (2A55: C023/C024 -> digits with 25B4 nibble swaps) and the bonus/ladder display paths |
| `2BFA`-`2C40` | code | 71 | multi-digit display helper: 9-digit walk with E=09 -> 25AD, used by the score displays (tail 2C36 re-enters at 2C14) |
| `2C41`-`2CFF` | filler | 191 | FF fill |
| `2D00`-`2D3A` | code | 59 | show four triple-stored values (C168/C171/C17A/C183) tagged 1-4 - attract-carousel step 11 (called from 2F58) and the high-score screen |
| `2D3B`-`2D5E` | code | 36 | helpers for it: 2D3B window select, 2D4F tag+value display, 2D59 C078=FF stub |
| `2D5F`-`2D62` | **deadcode** | 4 | orphan: LDAX D / ORI F0 / RET - unreferenced |
| `2D63`-`2DB5` | code | 83 | BCD-to-digit expansion of one triple-stored counter (2D63), group-of-four variant (2D96: C18C+) |
| `2DB6`-`2DEC` | code | 55 | carousel timing: C032 frame counter, C1B6/C1B9 slot rotation |
| `2DED`-`2E19` | code | 45 | attract carousel reset: lamps cleared, C078=02, C01D=10, C032=0E |
| `2E1A`-`2E5E` | code | 69 | game-over carousel init (called from 04EB): saves the lamp state to C07D/C080/C083/C086, C01D=1B, C030=C01E=1, C078=14 |
| `2E5F`-`2EE3` | code | 133 | carousel step: C078 decode (02/14/1B), C032 frame countdown, C01E hold, step C01D 10->1D wrap 10 (2EC0), then jump-table dispatch: entry from 3083 PUSHed, RET into it (2EE3) |
| `2EE4`-`300C` | code | 297 | the 14 carousel step handlers (2F70 2F8D 2F9D 2FA9 2FB9 2FC5 2FD5 2FE1 2FF1 2FFD 2F02 2F58 2EE4 2F10): score replays, high scores (2F58 -> 2D00), lamp sweeps; all rejoin at 2E6D |
| `300D`-`3082` | code | 118 | carousel frame service for C032 phases (reached from 2E95 while the step counter runs) |
| `3083`-`309E` | **table** | 28 | carousel jump table: 14 LE code pointers (see 2EE3) |
| `309F`-`30E4` | code | 70 | audit counter increments: games C300, C324, C30C, C318, C330 (PUSH H variants 309F-30BF), core at 30C0-30E4 |
| `30E5`-`3123` | code | 63 | coin audits: C354 (100 pta) / C360 (25 pta), 4-digit packed BCD with carry (30F0 core) |
| `3124`-`312B` | code | 8 | store A to B triples (lamp-table fill helper) |
| `312C`-`31DD` | code | 178 | TEST mode: C078=10, all-lamps-on/off patterns (3138-3187), then the mode loop 31B3: read cabinet (99); start-press edge toggles C07B and steps the audit zone C01D 1..3 (31D5) |
| `31DE`-`320C` | code | 47 | audit display: pointer = 320D table[C01D-1], 4 groups of 4 triple-stored counters -> C01F..C022, shown via 3213/2D4F |
| `320D`-`3212` | **table** | 6 | 3 LE NVRAM pointers C2DC C30C C33C - the three audit pages (16 counters each) |
| `3213`-`323C` | code | 42 | audit page display pattern helper (C022 nibble walk) |
| `323D`-`3254` | code | 24 | zone-step display helper (323D) and start-button latch (324E: C07B\|=01) |
| `3255`-`337F` | code | 299 | AJUSTES menu common: zone number + value redraw (via 25B9/2D4F), door-switch poll (EE at 33AD-ish / 99), C07B press bookkeeping; 3255 is the dispatcher entry the mode loops re-enter |
| `3380`-`33A4` | code | 37 | zone step: on press with a door switch down, C01D step 1..9 (CPI 0A at 3392), dispatcher: table 3490[2*(C01D-1)] -> PCHL at 33A4 |
| `33A5`-`33E2` | code | 62 | value step: on press with both switches up, C07B=1, re-read EE/99, step the current zone value |
| `33E3`-`348F` | code | 173 | zone value editors: BCD increment within per-zone bounds, triple-store write-back, display |
| `3490`-`34A1` | **table** | 18 | zone jump table: 9 LE code pointers 3593 35AC 36D0 3752 377C 35DE 3634 3695 3795 |
| `34A2`-`34B9` | **table** | 24 | switch-test contact-number table: 24 BCD entries (bit 7 = paralleled pair), the 0x4000 bits then the 16 chain positions; final FF = the floating SER input |
| `34BA`-`3592` | code | 217 | settings validation (boot, 34BA: C1E9 in 1-5, C1EC in 1-3, else cold init) and zone-display helpers (3570: show a triple at (HL)) |
| `3593`-`3823` | code | 657 | the nine zone handlers (table order = zone number): 3593 z1 balls/game, 35AC z2 extra-ball threshold, 36D0 z3 games per 25 pta, 3752 z4 games per 100 pta, 377C z5 number of specials, 35DE z6 / 3634 z7 / 3695 z8 replay scores 1-3, 3795 z9 contact test (live switches against the 34A2 table) |
| `3824`-`3853` | code | 48 | factory defaults writer (from cold init): C1E9 run = 03 02 21 31 00 06 11 15 (eight triple-stored settings) |
| `3854`-`3FFF` | filler | 1964 | FF fill to the end of the 16K |

### 1.1 The dead code, in full

All four orphans were checked by scanning the whole image for their address as
a little-endian word (the encoding any `JMP`/`CALL`/table slot would use):
zero occurrences each, and none is fall-through-reachable (each is preceded by
fill, a table, or an unconditional transfer).

| range | bytes | contents |
|---|---|---|
| `24A8`–`24B3` | 12 | `MVI C,#10 / MVI E,#FF / CALL 2432 / DCR C / JNZ / RET` — clock sixteen `0xFF` bytes out of the display chain. A display-blank helper that nothing calls |
| `25A6`–`25AC` | 7 | `PUSH D / LXI H,#C01F / JMP 25AD` — a seventh pointer-fetch stub, one more than the six tables in use |
| `284D` | 1 | a lone `RET` between two routines |
| `2D5F`–`2D62` | 4 | `LDAX D / ORI F0 / RET` — an orphaned nibble-mask helper |

The same four orphans exist byte-for-byte in set 2 (at the same addresses —
they sit in the unshifted display module), still unreferenced.

---

## 2. Computed jumps and control-flow idioms

Three computed jumps per set, all resolved by hand:

| site | mechanism | targets | justification |
|---|---|---|---|
| `004C` (both sets) | `XTHL / LXI H,#addr / PCHL` | set 1 `1985`, set 2 `1A0B` (`POP H / RET`) | the target is the literal loaded two bytes earlier; the idiom swaps it onto the stack to abandon the sound-send spin one call level up |
| `33A4` (set 2 `33A7`) | `PCHL` on a table word | zone jump table, set 1 `3490` (9 LE words), set 2 `349D` (25 LE words) | index = `C01D − 1`, bounds-checked at `338B`–`3394` (set 1: reject 0 and ≥ `0x0A`; set 2: reject 0 and ≥ `0x1A`, and the BCD step at set 2 `33E6` forces `09 → 10`, making slots 9–14 — all filled with the zone-9 handler `37C2` — unselectable) |
| `2EE3` (both sets) | `PUSH H` of a table word, then `RET` | attract-carousel table `3083` (14 LE words, byte-identical in both sets) | index = `(C01D + 1) & 0x0F` with `C01D` held in `0x10`–`0x1D` by the wrap at `2EC0` (`CPI 1E / JC` … `MVI A,#10`), so the index runs 1…13,0 |

Idioms worth knowing when reading the listing:

* **Triple-store NVRAM.** Every persistent value is kept three times in
  consecutive bytes. `15EC` writes a triple; `156A` reads one with a 2-of-3
  majority vote and **repairs the odd byte in place**; a three-way
  disagreement jumps straight into cold init (`01E9`). The warm-boot pass at
  `0186` majority-checks every triple from `C08A` to `C372` before trusting
  anything.
* **The undocumented `DSUB` (opcode `0x08`)** is executed at `0193` and
  `01F8` (set 2: `019B`, `0200`) as a 16-bit `HL == BC` loop compare
  (`PUSH H / DSUB / POP H / JNZ`). These are the only undocumented opcodes in
  either image (scanned: `08 10 18 28 38 CB D9 DD ED FD` over every traced
  instruction).
* **`RST 0` as cold reset** — at `000C` (reset loop while NVRAM magic is
  bad), `0243` (end of cold init), `0325` (end of fault recovery), and set 2
  equivalents. Control never returns.
* **The TRAP tick counters.** `C002`/`C003`/`C005`/`C006`/`C007` are
  decremented/advanced by the TRAP handler; `1779` (wait one tick) and `158D`
  (wait A ticks) are the foreground's only clocks.

---

## 3. Sound-command census

Every write to `0x8000`, with its command byte and call site. Three send
mechanisms exist: a bare `STA (8000)` with the value in `A`; the plain sender
`196C` (set 2 `19E5`) whose callers load `A` first; and the echo-verified
sender `1987` (set 2 `1A0D`) whose callers load `B` — a reply that does not
echo `B` jumps to the falta handler.

### 3.1 Set 1 — every send, by call site

(26 `STA (8000)` sites plus the two reply reads `0044`/`188E`; rows marked
`(B)` are callers of the echo sender `1987`, listed at their `MVI B` sites.)

| site | cmd | context |
|---|---|---|
| `00D3` | `96` | BORRADO mode entry (credits just cleared) |
| `022E` | `11` | cold init complete — then polls `77` (busy) at `0236` until the 2.05 s tune ends before `RST 0` |
| `0267` | `CC` | RST7.5 power-fail handler — re-runs the sound CPU's init, ≈1.94 s of silence. Dead under the driver: the line is never asserted (correctly — the handler spins forever) |
| `0276` | `00` | **the startup tone** — helper `0271`, called from `009E` (every boot) and `030C` (fault recovery). Sound `00` is the 3.11 s pulsing A#5; the helper waits 255 TRAP ticks (2.55 s) and then |
| `0283` | `88` (B) | …cuts it: stop-all, via the echo sender. So the power-on sound is command `00` truncated at 2.55 s |
| `0292` | `88` (B) | falta handler: stop all sound |
| `0297` | `96` | falta handler |
| `032B` | `69` | fault recovery, players-in-game exit |
| `039B` | `96` | attract entry (game over → attract) |
| `0470` | `B1` | ball served (the ball-start tune) |
| `057A` | `E1` | 25 pta coin accepted |
| `060F` | `E1` | 100 pta coin accepted |
| `0705` | `69` | ball-start path (`0700`) |
| `0AFC` | `E0` | bumper scored (the falling cascade) |
| `0C4B` | `F1` | extra ball collected |
| `0DCB`, `0DDB` | `90` | picabolas countdown — the siren sweep, two entry variants |
| `0E88` | `B1` | ball re-served |
| `0F0C` | `A0` | bonus-collect opening zap — then busy-polls `77` at `0F14` |
| `0F3B` | `B0` | bonus countdown (chords, then the ROM's own queued sweep) |
| `11DA` | `69` | end-of-turn path |
| `121A` | `41` | **game over.** Sound `41` is the two-note figure that repeats 255 times (≈31.7 s) because the sound ROM enters its repeat path with the counter at 0 (`sound-rom-map.md` §2.4). The game relies on it: the melody plays until the next command (a coin, the attract frame traffic) replaces it. The "bug" is load-bearing |
| `167F` | `F0` | drop-bank event in the bank-reset region |
| `1810` | `BB` | TRAP handler, NVRAM magic invalid (first boot) |
| `196C` | (A) | the sender itself. Callers: `EE` (door switches) from `00B8`, `00EB`, `33AF`; `77` (busy poll) from `0236`, `0F14`, `0FE5`, `166E` — note `166E`: the ROM **waits for sound-idle before firing a bank reset coil**; `99` (cabinet inputs) from `18C5` (every TRAP), `31B8` (TEST mode), `3378`/`33C5` (AJUSTES); `DD` (lamp frame open) from `19E8` |
| `1987` | (B) | the echo sender. Callers: `88` from `0063` (warm boot), `0283`, `0292`, `130B` (score-threshold award); `AA` (display LOAD strobe) from `242D` — the only `AA` site, once per display commit |
| `19F4` | data ×20 | the lamp/coil frame bytes `C034`–`C047` — **not commands**; the 8035 is in its `JNI` bulk loop consuming them. If it were not (early READY-guard release), bytes with low nibble 2–9/A/D/E would hard-reset the sound CPU, whose init asserts P2.4 — the system `/RESET` — and reboots the whole machine. This is why the derived guard bound matters (`hardware-findings.md` §11) |
| `19FE` | `FF` | frame terminator — the one value the sound dispatcher answers with a plain interrupt return |
| `2707` | table | the score chime: `A = table[273F + digit position]` |

**The chime table `273F`** (set 1): `10 10 30 40 50 60` — positions 10 pts and
100 pts both play `10` (the D5 rattle), then `30`/`40`/`50`/`60` (F3, C4, F4,
F5 single notes) for 1 000/10 000/100 000/1 000 000. Guarded by the `C07C` and
`C1DD` mutes at `26EC`–`26FA`.

So the complete set of command values set 1 ever sends is:

```
00 10 11 30 40 41 50 60 69 77 88 90 96 99 A0 AA B0 B1 BB CC DD E0 E1 EE F0 F1 FF
```

### 3.2 Cross-reference against the sound ROM's command map

* **Every value the game sends lands on a handled row** of
  `sound-rom-map.md` §2. None lands on the 168 hard-reset values. The two
  init rows that are reached — `CC` (re-init from `0A0`) only from the
  power-fail handler that then spins forever, and `BB` (the `$403` P1 burst)
  only from the first-boot TRAP path — are both appropriate where they occur.
* **`FF` is sent deliberately** as the frame terminator; the sound ROM's
  "plain ISR return" for `FF` is exactly what a terminator needs.
* **Tunes the sound ROM carries that no game ROM ever triggers**: `01 20 21
  31 51 61 70 71 80 81 91 A1 C0 C1 D0 D1` — sixteen of the 32 effect
  commands. (`31` shares its tune with `F0`, which is sent; `21/71/80/81/91`
  alias `7AF`'s note, never sent; the `C0`/`70` chime-ladder rungs are never
  reached because the game's own chime table stops at `60`.) The four
  dead-in-the-sound-ROM tunes stay dead from this side too.
* **For the startup-sound investigation**: the boot sound is `00` (3.11 s
  pulsing tone) sent at `0276` on every boot via `0271`, cut by `88` after
  exactly 255 TRAP ticks = 2.55 s. Cold init additionally plays `11` (2.05 s)
  to completion — the busy-poll at `0236` — *before* the final `RST 0`, so a
  first power-up plays `11`, resets, then plays `00` truncated.

### 3.3 Set 2's census differs in exactly one datum

Set 2 sends from the same 26 relocated sites (byte listing in
`gamemap/` working files; the map from site to command is unchanged) — but
**its chime table at `273F` reads `10 10 E0 90 A0 60`**: the 1 000/10 000/
100 000 chimes become the bumper cascade (`E0`), the siren (`90`) and the
rising zap (`A0`). Set 2 therefore **never sends `30`, `40` or `50`**, and its
sent set is:

```
00 10 11 41 60 69 77 88 90 96 99 A0 AA B0 B1 BB CC DD E0 E1 EE F0 F1 FF
```

Set 2 also adds two `99` (cabinet read) sites: `0293` — the falta handler
re-reads the cabinet — and `0411` in attract, both serving the new coin
conditioner (§6.3).

---

## 4. The interrupt structure, from the map

| vector | target | role | notes from the full trace |
|---|---|---|---|
| RESET `0000` | — | magic test → warm/cold | nothing in the reset loop writes the magic; TRAP does (`1806`–`1822`). Measured: the cold NVRAM boot takes the `BB`-send path once, seeds `C000`, `RST 0`s |
| TRAP `0024` | `1800` (set 2 `19DA`) | 100 Hz mains | the whole output side lives here: lamp rebuild, display service, switch scan, cabinet poll, frame send. Set 2 wraps it in a re-entrancy sentinel (`C089`, §6.2) |
| RST5.5 `002C` | `003F` | sound reply | two exits: echo-armed (`C033 == AA`) escapes the sender's spin via the `XTHL`/`PCHL` idiom; unarmed reads and discards the reply (`RNZ`), and a zero reply falls through the same escape |
| RST6.5 `0034` | `0286` (set 2 `028E`) | falta (tilt) | `RNZ` if already latched. Stops sound, lights luz falta, saves lamp state, E-fills the display (`2A19`: 8279 command `90`, inhibit `A4`/`A8`, 16 × `EE` twice) |
| RST7.5 `003C` | `0244` (set 2 `024C`) | power fail | terminal: `CC` to the sound CPU, spin at `026A`. The TRAP handler opens its one-instruction window (`182F`) and resets its latch (`SIM #1D` at `194C`) every pass, so the `SIM` bit-4 core fix is exercised even though the interrupt never fires |

`188E` (`LDA 8000` inside the TRAP handler) reads and discards the reply latch
once per pass — it is what keeps a late, unwanted reply from leaving RST5.5
pending across frames.

---

## 5. NVRAM, as the code uses it

Derived from the 553 absolute NVRAM references (set 2: 670) plus the pointer
tables. Values are triple-stored (§2) unless marked single. This is a working
map of the regions the code gives meaning to, not a claim that every byte in
between is unused.

| range | contents |
|---|---|
| `C000` | magic `0x55` (single; seeded by TRAP on first boot) |
| `C001` | machine state: `AA` = init in progress, `00` = normal (single) |
| `C002`–`C007` | TRAP tick counters: `C002` one-shot, `C003` multi-tick wait, `C005` coin-pulse timeout, `C006` blink counter (sign also picks the bola-extra side), `C007` picabolas countdown |
| `C008`–`C00C` | lamp-state save slots (falta / boot restore) |
| `C01C` | falta latch (`FF` = faulted) |
| `C01D` | zone / carousel / audit step counter (context-dependent: 1–9 AJUSTES, `10`–`1D` carousel, 1–3 TEST audits) |
| `C023`–`C025` | BCD display scratch |
| `C026`–`C029` | the four switch bytes: `0x4000` port, cabinet (via sound `99`), 74165 chain low/high |
| `C02A`–`C02E` | switch edge memories |
| `C030`–`C033` | carousel step shadow, `C033` = echo-arm flag |
| `C034`–`C047` | the 20-byte lamp/coil frame; `C04D` frame pointer, `C04F` mains phase |
| `C078` | display mode selector, `C07B` menu button state, `C07C` chime mute |
| `C07D`–`C088` | attract lamp-state save |
| `C08A`–`C08C` | first checked triple; `C08D`/`C090` credits units/tens |
| `C099`, `C0B1`, `C108`, `C15F`, `C207`, `C2D9` | the six sentinels `55/AA/55/AA/55/AA` |
| `C0B7`–`C106` | per-player display copies (pointer table `255C`) |
| `C10E`–`C15D` | per-player scores: 7 BCD digits × 3 copies each, players at `C10E C123 C138 C14D` (table `254D`) |
| `C162`–`C186` | player group values (tables `256B`); `C168`/`C171`/`C17A`/`C183` shown by the carousel high-score screen |
| `C18F`–`C1B2` | player group (table `257A`) |
| `C1B3` | current player, `C1B6` players in game, `C1B9` last shown value |
| `C1BC`–`C1C7` | the LFSR state, four triples (`2300`) |
| `C1C8`–`C1D3` | per-player flags (table `258F`) |
| `C1E3` | ball number; `C1E9`+3n the eight settings triples (defaults `03 02 21 31 00 06 11 15` from `3824`) |
| `C20A` | mode flag the boot dispatches on: `10` in-game, `30` attract, `40` resume-interrupted-game (read from the `0102` dispatch) |
| `C20D`–`C218` | per-player lamp-bit groups (table `259E`) |
| `C219`–`C2A8` | the lamp tables: `C219` steady, `C249` force-on, `C279` force-off (each: 7 IC1/IC2 triples + 3 IC3/IC7 triples per phase pair); `C226`/`C22C` the live avance ladder; `C228` game-over/bumper lamp byte; `C231`/`C237` coil bytes; `C23D` start-lamp/doble/triple byte |
| `C2A9`–`C2D8` | the phase-selected frame sources rebuilt every TRAP (`1844`) |
| `C2DC`–`C36B` | the three audit pages, 16 triples each (`C2DC` games, `C30C`, `C33C`; coin audits at `C354`/`C360` inside page 3) |
| `C372` | end of the initialised/checked area (the `DSUB` loops' bound) |
| `C373`–`C7FF` | uninitialised + stack (set 1 stack base `C7FF`) |
| set 2 only: `C7D0`–`C7FF` | `C7D0`/`C7D1` coin-conditioner counters, `C7D2` conditioner bypass flag (`99`), `C7E0`–`C7E7` stuck-contact watchdog counters, `C7EA`–`C7EE` extra-ball/replay audits + conditioner flags, `C7F1`–`C7FD` the ten zone-10–19 settings (single bytes), `C7FE`/`C7FF` bonus-collect flag pair; stack base `C7CF` |

---

## 6. Set 2, as a structured diff

Raw byte identity is only 40.1 % — misleading, because one inserted byte shifts
every following address operand. Aligned at the instruction level with ROM- and
NVRAM-pointing operands abstracted (`align.py`, `difflib` over 5 120 vs 5 667
instruction tokens), the two programs are **94.4 % identical**: set 2 is set 1
plus ~40 insertions and two one-instruction deletions. The full alignment
(every equal block with its shift, every insertion) is in the working files;
what follows is every diverging region with its meaning.

### 6.1 What did not change

The display module `2400`–`25AC`, the LFSR `2300`, the score/chime engine
`25AD`–`273E` (minus the table), the carousel `2D63`–`3083`+table, the audit
code, the switch-test table (byte-identical), the four dead-code orphans, and
the whole program structure. The nine original zone handlers are relocated
+`0x2D` unchanged.

### 6.2 The TRAP re-entrancy sentinel (new)

Set 2's TRAP vector targets `19DA`: `PUSH PSW / LDA C089 / CPI 55 / JNZ 1800`.
`1800` stamps `C089 = 55`, runs the set-1 handler body, and the exit at `19D1`
clears it. A TRAP that fires while `C089` is still `55` — a pass that overran
its 10 ms — returns immediately (`19E3`: `POP PSW / RET`-shape exit). Boot and
falta paths clear the sentinel (`0050`, `018A`, `0299`). Set 1 has no such
guard.

### 6.3 The sound-send spin replaces `HLT` (new — and driver-relevant)

Set 1's sender: `196C: STA 8000 / SIM #0E / … EI / HLT / RET` — sleeps until
the RST5.5 reply. **Set 2's sender at `19E5` does not halt**: after `EI` it
runs a fixed ≈50-iteration `DAD`/`JC` spin (`19F4`–`1A02`) and returns. If the
reply arrives inside the spin, RST5.5's handler loads it into `A`; if not, the
caller sees `A = 0` and a later reply is read and discarded by the unarmed
RST5.5 path. The factory replaced a sleep-forever-on-a-lost-wake with a
bounded spin — the exact structural race PinMAME's core still has for set 1
(`hardware-findings.md` §15.3) was evidently worth a firmware change to
Recreativos Franco. The echo-verified variant (`1A0D`) still spins on the
`1A03` loop and escapes through `1A0B`.

### 6.4 The coin-contact conditioner (new)

Inserted into the TRAP switch scan (`18D8`–`1930`): for each coin bit (`0x10`,
`0x20`) of the cabinet byte, a consecutive-closure counter at `C7D0`/`C7D1`.
A closure shorter than 2 passes is suppressed (debounce); a longer one passes
— unless the bypass flag `C7D2` ≠ `99`, in which case the validated closure
also clears a flag bit in `C7EE`. `C7D2` is stamped `99` in attract (`0411`)
and on falta (`0295`), cleared on the coin paths (`042F`, `059F`, `0642`) —
i.e. a coin is only honoured when the machine was in a state that armed it.
The falta handler and every coin path also reset `C7EE` to `FF`. Eleven NOPs
pad the scan where set 1's shorter sequence sat (`18C1`–`18CB`).

### 6.5 The stuck-contact watchdog (new)

`070E`–`0713`: `LDA C7FA / ANI 01 / CNZ 3ABF` — the watchdog at `3ABF`
(counters `C7E0`–`C7E7`, switches 11/12/18/47, fault past `0x7F` — measured in
`hardware-findings.md`) is gated on bit 0 of `C7FA`, the zone-18 setting
(`vpx-table-reference.md` §5.1.1). The fault
recovery gains a related 7-pass countdown (`107A`–`108E`) re-entering the
falta handler while the offending contact stays closed, and recovery also
honours `C7FA` when deciding which contacts must clear (`0338`–`034F`).

### 6.6 The gameplay-setting hooks (new, one per zone)

Each of the ten new zones is a small guard inserted into set-1 code, plus its
handler/editor in the new block:

| insertion | zone (NVRAM) | effect |
|---|---|---|
| `0C4A`, `0CBC`–`0CC4`, `123A`–`124x`, `12C1` | 13 (`C7F4`), counter `C7F7` | consecutive-extra-ball cap per ball in play |
| `0C78`–`0C80` | 17 (`C7F9`) | completed diana lights both bumper lamps → bumpers pay 10 000 |
| `0F3F`–`0F53` | 12 (`C7F3`) | ladder reset behaviour on picabolas collect |
| `0F73`–`0F88`, `0F9A`, `1048`–`1055`, `11E6`–`11EE` | 19 (`C7FD`), flag `C7FE` | end-of-ball bonus collect through the picabolas countdown |
| `10D1` | 15 (`C7F6`) | 100 PUNTOS lane pays 1 000 |
| `176D`–`1789` | 16 (`C7F8`) | credit cap: BCD nibbles compared against tens/units before adding |
| `120A`–`121C` | (`C7EC`) | game-over lamp-bit clear when an extra-ball replay audit is pending |
| `122A` | audit `C7EA` | counts extra-ball replays |
| `0824` (reads `C229`), `0DD8`/`0DE0`/`0E43`/`0E4B` (`C7F0` collect-variant marker), `0E22` (`CALL 3A43`) | 10/11/14 (`C7F1`/`C7F2`/`C7F5`) | left/right special bank-reset behaviour, diana-completion score, collect variants |

### 6.7 The new code block `3880`–`3B4D` (set-2-only, fully classified)

All reachable code, no data, no dead bytes: the extended factory-defaults
writer (`3851`–`38DE`: the eight original triples via `162C`, then `C7F1`–
`C7FF` singles = `01 01 01 01 03 10 00 15 01 01 00 00 01 FF FF` and the
watchdog counters zeroed), the ten zone handlers (`3971 3980 398F 399E 39B2
39CD 39E9 3A05 3A14 3A23` — from the jump table, one per zone 10–19), their
shared value editors, the helpers `3A43`/`3B46` used by the gameplay hooks,
and the watchdog `3ABF`–`3B4D`.

### 6.8 Region table, set 2

| range | class | n | contents |
|---|---|---|---|
| `0000`-`000C` | code | 13 | RESET (byte-identical to set 1 except LXI SP,#C7CF - the stack base drops to leave C7D0-C7FF free) |
| `000D`-`0023` | filler | 23 | FF fill |
| `0024`-`0026` | code | 3 | TRAP vector: JMP 19DA |
| `0027`-`002B` | filler | 5 | FF fill |
| `002C`-`002E` | code | 3 | RST5.5 vector: JMP 003F |
| `002F`-`0033` | filler | 5 | FF fill |
| `0034`-`0036` | code | 3 | RST6.5 vector: JMP 028E |
| `0037`-`003B` | filler | 5 | FF fill |
| `003C`-`004C` | code | 17 | RST7.5 vector (JMP 024C) + RST5.5 handler; PCHL target 1A0B |
| `004D`-`036B` | code | 799 | boot, modes, RST7.5/RST6.5 handlers, fault recovery - set 1 004D-033E shifted +4..+3B with small insertions (coin-audit calls at 0050, falta cabinet re-read at 028E-0299, recovery differences 032A-034F) |
| `036C`-`0370` | filler | 5 | FF fill |
| `0371`-`0686` | code | 790 | attract, game start, coin paths - set 1 0350-0634 shifted +21..+52 with insertions (attract cabinet read 0411-041C, coin conditioning hooks) |
| `0687`-`06FF` | filler | 121 | FF fill |
| `0700`-`17DF` | code | 4320 | in-play, drain, game over, thresholds, helpers, TRAP-side coil/credit code - set 1 0700-1785 shifted +8..+5A; insertions include the watchdog call at 0713 (CALL 3ABF), zone-13 extra-ball cap checks (0C78-0CC4 area), zone-19 bonus-collect entries (0F3F-0F88 area), end-of-turn audit/zero of C7F7 (11E6-124x area), and the zone-15/17 scoring variants |
| `17E0`-`17FF` | filler | 32 | FF fill |
| `1800`-`1AD8` | code | 729 | TRAP handler block: entry at 19DA (vector), body = set 1 1800-1A52 shifted +4..+86, with the two-pass coin-contact conditioner 18D8-1930 (C7D0/C7D1 counters, C7D2=99 bypass) inserted into the switch scan; frame send at 1A6E-1A89; lamp frame builder to 1AD8 |
| `1AD9`-`22FF` | filler | 2087 | FF fill (set 1: 1A53-22FF; 134 bytes shorter here because the TRAP block grew) |
| `2300`-`2375` | code | 118 | LFSR random generator + loteria draw (byte-identical logic; only NVRAM operands moved) |
| `2376`-`23FF` | filler | 138 | FF fill |
| `2400`-`24A7` | code | 168 | display serial writer + per-TRAP display service (common code, byte-identical stream) |
| `24A8`-`24B3` | **deadcode** | 12 | same orphan blanking loop as set 1, still unreferenced |
| `24B4`-`254C` | code | 153 | score -> display transfer |
| `254D`-`2554` | **table** | 8 | 4 LE NVRAM pointers C10F C124 C139 C14E (set 1 values +1: the whole NVRAM block above C08D moved) |
| `2555`-`255B` | code | 7 | stub |
| `255C`-`2563` | **table** | 8 | 4 LE NVRAM pointers C0B8 C0CD C0E2 C0F7 |
| `2564`-`256A` | code | 7 | stub |
| `256B`-`2572` | **table** | 8 | 4 LE NVRAM pointers C163 C16C C175 C17E |
| `2573`-`2579` | code | 7 | stub |
| `257A`-`2581` | **table** | 8 | 4 LE NVRAM pointers C190 C199 C1A2 C1AB |
| `2582`-`258E` | code | 13 | stubs |
| `258F`-`2596` | **table** | 8 | 4 LE NVRAM pointers C1C9 C1CC C1CF C1D2 |
| `2597`-`259D` | code | 7 | stub |
| `259E`-`25A5` | **table** | 8 | 4 LE NVRAM pointers C20E C211 C214 C217 |
| `25A6`-`25AC` | **deadcode** | 7 | same orphan stub as set 1 |
| `25AD`-`273E` | code | 402 | display dispatch, score add, score commit + chime |
| `273F`-`2744` | **table** | 6 | chime ladder: 10 10 E0 90 A0 60 - set 2 replaces the 1000/10000/100000 chimes (set 1: 30 40 50) with the bumper cascade E0, the siren 90 and the zap A0 |
| `2745`-`284C` | code | 264 | score display propagate |
| `284D`-`284D` | **deadcode** | 1 | same orphan RET byte |
| `284E`-`2C41` | code | 1012 | display writers, buffer rebuild, fault fill (2A1A), value display - set 1 284E-2C40 shifted +0..+1 (one 1-byte insertion at 2888) |
| `2C42`-`2CFF` | filler | 190 | FF fill |
| `2D00`-`2D5E` | code | 95 | four-value display + helpers (identical structure; NVRAM operands +1) |
| `2D5F`-`2D62` | **deadcode** | 4 | same orphan |
| `2D63`-`3082` | code | 800 | carousel, audits, coin audits, TEST mode - set 1 2D63-3082 with NVRAM operands moved |
| `3083`-`309E` | **table** | 28 | carousel jump table: 14 LE pointers, byte-identical to set 1 |
| `309F`-`320C` | code | 366 | audit increments, TEST mode loop |
| `320D`-`3212` | **table** | 6 | 3 LE NVRAM pointers C2DD C30D C33D (audit pages, set 1 values +1) |
| `3213`-`349C` | code | 650 | audit display, AJUSTES menu common, zone/value stepping - the zone step at 33E6-33EE forces the BCD counter 09 -> 10, which is what makes table entries 9-14 unselectable |
| `349D`-`34CE` | **table** | 50 | zone jump table: 25 LE pointers - 9 zone handlers, 6 dead slots (all 37C2 = the zone-9 handler), 10 new zone handlers 3971-3A23 |
| `34CF`-`34E6` | **table** | 24 | switch-test contact-number table, byte-identical to set 1 |
| `34E7`-`3B4D` | code | 1639 | settings validation, zone-display helpers, the nine original zone handlers (35C0-37E8, set 1 3593-3823 shifted +2D), factory defaults (3851, now 11 settings: the set-1 eight plus the C7F1-C7FD group), and the set-2-only block 3880-3B4D: the ten new zone handlers (3971 z10 .. 3A23 z19), their value editors, the C7Ex watchdog (3ABF: switches 11/12/18/47 held-closed counters, past 7F -> falta), and the C7D0-area service code |
| `3B4E`-`3FFE` | filler | 1201 | FF fill |
| `3FFF`-`3FFF` | filler | 1 | one byte 0xD0 - not FF, referenced by nothing in either image; a programmer artefact, not code or data the ROM reads |

The one non-`0xFF` filler byte: `3FFF = 0xD0`. Nothing in either image
references `3FFF`; there is no checksum code in the ROM. A programming
artefact, recorded so nobody hunts for it later.

---

## 7. Static vs. dynamic coverage

Seven sessions against the live driver (headless, private NVRAM per session,
coverage started before the ROM finishes booting so the boot paths are
captured): one per boot mode (JUEGO, BORRADO, TEST, AJUSTES ×2 — the second
walking every zone with twelve value presses each and pulsing all 24 test
contacts), a full played game with tilt/recovery, and a deep session — 260 s
of attract (the carousel stepped through all of `C01D` `10`–`1C`, measured), a
two-player game to over 1 000 000 per player (both players' score thresholds
crossed, replays paid) with 29 CPU-filtered instrument points, plus a
dedicated tilt run adding four more (33 in all).

**Results.** Of the 5 120 static instruction starts:

* **≥ `0x1000` (unambiguous): 3 151 of 3 571 executed (88 %).**
* **< `0x1000`, outside the sound-code overlap: 842 of 1 148 (73 %).**
* The 401 overlap addresses cannot be claimed from the bitmap; the instrument
  points stand in for them: `004D`, `00B3`, `0102`, `0186`, `01E9`, `0271`,
  `0350`, `03B5`, `0470`, `0508`, `0545`, `055F`, `057A`, `0700`, `0705`,
  `0AFC`, `0C63` all counted (e.g. `03B5` attract ×3 142, `0700` in-play
  ×10 487, `01E9` cold init ×1), and `0244` (RST7.5) counted **zero**, the
  expected value. The 100-pta path (`05F4`/`060F`, both inside overlap) is
  confirmed by state instead: one switch-26 pulse paid 5 credits.

**Every gap explained.** The uncovered static code falls into these classes,
each verified by reading the code at the reported ranges:

| class | ranges (set 1) | why not executed |
|---|---|---|
| needs an input the driver never produces | `0244`–`0270` (RST7.5 handler, plus its head in the overlap zone, bitmap-zero from both CPUs); `055C` (stuck coin — the driver's coin one-shot always opens inside the 20-tick window) | correct behaviour, not a gap |
| needs 3–4 players | `1372`–`13CB` (threshold blocks, players 3–4) | two-player session |
| needs game states the automated stimuli did not reach | `0C87`–`0C9B` + `0D27`–`0D65` (extra-ball / picabolas-especial arming at exact ladder rungs), `0E14`–`0E93` (unscored-ball re-serve — every automated ball scored), `0ED2`–`0FFE` + `1001`–`1023` (end-of-ball bonus collect, countdown and picabolas coil — the ladder flag never armed in these runs; `tools/rfranco_game.py` demonstrates the same path live, so this is a stimulus gap), `13F0`–`1453` (rampa special-collect award — lamp 52 never lit for the blind pulse; the knocker itself was covered via the score-threshold award), `1656`–`1666` (bank-reset coil path), `0339`–`033C` (recovery with a ball on the picabolas contact) | reachable in play; the harness tools cover several of them in their own runs |
| rare-value branches | `1615`–`161B`, `2967`–`2992` (credits ≥ 10 display/borrow), `3107`–`3121` (coin-audit BCD carries), `2361`–`2367` (the loteria tiers not drawn), `2621`–`26C4` pieces (score digit positions/carries not produced), assorted 2–10-byte else-arms throughout | value-dependent |
| menu/mode edges | `33FD`–`3401`, `3456`–`348F` pieces, `358F`–`3809` pieces (zone-value wrap branches, the contact-test per-closure display, settings-validation failure arms `34E6`/`3512` — impossible with healthy NVRAM), `2DD8`–`2E19` (one carousel entry variant), `30A6`–`30DB` (audit pages not incremented by these scenarios), display-module entries `2400` (used only by RST7.5), `2448`–`244E`, `24F1` | mode-dependent |
| warm-boot / falta edges in the overlap zone, bitmap-zero | `0057`, `0111`, `0117`, `0174`, `0179`, `01D3`–`01D6`, `0537`, `05CD` | validation-failure and coin-timing else-arms. The falta handler and recovery themselves (both in the overlap zone) were closed with a dedicated CPU-filtered run: tilt during play counted `0286` ×1 and `030C` ×1, `0244` ×0, and the recovery's `RST 0` re-boot counted `0102` a second time, ending with `C01C = 00` |

No uncovered range is unexplained, and none of the explanations required
amending the static classification: everything the dynamic pass executed lies
inside the statically-traced code, and nothing classified as data, dead or
fill was ever executed (checked against the merged bitmap for `≥ 0x1000` and
the clean subset below it).

---

## 8. Judgement: is the PinMAME driver missing anything?

Measured against the complete map, with severity. The short answer: **no
behaviour the ROMs exercise is unmodelled or mis-modelled; three items are
worth recording, none requires driver-source changes to make the game
correct.**

### 8.1 Verified present and correct (from the map's side)

* **Every I/O the ROMs perform is modelled.** The exhaustive operand scan
  (§2, §3) finds exactly: `LDA 4000` (one site per set — mapped, active-low
  playfield byte), 26 `STA`/2 `LDA` at `8000` (latch pair with the READY
  stall model), 553/670 NVRAM references (`C000`–`C7FF`, mapped, 0-filled on
  first boot — and the ROM's own triple-store + sentinel machinery is what
  makes 0-fill land in cold init cleanly), `OUT` at two sites (`00`, `FF` —
  the driver clocks both serial chains on any `OUT`, which is what the
  hardware's one-decode does), `RIM` at `1801` and `18A8`, and `SIM` at six
  sites — all covered by the five core fixes. No `IN` exists. (One correction
  to `hardware-findings.md` §10, which lists a third `RIM` at `0x34B1`: that
  byte is the `0x20` *contact 20* entry of the switch-test table at
  `34A2`–`34B9`, data, not code — a Ghidra misread.)
* **The undocumented `DSUB` (`0x08`)** at `0193`/`01F8` — the warm-boot NVRAM
  check depends on its Z flag over the full 16 bits. PinMAME's core implements
  it for `cputype == 8085` (`i8085cpu.h:116` `M_DSUB`, Z corrected by the
  `if (l != 0) A &= ~ZF` line), and this driver's CPU is an 8085A. Verified
  working every boot; worth recording because a core "cleanup" that dropped
  the undocumented ops would brick both sets at warm boot.
* **RST7.5 deliberately not driven** — the map confirms the handler is
  terminal (spin at `026A` after `CC`), so the driver's choice is the only
  correct one.
* **No game-sent sound command mis-lands.** §3.2: nothing reaches the sound
  ROM's 168 hard-reset values; the frame bytes rely on the `JNI` bulk loop,
  which the READY guard keeps honest. The `41` game-over melody's 255 repeats
  are terminated by the next real command, so the sound ROM's odd repeat
  count is load-bearing, not a defect to fix.
* **The stuck-coin fault path (`0545`→`055C`)** cannot be provoked through
  the driver's coin one-shot, which always opens the contact within the
  20-tick window. That is a fidelity footnote, not a gap: the path exists for
  a physically jammed coin switch, and the debugger can still reach it by
  holding the raw switch bit.

### 8.2 Recorded, no action needed

1. **The set-1 `HLT` wake race is real but firmware-acknowledged.**
   `hardware-findings.md` §15.3 already records that a reply landing between
   `STA (8000)` and `SIM #0E` would leave the 8085 halted (the core's
   `i8085_set_RST55()` returns early when masked and nothing re-evaluates on
   unmask). The map adds a datum: **set 2's firmware replaced the `HLT` with
   a bounded spin** (§6.3) — the manufacturer evidently met this on hardware.
   Severity: low (never observed in any soak; set 2 immune by construction).
   A core mask-reveal recheck, as in newer MAME, would close it for set 1.
2. **Set 2's reply window is timing-sensitive by design.** Its sender gives
   the 8035 only the ≈50-iteration spin (plus the READY stall) to answer
   `EE`/`99`/`77`/`DD`; a reply after the spin is discarded and the caller
   sees 0. The current interleave (250) passes every harness; anyone lowering
   it further should know this is the mechanism that will break first on set 2
   — before the §7.3 symptoms in `driver-notes.md`.
3. **The sound CPU's latched P1.6 output is modelled as write-only.** The map
   shows the game drives it with strict discipline — set (`96`) in attract,
   game over, falta and BORRADO; cleared (`69`) at every ball/game start and
   on recovery exit — i.e. it is an "out of play" flag leaving the sound board
   toward the driver board. The driver deliberately latches nothing for it
   (`rfranco.c:691`), and nothing in the emulated machine reads it. If a
   physical trace ever identifies it (RL1 coil-supply relay and coin-lockout
   are the natural candidates — inference, unverified), a front end might want
   it surfaced as an output; that would be a five-line change in
   `rfranco_scpu_p1_w`. Until then there is nothing to model.

### 8.3 Checked for and absent

No unexpected interrupt use (all five vectors accounted for, §4); no ROM
self-reads that a banking model could break; no reads of `0x4000` outside the
one scan site; no write anywhere outside `0x8000`/NVRAM; no timing loop that
depends on instruction cycle counts finer than the TRAP tick (the two spin
idioms — set 2's `19F4` delay and the `1779`/`158D` tick waits — are the only
time bases, and the first is the one flagged in 8.2.2); no NVRAM cell with
game-visible meaning outside §5 (set 2's `C7D0`–`C7FF` block was the last
undocumented region, §6.4–§6.6).

---

## 9. Files

The disassembler, tracer and instruction-level aligner are committed as
`../tools/dis85.py` and `../tools/rom_diff.py`. Everything in this document that
depends on them can be regenerated:

```bash
tools/rom_diff.py inventory                  # hashes, sizes, checksum scheme
tools/rom_diff.py coverage                   # the byte-count check in §0
tools/rom_diff.py sound                      # the command census in §3
tools/rom_diff.py matrix                     # the revision ordering
tools/rom_diff.py hunks OLD NEW              # every changed hunk, disassembled
tools/rom_diff.py shifts OLD NEW             # NVRAM/code address remapping
```

Still scratch, not committed, and reproducible from the ROMs plus this document:
`anno_sf.json`/`anno_fa.json` (computed-jump resolutions),
`mapdef_sf.py`/`mapdef_fa.py` + `build_map.py` (the verified byte maps),
`scanflow.py` (I/O and idiom census), `soundcode.py` (the sound-ROM overlap
ranges), `cover.py`/`deep.py` + `cov/*.json` (the dynamic sessions),
`compare_cov.py` (the static/dynamic reconciliation).
