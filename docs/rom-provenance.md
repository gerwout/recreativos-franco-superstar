# ROM sets and provenance — Super Star (Recreativos Franco, 1986)

Two complete, verified sets. File names and set names follow MAME's
`src/mame/pinball/supstarf.cpp` so the sets are interchangeable with MAME's.

Built sets live in `../roms/`; the source dumps in `../romdumps/`. The build
recipe is in `../roms/README.md`.

> **Superseded in part.** Two further IC19 revisions have since been dumped
> (`77C43E87` and `51697AFF`, from `romdumps/super_star_setC.zip` and
> `romdumps/super_star_rev3.zip`). There are **four** firmware revisions, and the
> two documented here are the first and the last of the chain — so "set 2" below
> is rev. **4**, not rev. 2. Everything this document says about those two images
> and about the sound ROM still holds; the ordering claim in §2 is still correct
> as far as it goes. See `rom-revision-chain.md` for the full four-way analysis.

---

## 1. The two sets

### `supstarf` — set 1 (MAME parent)

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `m31-a-01187.ic19` | 16384 | `AB8B1148` | `496d3c9664386ae64e94462db2fdd36811a68a87` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

Both files match MAME's `supstarf` definitions exactly.

### `supstarfa` — set 2 (MAME clone)

| File | Size | CRC32 | SHA-1 |
|---|---|---|---|
| `27c128.ic19` | 16384 | `9A440461` | `e2f8dcf95084f755d3a34d77ba2649602687a610` |
| `2532.ic4` | 4096 | `D6D7EEE2` | `60e497c8845320eea01662d894d0b16349ebb7e4` |

The game ROM matches MAME's `supstarfa` exactly. **The sound ROM deliberately
differs from MAME's `supstarfa` entry**, which still carries a `BAD_DUMP`
(`B6EF3C7A`). See §3.

---

## 2. Set 2 is the newer firmware

MAME's parent/clone ordering is not chronological. **Set 2 (`9A440461`) is the
later revision.**

| | set 1 `AB8B1148` | set 2 `9A440461` |
|---|---|---|
| MAME set | `supstarf` (parent) | `supstarfa` (clone) |
| chip label | `m31-a-01187` (factory part number) | `27c128` (generic) |
| operator adjustment zones | **9** | **19** (a 25-entry jump table, six of whose entries are unreachable) |
| bytes used | 12 199 | 13 096 (+897) |
| stack base | `C7FF` | `C7CF` (0x30 more NVRAM reserved) |
| NVRAM references in `C7xx` | 1 (the `LXI SP` operand) | 22, across 79 instructions |
| 8-bit checksum byte | none (whole-ROM sum `0x02`) | yes — `0xD0` at `0x3FFF`, sum `0x00` |

Decisive evidence:

* The adjustment menu is a computed jump through a table indexed by `(C01D-1)`.
  Set 1 range-checks `CPI $0A` against a 9-entry table at `3490`–`34A1`; set 2
  checks `CPI $1A` against a 25-entry table at `349D`–`34CE`. **Set 2's first nine
  targets are set 1's nine, in the same order, uniformly +0x2D.** Entries 10–15
  are filler pointing at zone 9's handler; 16–25 are new handlers at `3971`–`3A23`,
  living in what is `0xFF` fill in set 1.

  Note the table's size overstates the menu. `C01D` is BCD and `33DD` steps it
  `0x09 → 0x0A → 0x10`, so the six filler entries can never be selected and the
  menu is **nineteen zones**, shown as 1–9 and 10–19. Walking it on the running
  machine (`tools/rfranco_zones.py`) confirms it: set 1 reaches 1–9 and set 2
  reaches 1–9 and 10–19, then wraps.
* Set 2 adds a remap trampoline at `33DD`: on reaching zone `0x0A` it forces
  `C01D = 0x10`. Extending a menu produces that; stripping one does not.
* 99.6% of set 1's 4733 instructions align into set 2 as pure insertions
  (452 inserted, 7 removed — both removals are dead code or a refactor). None of
  set 1's 134 call targets is absent from set 2; set 2 adds 6.
* **The factory manual documents exactly 9 zones**, so the manual describes set 1.

Neither ROM contains any ASCII text, version string or date (checked against raw,
high-bit-stripped and XOR `0x20`/`0x40`/`0x80`/`0xFF` interpretations).

The playfield switch-test table is byte-identical in both revisions:

```
A5 06 08 03 09 07 A1 04 A7 A6 11 13 12 14 15 20 19 18 17 16 02 01 05 FF
```

Same machine, same wiring; firmware revision only. (The 24 entries are the eight
`0x4000` contacts followed by the sixteen serial-chain positions, holding the
manual's contact number in BCD. Bit 7 marks the four contacts that are wired in
parallel with another one, which is why the manual's contacts 10, 22, 23 and 24
never appear in the test on their own. The last entry, `FF`, is IC5's floating
serial input.)

**Consequence for the driver:** develop against **set 1**, because the manual
documents its 9-zone behaviour and that is what can be validated without
hardware. Keep MAME's set names for interoperability.

---

## 3. The sound ROM: one good image, three reproduced faults

Sixteen dumps of the 2532 exist across the source archives, but only **four
distinct images**. Every fault was reproduced exactly against the good image,
which is what establishes the good image as correct.

| Image | CRC32 | Copies | Diagnosis |
|---|---|---|---|
| good | `D6D7EEE2` | 6 + a standalone RAR | correct |
| `sonido` | `B6EF3C7A` | 1 | **D5 stuck high** — `sonido == (good \| 0x20)` byte for byte; all other seven bits identical |
| `ss2532tmsSINadaptador` | `803985F9` | 2 | **A11 undriven** — both 2 KB halves identical, and equal to `good[0:2048]`. A TMS2532 read on a 2732 profile without the pinout adapter |
| `ss19041932` family | `53A82675` | 5 | **A8 stuck high** — pages 0, 2, 4, 6 return the contents of pages 1, 3, 5, 7 |

`ss19041932b` (CRC `53755A0D`) is the A8 fault plus two unstable bytes at offsets
`0x000`–`0x001` — an electrically marginal read; discarded.

The good image was independently confirmed by six reads across five manufacturer
device profiles (Intel, Mitsubishi, National, Thomson, TMS), all byte-identical.
That is also what proves the bit-reversed data bus (see `driver-notes.md` §4) is
board wiring rather than a dumping artefact.

### 3.1 MAME's `supstarfa` BAD_DUMP flag can be retired

`sonido` is the 2014 dump taken alongside set 2's game ROM, and it reconstructs to
the good image **exactly** by clearing bit 5:

```python
bytes(b | 0x20 for b in good) == sonido    # True, all 4096 bytes
```

A single stuck data line over otherwise perfect data proves the physical 2532 in
that machine held the same contents as the good dump. Both sets therefore
legitimately share sound ROM `D6D7EEE2`, and MAME's

```
ROM_LOAD("2532.ic4", 0x0000, 0x1000, BAD_DUMP CRC(b6ef3c7a) SHA1(aabb6f8569685fc3a917a7bb5ebfcc4b20086b15))
```

can be replaced with set 1's good hash. This closes a documented bad dump with six
independent corroborating reads.

Two corrections to MAME's comment on that line while anyone is in there:

* It reads *"D6 stuck high and probably totally garbage."* The affected line
  carries mask `0x20`, which is D5 in D0–D7 numbering and D6 in the older TI
  D1–D8 numbering — the same physical pin either way, so the comment is not wrong,
  just ambiguous.
* It is **not** "totally garbage". It is a clean single-bit-line fault over
  otherwise perfect data, which is precisely why it reconstructs exactly.

### 3.2 `leer.txt`

The 2014 notes file in the set-2 archive reads:

```
cpu 27c128 y chesun cc00.
sonido 2532 y chesun 5c56.
```

*chesun* = "checksum". `cc00` matches set 2's game ROM (16-bit sum `0xCC00`).
**`5c56` documents the faulty `sonido` dump** — the good sound ROM sums to
`0xD9D6`. Do not use `leer.txt` to validate the sound ROM.

### 3.3 A note on the upper 2 KB

Offsets `0x800`–`0xFFF` of the sound ROM contain only four distinct byte values
(`0x00`, `0x20`, `0xA0`, `0xA7`). This is genuine rather than a dump artefact: the
good image's two 2 KB halves differ, which proves A11 was driven. Purpose not
determined — plausibly a waveform or duration table. It is unaffected by the
bit-reversal question either way, since the driver reverses the whole 4 KB region.

---

## 4. Game ROM integrity

The two IC19 images differ in **9819 of 16384 bytes (59.9%)**. They are two
separate revisions, not variant dumps of one chip. Both open with the same 8085
boot sequence but with different stack pointers and warm-boot vectors:

```
set 1: 31 FF C7  LXI SP,C7FF   ...  CA 86 01  JZ 0186
set 2: 31 CF C7  LXI SP,C7CF   ...  CA 8A 01  JZ 018A
```

Both then do `LDA C000` / `XRI 55`, probing the 5517 NVRAM at `0xC000` for a
`0x55` magic byte, which corroborates the documented `0xC000`–`0xC7FF` RAM window.

Neither ROM is mirrored; all four 4 KB banks are distinct in both.

Set 2 carries a checksum-correction byte: the 8-bit sum of all 16384 bytes is
`0x00`, with `0xD0` at offset `0x3FFF`. Set 1 does not use that scheme (8-bit sum
`0x02`, last byte `0xFF`), so its integrity rests on the SHA-1 match with MAME
rather than on a self-check.

---

## 5. Board reference (from the manual's component lists)

The manual settles two of MAME's open questions: the display controller is an
**8279**, not an "i8259" as MAME's TODO guesses, and **IC7 is the 8035 sound CPU**
while IC4 is its 2532 — MAME's socket labelling is correct.

| Function | Part | Socket |
|---|---|---|
| Main CPU | Intel 8085A @ 5.0688 MHz (X1) | IC9 |
| Game ROM | 27128, 16 KB → `0x0000`–`0x3FFF` | **IC19** |
| Second game ROM socket | — unpopulated | IC14 |
| NVRAM | 5517 2K×8, battery-backed → `0xC000`–`0xC7FF` | IC11 |
| Sound CPU | Intel 8035 @ XTAL/2 (8085 CLK OUT, pin 37) | IC7 |
| Sound ROM | 2532, 4 KB → `0x000`–`0xFFF`, bit-reversed data bus | **IC4** |
| Sound generators | 2 × AY-3-8910 @ XTAL/6 (8035 T0, pin 1) | IC2 (PSG2, inputs), IC3 (PSG1, outputs) |
| CPU ↔ sound latches | 4 × Intel 8212 | IC1, IC5, IC6, IC10 |
| Audio amp | LM380 | IC20 |
| Display controller | Intel 8279 | display board IC2 |
| Display serial input | 74164 | display board IC1 |
| Digit select / segments | 74159 + 2 × 7447 | display board IC6 / IC5, IC7 |
| Lamp & coil decoders | 4 × CD4028 | driver board IC1, IC2, IC3, IC7 |
| Switch shift registers | 2 × 74165 | driver board IC5, IC6 |
