# Super Star — the four game-ROM revisions, and their order

Two new IC19 dumps arrived in `romdumps/super_star_rev3.zip` and
`romdumps/super_star_setC.zip`. Both are genuine, previously unpreserved Super
Star firmware. Neither is newer than the two sets already known: **they sit
between them**, and the four images form a single linear revision chain.

```
rev. 1  m31-a-01187.ic19  AB8B1148   supstarf    MAME parent / PinMAME supstarf
rev. 2  27128Prg.bin      77C43E87   supstarfc   NEW - PinMAME "set C"
rev. 3  super.dat         51697AFF   supstarfb   NEW - PinMAME "set B"
rev. 4  27c128.ic19       9A440461   supstarfa   MAME clone / PinMAME supstarfa
```

**The PinMAME set letters are not chronological.** `supstarfb` and `supstarfc`
were named before the order was known, and "set B / set C" was chosen precisely
so as not to imply one — a good call, since set C turns out to be the earlier
firmware. The letters are the stable identifiers; this document supplies the
order they deliberately do not encode.

A fifth file in `super_star_setC.zip`, `m1-31_b_1704.ic32`, is **not Super Star
and not a pinball ROM** — see §7.

---

## 1. What the archives contain

| Archive | File | Size | CRC32 | SHA-1 | Zip date | Verdict |
|---|---|---|---|---|---|---|
| `super_star_rev3.zip` | `super.dat` | 16384 | `51697AFF` | `d10c6456716ca49cce590996e7271b8cd7026f38` | 2015-03-27 | **new — rev. 3 = `supstarfb`, set B** |
| `super_star_setC.zip` | `27128Prg.bin` | 16384 | `77C43E87` | `efdf60b53ac105985ca6d4eeb6ed48b893bb7ad8` | 2016-10-14 | **new — rev. 2 = `supstarfc`, set C** |
| | `super.dat` | 16384 | `51697AFF` | `d10c6456716ca49cce590996e7271b8cd7026f38` | 2015-03-27 | duplicate of the above |
| | `m31-a-01187.ic19` | 16384 | `AB8B1148` | `496d3c9664386ae64e94462db2fdd36811a68a87` | 2014-11-27 | known — rev. 1 |
| | `27c128.ic19` | 16384 | `9A440461` | `e2f8dcf95084f755d3a34d77ba2649602687a610` | 2014-11-27 | known — rev. 4 |
| | `m1-31_b_1704.ic32` | 16384 | `A74A85B7` | `f562495a6b97f34165cc9fd5c750664701cac21f` | 2020-03-16 | **different machine** (§7) |

So `super_star_setC.zip` is a collection archive: the two already-known Super
Star ROMs, the two new ones, and one stray from an unrelated Recreativos Franco
board. Only **two** images in the two archives are new.

Neither archive carries a notes file or zip comment. **The zip dates are dump
dates, not release dates** — `27128Prg.bin` was dumped after `super.dat` but is
the earlier firmware. The ordering below rests on the code, not the timestamps.

No sound ROM was included in either archive. See §6 for why the known-good
`2532.ic4` is nevertheless the correct pairing for all four sets.

---

## 2. Method

The same three-pass approach as `game-rom-map.md`, reused because rev. 2 and
rev. 3 are byte-aligned to rev. 1's layout and inherit its complete byte map:

1. **Recursive-descent 8085 trace** from the reset vector and all four hardware
   vectors (TRAP `0024`, RST5.5 `002C`, RST6.5 `0034`, RST7.5 `003C`), with the
   operator-menu jump table resolved per image from its own dispatcher.
2. **Instruction-level alignment** (`difflib` over normalised instruction
   streams, ROM- and NVRAM-pointing operands abstracted to their region class)
   so that a one-byte insertion does not register as thousands of differences.
3. **Byte classification** of every image: traced code, referenced data tables,
   known dead code, `0xFF` fill — with the residue compared against rev. 1's
   published classification.

Raw byte identity is worthless here and actively misleading. `super.dat` shares
only 79.6 % of its bytes with rev. 1, yet the two differ by **25 inserted and 2
deleted instructions out of ~4 900**: one inserted byte shifts every following
address operand.

Every figure in this document is reproducible from the committed tools
(`../tools/dis85.py`, `../tools/rom_diff.py`) against the built sets in
`../roms/`:

```bash
tools/rom_diff.py inventory     # §1  hashes, sizes, the checksum scheme
tools/rom_diff.py matrix        # §3.1 instruction counts and the hunk matrix
tools/rom_diff.py coverage      # §6  byte classification and residue
tools/rom_diff.py sound         # §6  command census and the chime table
tools/rom_diff.py hunks roms/supstarf.zip:m31-a-01187.ic19 \
                        roms/supstarfc.zip:27128Prg.bin      # §4
tools/rom_diff.py hunks roms/supstarfc.zip:27128Prg.bin \
                        roms/supstarfb.zip:super.dat          # §5
tools/rom_diff.py shifts roms/supstarf.zip:m31-a-01187.ic19 \
                         roms/supstarfc.zip:27128Prg.bin      # §4 NVRAM shift
```

---

## 3. The ordering evidence

### 3.1 The edit distances form an additive path

Instruction-level hunk counts between every pair:

| | rev. 1 | rev. 2 | rev. 3 | rev. 4 |
|---|---|---|---|---|
| **rev. 1** | — | **8** | 15 | 57 |
| **rev. 2** | 8 | — | **9** | 52 |
| **rev. 3** | 15 | 9 | — | **43** |
| **rev. 4** | 57 | 52 | 43 | — |

The consecutive distances are 8, 9, 43, and every skip distance is the sum of
the steps it spans: rev1–rev3 = 15 ≈ 8 + 9, rev2–rev4 = 52 = 9 + 43, rev1–rev4
= 57 ≈ 8 + 9 + 43. That is a path metric — the four images lie on one line, in
this order. No other permutation is additive.

### 3.2 Everything grows, monotonically

| | rev. 1 | rev. 2 | rev. 3 | rev. 4 |
|---|---|---|---|---|
| instructions | 4 914 | 4 927 | 4 949 | 5 462 |
| non-`0xFF` bytes | 11 303 | 11 324 | 11 355 | 12 517 |
| traced code bytes | 10 736 | 10 762 | 10 796 | 11 932 |
| stack base | `C7FF` | `C7FF` | `C7FF` | `C7CF` |
| warm-boot vector | `0186` | `0186` | `018A` | `018A` |
| RST6.5 handler | `0286` | `028A` | `028E` | `028E` |
| RST7.5 handler | `0244` | `0248` | `024C` | `024C` |
| TRAP vector | `1800` | `1800` | `197F` | `19DA` |
| operator menu | 9 zones | 9 zones | 9 zones | 19 zones |
| checksum byte | none | none | none | `D0` at `3FFF` |

Each step is dominated by insertions in the forward direction (11, 22, 507
instructions) and by deletions in the reverse (1, 8, 5). Firmware accretes.

### 3.3 The decisive artefact: eleven orphan NOPs

`super.dat` and rev. 4 are **byte-identical** across the whole TRAP switch scan,
including eleven `00` bytes at `18C1`–`18CB` and a twelfth at `18CF`:

```
rev. 1  ... 0F 77 D3 00 F2 A8 18 23 1D F2 A6 18 | 3A 00 40 | 32 26 C0 | 3E 99 | CD 6C 19 ...
rev. 2  ... 0F 77 D3 00 F2 B7 18 23 1D F2 B5 18 | 3A 00 40 | 32 26 C0 | 3E 99 | CD 7E 19 ...
rev. 3  ... 0F 77 D3 00 F2 AC 18 23 1D F2 AA 18 | 00 x11 | 3A 00 40 | 00 | 32 26 C0 | 3E 99 | CD 8A 19 ...
rev. 4  ... 0F 77 D3 00 F2 AC 18 23 1D F2 AA 18 | 00 x11 | 3A 00 40 | 00 | 32 26 C0 | 3E 99 | CD E5 19 | C5 D5 E5 47 21 EE C7 11 D0 C7 ...
```

Those NOPs are **exactly eleven bytes**, which is exactly the size of the TRAP
re-entrancy prologue that rev. 2 carries inline at `1800`:

```
1800: F5           PUSH PSW          1
1801: 3A 89 C0     LDA  $C089        3
1804: FE 55        CPI  #55          2
1806: C2 0B 18     JNZ  $180B        3
1809: F1           POP  PSW          1
180A: C9           RET               1   = 11 bytes
```

The story is unambiguous. Rev. 2 introduced the sentinel and put its prologue at
the top of the handler, pushing the entire TRAP body down eleven bytes. Rev. 3
moved that prologue out to `197F`, which pulled the body back up to rev. 1's
addresses — and the author padded the tail of the scan with eleven NOPs so that
`LDA $4000` landed on `18CC` again, where it had always been. Rev. 4 inherits
the padding verbatim and finally spends the headroom on the coin conditioner.

Rev. 2's inline arrangement is a state that only makes sense *between* "no
sentinel at all" and "sentinel relocated". Reading the chain backwards would
require the factory to have un-relocated a working prologue and deleted its own
padding.

### 3.4 Fixes are never reverted

* Rev. 3 replaces the sound sender's `HLT` with a bounded ~50-iteration spin —
  the lost-wake race fix (`game-rom-map.md` §6.3). Rev. 4 keeps it. Revs. 1
  and 2 still `HLT`.
* Rev. 4 turns three hardcoded gameplay constants into NVRAM settings reads:
  `MVI A,#03` → `LDA $C7F5`, `MVI A,#01` → `LDA $C7F6`, and the credit-cap
  compare `CPI #02 / JNC` → a fifteen-instruction `C7F8` nibble comparison.
  Settings become constants only going backwards in time.
* The chime ladder at `273F` is `10 10 30 40 50 60` in revs. 1–3 and
  `10 10 E0 90 A0 60` in rev. 4 alone — the change that makes rev. 4 the only
  revision that never sends sound commands `30`, `40` or `50`.
* The factory manual documents **nine** adjustment zones. Revs. 1–3 have nine;
  only rev. 4 has nineteen. The manual describes the first three revisions.

---

## 4. Step 1 — rev. 1 → rev. 2 (`27128Prg.bin`)

**One functional change: the TRAP re-entrancy sentinel.** +13 instructions,
+21 bytes, 8 hunks.

A new NVRAM byte is allocated at `C089`. Every variable from `C08A` to `C373`
shifts up by one; `C000`–`C086` is untouched. That single insertion is what
makes the raw byte diff 1 502 bytes wide.

| site | change |
|---|---|
| `1801` | prologue, inline at the head of the TRAP handler: `LDA C089 / CPI 55 / JNZ 180B / POP PSW / RET` — a TRAP that fires while the previous one is still running returns immediately; otherwise `180B` stamps `C089 = 55` |
| `1975` | handler exit rewritten: `MVI A,#00 / STA C089 / POP PSW / RZ` replaces rev. 1's `JZ 196A`, and the now-redundant `POP PSW` at `196A` goes with it — this is the one deleted instruction of the step |
| `0186` | warm-boot NVRAM validation clears the sentinel |
| `028A` | falta (RST6.5) handler clears the sentinel |
| `274D`, `2BD1`, `2BE0` | display-shadow loop bounds `CPI #AE` → `CPI #AF`, a consequence of the `C0xx` shift, not a separate change |

That is all eight hunks. Nothing else differs. The operator menu, the display module, the carousel, the
scoring engine, the switch-test table and the factory defaults are untouched.

## 5. Step 2 — rev. 2 → rev. 3 (`super.dat`)

**Three functional changes.** +22 instructions, +31 bytes, 9 hunks. The NVRAM
layout does not move at all — all 932 aligned NVRAM operands are identical.

### 5.1 The sound sender stops halting

```
rev. 2   198D: 76              HLT                     ; sleep until the RST5.5 reply
rev. 3   1999: E5 D5           PUSH H / PUSH D
         199B: 21 32 00        LXI  H,$0032
         199E: 11 FF FF        LXI  D,$FFFF
         19A1: 19              DAD  D                  ; 50-iteration bounded spin
         19A2: DA A1 19        JC   $19A1
         19A5: D1 E1 C9        POP D / POP H / RET
```

This is the fix `game-rom-map.md` §6.3 describes for rev. 4, and it enters the
line **here**, one revision earlier. A sender that halts waiting for a reply
that never arrives wedges the machine; a bounded spin returns with `A = 0` and
lets the caller carry on. It is the same structural race PinMAME's core still
has for rev. 1 (`hardware-findings.md` §15.3).

### 5.2 The TRAP sentinel prologue moves

The prologue leaves `1800` and reappears at `197F`, immediately ahead of the
sender, with the TRAP vector at `0024` retargeted `JMP 1800` → `JMP 197F`. The
handler body returns to rev. 1's addresses and the eleven NOPs of §3.3 restore
the alignment of everything after it. A third clear site is added at `0050`, in
the warm-boot continuation.

### 5.3 An explicit stack reset on the attract entry

```
0353: 31 FF C7        LXI SP,$C7FF
```

inserted at the head of the game-over → attract path. Recovery no longer
depends on the stack being balanced when it gets there.

### 5.4 Two display touch-ups

An extra `CALL $244F` at `2888` in the player-score display writer, and a
redundant `PUSH PSW / POP PSW` pair removed at `28AF`.

## 6. Step 3 — rev. 3 → rev. 4 (`27c128.ic19`, `supstarfa`)

The large one: +513 instructions, +1 162 bytes, 43 hunks, and the only step that
changes the NVRAM map (stack base `C7FF` → `C7CF`, freeing `C7D0`–`C7FF` for 21
new variables). This step is already documented in full in `game-rom-map.md`
§6.2–§6.8; it adds the coin-contact conditioner, the stuck-contact watchdog, ten
new operator zones (menu 9 → 19), the `3880`–`3B4D` code block, the new chime
ladder, and the `0xD0` checksum-correction byte at `3FFF`.

What this analysis adds is that **two of the fixes §6.2 and §6.3 attribute to
rev. 4 did not originate there**: the TRAP sentinel arrived in rev. 2 and the
bounded sender spin in rev. 3. Rev. 4 inherited both.

The other 34 hunks are pure insertions of the new material. The nine that edit
rev. 3's code in place are worth listing, because three of them are the clearest
directional evidence in the whole chain — a hardcoded constant becoming a
settings read:

| rev. 3 | rev. 4 | what |
|---|---|---|
| `033A` `JMP 032D` + 4 instrs | — | fault recovery replaced by the `C7FA`-gated version (§6.5) |
| `03D6` `CPI #05` | `CPI #00` | attract-loop compare |
| `0C54` `MVI A,#03` | `LDA $C7F5` | **zone 14** — diana completion score becomes adjustable |
| `0DB4` `JNZ 0DD6` | `JZ 0DEB / MVI A,#02 / STA C7F0 / JMP 0E0A` | collect-variant marker |
| `0EC8` 6 instrs | `NOP` | ball-end contact check removed |
| `1044` `MVI A,#01` | `LDA $C7F6` | **zone 15** — 100 PUNTOS lane score becomes adjustable |
| `172D` `CPI #02 / JNC` | 15 instrs comparing `C7F8` nibbles | **zone 16** — credit cap becomes adjustable |
| `3275`, `3392` `CPI #0A` | `CPI #1A` | the menu bound, 9 zones → 25 table entries |

Settings become constants only going backwards in time, which is why this step
cannot be read the other way round.

### The sound interface never changes

All four revisions send from **26 `STA $8000` sites** with the same sixteen
direct immediates (`00 11 41 69 90 96 A0 B0 B1 BB CC E0 E1 F0 F1 FF`) and the
same six control commands through the two senders (`77 88 99 AA DD EE`). Not one
sound-command immediate is altered anywhere in the chain; rev. 4's only change
is the chime *table*, which reorders existing commands. The 8035 sound board and
its 2532 therefore need not have changed, and pairing all four game ROMs with
the known-good `2532.ic4` (`D6D7EEE2`) is sound.

### Integrity

Neither new image carries a checksum byte — rev. 1 does not either; only rev. 4
does. Instead, both were classified byte by byte. Their unclassified residue is
**the same 28 ranges, at the same addresses, as rev. 1's**: the six NVRAM
pointer tables at `254D`–`259E`, the chime table `273F`, the carousel handlers
and jump table `2D00`–`309E`, the audit pointers `320D`, the zone jump table and
switch-test table `3490`–`34B8`, and the four known dead-code orphans. Nothing
in either image is unaccounted for, and no region decodes as garbage. The
playfield switch-test table

```
A5 06 08 03 09 07 A1 04 A7 A6 11 13 12 14 15 20 19 18 17 16 02 01 05 FF
```

is byte-identical in all four revisions — same machine, same wiring, firmware
revision only.

---

## 7. `m1-31_b_1704.ic32` is not a Super Star ROM

It is **Baby & Bombo**, a Recreativos Franco slot machine from 1987, and it is
already preserved: MAME's `bbombo` set in `src/mame/recfranco/rfslots8085.cpp`
carries this exact file under this exact name, with a matching CRC32 `A74A85B7`
and SHA-1 `f562495a…`.

The ROM's own code settles which board it runs on, independently of MAME's
filing. Tracing its 5 060 instructions and collecting every external address it
touches gives:

| region | refs | what MAME's `rf53_3297` map puts there |
|---|---|---|
| `8000`–`87FF` | 780 | battery-backed RAM (`SP` is initialised to `87FF`) |
| `9000`–`9001` | 6 | 8279 data / status–command |
| `AA00`–`AA05` | 28 | 8155 RAM-I/O-timer |
| `B000`–`B003` | 30 | 8255 PPI |

That is the Recreativos Franco **53/3297** board, exactly — and MAME's board
diagram for it shows an `M1-31/B-1704` ROM in socket IC32, which is this file's
name. The machine has coin hoppers and electromechanical reels.

Super Star's CPU board is **53/3291**. Its game ROM is at IC19, its RAM is at
`C000`–`C7FF`, it has no 8155 and no 8255, and it drives its 8279 serially
through the 8085's SOD/SID pins rather than through a memory-mapped port. None
of the addresses above appear anywhere in any Super Star revision, and none of
Super Star's appear in this ROM. Its reset sequence differs from the very first
instruction: Super Star opens `LXI SP,$C7FF / DI / LDA $C000 / XRI #55`, this
one opens `DI / MVI A,#1C / SIM / LXI SP,$87FF`.

It is a stray file in a Super Star collection archive, not a Super Star
variant. Nothing needs to be done with it — it is already dumped and emulated.

---

## 8. Consequences

### 8.1 Two ROM sets to add

Built into `../roms/`, each pairing the new game ROM with the verified sound ROM,
using the set names and internal filenames of the proposed PinMAME entries:

| set | file | CRC32 | SHA-1 |
|---|---|---|---|
| `supstarfb` — set B (rev. 3) | `super.dat` | `51697AFF` | `d10c6456716ca49cce590996e7271b8cd7026f38` |
| | `2532.ic4` | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |
| `supstarfc` — set C (rev. 2) | `27128Prg.bin` | `77C43E87` | `efdf60b53ac105985ca6d4eeb6ed48b893bb7ad8` |
| | `2532.ic4` | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

Both were verified byte for byte against those entries: exact filenames (the
capital `P` in `27128Prg.bin` included), sizes, CRC32s and SHA-1s, two files per
zip and no extras. `RFRANCO_ROMSTART` in `../pinmame/src/wpc/rfranco.h` loads
`0x4000` for the game ROM and `0x1000` for the sound ROM, which both sets supply.

Neither game ROM appears in PinMAME `master` (now at upstream `99d8c322`, which
already carries `src/wpc/rfranco.c`) nor in the MAME tree — both CRCs are absent
from both source trees. They are genuinely unpreserved.

### 8.2 `supstarfa`'s description is now wrong

PinMAME's `rfrancogames.c` calls `supstarfa` *"Super Star (rev. 2)"*. It is
rev. **4** of four. Its source comment also credits it with the sender's
`HLT` replacement and the TRAP sentinel; both belong to earlier revisions.

### 8.3 Nothing changes for the driver itself

All four revisions use the same hardware, the same NVRAM window, the same 26
sound-send sites and the same switch-test table. Revs. 2 and 3 need only
`RFRANCO_ROMSTART` entries and `CORE_CLONEDEFNV` lines; no driver code.

**Not yet done:** the two new images have not been booted under PinMAME. That
needs the two clone entries added to `rfrancogames.c` first, after which
`tools/rfranco_check.py` and `tools/rfranco_zones.py` can confirm they boot,
attract, and walk their nine-zone menu. The analysis above is entirely static.
