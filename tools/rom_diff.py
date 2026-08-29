#!/usr/bin/env python3
"""Compare Super Star game ROM revisions at the instruction level.

Raw byte diffs between these images are useless: one inserted NVRAM byte shifts
every following address operand, so two revisions differing by 13 instructions
look 1502 bytes apart. This aligns disassembled instruction streams with ROM-
and NVRAM-pointing operands abstracted to their region class, which makes
insertions, deletions and genuine edits visible as such.

It produced `docs/rom-revision-chain.md`. Modes:

    tools/rom_diff.py inventory  ROM...        hashes, sizes, checksum scheme
    tools/rom_diff.py matrix     ROM...        pairwise hunk counts (ordering)
    tools/rom_diff.py hunks      OLD NEW       every changed hunk, disassembled
    tools/rom_diff.py shifts     OLD NEW       NVRAM/code address remapping
    tools/rom_diff.py coverage   ROM...        byte classification, residue
    tools/rom_diff.py sound      ROM...        sound-command census

With no ROM arguments the four built sets in `roms/` are used:

    tools/rom_diff.py matrix

The ordering argument in `rom-revision-chain.md` §3.1 is `matrix`: the
consecutive hunk counts (8, 9, 43) form an additive path, and every skip
distance is the sum of the steps it spans, which is what fixes the sequence.
"""
import argparse
import collections
import difflib
import hashlib
import os
import sys
import zipfile
import zlib

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import dis85

ROMS = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'roms')

# The four built sets, in chronological order - which is also set-name order,
# since PinMAME numbers them by revision.
DEFAULT_SETS = [
    ('supstarf1', 'supstarf1.zip', 'm31-a-01187.ic19'),
    ('supstarf2', 'supstarf2.zip', '27128Prg.bin'),
    ('supstarf3', 'supstarf3.zip', 'super.dat'),
    ('supstarf4', 'supstarf4.zip', '27c128.ic19'),
]


def load(spec):
    """Load a ROM image. `spec` is a path, or `set.zip:member`."""
    if ':' in spec and spec.split(':', 1)[0].endswith('.zip'):
        z, member = spec.split(':', 1)
        with zipfile.ZipFile(z) as f:
            return f.read(member)
    with open(spec, 'rb') as f:
        return f.read()


def default_images():
    out = []
    for label, zipname, member in DEFAULT_SETS:
        path = os.path.join(ROMS, zipname)
        if not os.path.exists(path):
            sys.exit(f'{path} not found - build the sets first (see roms/README.md)')
        with zipfile.ZipFile(path) as f:
            out.append((label, f.read(member)))
    return out


def images(args):
    if not args:
        return default_images()
    return [(os.path.basename(a).split(':')[-1], load(a)) for a in args]


# ---------------------------------------------------------------- tracing

def zone_table_targets(rom):
    """Recover the operator-menu jump table's targets.

    The dispatcher is `LXI H,tbl / DAD D / DAD D / MOV E,M / INX H / MOV D,M /
    XCHG / PCHL`, bounded by a `CPI` just above it (game-rom-map.md §2). Set 1
    checks `CPI 0A` against a 9-entry table; set 2 `CPI 1A` against 25 entries.
    """
    pat = bytes([0x19, 0x19, 0x5E, 0x23, 0x56, 0xEB, 0xE9])
    i = rom.find(pat)
    if i < 3 or rom[i - 3] != 0x21:
        return []
    table = rom[i - 2] | rom[i - 1] << 8
    j = rom.rfind(b'\xFE', max(0, i - 40), i)
    count = rom[j + 1] - 1 if j > 0 else 9
    out = []
    for k in range(count):
        t = rom[table + 2 * k] | rom[table + 2 * k + 1] << 8
        if t < 0x4000:
            out.append(t)
    return out


def instruction_starts(rom):
    return sorted(dis85.trace(rom, extra_roots=zone_table_targets(rom)))


def normalise(rom, addr):
    """Instruction token with address operands abstracted by region class.

    This is what makes the alignment work: a `CALL $1987` and a `CALL $1999`
    that are the same call to a relocated routine both become `CALL ROM`, so
    only real edits register as differences.
    """
    op = rom[addr]
    mnemonic = dis85.OPS[op][0]
    if '{a}' in mnemonic:
        t = rom[addr + 2] << 8 | rom[addr + 1]
        if t < 0x4000:
            cls = 'ROM'
        elif 0xC000 <= t < 0xC800:
            cls = 'NVR'
        else:
            cls = f'{t:04X}'
        return mnemonic.replace('{a}', cls)
    if '{d}' in mnemonic:
        return mnemonic.replace('{d}', f'{rom[addr + 1]:02X}')
    return mnemonic


def stream(rom):
    starts = instruction_starts(rom)
    return starts, [normalise(rom, a) for a in starts]


def opcodes_between(a, b):
    _, ta = stream(a)
    _, tb = stream(b)
    return difflib.SequenceMatcher(None, ta, tb, autojunk=False).get_opcodes()


# ---------------------------------------------------------------- modes

def cmd_inventory(args):
    print(f"{'image':<16}{'size':>7}{'CRC32':>10}{'sum8':>6}{'sum16':>7}  sha1")
    for label, d in images(args.roms):
        print(f'{label:<16}{len(d):>7}{zlib.crc32(d) & 0xffffffff:>10X}'
              f'{sum(d) & 0xFF:>6X}{sum(d) & 0xFFFF:>7X}  {hashlib.sha1(d).hexdigest()}')
    print()
    print('A whole-image 8-bit sum of 0x00 means a checksum-correction byte at 0x3FFF;')
    print('only rev. 4 (supstarf4) uses that scheme.')


def cmd_matrix(args):
    imgs = images(args.roms)
    print('Instruction counts:')
    counts = {}
    for label, d in imgs:
        counts[label] = len(stream(d)[1])
        print(f'  {label:<16}{counts[label]:>6}')
    print()
    print('Pairwise hunk counts (insert + delete + replace blocks):')
    print(f"{'':<16}" + ''.join(f'{l.split("/")[0]:>10}' for l, _ in imgs))
    for la, da in imgs:
        row = f'{la:<16}'
        for lb, db in imgs:
            n = 0 if la == lb else sum(
                1 for tag, *_ in opcodes_between(da, db) if tag != 'equal')
            row += f'{n:>10}'
        print(row)
    print()
    print('A chain shows as an additive path: consecutive distances small, and every')
    print('skip distance equal to the sum of the steps it spans.')


def _disasm(rom, addr, n):
    out = []
    for _ in range(n):
        text, ln, _t = dis85.decode(rom, addr)
        raw = ' '.join(f'{b:02X}' for b in rom[addr:addr + ln])
        out.append(f'      {addr:04X}: {raw:<9} {text}')
        addr += ln
    return out


def cmd_hunks(args):
    a, b = load(args.old), load(args.new)
    sa, _ = stream(a)
    sb, _ = stream(b)
    print(f'{os.path.basename(args.old)} -> {os.path.basename(args.new)}')
    eq = ins = dele = rep = 0
    for tag, i1, i2, j1, j2 in opcodes_between(a, b):
        if tag == 'equal':
            eq += i2 - i1
            continue
        if tag == 'insert':
            ins += j2 - j1
        elif tag == 'delete':
            dele += i2 - i1
        else:
            rep += max(i2 - i1, j2 - j1)
        aa = sa[i1] if i1 < len(sa) else -1
        bb = sb[j1] if j1 < len(sb) else -1
        print(f'\n  {tag.upper():<7} old ${aa:04X}  new ${bb:04X}  '
              f'(old {i2 - i1}, new {j2 - j1} instrs)')
        ctx = max(0, i1 - args.context)
        if i1 > ctx:
            print('    [context]')
            print('\n'.join(_disasm(a, sa[ctx], i1 - ctx)))
        if i2 > i1:
            print('    [removed]')
            print('\n'.join(_disasm(a, sa[i1], i2 - i1)))
        if j2 > j1:
            print('    [added]')
            print('\n'.join(_disasm(b, sb[j1], j2 - j1)))
    print(f'\n  aligned equal {eq}, inserted {ins}, deleted {dele}, replaced {rep}')


def cmd_shifts(args):
    a, b = load(args.old), load(args.new)
    sa, _ = stream(a)
    sb, _ = stream(b)
    nvram = collections.Counter()
    rom_delta = collections.Counter()
    for tag, i1, i2, j1, j2 in opcodes_between(a, b):
        if tag != 'equal':
            continue
        for k in range(i2 - i1):
            x, y = dis85.target(a, sa[i1 + k]), dis85.target(b, sb[j1 + k])
            if x is None or y is None:
                continue
            if 0xC000 <= x < 0xC800 and 0xC000 <= y < 0xC800:
                nvram[(x, y)] += 1
            elif x < 0x4000 and y < 0x4000:
                rom_delta[y - x] += 1
    print(f'{os.path.basename(args.old)} -> {os.path.basename(args.new)}\n')
    deltas = collections.Counter()
    for (x, y), n in nvram.items():
        deltas[y - x] += n
    print(f'  NVRAM operand deltas: {dict(sorted(deltas.items()))}')
    moved = sorted({x for x, y in nvram if x != y})
    same = sorted({x for x, y in nvram if x == y})
    if moved:
        below = [s for s in same if s < moved[0]]
        line = f'  {len(moved)} NVRAM addresses shift, lowest {moved[0]:04X}'
        if below:
            line += f'; unchanged up to {max(below):04X}'
        print(line)
        print('  -> a variable was inserted at the boundary')
    else:
        print('  NVRAM layout unchanged')
    print(f'  ROM code-address deltas: {dict(sorted(rom_delta.items()))}')


def cmd_coverage(args):
    for label, d in images(args.roms):
        starts = instruction_starts(d)
        covered = bytearray(len(d))
        for a in starts:
            for i in range(a, min(a + dis85.length(d[a]), len(d))):
                covered[i] = 1
        code = sum(covered)
        fill = sum(1 for i in range(len(d)) if not covered[i] and d[i] == 0xFF)
        residue = [i for i in range(len(d)) if not covered[i] and d[i] != 0xFF]
        ranges, cur = [], None
        for i in residue:
            if cur and i == cur[1] + 1:
                cur[1] = i
            else:
                if cur:
                    ranges.append(cur)
                cur = [i, i]
        if cur:
            ranges.append(cur)
        print(f'{label:<16} code {code:>6}  0xFF fill {fill:>6}  '
              f'residue {len(residue):>4} in {len(ranges)} ranges')
        print('      ' + ', '.join(f'{lo:04X}-{hi:04X}' for lo, hi in ranges))
    print()
    print('Residue should be the known data tables and dead-code orphans only')
    print('(game-rom-map.md §1). Identical range sets across revisions is the')
    print('integrity check for the images that carry no checksum byte.')


def cmd_sound(args):
    for label, d in images(args.roms):
        starts = instruction_starts(d)
        sender = d.find(bytes([0x32, 0x00, 0x80, 0x3E, 0x0E, 0x30]))
        echo = d.find(bytes([0x78, 0x32, 0x33, 0xC0, 0xCD]))
        sites = [a for a in starts if d[a] == 0x32 and dis85.target(d, a) == 0x8000]
        direct = set()
        for i, a in enumerate(starts):
            if d[a] != 0x3E:
                continue
            for b in starts[i + 1:i + 4]:
                if d[b] == 0x32 and dis85.target(d, b) == 0x8000:
                    direct.add(d[a + 1])
        control = set()
        pa = pb = None
        for a in starts:
            op = d[a]
            if op == 0x3E:
                pa = d[a + 1]; continue
            if op == 0x06:
                pb = d[a + 1]; continue
            t = dis85.target(d, a)
            if t is not None:
                if t == sender and pa is not None:
                    control.add(pa)
                if t == echo and pb is not None:
                    control.add(pb)
            if op in dis85.CALL_OPS | dis85.JUMP_OPS | {0xC9}:
                pa = pb = None
        chime = d[0x273F:0x2745]
        print(f'{label:<16} sender@{sender:04X} echo@{echo:04X}  '
              f'{len(sites)} STA $8000 sites')
        print(f'      direct:  {" ".join(f"{c:02X}" for c in sorted(direct))}')
        print(f'      control: {" ".join(f"{c:02X}" for c in sorted(control))}')
        print(f'      chime table @273F: {" ".join(f"{b:02X}" for b in chime)}')
    print()
    print('An unchanged command vocabulary is what justifies pairing every game')
    print('ROM revision with the same 2532 sound ROM.')


def main():
    p = argparse.ArgumentParser(description=__doc__,
                                formatter_class=argparse.RawDescriptionHelpFormatter)
    sub = p.add_subparsers(dest='mode', required=True)
    for name, fn in (('inventory', cmd_inventory), ('matrix', cmd_matrix),
                     ('coverage', cmd_coverage), ('sound', cmd_sound)):
        s = sub.add_parser(name)
        s.add_argument('roms', nargs='*')
        s.set_defaults(func=fn)
    for name, fn in (('hunks', cmd_hunks), ('shifts', cmd_shifts)):
        s = sub.add_parser(name)
        s.add_argument('old')
        s.add_argument('new')
        s.add_argument('--context', type=int, default=3)
        s.set_defaults(func=fn)
    args = p.parse_args()
    args.func(args)


if __name__ == '__main__':
    main()
