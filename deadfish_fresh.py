#!/usr/bin/env python3
import itertools
import re
from collections import Counter

with open("codex", "r", encoding="utf-8", errors="replace") as f:
    data = f.read()

print("=== Raw symbol inventory ===")
print(Counter(data))

print("\n=== Hypothesis: base-3 digits, grouped by > or ry ===")
for split_name, pattern in [('>', r'>'), ('ry', r'ry')]:
    groups = [g for g in re.split(pattern, data) if g.strip(' \n\t')]
    clean_groups = [g for g in groups if all(c in 'dsi' for c in g)]
    print(f"\n[{split_name}] total groups={len(groups)} clean dsi-only={len(clean_groups)}")
    if not clean_groups:
        continue
    for d, s, i in itertools.permutations([0, 1, 2]):
        m = {'d': d, 's': s, 'i': i}
        vals = []
        for g in clean_groups:
            n = 0
            for ch in g:
                n = n * 3 + m[ch]
            vals.append(n)
        printable = sum(1 for v in vals if 32 <= v <= 126) / max(1, len(vals))
        if printable > 0.6:
            text = ''.join(chr(v) if 32 <= v <= 126 else f'[{v}]' for v in vals)
            print(f"  d={d} s={s} i={i}: {printable:.2f} -> {text[:150]}")

print("\n=== Hypothesis: d/s as bits, i as separator ===")
for d_bit, s_bit in [('0', '1'), ('1', '0')]:
    stripped = data.replace('r', '').replace('y', '').replace('>', '')
    segs = [s for s in re.split('i+', stripped) if s]
    bits_per_seg = Counter(len(s) for s in segs)
    print(f"d={d_bit} s={s_bit}: {len(segs)} segments, lengths: {bits_per_seg.most_common(10)}")
    chars = []
    for seg in segs:
        b = seg.replace('d', d_bit).replace('s', s_bit)
        try:
            n = int(b, 2)
            chars.append(chr(n) if 32 <= n <= 126 else f'[{n}]')
        except Exception:
            chars.append('?')
    text = ''.join(chars)
    printable = sum(1 for c in chars if len(c) == 1) / max(1, len(chars))
    if printable > 0.5:
        print(f"  -> {printable:.2f} printable: {text[:200]}")

print("\n=== Hypothesis: Morse-style (d=., s=-, i=letter-gap) ===")
MORSE = {
    '.-':'A','-...':'B','-.-.':'C','-..':'D','.':'E','..-.':'F','--.':'G',
    '....':'H','..':'I','.---':'J','-.-':'K','.-..':'L','--':'M','-.':'N',
    '---':'O','.--.':'P','--.-':'Q','.-.':'R','...':'S','-':'T','..-':'U',
    '...-':'V','.--':'W','-..-':'X','-.--':'Y','--..':'Z',
    '-----':'0','.----':'1','..---':'2','...--':'3','....-':'4',
    '.....':'5','-....':'6','--...':'7','---..':'8','----.':'9',
}
morse_src = data.replace('d', '.').replace('s', '-')
stripped2 = morse_src.replace('r', '').replace('y', '').replace('>', '')
letters = re.split('i+', stripped2)
decoded = ''.join(MORSE.get(l, '?') for l in letters if l)
print(f"  {decoded[:300]}")
