#!/usr/bin/env python3
"""Export analysis artifacts for the Super Star ROMs via PyGhidra.

Run with the venv interpreter:
    GHIDRA_INSTALL_DIR=/usr/share/ghidra \
    /code/superstar/ghidra/venv/bin/python export_analysis.py <binary> <lang>

Writes listing, I/O map, off-ROM references, function inventory and
disassembly-coverage reports to /code/superstar/ghidra/out/.
"""
import os
import sys

OUT_DIR = os.environ.get("SS_OUT", "/code/superstar/ghidra/out")
PROJ_LOC = "/code/superstar/ghidra/proj"
PROJ_NAME = "SuperStar"

os.makedirs(OUT_DIR, exist_ok=True)

import pyghidra  # noqa: E402

pyghidra.start()


def export(prog_path):
    """prog_path is the in-project path, e.g. '/ic19_game.bin'."""
    name = os.path.basename(prog_path).replace(".bin", "")
    project = pyghidra.open_project(PROJ_LOC, PROJ_NAME)
    try:
        with pyghidra.program_context(project, prog_path) as prog:
            _export_program(prog, name)
    finally:
        project.close()


def _export_program(prog, name):
    from ghidra.program.flatapi import FlatProgramAPI

    api = FlatProgramAPI(prog)
    if True:
        listing = prog.getListing()
        fm = prog.getFunctionManager()
        st = prog.getSymbolTable()
        mem = prog.getMemory()
        top = prog.getMaxAddress().getOffset()

        instrs = list(listing.getInstructions(True))

        # ---------------------------------------------------------- listing
        with open(f"{OUT_DIR}/{name}_listing.asm", "w") as fh:
            fh.write(f"; {name}  0x0000 - 0x{top:04X}\n")
            for ins in instrs:
                addr = ins.getAddress()
                raw = " ".join(f"{b & 0xFF:02X}" for b in ins.getBytes())
                sym = st.getPrimarySymbol(addr)
                lbl = f"   ; <{sym.getName()}>" if sym else ""
                fh.write(f"{addr}  {raw:<12} {ins}{lbl}\n")

        # ------------------------------------------------------- I/O + ctrl
        io, ctrl = [], []
        for ins in instrs:
            m = ins.getMnemonicString().upper()
            s = str(ins)
            if m in ("IN", "OUT"):
                io.append((ins.getAddress(), m, s))
            elif m in ("SIM", "RIM", "EI", "DI", "HLT"):
                ctrl.append((ins.getAddress(), m, s))
            elif m in ("INS", "OUTL", "MOVX", "MOVD", "ANLD", "ORLD", "IN", "OUT"):
                io.append((ins.getAddress(), m, s))

        with open(f"{OUT_DIR}/{name}_io.txt", "w") as fh:
            fh.write(f"=== I/O instructions ({len(io)}) ===\n")
            for a, m, s in io:
                fh.write(f"{a}  {m:<6} {s}\n")
            fh.write(f"\n=== control/interrupt opcodes ({len(ctrl)}) ===\n")
            for a, m, s in ctrl:
                fh.write(f"{a}  {m:<6} {s}\n")

        # --------------------------------------------- refs above ROM top
        offrom = {}
        for ins in instrs:
            for ref in ins.getReferencesFrom():
                t = ref.getToAddress()
                if t is None or not ref.getReferenceType().isData():
                    continue
                off = t.getOffset()
                if off > top:
                    offrom.setdefault(off, []).append(
                        (ins.getAddress(), str(ins), str(ref.getReferenceType()))
                    )

        with open(f"{OUT_DIR}/{name}_offrom_refs.txt", "w") as fh:
            fh.write(
                f"=== data refs above 0x{top:04X} "
                f"({len(offrom)} distinct targets) ===\n"
            )
            for off in sorted(offrom):
                fh.write(f"\n--- 0x{off:04X}  ({len(offrom[off])} refs)\n")
                for a, s, rt in offrom[off]:
                    fh.write(f"    {a}  {s:<28} {rt}\n")

        # -------------------------------------------------------- functions
        fns = list(fm.getFunctions(True))
        with open(f"{OUT_DIR}/{name}_functions.txt", "w") as fh:
            fh.write(f"=== functions ({len(fns)}) ===\n")
            for f in fns:
                nrefs = len(list(api.getReferencesTo(f.getEntryPoint())))
                fh.write(
                    f"{f.getEntryPoint()}  {f.getName():<24} "
                    f"size={f.getBody().getNumAddresses():<6} refs={nrefs}\n"
                )

        # --------------------------------------------------------- coverage
        from ghidra.program.model.address import AddressSet

        undef = AddressSet(mem)
        for ins in instrs:
            undef.delete(ins.getMinAddress(), ins.getMaxAddress())
        for d in listing.getDefinedData(True):
            undef.delete(d.getMinAddress(), d.getMaxAddress())

        total = mem.getNumAddresses()
        with open(f"{OUT_DIR}/{name}_coverage.txt", "w") as fh:
            fh.write(f"total bytes     : {total}\n")
            fh.write(f"undefined bytes : {undef.getNumAddresses()}\n")
            fh.write(
                f"disassembled    : "
                f"{100.0 * (total - undef.getNumAddresses()) / total:.1f}%\n"
            )
            fh.write("\n=== undefined ranges (>=4 bytes) ===\n")
            for rng in undef.getAddressRanges():
                if rng.getLength() >= 4:
                    fh.write(
                        f"  {rng.getMinAddress()} - {rng.getMaxAddress()}"
                        f"  ({rng.getLength()})\n"
                    )

        print(
            f"{name}: {len(instrs)} instrs, {len(fns)} functions, "
            f"{len(io)} I/O, {len(offrom)} off-ROM targets"
        )


if __name__ == "__main__":
    export(sys.argv[1])
