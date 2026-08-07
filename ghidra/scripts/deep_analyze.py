#!/usr/bin/env python3
"""Deep-analyse the Super Star 8085 game ROM.

Ghidra's flow-following alone reaches only ~8% of this ROM: the rest is
entered through the 8085 interrupt vectors and via jump tables. This script
seeds the address space with the real hardware layout (verified against the
machine manual and MAME's supstarf.cpp memory map), marks every 8085 vector
as an entry point, then iteratively disassembles whatever remains.

Usage:
    GHIDRA_INSTALL_DIR=/usr/share/ghidra \
    /code/superstar/ghidra/venv/bin/python deep_analyze.py
"""
import os

PROJ_LOC = "/code/superstar/ghidra/proj"
PROJ_NAME = "SuperStar"

import pyghidra  # noqa: E402

pyghidra.start()

# 8085 hardware vectors. RST n are the software RST opcodes; TRAP/RST5.5/6.5/7.5
# are the hardware interrupt pins.
VECTORS = [
    (0x0000, "RESET"),
    (0x0008, "RST_1"),
    (0x0010, "RST_2"),
    (0x0018, "RST_3"),
    (0x0020, "RST_4"),
    (0x0024, "TRAP"),
    (0x0028, "RST_5"),
    (0x002C, "RST_5_5"),   # 8212 sound latch -> main CPU
    (0x0030, "RST_6"),
    (0x0034, "RST_6_5"),
    (0x0038, "RST_7"),
    (0x003C, "RST_7_5"),
]

# Off-ROM regions, from the manual (CPU board 53/3291) and MAME's main_map.
BLOCKS = [
    ("SOUNDLATCH", 0x8000, 0x1, "8212 latches IC5/IC6: read=from sound, write=strobe"),
    ("NVRAM", 0xC000, 0x800, "5517 2Kx8 battery-backed RAM at IC11"),
]


def main():
    project = pyghidra.open_project(PROJ_LOC, PROJ_NAME)
    try:
        with pyghidra.program_context(project, "/ic19_game.bin") as prog:
            run(prog)
    finally:
        project.close()


def run(prog):
    from ghidra.program.flatapi import FlatProgramAPI
    from ghidra.program.model.address import AddressSet
    from ghidra.program.model.symbol import SourceType
    from ghidra.app.cmd.disassemble import DisassembleCommand
    from ghidra.util.task import ConsoleTaskMonitor

    api = FlatProgramAPI(prog)
    monitor = ConsoleTaskMonitor()
    mem = prog.getMemory()
    af = prog.getAddressFactory().getDefaultAddressSpace()
    st = prog.getSymbolTable()

    tx = prog.startTransaction("deep analyze")
    try:
        # ---- 1. create the off-ROM hardware blocks so refs resolve ----------
        for name, start, size, comment in BLOCKS:
            addr = af.getAddress(start)
            if mem.getBlock(addr) is None:
                blk = mem.createUninitializedBlock(name, addr, size, False)
                blk.setRead(True)
                blk.setWrite(True)
                blk.setComment(comment)
                print(f"  created block {name} @ 0x{start:04X} size 0x{size:X}")

        # ---- 2. mark the 8085 vectors as entry points ----------------------
        for off, label in VECTORS:
            addr = af.getAddress(off)
            if not mem.contains(addr):
                continue
            b = mem.getByte(addr) & 0xFF
            if b == 0xFF:                       # unused vector, left as 0xFF fill
                continue
            st.createLabel(addr, label, SourceType.USER_DEFINED)
            api.addEntryPoint(addr)
            DisassembleCommand(addr, None, True).applyTo(prog, monitor)
            print(f"  vector {label:<8} @ 0x{off:04X}  first byte 0x{b:02X}")

        # ---- 3. iteratively disassemble whatever is still undefined --------
        # Sweep forward through gaps; each pass may reveal more flow.
        for pass_no in range(1, 9):
            undef = AddressSet(mem)
            for ins in prog.getListing().getInstructions(True):
                undef.delete(ins.getMinAddress(), ins.getMaxAddress())
            for d in prog.getListing().getDefinedData(True):
                undef.delete(d.getMinAddress(), d.getMaxAddress())

            targets = []
            for rng in undef.getAddressRanges():
                a = rng.getMinAddress()
                # only inside the ROM image
                if a.getOffset() > 0x3FFF:
                    continue
                # skip 0xFF filler
                try:
                    if (mem.getByte(a) & 0xFF) == 0xFF:
                        continue
                except Exception:
                    continue
                targets.append(a)

            if not targets:
                break
            for a in targets:
                DisassembleCommand(a, None, True).applyTo(prog, monitor)

            remaining = undef.getNumAddresses()
            print(f"  pass {pass_no}: {len(targets)} gap starts, "
                  f"{remaining} undefined bytes before pass")

        # ---- 4. rebuild functions ------------------------------------------
        from ghidra.app.cmd.function import CreateFunctionCmd

        created = 0
        for sym in st.getAllSymbols(True):
            pass
        # create functions at every call target
        for ins in prog.getListing().getInstructions(True):
            m = ins.getMnemonicString().upper()
            if m in ("CALL", "CC", "CNC", "CZ", "CNZ", "CP", "CM", "CPE", "CPO"):
                for ref in ins.getReferencesFrom():
                    t = ref.getToAddress()
                    if t is None or t.getOffset() > 0x3FFF:
                        continue
                    if prog.getFunctionManager().getFunctionAt(t) is None:
                        if CreateFunctionCmd(t).applyTo(prog, monitor):
                            created += 1
        print(f"  created {created} functions from call targets")

        prog.endTransaction(tx, True)
    except Exception:
        prog.endTransaction(tx, False)
        raise

    prog.save("deep analyze", monitor)

    # ---- report ------------------------------------------------------------
    undef = AddressSet(mem)
    for ins in prog.getListing().getInstructions(True):
        undef.delete(ins.getMinAddress(), ins.getMaxAddress())
    for d in prog.getListing().getDefinedData(True):
        undef.delete(d.getMinAddress(), d.getMaxAddress())
    rom_undef = 0
    for rng in undef.getAddressRanges():
        if rng.getMinAddress().getOffset() <= 0x3FFF:
            lo = rng.getMinAddress().getOffset()
            hi = min(rng.getMaxAddress().getOffset(), 0x3FFF)
            rom_undef += hi - lo + 1
    print(f"\nROM coverage: {100.0 * (16384 - rom_undef) / 16384:.1f}% "
          f"({16384 - rom_undef}/16384 bytes)")
    print(f"functions: {prog.getFunctionManager().getFunctionCount()}")


if __name__ == "__main__":
    main()
