# Export analysis artifacts for the Super Star ROMs.
# Dumps: full listing, I/O port usage, off-ROM memory refs, special opcodes,
# function inventory. Written for Ghidra headless (-postScript).
# @category SuperStar

import os

from ghidra.program.model.address import AddressSet
from ghidra.program.model.symbol import RefType

OUT_DIR = os.environ.get("SS_OUT", "/code/superstar/ghidra/out")
if not os.path.isdir(OUT_DIR):
    os.makedirs(OUT_DIR)

prog = currentProgram
name = prog.getName().replace(".bin", "")
listing = prog.getListing()
fm = prog.getFunctionManager()

base = prog.getMinAddress()
top = prog.getMaxAddress()


def w(fh, s):
    fh.write(s + "\n")


# ---------------------------------------------------------------- full listing
with open(os.path.join(OUT_DIR, name + "_listing.asm"), "w") as fh:
    w(fh, "; %s  %s - %s" % (name, base, top))
    for ins in listing.getInstructions(True):
        addr = ins.getAddress()
        bytestr = " ".join("%02X" % (b & 0xFF) for b in ins.getBytes())
        lbl = ""
        sym = prog.getSymbolTable().getPrimarySymbol(addr)
        if sym is not None and sym.isPrimary():
            lbl = "  ; <%s>" % sym.getName()
        w(fh, "%s  %-12s %s%s" % (addr, bytestr, ins, lbl))

# ------------------------------------------------------------------ I/O ports
io = []
special = []
for ins in listing.getInstructions(True):
    m = ins.getMnemonicString().upper()
    if m in ("IN", "OUT"):
        io.append((ins.getAddress(), m, str(ins)))
    if m in ("SIM", "RIM", "EI", "DI", "HLT", "RST"):
        special.append((ins.getAddress(), m, str(ins)))
    # MCS-48 I/O
    if m in ("INS", "OUTL", "MOVX", "ANL", "ORL") and (
        "BUS" in str(ins).upper() or " P1" in str(ins).upper() or " P2" in str(ins).upper()
    ):
        io.append((ins.getAddress(), m, str(ins)))

with open(os.path.join(OUT_DIR, name + "_io.txt"), "w") as fh:
    w(fh, "=== I/O instructions (%d) ===" % len(io))
    for a, m, s in io:
        w(fh, "%s  %-6s %s" % (a, m, s))
    w(fh, "")
    w(fh, "=== control / interrupt opcodes (%d) ===" % len(special))
    for a, m, s in special:
        w(fh, "%s  %-6s %s" % (a, m, s))

# --------------------------------------------------- references outside the ROM
offrom = {}
for ins in listing.getInstructions(True):
    for ref in ins.getReferencesFrom():
        t = ref.getToAddress()
        if t is None:
            continue
        if not ref.getReferenceType().isData():
            continue
        off = t.getOffset()
        if off > top.getOffset():
            offrom.setdefault(off, []).append(
                (ins.getAddress(), str(ins), str(ref.getReferenceType()))
            )

with open(os.path.join(OUT_DIR, name + "_offrom_refs.txt"), "w") as fh:
    w(fh, "=== data references above 0x%04X (%d distinct targets) ==="
          % (top.getOffset(), len(offrom)))
    for off in sorted(offrom):
        w(fh, "")
        w(fh, "--- 0x%04X  (%d refs)" % (off, len(offrom[off])))
        for a, s, rt in offrom[off]:
            w(fh, "    %s  %-28s %s" % (a, s, rt))

# ------------------------------------------------------------------- functions
with open(os.path.join(OUT_DIR, name + "_functions.txt"), "w") as fh:
    fns = list(fm.getFunctions(True))
    w(fh, "=== functions (%d) ===" % len(fns))
    for f in fns:
        body = f.getBody()
        w(fh, "%s  %-24s size=%-6d entry_refs=%d"
              % (f.getEntryPoint(), f.getName(), body.getNumAddresses(),
                 len(list(getReferencesTo(f.getEntryPoint())))))

# --------------------------------------------------------------- undefined gaps
undef = AddressSet(prog.getMemory())
for ins in listing.getInstructions(True):
    undef.delete(ins.getMinAddress(), ins.getMaxAddress())
for d in listing.getDefinedData(True):
    undef.delete(d.getMinAddress(), d.getMaxAddress())

with open(os.path.join(OUT_DIR, name + "_coverage.txt"), "w") as fh:
    total = prog.getMemory().getNumAddresses()
    w(fh, "total bytes      : %d" % total)
    w(fh, "undefined bytes  : %d" % undef.getNumAddresses())
    w(fh, "disassembled     : %.1f%%"
          % (100.0 * (total - undef.getNumAddresses()) / total))
    w(fh, "")
    w(fh, "=== undefined ranges ===")
    for rng in undef.getAddressRanges():
        if rng.getLength() >= 4:
            w(fh, "  %s - %s  (%d)" % (rng.getMinAddress(), rng.getMaxAddress(),
                                       rng.getLength()))

print("ExportAnalysis: wrote artifacts for %s to %s" % (name, OUT_DIR))
