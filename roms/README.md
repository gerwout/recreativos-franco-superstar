# Super Star (Recreativos Franco, 1986) — ROM sets

Two complete, verified ROM sets built from the dumps in `../romdumps/`.
File names and set names follow MAME's `src/mame/pinball/supstarf.cpp` so the sets
are interchangeable with MAME's.

## Contents

### `supstarf.zip` — set 1 (recommended)

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `m31-a-01187.ic19` | 16384 | `AB8B1148` | `496d3c9664386ae64e94462db2fdd36811a68a87` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

Both files match MAME's `supstarf` definitions exactly.

### `supstarfa.zip` — set 2

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `27c128.ic19` | 16384 | `9A440461` | `e2f8dcf95084f755d3a34d77ba2649602687a610` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

The game ROM matches MAME's `supstarfa` exactly. **The sound ROM intentionally
differs from MAME's `supstarfa` entry**, which still carries a `BAD_DUMP`
(`B6EF3C7A`). See "Sound ROM" below — the good dump is provably the same data.

## Source archives

| Archive | Contents |
|---|---|
| `romdumps/start ranco ic19 128.rar` | set 1 game ROM (IC19) |
| `romdumps/super_start_franco2532.rar` | sound ROM (IC4), good dump |
| `romdumps/super star.zip` | set 2 game ROM + 16 sound-ROM dump attempts + `leer.txt` |

## Verification performed

### Game ROMs — two genuinely different program revisions

The two IC19 images differ in **9819 of 16384 bytes (59.9%)**. They are not
variant dumps of one chip; they are separate revisions. Both open with the same
8085 boot sequence but with different stack pointers and warm-boot vectors:

```
set 1: 31 FF C7  LXI SP,C7FF   ...  CA 86 01  JZ 0186
set 2: 31 CF C7  LXI SP,C7CF   ...  CA 8A 01  JZ 018A
```

Both then do `LDA C000` / `XRI 55` — probing the 5517 NVRAM at `0xC000` for a
`0x55` magic byte, which corroborates the documented `0xC000–0xC7FF` RAM window.

Neither ROM is mirrored; all four 4 KB banks are distinct in both.

Set 2 carries a checksum-correction byte: the 8-bit sum of all 16384 bytes is
`0x00`, with `0xD0` at offset `0x3FFF`. Set 1 does **not** use this scheme (8-bit
sum `0x02`, last byte `0xFF`), so its integrity rests on the SHA-1 match with
MAME rather than on a self-check.

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

### Why set 2 gets the good sound ROM

`sonido` — the 2014 dump taken alongside set 2's game ROM — reconstructs to the
good image *exactly* by clearing bit 5:

```python
bytes(b | 0x20 for b in good) == sonido   # True, all 4096 bytes
```

A single stuck data line over otherwise perfect data proves the physical 2532 in
that machine held the same contents as the good dump. So both sets legitimately
share sound ROM `D6D7EEE2`, and MAME's `BAD_DUMP` flag on `supstarfa` can be
retired.

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

mkdir -p supstarf supstarfa
cp "start ranco ic19 128.BIN"   supstarf/m31-a-01187.ic19
cp super_start_franco2532.BIN   supstarf/2532.ic4
cp "super star/super"           supstarfa/27c128.ic19
cp super_start_franco2532.BIN   supstarfa/2532.ic4

(cd supstarf  && zip -X -9 ../supstarf.zip  m31-a-01187.ic19 2532.ic4)
(cd supstarfa && zip -X -9 ../supstarfa.zip 27c128.ic19 2532.ic4)
```

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
