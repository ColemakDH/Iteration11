#!/usr/bin/env python3
"""
Treats 'ry' as a single atomic output+reset token (confirmed: r is always
followed by y). '>' is stripped as formatting noise. Tests all 6
permutations of d/s/i as inc/dec/square.
"""
import itertools

with open("codex", "r", encoding="utf-8", errors="replace") as f:
    data = f.read()

for inc, dec, sq in itertools.permutations(['d', 's', 'i']):
    acc = 0
    out = []
    for ch in data:
        if ch == '>':
            continue
        if ch == 'y':
            continue
        if ch == 'r':
            out.append(acc)
            acc = 0
            continue
        if ch == inc:
            acc += 1
        elif ch == dec:
            acc -= 1
        elif ch == sq:
            acc *= acc
            if acc.bit_length() > 2000:
                acc = 0
    text = ''.join(chr(v) if 32 <= v <= 126 else f'[{v}]' for v in out)
    printable = sum(1 for v in out if 32 <= v <= 126) / max(1, len(out))
    print(f"inc={inc} dec={dec} sq={sq}: {printable:.2f} printable, {len(out)} outputs")
    print(f"  {text[:200]}")
