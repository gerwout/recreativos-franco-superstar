# Super Star (Recreativos Franco, 1986)

Reverse engineering tools and documentation for the Recreativos Franco
*Super Star* pinball machine — and the home of the analysis behind its PinMAME
driver. The driver is upstream: `src/wpc/rfranco.c` in
[`vpinball/pinmame`](https://github.com/vpinball/pinmame), with sets `supstarf`
and `supstarfa`.

The machine: Intel 8085A game CPU, an Intel 8035 sound CPU driving two
AY-3-8910s, four CD4028 decoders multiplexing lamps and coils over the two
mains phases, and serial I/O for everything — the switches arrive one bit at a
time on the 8085's SID pin. Both ROMs are mapped byte by byte with nothing
unexplained; see `docs/`.

## Contents

| Path | What it is |
|---|---|
| `docs/vpx-table-reference.md` | For Visual Pinball table authors: switches, lamps, solenoids, display, operator menus, pitfalls. Also in Spanish: `vpx-table-reference.es.md` |
| `docs/hardware-findings.md` | The full hardware analysis and its audit trail |
| `docs/game-rom-map.md`, `docs/sound-rom-map.md` | Every byte of both ROMs classified: code, tables, dead code, filler |
| `docs/rom-revision-chain.md` | The four game-ROM revisions: what each changed, and the evidence for their order |
| `docs/rom-provenance.md` | Where every dump came from, and the sound ROM's three reproduced failure modes |
| `docs/driver-notes.md` | For PinMAME reviewers: the driver's architecture and the 8085 core fixes it needed |
| `docs/pinmame-keyboard-reference.md` | Which key closes which switch in standalone PinMAME |
| `docs/questions-for-a-real-machine.md` | The few things only a physical board can settle |
| `docs/upstream-prs.md` | How the PinMAME work is split into branches, and in what order to merge them |
| `roms/` | All four ROM sets, PinMAME/MAME-compatible zips with hashes |
| `tools/rfranco_*.py` | The regression harnesses that keep the driver honest |
| `tools/dis85.py`, `tools/rom_diff.py` | 8085 disassembler/tracer, and the instruction-level ROM comparison behind the revision chain |
| `super-star-pinball-manual.md` / `.pdf` | The factory manual — transcription and original scan |
| `ghidra/` | Disassembly project and export scripts |

## The four ROM revisions — use `supstarfa`

There are **four** firmware revisions, not two. They form a single linear chain,
and the two sets MAME has are its first and last links; two more were dumped
later and sit in between. The PinMAME set letters are deliberately *not*
chronological — they were assigned before the order was known:

| chronological | image | CRC32 | set |
|---|---|---|---|
| rev. 1 | `m31-a-01187.ic19` | `AB8B1148` | `supstarf` |
| rev. 2 | `27128Prg.bin` | `77C43E87` | `supstarfc` ("set C") |
| rev. 3 | `super.dat` | `51697AFF` | `supstarfb` ("set B") |
| rev. 4 | `27c128.ic19` | `9A440461` | `supstarfa` |

**`supstarfa.zip` is still the preferred set.** It is the last of the four, and
the difference is not cosmetic: reverse engineering rev. 1 turned up real defects
that later revisions demonstrably fix. What each one added:

* **rev. 2 — a TRAP re-entrancy guard.** A sentinel at the new NVRAM byte `C089`
  so the 100 Hz mains-zero-cross handler cannot re-enter itself. Rev. 1 has none.
* **rev. 3 — the inter-CPU wake race.** Rev. 1 and 2 send a sound command and
  then `HLT` waiting for the reply interrupt; a reply landing in the
  two-instruction gap before the halt leaves the CPU halted until something else
  wakes it. Rev. 3 replaces the `HLT` with a bounded polling spin — the factory
  evidently met this on hardware. It also adds an explicit stack reset on the
  attract entry.
* **rev. 4 — stuck-contact protection.** A welded or jammed contact on the
  bumpers, the 10-puntos slingshots or the picabolas scores forever on the first
  three. Rev. 4 adds a watchdog that faults the machine after ~128 consecutive
  game-loop passes with the contact closed (operator zone 18 can disable it).
* **rev. 4 — coin-contact conditioning.** Debounce state for the coin switches
  that the earlier three lack.

Rev. 4 also extends the operator menu from 9 to 19 adjustment zones and changes
two defaults in play (the 100-puntos lane pays 1 000 instead of 100, and a
completed target bank lights the bumpers for 10 000). Revs. 1–3 all have the nine
zones the factory manual documents.

The ordering evidence and a per-revision changelog are in
`docs/rom-revision-chain.md`; `tools/rom_diff.py` regenerates all of it.

One bug is in the **sound ROM shared by both revisions** and is emulated
faithfully: the ball-start handler queues three musical phrases but plays only
the first, because the tune terminator wipes the stack pointer — confirmed
against a recording of a real machine (`docs/sound-rom-map.md` §6).

## Status

`supstarf` and `supstarfa` are fully playable in PinMAME and marked working —
coins, a complete multi-player game, specials, replay and knocker, bonus,
operator menus, sound. Every claim in the docs is labelled measured or inferred;
the one remaining inference in the driver (which physical coil sits on the
replay output) is documented in `docs/questions-for-a-real-machine.md`.

`supstarfb` and `supstarfc` are built in `roms/` and analysed in full, but have
**not** been run yet: the driver has no entries for them. Adding two
`RFRANCO_ROMSTART` + `CORE_CLONEDEFNV` blocks to `src/wpc/rfrancogames.c` is all
they need — no driver code, since all four revisions share the same hardware,
NVRAM window, sound interface and switch wiring. Everything in
`docs/rom-revision-chain.md` is static analysis until that happens.
