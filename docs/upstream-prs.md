# Upstream pull requests

The Super Star work is split into three branches in the `pinmame` checkout, one
per subsystem, each a separate PR against `vpinball/pinmame`. Every original
commit message is preserved: each branch is a single squashed commit whose body
carries the messages of the commits that touched that subsystem, oldest first.

The harness (`tools/rfranco_*.py`) and the documentation live in *this* repo,
not in PinMAME, so none of it is part of these PRs.

## Merge order

| # | Branch | Depends on |
|---|---|---|
| 1 | `feature/i8085-core-fixes` | nothing — **merge this first** |
| 2 | `feature/remote-debug-improvements` | nothing — independent, any time |
| 3 | `feature/rfranco-superstar-driver` | **#1** |

**Only 1 → 3 is a hard dependency, and it is a compile error rather than a
subtlety.** Verified by building each branch on its own: #1 and #2 build clean,
#3 alone fails with

```
src/wpc/rfranco.c:347:5: error: implicit declaration of function
'i8085_set_SID_callback'; did you mean 'i8085_set_SOD_callback'?
```

because the driver installs a SID callback that #1 adds. Merging #1 into #3
resolves it with no conflicts, builds clean, and passes the harness on both ROM
sets. #2 is independent of both and can go in at any point.

One testing-only note: `tools/rfranco_mech.py` drives `/api/mechanics`, which
#2 adds. The driver works without #2; only that one harness needs it.

Two commits touched two subsystems each (`422ec00d`, which carried both an 8085
fix and the driver's introduction, and `64dfb400`, whose `/api/mechanics`
endpoint is separable from its driver changes). Their full original messages are
kept on both branches, each marked with a note saying so.

---

## PR 1 — 8085A core

**Branch:** `feature/i8085-core-fixes` → base `master`

**Title:**

```
i8085: fix RIM/SIM, the EI delay, TRAP re-arming and callback loss
```

**Body:**

```markdown
Five defects in the 8085A core, all found while bringing up a driver that drives
its display and reads its switches through the serial pins. None of the fixes is
specific to that machine.

- **RIM returned `I.IM` raw.** That register holds the masks and IE in the
  positions the RIM byte expects, but `IM_TRAP` (0x10) sat where the RST5.5
  pending flag belongs and `IM_SOD` (0x40) where RST7.5 pending belongs, and SID
  was only ever reported if a driver had pushed a value in beforehand. The byte
  is now composed properly.
- **SIM ignored bit 4 (R7.5).** RST7.5 is edge triggered and latches, so unlike
  RST5.5/6.5 it is never cleared by the line going low — only by SIM or by the
  interrupt being taken. Without handling bit 4 the latch sticks and the handler
  re-enters forever.
- **`i8085_reset()` wiped the callbacks.** It memsets the whole register struct,
  which dropped the irq, sod and sid callbacks a driver installs at init. Those
  are wiring, not CPU state.
- **EI took effect immediately.** On real hardware an interrupt is not
  recognised until the instruction after EI has completed, and service routines
  rely on it: an ISR ending `EI / POP PSW / RET` needs the POP to run first or
  the frame is left half unwound.
- **TRAP could only ever fire once.** `i8085_set_TRAP()` gated on `I.ISRV`, an
  "in service" lock that only EI clears — but a TRAP handler is free to run with
  interrupts disabled and simply RET. The lock then stayed set forever, blocking
  not just further TRAPs but RST5.5/6.5/7.5 as well. It now gates on the pending
  flag, which `Interrupt()` clears as it takes the interrupt, so a new edge
  re-arms while a second edge arriving before the first is taken is still
  ignored.

Adds `i8085_set_SID_callback()` so hardware that clocks serial data in is
sampled at the moment RIM executes rather than ahead of time.
`i8085_set_SID()` still works for drivers that prefer to push.

### Risk to existing drivers

This core is not unused, and these changes are not free of consequence for the
two drivers already on it:

- `src/wpc/regama.c` (Regama Trebol, added 2020) instantiates an `8085A` and
  drives **both** serial pins — `i8085_set_SID()` for the battery-good line and
  `i8085_set_SOD_callback()`.
- `src/wpc/micropin.c` has an `8085A` machine.

The RIM composition change, the EI delay, the TRAP re-arm and the callback
preservation all apply to them. I have no ROMs for either and could not test
them; a smoke test from someone who has would be worth having before this is
merged.

### Testing

Builds clean. Exercised continuously by the Super Star driver (PR 3), which
reaches the CPU through SID, SOD, TRAP and RST6.5 — its harness covers boot,
a full game, the sound protocol, the front-end mechanics handover and a
six-game soak, and passes on both ROM sets.
```

---

## PR 2 — remote debug API

**Branch:** `feature/remote-debug-improvements` → base `master`

**Title:**

```
remote_debug: filter by CPU, expose the mechanics flag, fix column 0 names
```

**Body:**

```markdown
Three independent improvements to the remote debug API. No emulation behaviour
changes.

- **Per-CPU filtering for breakpoints, instrumentation points and tracepoints.**
  The per-instruction hook read `activecpu_get_reg(REG_PC)` with no idea which
  processor was running, so on a multi-CPU board any point below the smaller
  CPU's ROM size counted hits from both. On the board this was found on, that
  made every measurement of the main CPU's low addresses meaningless — `0x0286`
  is an error path in the game ROM and a `MOV` inside a live voice routine in
  the sound ROM. All three point types now carry an optional `cpu` field,
  exposed as `&cpu=N` on the endpoints and reported back in the JSON. Omitted,
  it keeps the old any-CPU behaviour.
- **`/api/mechanics`** reads and sets `g_fHandleMechanics`. The standalone build
  pins the flag at `0xff` with no route to change it, which leaves the
  front-end-owned ball path untestable in any driver that has one.
- **`switch_name()` no longer mislabels column 0.** It gave switches 1–8 the WPC
  coin-door names ("Coin 1".."Escape") whatever the game. Column 0 is the coin
  door on WPC and whatever its driver makes it elsewhere, so the table is now
  gated on `GEN_ALLWPC` and otherwise falls through to the empty name that the
  rest of such a driver's switches already report.

### Testing

Builds clean on its own. The endpoints are driven continuously by the Super Star
harness; the CPU filtering and `/api/mechanics` are what make its instruction
counting and its mechanics test possible at all.
```

---

## PR 3 — Recreativos Franco driver

**Branch:** `feature/rfranco-superstar-driver` → base `master`
**Requires PR 1 to be merged first** (compile error otherwise, see above).

**Title:**

```
rfranco: new driver for Recreativos Franco Super Star (1986)
```

**Body:**

```markdown
A new driver for Recreativos Franco's *Super Star* (Spain, 1986), with two ROM
sets — `supstarf` (rev. 1, the revision the factory manual documents) and
`supstarfa` (rev. 2, newer firmware).

**This needs the 8085A core fixes in #<PR 1> and will not compile without
them:** the driver installs a SID callback via `i8085_set_SID_callback()`, and
at run time it depends on TRAP re-arming and on the one-instruction EI delay.

### The hardware

8085A main CPU with a 27128 at IC19 and 5517 battery-backed RAM at IC11, plus an
8035 sound CPU with a 2532 at IC4 driving two AY-3-8910s. Four 8212s carry the
command path between the two processors. The I/O is serial throughout: the
display chain hangs off SOD, the playfield switches are clocked back in through
SID, and any OUT instruction is the shared shift clock.

Two details worth knowing:

- TRAP carries the mains zero cross and is load bearing at boot. The reset path
  tests an NVRAM magic byte and RSTs back to `0000` when it fails, and it is the
  TRAP handler that seeds the magic — so without TRAP re-arming the machine
  never comes up at all.
- The 2532's data pins are wired to the 8035's AD0–AD7 in reverse order, so the
  sound image is bit-reversed at init. Straight off the chip it has 5 RET
  opcodes in 2K and no jump at either vector; reversed it has 172 JMP, 88 CALL,
  28 RET and the expected vector layout.

### State

Both sets are playable. A coin gives a credit, the start button serves a ball,
playfield contacts score, the drop-target banks light their specials, collecting
one awards a replay, each ball ends into the next with its bonus paid, and the
last ball ends the game with the final score held. Lamps, coils and the two
mains phases follow the ROM's own tables, and all four operator door modes work.

The two operator door switches are modelled as toggles in a pseudo coin-door
column (switches 1 and 2, keys `7` and `8`), following Williams System 4–11 —
they have to be movable while the machine runs, because the adjustments menu
re-reads them on every pass to decide what the start button does.

### Provenance

The map was derived from the factory manual, a disassembly of both game ROMs and
measurement on the running machine. Where the manual and the ROM disagree the
ROM was followed and the disagreement is recorded in the source, along with the
one inference that only a real board can settle (which 4028 output carries the
knocker).

### Testing

A regression harness drives the machine over the debug HTTP API and asserts on
boot health, a complete game, the sound command protocol, the front-end
mechanics handover and a six-game soak. All pass on both ROM sets. The harness
lives outside this repository.
```
