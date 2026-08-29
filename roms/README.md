# Super Star (Recreativos Franco, 1986) — ROM sets

Four complete, verified ROM sets built from the dumps in `../romdumps/`.
Set names follow the PinMAME driver, `src/wpc/rfrancogames.c`. The internal ROM
filenames follow MAME's `src/mame/pinball/supstarf.cpp`, so the two sets MAME
knows are interchangeable with MAME's.

**There are four firmware revisions, not two.** They form a single linear chain,
and MAME's two sets are its first and last links:

```
chronological  image             CRC32      set name    where
-------------  ----------------  --------   ---------   ---------------------------
rev. 1         m31-a-01187.ic19  AB8B1148   supstarf1   MAME parent (supstarf)
rev. 2         27128Prg.bin      77C43E87   supstarf2   NEW - formerly "set C"
rev. 3         super.dat         51697AFF   supstarf3   NEW - formerly "set B"
rev. 4         27c128.ic19       9A440461   supstarf4   MAME clone (supstarfa)
```

**The PinMAME set names are chronological.** They were not always: the two new
sets were first labelled "set B" and "set C", lettered before the order was known
and deliberately chosen so as not to imply one — set C is the earlier firmware of
the two. PinMAME now numbers all four in revision order, so those letters survive
only in older notes and in MAME, which still calls rev. 1 `supstarf` and rev. 4
`supstarfa`. The set names and the internal ROM filenames here match the PinMAME
driver entries exactly.

The ordering evidence, and what each revision changed, is in
`../docs/rom-revision-chain.md`. All four share the same sound ROM (§ Sound ROM).

## Contents

### `supstarf1.zip` — rev. 1

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `m31-a-01187.ic19` | 16384 | `AB8B1148` | `496d3c9664386ae64e94462db2fdd36811a68a87` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

Both files match MAME's `supstarf` definitions exactly.

### `supstarf2.zip` — rev. 2 (new; formerly "set C")

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `27128Prg.bin` | 16384 | `77C43E87` | `efdf60b53ac105985ca6d4eeb6ed48b893bb7ad8` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

Rev. 1 plus one change: the TRAP re-entrancy sentinel at the new NVRAM byte
`C089`. Not in MAME.

### `supstarf3.zip` — rev. 3 (new; formerly "set B")

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `super.dat` | 16384 | `51697AFF` | `d10c6456716ca49cce590996e7271b8cd7026f38` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

Set C plus the bounded sender spin that replaces `HLT`, the relocated TRAP
sentinel, and an explicit stack reset on the attract entry. Not in MAME.

### `supstarf4.zip` — rev. 4 (recommended)

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `27c128.ic19` | 16384 | `9A440461` | `e2f8dcf95084f755d3a34d77ba2649602687a610` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

The last of the four, and the most capable: 19 operator zones instead of 9, the
coin-contact conditioner and the stuck-contact watchdog. The game ROM matches
MAME's `supstarfa` exactly. **The sound ROM intentionally differs from MAME's
`supstarfa` entry**, which still carries a `BAD_DUMP` (`B6EF3C7A`). See "Sound
ROM" below — the good dump is provably the same data.

> MAME still labels this set *"Super Star (rev. 2)"*. With revs. 2 and 3 now
> dumped, that label is wrong: it is rev. 4, which is what PinMAME now calls it.

## Source archives

| Archive | Contents |
|---|---|
| `romdumps/start ranco ic19 128.rar` | rev. 1 game ROM (IC19) |
| `romdumps/super_start_franco2532.rar` | sound ROM (IC4), good dump |
| `romdumps/super star.zip` | rev. 4 game ROM + 16 sound-ROM dump attempts + `leer.txt` |
| `romdumps/super_star_setC.zip` | rev. 2 and rev. 3 game ROMs, plus copies of rev. 1 and rev. 4 and one stray ROM from an unrelated machine |
| `romdumps/super_star_rev3.zip` | rev. 3 game ROM (duplicate of the setC copy) |

`super_star_setC.zip` also contains `m1-31_b_1704.ic32`, which is **not a Super
Star ROM**: it is Recreativos Franco's *Baby & Bombo* slot machine (MAME
`bbombo`, board 53/3297), already preserved. See `../docs/rom-revision-chain.md`
§7.

## Verification performed

### Game ROMs — four genuinely different program revisions

The four IC19 images are separate firmware revisions, not variant dumps of one
chip. All four open with the same 8085 boot sequence — `LDA C000` / `XRI 55`,
probing the 5517 NVRAM at `0xC000` for a `0x55` magic byte, which corroborates
the documented `0xC000–0xC7FF` RAM window — but with different stack bases and
warm-boot vectors:

```
rev. 1: 31 FF C7  LXI SP,C7FF   ...  CA 86 01  JZ 0186
rev. 2: 31 FF C7  LXI SP,C7FF   ...  CA 86 01  JZ 0186
rev. 3: 31 FF C7  LXI SP,C7FF   ...  CA 8A 01  JZ 018A
rev. 4: 31 CF C7  LXI SP,C7CF   ...  CA 8A 01  JZ 018A
```

None is mirrored; all four 4 KB banks are distinct in every image.

Raw byte identity is misleading here — one inserted byte shifts every following
address operand — so the four were compared at the instruction level, with ROM-
and NVRAM-pointing operands abstracted. The hunk counts form an additive path
(rev1–rev2 = 8, rev2–rev3 = 9, rev3–rev4 = 43, and every skip distance is the sum
of the steps it spans), which is what fixes the order. Instruction counts grow
monotonically along it: 4 914 → 4 927 → 4 949 → 5 462.

Only rev. 4 carries a checksum-correction byte: the 8-bit sum of all 16384 bytes
is `0x00`, with `0xD0` at offset `0x3FFF`. The other three do not use that scheme.
Revs. 1 and 4 rest on their SHA-1 match with MAME; revs. 2 and 3 were instead
classified byte by byte, and their unclassified residue is the same 28 ranges, at
the same addresses, as rev. 1's — the known data tables and dead-code orphans,
nothing else.

Full ordering evidence and a per-revision changelog: `../docs/rom-revision-chain.md`.

### Sound ROM — one good image, three distinct failure modes

Of the 16 sound dumps in `super star.zip`, only **4 distinct images** exist.
Each fault was reproduced exactly, which is what establishes the good dump as
correct:

| Image | CRC32 | Copies | Diagnosis |
|---|---|---|---|
| good | `D6D7EEE2` | 6 + the standalone RAR | correct |
| `sonido` | `B6EF3C7A` | 1 | **D5 stuck high** — `sonido == (good \| 0x20)` byte-for-byte, all other 7 bits identical |
| `ss2532tmsSINadaptador` | `803985F9` | 2 | **A11 undriven** — both 2 KB halves identical, and equal to `good[0:2048]`. TMS2532 read on a 2732 profile without the pinout adapter |
| `ss19041932` family | `53A82675` | 5 | **A8 stuck high** — pages 0,2,4,6 return the contents of pages 1,3,5,7 |

(`ss19041932b`, CRC `53755A0D`, is the A8 fault plus two unstable bytes at
offsets `0x000`–`0x001` — an electrically marginal read; discarded.)

The good image was independently confirmed by six reads across five manufacturer
device profiles (Intel, Mitsubishi, National, Thomson, TMS), all byte-identical.

### Why all four sets get the same sound ROM

`sonido` — the 2014 dump taken alongside rev. 4's game ROM — reconstructs to the
good image *exactly* by clearing bit 5:

```python
bytes(b | 0x20 for b in good) == sonido   # True, all 4096 bytes
```

A single stuck data line over otherwise perfect data proves the physical 2532 in
that machine held the same contents as the good dump. So revs. 1 and 4
legitimately share sound ROM `D6D7EEE2`, and MAME's `BAD_DUMP` flag on
`supstarfa` can be retired.

No sound ROM was dumped alongside revs. 2 and 3, so their pairing rests on the
game ROMs' side of the interface, which does not change: all four revisions send
from **26 `STA $8000` sites** with the same sixteen direct immediates
(`00 11 41 69 90 96 A0 B0 B1 BB CC E0 E1 F0 F1 FF`) and the same six control
commands through the two senders (`77 88 99 AA DD EE`). Not one sound-command
immediate differs anywhere in the chain. Rev. 4's only change is the chime
*table* at `273F` (`10 10 30 40 50 60` → `10 10 E0 90 A0 60`), which reorders
commands the sound ROM already implements. The 8035 board and its 2532 need not
have changed across any of the four.

> Note on bit numbering: MAME's source comment reads *"D6 stuck high and probably
> totally garbage."* The affected line carries mask `0x20`, which is D5 in D0–D7
> numbering and D6 in the older TI D1–D8 numbering — the same physical pin either
> way. The dump is also not "garbage": it is a clean single-bit-line fault.

### `leer.txt`

```
cpu 27c128 y chesun cc00.
sonido 2532 y chesun 5c56.
```

*chesun* = "checksum". The `cc00` figure matches set 2's game ROM (16-bit sum
`0xCC00`). **The `5c56` figure documents the faulty `sonido` dump** — the good
sound ROM sums to `0xD9D6`. Do not use `leer.txt` to validate the sound ROM.

## Sound ROM content note

Offsets `0x800–0xFFF` contain only four distinct byte values (`0x00`, `0x20`,
`0xA0`, `0xA7`). This is genuine, not a dump artifact — the good image's two 2 KB
halves differ, which proves A11 was driven. Purpose not yet determined.

## Reproducing this build

```bash
cd romdumps
unrar x "start ranco ic19 128.rar" && unrar x super_start_franco2532.rar
unzip "super star.zip"
unzip -j super_star_setC.zip 27128Prg.bin super.dat -d setC

mkdir -p supstarf1 supstarf2 supstarf3 supstarf4
cp "start ranco ic19 128.BIN"   supstarf1/m31-a-01187.ic19
cp super_start_franco2532.BIN   supstarf1/2532.ic4
cp setC/27128Prg.bin            supstarf2/27128Prg.bin
cp super_start_franco2532.BIN   supstarf2/2532.ic4
cp setC/super.dat               supstarf3/super.dat
cp super_start_franco2532.BIN   supstarf3/2532.ic4
cp "super star/super"           supstarf4/27c128.ic19
cp super_start_franco2532.BIN   supstarf4/2532.ic4

(cd supstarf1 && zip -X -9 ../supstarf1.zip m31-a-01187.ic19 2532.ic4)
(cd supstarf2 && zip -X -9 ../supstarf2.zip 27128Prg.bin     2532.ic4)
(cd supstarf3 && zip -X -9 ../supstarf3.zip super.dat        2532.ic4)
(cd supstarf4 && zip -X -9 ../supstarf4.zip 27c128.ic19      2532.ic4)
```

The two new sets keep their dump filenames verbatim — `super.dat` and
`27128Prg.bin`, including the capital `P` — because that is what the PinMAME
driver entries name. The older two keep their socket-suffixed names. Both new
names are distinct from `supstarf4`'s `27c128.ic19`, so a missing file cannot
silently fall back to another set's image.

`RFRANCO_ROMSTART` (`src/wpc/rfranco.h`) loads the first file at `0x0000` for
`0x4000` bytes and the second at `0x0000` for `0x1000`, which is what all four
sets provide.

## Hardware reference

From the machine manual (`../super-star-pinball-manual.md`, CPU board 53/3291)
and MAME's driver:

| Function | Part | Socket |
|---|---|---|
| Main CPU | Intel 8085A @ 5.0688 MHz (X1) | IC9 |
| Game ROM | 27128, 16 KB → `0x0000–0x3FFF` | **IC19** |
| Second game ROM | — unpopulated | IC14 |
| NVRAM | 5517 2K×8, battery-backed → `0xC000–0xC7FF` | IC11 |
| Sound CPU | Intel 8035 @ XTAL/2 (8085 CLK OUT, pin 37) | IC7 |
| Sound ROM | 2532, 4 KB → `0x000–0xFFF` | **IC4** |
| Sound generators | 2× AY-3-8910 @ XTAL/6 (8035 T0, pin 1) | IC2, IC3 |
| CPU↔sound latches | 4× Intel 8212 | IC1, IC5, IC6, IC10 |
| Audio amp | LM380 | IC20 |

The manual's component list resolves MAME's open question about "IC7": IC7 is the
**8035 sound CPU**, and IC4 is the 2532 sound ROM — MAME's socket labelling is
correct.
