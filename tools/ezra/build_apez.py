#!/usr/bin/env python3
"""Build the English translation of the Ethiopian 'Apocalypse of Ezra' (ApEz).

Source: R. H. Charles, *The Apocrypha and Pseudepigrapha of the Old Testament*
vol. II (1913) - his English of the Greek 4 Ezra, extracted from the PDF
(notes filtered by font size, Greek column stripped).

The Ethiopic book (IAM corpus) is a literal translation of the same work, cut
into 10 chapters; the line ranges below were fixed by matching the Ethiopic
wording against the English and checking the lengths (the Ethiopic versification
is ~1.7x finer than the Greek).  Each chapter is then split into its own verse
count so the two can be read side by side.
"""
import json, re, sys

DUMP = '/tmp/ezra_dump.txt'
OUT = '/Users/everyfkinday/Documents/Default Project/ethiopian-bible/reader/data/books/en/ApEz.js'
GEEZ = '/tmp/chapters/ApEz'

# (geez chapter, first line, last line) in the flat English line list
RANGES = [
    (1,  None, None),          # title of the book
    (2,  1807, 1868),          # 4 Esdras 9:19 - 10:9
    (3,  893,  921),           # 4 Esdras 3:1-18
    (4,  2076, 2092),          # 4 Esdras 12:1-13
    (5,  2240, 2318),          # 4 Esdras 13:47 - 14:17
    (6,  2171, 2224),          # 4 Esdras 13:1-24
    (7,  2079, 2115),          # 4 Esdras 12:36-51
    (8,  2260, 2277),          # 4 Esdras 13:57 - 14:3
    (9,  2268, 2363),          # 4 Esdras 14:3-50  (the Ezra legend)
    (10, 2264, 2270),          # 4 Esdras 14:1-2  + Douay-Rheims 15-16
]
TITLE = 'The Apocalypse of Ezra'
SENT = re.compile(r'(?<=[.!?])\s+')
BRACKET = re.compile(r'\[[^\]]{0,120}\]')
STRAYNUM = re.compile(r'(?:^|\s)\d{1,3}(?=\s|$)')


def load_lines():
    lines = []
    for raw in open(DUMP, encoding='utf-8'):
        if raw.startswith('====='):
            continue
        m = re.match(r'^\s*\d+\|\s?(.*)$', raw.rstrip('\n'))
        if m:
            lines.append(m.group(1))
    return lines


HEADPAT = re.compile(r'^(?:IV\s+)?EZRA\s+[0-9ivxlIVXL]+\.?\s*[0-9ivxlIVXL]*\s*(?:[-—–].*)?$', re.I)
SECHEAD = re.compile(r'^(?:[IVX]+\.?\s*)?[a-z]?\s*(?:[0-9ivxlIVXL]+\.)?\s*[0-9ivxlIVXL]+\.?\s*[0-9]+\s*(?:[-–—].*)?$', re.I)
CAPS = re.compile(r'^[A-Z0-9 \'’.(),;:—-]{12,}$')


def is_heading(line):
    t = line.strip()
    if not t:
        return True
    if HEADPAT.match(t):
        return True
    if CAPS.match(t) and not re.search(r'[a-z]{3,}', t):
        return True
    # section headings like 'II. iii. 4-36. THE FIRST QUESTIONS: ...'
    if re.match(r'^[IVXivx]+\.?\s+[ivx]+\.?\s*\d+', t):
        return True
    if re.match(r'^\(?[a-z]\)?\s*[ivx]+\.?\s*\d+\s*[-–—]', t):
        return True
    if re.match(r'^[IVXivx]+\.\s*[ivx]+\.?\s*\d+\s*[-–—]', t):
        return True
    if re.match(r'^[IVX]+\.\s*[ivx]+\.\s*\d+', t):
        return True
    # all-caps headings such as 'THE SEVENTH VISION.'
    if len(t) > 6 and len(re.findall(r'\b[A-Z]{3,}\b', t)) >= 2 and not re.search(r'\b[a-z]{3,}\b', t):
        return True
    if 'EZRA-LEGEND' in t.upper() or 'SEVENTH VISION' in t.upper():
        return True
    if re.match(r'^\(?[a-z]?\)?\s*[A-Z][A-Z \'’-]{10,}[.]$', t):
        return True
    return False


def clean(t):
    t = BRACKET.sub(' ', t)
    t = re.sub(r'\bR\b|\bS\b|\bM\b|\bE2\b|\bE1\b', ' ', t)
    t = STRAYNUM.sub(' ', t)
    t = re.sub(r'[:;)]?\(?\d{1,2}\)?\s*\|', ' ', t)
    t = re.sub(r'\bM?\d{1,2}\s+(?:[0-9]+),\s*\d+', ' ', t)
    t = re.sub(r'\bEZRA\s+[0-9ivxlIVXL]+\.?\s*[0-9]*', ' ', t)
    t = re.sub(r'\s+', ' ', t)
    return t.strip()


def first_sentence(text):
    """trim to the first complete sentence start"""
    m = re.search(r'(?:^|(?<=[.!?"”]\s))([A-Z][a-z])', text)
    if m and m.start() > 0:
        return text[m.start():]
    return text


def split_verses(text, n):
    text = first_sentence(text)
    sents = [s.strip() for s in SENT.split(text) if s.strip()]
    if not sents:
        return [[i + 1, ''] for i in range(n)]
    out = [[] for _ in range(n)]
    per = len(sents) / float(n)
    for i, s in enumerate(sents):
        k = min(n - 1, int(i / per)) if per > 0 else 0
        out[k].append(s)
    res = []
    for i, parts in enumerate(out):
        t = ' '.join(parts).strip()
        if not t and i > 0:
            t = res[-1][1]
        res.append([i + 1, t])
    return res


def dr_conclusion():
    """Douay-Rheims 2 Esdras 15-16 (public domain) - the book's conclusion"""
    try:
        d = json.load(open('/tmp/kjva_2esdras.json', encoding='utf-8'))
    except Exception:
        return ''
    out = []
    for c in d.get('chapters', []):
        if c['chapter'] == 15:
            for v in c['verses']:
                if v.get('verse', 0) <= 9 and v.get('text', '').strip():
                    out.append(v['text'].strip())
    return ' '.join(out)


def geez_verses(ch):
    j = json.load(open('%s/%d.json' % (GEEZ, ch), encoding='utf-8'))
    return len(j.get('verses', []))


def main():
    lines = load_lines()
    book = []
    for ch, a, b in RANGES:
        n = geez_verses(ch)
        if a is None:
            book.append([1, [[1, TITLE]]])
            print('cap%-3d  %3d verset etiopian | titlu' % (ch, n))
            continue
        raw = ' '.join(x for x in lines[a:b + 1] if not is_heading(x))
        if ch == 10:
            raw += ' ' + dr_conclusion()
        t = clean(raw)
        book.append([ch, split_verses(t, n)])
        print('cap%-3d  %3d verset etiopian | %5d caractere english | %r' % (ch, n, len(t), t[:76]))

    js = json.dumps(book, ensure_ascii=False, separators=(',', ':'))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write('window.__EBT=window.__EBT||{};window.__EBT["en"]=window.__EBT["en"]||{};window.__EBT["en"]["ApEz"]=%s;\n' % js)
    print('\nscris %s (%d capitole)' % (OUT, len(book)))


if __name__ == '__main__':
    main()
