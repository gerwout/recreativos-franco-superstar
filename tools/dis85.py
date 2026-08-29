#!/usr/bin/env python3
"""Intel 8085 disassembler and recursive-descent tracer.

The library behind `rom_diff.py`. It exists because the Super Star game ROM
comparison needs *instruction boundaries*, not just bytes: one inserted byte
shifts every following address operand, so a raw byte diff between two firmware
revisions is noise. Aligning at the instruction level, with address operands
abstracted by region, turns a 9819-byte diff into ~40 insertions.

Covers the documented 8080/8085 set plus the undocumented 8085 opcodes this ROM
actually uses — `DSUB` (0x08) appears twice in the game ROM as a 16-bit loop
compare (`game-rom-map.md` §1, addresses 0193 and 01F8). All 256 opcodes are
assigned so a linear sweep can never fall off the table.

    from dis85 import decode, trace, OPS
    text, length, target = decode(rom, 0x1800)
    starts = trace(rom, [0x0000, 0x0024, 0x002C, 0x0034, 0x003C])
"""

R8 = ['B', 'C', 'D', 'E', 'H', 'L', 'M', 'A']
ALU = ['ADD', 'ADC', 'SUB', 'SBB', 'ANA', 'XRA', 'ORA', 'CMP']
ALU_IMM = ['ADI', 'ACI', 'SUI', 'SBI', 'ANI', 'XRI', 'ORI', 'CPI']
RP = ['B', 'D', 'H', 'SP']
RP_PSW = ['B', 'D', 'H', 'PSW']
CC = ['NZ', 'Z', 'NC', 'C', 'PO', 'PE', 'P', 'M']

# opcode -> (mnemonic template, byte length).  {a} = addr16 operand, {d} = imm8.
OPS = {}


def _o(code, mnemonic, length):
    OPS[code] = (mnemonic, length)


for i, rp in enumerate(RP):
    _o(0x01 + i * 0x10, f'LXI {rp},{{a}}', 3)
    _o(0x03 + i * 0x10, f'INX {rp}', 1)
    _o(0x09 + i * 0x10, f'DAD {rp}', 1)
    _o(0x0B + i * 0x10, f'DCX {rp}', 1)
for i, r in enumerate(R8):
    _o(0x04 + i * 8, f'INR {r}', 1)
    _o(0x05 + i * 8, f'DCR {r}', 1)
    _o(0x06 + i * 8, f'MVI {r},{{d}}', 2)
_o(0x02, 'STAX B', 1); _o(0x12, 'STAX D', 1)
_o(0x0A, 'LDAX B', 1); _o(0x1A, 'LDAX D', 1)
_o(0x07, 'RLC', 1); _o(0x0F, 'RRC', 1); _o(0x17, 'RAL', 1); _o(0x1F, 'RAR', 1)
_o(0x20, 'RIM', 1); _o(0x30, 'SIM', 1)
_o(0x27, 'DAA', 1); _o(0x2F, 'CMA', 1); _o(0x37, 'STC', 1); _o(0x3F, 'CMC', 1)
_o(0x00, 'NOP', 1)
_o(0x22, 'SHLD {a}', 3); _o(0x2A, 'LHLD {a}', 3)
_o(0x32, 'STA {a}', 3);  _o(0x3A, 'LDA {a}', 3)
# undocumented 8085
_o(0x08, 'DSUB', 1); _o(0x10, 'ARHL', 1); _o(0x18, 'RDEL', 1)
_o(0x28, 'LDHI {d}', 2); _o(0x38, 'LDSI {d}', 2)
_o(0xCB, 'RSTV', 1); _o(0xD9, 'SHLX', 1); _o(0xED, 'LHLX', 1)
_o(0xDD, 'JNK {a}', 3); _o(0xFD, 'JK {a}', 3)
for d in range(8):
    for s in range(8):
        c = 0x40 + d * 8 + s
        _o(c, 'HLT' if c == 0x76 else f'MOV {R8[d]},{R8[s]}', 1)
for i, a in enumerate(ALU):
    for s, r in enumerate(R8):
        _o(0x80 + i * 8 + s, f'{a} {r}', 1)
for i, m in enumerate(ALU_IMM):
    _o(0xC6 + i * 8, f'{m} {{d}}', 2)
for i, c in enumerate(CC):
    _o(0xC0 + i * 8, f'R{c}', 1)
    _o(0xC2 + i * 8, f'J{c} {{a}}', 3)
    _o(0xC4 + i * 8, f'C{c} {{a}}', 3)
for i, rp in enumerate(RP_PSW):
    _o(0xC1 + i * 0x10, f'POP {rp}', 1)
    _o(0xC5 + i * 0x10, f'PUSH {rp}', 1)
for i in range(8):
    _o(0xC7 + i * 8, f'RST {i}', 1)
_o(0xC3, 'JMP {a}', 3); _o(0xC9, 'RET', 1); _o(0xCD, 'CALL {a}', 3)
_o(0xD3, 'OUT {d}', 2); _o(0xDB, 'IN {d}', 2)
_o(0xE3, 'XTHL', 1); _o(0xE9, 'PCHL', 1); _o(0xEB, 'XCHG', 1); _o(0xF9, 'SPHL', 1)
_o(0xF3, 'DI', 1); _o(0xFB, 'EI', 1)

assert len(OPS) == 256, f'opcode table incomplete: {len(OPS)}'

# Opcodes after which control does not fall through to the next address.
# RST n is terminal here: this ROM uses RST 0 only as a cold reset, and the
# first tracer pass that modelled it as a call walked into the vector area's
# 0xFF fill and decoded 23 phantom RST 7s (game-rom-map.md §0).
FLOW_STOP = {0xC3, 0xC9, 0xE9, 0x76,
             0xC7, 0xCF, 0xD7, 0xDF, 0xE7, 0xEF, 0xF7, 0xFF}

CALL_OPS = {0xCD} | {0xC4 + i * 8 for i in range(8)}
JUMP_OPS = {0xC3} | {0xC2 + i * 8 for i in range(8)} | {0xDD, 0xFD}

# The four hardware vectors, plus reset.
ENTRY_POINTS = [0x0000, 0x0024, 0x002C, 0x0034, 0x003C]


def length(opcode):
    """Byte length of an opcode."""
    return OPS[opcode][1]


def target(rom, addr):
    """The 16-bit operand of a 3-byte instruction, or None."""
    op = rom[addr]
    mnemonic, n = OPS[op]
    if n == 3 and '{a}' in mnemonic:
        return rom[addr + 2] << 8 | rom[addr + 1]
    return None


def decode(rom, addr):
    """Disassemble one instruction. Returns (text, length, target-or-None)."""
    op = rom[addr]
    mnemonic, n = OPS[op]
    if '{a}' in mnemonic:
        t = rom[addr + 2] << 8 | rom[addr + 1]
        return mnemonic.replace('{a}', f'${t:04X}'), n, t
    if '{d}' in mnemonic:
        return mnemonic.replace('{d}', f'#{rom[addr + 1]:02X}'), n, None
    return mnemonic, n, None


def trace(rom, entries=None, extra_roots=(), limit=0x4000):
    """Recursive descent from `entries` plus `extra_roots`.

    Returns the set of instruction start addresses. This is an
    over-approximation: both sides of every branch are followed. Computed jumps
    (PCHL through a table) are not resolved here — pass their targets in via
    `extra_roots`; `rom_diff.zone_table_targets` recovers the operator-menu one.
    """
    starts = set()
    todo = list(ENTRY_POINTS if entries is None else entries) + list(extra_roots)
    while todo:
        addr = todo.pop()
        while 0 <= addr < limit and addr not in starts:
            op = rom[addr]
            n = OPS[op][1]
            if addr + n > limit:
                break
            starts.add(addr)
            t = target(rom, addr)
            if t is not None and t < limit and (op in JUMP_OPS or op in CALL_OPS):
                todo.append(t)
            if op in FLOW_STOP:
                break
            addr += n
    return starts
