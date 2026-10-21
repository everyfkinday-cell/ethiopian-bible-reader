#!/usr/bin/env python3
"""Build a Greek-numbered verse map of 4 Ezra from Charles's APOTP vol. II.

Reliable anchors:
  * section headings in the body, e.g. 'II. iii. 4-36.', '(a) iv. 1-11.'
  * the running head (used only where no heading is present)
  * inline verse numbers
"""
import json, os, re, sys
import pypdf

PDF = '/tmp/charles2.pdf'
CACHE = '/tmp/ezra_lines.json'
OUT = '/tmp/ezra_greek_verses.json'
PAGES = (556, 638)
MAIN_FS = 9.3

ROM = {'i': 1, 'ii': 2, 'iii': 3, 'iv': 4, 'v': 5, 'vi': 6, 'vii': 7, 'viii': 8, 'ix': 9,
       'x': 10, 'xi': 11, 'xii': 12, 'xiii': 13, 'xiv': 14, 'xv': 15, 'xvi': 16}
ROM_FIX = {'1': 'i', '2': 'ii', '3': 'iii', '4': 'iv', '5': 'v', '6': 'vi', '7': 'vii',
           '8': 'viii', '9': 'ix', '1v': 'v', 'lv': 'v', 'll': 'ii', 'lll': 'iii',
           'lviii': 'viii', 'lx': 'x', 'lxi': 'xi', 'lxii': 'xii', 'lxiii': 'xiii'}
GREEK = re.compile(r'[Ͱ-Ͽἀ-῿֐-׿؀-ۿﭐ-﷿ﹰ-﻿]')
NOISE = re.compile(r'[©®™°§¶«»‎‏]|&quot;|&\w+;')
HEAD = re.compile(r'^IV?\s+EZRA\s+(\d{1,2})\.?\s*(\d+)?\s*(?:[-—–]\s*(\d{1,2})\.?\s*(\d+))?', re.I)
SEC = re.compile(r'^[\(\[]?\s*([ivxlIVXL]{1,7})\.?\s+([ivxlIVXL]{1,7})\.?\s*(\d+)\s*(?:[-–]\s*(?:v\.?\s*)?(\d+))?', re.I)
VERSE = re.compile(r'^\s*(\d{1,3})\s*[\.\)]?\s*(.*)$')


def chapnum(t):
    t = (t or '').strip().lower().replace('ı', 'i')
    if t.isdigit():
        n = int(t)
        return n if 1 <= n <= 16 else None
    return ROM.get(ROM_FIX.get(t, t))


def clean(t):
    t = GREEK.sub(' ', t)
    t = NOISE.sub(' ', t)
    t = re.sub(r'\*+', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return re.sub(r'\s+([,.;:!?])', r'\1', t).strip()


def build_pages():
    r = pypdf.PdfReader(PDF)
    pages = []
    for i in range(PAGES[0], PAGES[1]):
        items = []

        def v(text, cm, tm, fd, fs):
            if text and text.strip() and fs >= MAIN_FS:
                items.append((round(tm[5], 1), round(tm[4], 1), text))
        try:
            r.pages[i].extract_text(visitor_text=v)
        except Exception:
            continue
        rows = {}
        for y, x, t in items:
            rows.setdefault(round(y, 0), []).append((x, t))
        lines = []
        for y in sorted(rows, reverse=True):
            line = clean(' '.join(t for x, t in sorted(rows[y])))
            if line:
                lines.append(line)
        pages.append({'idx': i, 'lines': lines})
    json.dump(pages, open(CACHE, 'w', encoding='utf-8'), ensure_ascii=False)
    return pages


def main():
    pages = json.load(open(CACHE, encoding='utf-8')) if os.path.exists(CACHE) else build_pages()
    verses = {}
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
                        verses.setdefault((ch, v), []).append(rest)
                    continue
            verses.setdefault((ch, v), []).append(line)
    out = {}
    for (c, vv), parts in verses.items():
        t = clean(' '.join(parts))
        if len(t) > 3:
            out.setdefault(c, {})[vv] = t
    json.dump(out, open(OUT, 'w', encoding='utf-8'), ensure_ascii=False, indent=0)
    print('capitole: %d | versete: %d' % (len(out), sum(len(x) for x in out.values())))
    for c in sorted(out):
        ks = sorted(out[c])
        print('  cap%-3s %3d versete (max v%-3d) | v%d: %r' % (c, len(out[c]), ks[-1], ks[0], (out[c].get(ks[0]) or '')[:70]))


if __name__ == '__main__':
    main()
