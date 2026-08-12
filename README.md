# Super Star (Recreativos Franco, 1986)

Reverse engineering tools and documentation for the Recreativos Franco
*Super Star* pinball machine — and the home of the analysis behind its PinMAME
driver (`supstarf` / `supstarfa`, in the
[`feature/superstar-recreativos-franco`](https://github.com/gerwout/pinmame/tree/feature/superstar-recreativos-franco)
branch of the PinMAME fork).

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
| `docs/driver-notes.md` | For PinMAME reviewers: the driver's architecture and the 8085 core fixes it needed |
| `docs/pinmame-keyboard-reference.md` | Which key closes which switch in standalone PinMAME |
| `docs/questions-for-a-real-machine.md` | The few things only a physical board can settle |
| `roms/` | Both ROM sets, PinMAME/MAME-compatible zips with hashes |
| `tools/` | The regression harnesses that keep the driver honest |
| `super-star-pinball-manual.md` / `.pdf` | The factory manual — transcription and original scan |
| `ghidra/` | Disassembly project and export scripts |

## The two ROM revisions — use rev. 2

**`supstarfa.zip` — "Super Star (rev. 2)" — is the preferred set.** It is the
newer firmware, and the difference is not cosmetic: reverse engineering rev. 1
turned up real defects that rev. 2 demonstrably fixes.

Bugs identified in rev. 1 (`supstarf.zip`):

* **An inter-CPU wake race.** Rev. 1 sends a sound command and then `HLT`s
  waiting for the reply interrupt; a reply landing in the two-instruction gap
  before the halt leaves the CPU halted until something else wakes it. Rev. 2
  replaces the `HLT` with a bounded polling spin — the factory evidently met
  this on hardware.
* **No stuck-contact protection.** A welded or jammed contact on the bumpers,
  the 10-puntos slingshots or the picabolas scores forever on rev. 1. Rev. 2
  adds a watchdog that faults the machine after ~128 consecutive game-loop
  passes with the contact closed (operator zone 18 can disable it).
* **No TRAP re-entrancy guard.** Rev. 2 adds a sentinel so the 100 Hz
  mains-zero-cross handler cannot re-enter itself.
* **No coin-contact conditioning.** Rev. 2 adds debounce state for the coin
  switches that rev. 1 lacks.

Rev. 2 also extends the operator menu from 9 to 19 adjustment zones and changes
two defaults in play (the 100-puntos lane pays 1 000 instead of 100, and a
completed target bank lights the bumpers for 10 000). Rev. 1 remains the
revision the factory manual documents.

One bug is in the **sound ROM shared by both revisions** and is emulated
faithfully: the ball-start handler queues three musical phrases but plays only
the first, because the tune terminator wipes the stack pointer — confirmed
against a recording of a real machine (`docs/sound-rom-map.md` §6).

## Status

Both sets are fully playable in PinMAME and marked working — coins, a complete
multi-player game, specials, replay and knocker, bonus, operator menus, sound.
Every claim in the docs is labelled measured or inferred; the one remaining
inference in the driver (which physical coil sits on the replay output) is
documented in `docs/questions-for-a-real-machine.md`.
