#!/usr/bin/env python3
"""Locate the Greek position of the 10 Ethiopic chapters of the Apocalypse of
Ezra inside Charles's English translation of the Greek 4 Ezra (APOTP vol. II),
and emit the English text for the chapters that can be aligned with certainty.

The Ethiopic 'Apocalypse of Ezra' translates the Greek 4 Esdras literally and
was divided by the Ethiopic editors into 10 chapters.  The English 2 Esdras
(KJV / Douay-Rheims) translates the LATIN recension, which differs in places
and omits verses the Ethiopic has - so the Greek-based translation of Charles
is the only faithful base.
"""
import json, os, re, sys

CACHE = '/tmp/ezra_lines.json'
SEC = re.compile(r'^[\(\[]?\s*([ivxlIVXL]{1,7})\.?\s+([ivxlIVXL]{1,7})\.?\s*(\d+)\s*(?:[-–]\s*(?:v\.?\s*)?(\d+))?', re.I)
HEAD = re.compile(r'^IV?\s+EZRA\s+(\d{1,2})\.?\s*(\d+)?\s*(?:[-—–]\s*(\d{1,2})\.?\s*(\d+))?', re.I)
VERSE = re.compile(r'^\s*(\d{1,3})\s*[\.\)]?\s*(.*)$')
ROM = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9,
       'x': 10, 'xi': 11, 'xii': 12, 'xiii': 13, 'xiv': 14, 'xv': 15, 'xvi': 16}
ROM_FIX = {'1': 'i', '2': 'ii', '3': 'iii', '4': 'iv', '5': 'v', '6': 'vi', '7': 'vii',
           '8': 'viii', '9': 'ix', '1v': 'v', 'lv': 'v', 'll': 'ii', 'lll': 'iii'}


def chapnum(t):
    t = (t or '').strip().lower().replace('ı', 'i')
    if t.isdigit():
        n = int(t)
        return n if 1 <= n <= 16 else None
    return ROM.get(ROM_FIX.get(t, t))


def build_index():
    """ordered [(greek_ch, greek_verse, text)] for the 4 Ezra section"""
    pages = json.load(open(CACHE, encoding='utf-8'))
    out = []
    ch, v = 3, 1
    for pg in pages:
        for line in pg['lines']:
            m = HEAD.match(line)
            if m and len(line) < 40:
                c = chapnum(m.group(1))
                if c:
                    ch = c
                    if m.group(2):
                        v = int(m.group(2))
                continue
            ms = SEC.match(line)
            if ms and len(line) < 80:
                c = chapnum(ms.group(2))
                if c:
                    ch = c
                    if ms.group(3):
                        v = int(ms.group(3))
                continue
            mv = VERSE.match(line)
            if mv:
                n = int(mv.group(1))
                if 0 < n < 200:
                    v = n
                    rest = mv.group(2).strip()
                    if rest:
                        out.append((ch, v, rest))
                    continue
            out.append((ch, v, line))
    return out


def find(idx, phrase):
    lo = phrase.lower()
    return [(i, ch, v, t) for i, (ch, v, t) in enumerate(idx) if lo in t.lower()]


if __name__ == '__main__':
    idx = build_index()
    print('elemente ordonate: %d' % len(idx))
    for phrase in ['In the thirtieth year', 'after seven days', 'went forth and walked in the field',
                   'earthquake', 'I saw', 'holy temple', 'Azariah', 'fasting', 'Darius']:
        hits = find(idx, phrase)
        print('  %-32s -> %s' % (phrase, [(ch, v) for _, ch, v, _ in hits[:3]]))
