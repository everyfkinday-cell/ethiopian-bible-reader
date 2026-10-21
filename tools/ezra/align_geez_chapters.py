#!/usr/bin/env python3
"""Locate the 10 Ethiopic chapters of the Apocalypse of Ezra inside Charles's
English translation of the Greek 4 Ezra, by matching the (literal) Ethiopic
wording against the English through a hand-built glossary."""
import json, re, glob, sys, difflib

PAGES = json.load(open('/tmp/ezra_lines.json', encoding='utf-8'))

# --- glossary: Ge'ez transliteration -> English (literal equivalents) -------
G = {
    'wäʾəməzə': 'and it came to pass', 'fäläṭu': 'after', 'zäyäʿärəgə': 'these things',
    'mäsafənətä': 'earth', 'mäsafənətə': 'earth', 'ʾäbəyatä': 'quiet',
    'ʾäbäwihomu': 'mountains', 'bäbäḥəzäbihomu': 'still', 'ʾänəsətomu': 'air',
    'wädäqiqomu': 'stirred', 'ʾäwalədihomu': 'silence', 'ʾägəbərətihomu': 'of the earth',
    'ʾäʾəmatihomu': 'great', 'kaləʾu': 'after these things', 'yənəgərə': 'when',
    'nəguśä': 'king', 'nəguś': 'king', 'farəsə': 'babylon', 'mäfarəsə': 'babylon',
    'qirosə': 'thirtieth', 'qädami': 'thirtieth', 'ʿamätä': 'year', 'ʿamätə': 'year',
    'yəbäṣəḥə': 'lying', 'qalä': 'troubled', 'ʾəgəziʾäbəḥerə': 'spirit',
    'zänäbäbä': 'arose', 'ʾäfä': 'great', 'ʾerəməyasə': 'vision', 'mänəfäsä': 'thoughts',
    'wäsäbäkä': 'saw', 'ʾämä': 'and', 'ʾamä': 'and', 'mäṣəʾä': 'moses',
    'darəyosə': 'daniel', 'darəyo': 'daniel', 'ʾəgəziʾäbəḥerə': 'spirit',
    'fasika': 'earthquake', 'ʾämələku': 'land', 'ʾirusalemə': 'judah', 'ʾäśuru': 'terror',
    'läqädami': 'all', 'wärəḫə': 'land', 'wäʾäqämomu': 'round about', 'läkahənatə': 'it',
    'sisanəsə': 'prayer', 'mäləʾäkä': 'open', 'qele': 'field', 'wäzäfinəqisə': 'fasting',
    'wäsätäräburəzanisə': 'sins', 'mäqədäsə': 'holy', 'betä': 'house',
    'yona': 'jonathan', 'nasibu': 'nason', 'bäʾənətä': 'prayer', 'bəzuḫatə': 'writing',
    'wäʿäbiyatə': 'messenger', 'mäṣəḥäfä': 'book', 'mäṣəḥäf': 'book',
    'wälədä': 'son of', 'ʾäzarəyasə': 'azariah', 'ezerəyu': 'zerubbabel',
    'keləqəyusə': 'chelqias', 'salemə': 'salem', 'säduluqu': 'salu',
    'mäfarəsə': 'babylon', 'ʿəzəra': 'esdras', 'ezra': 'esdras',
    'wäʾibäləʿä': 'went up', 'wäisätəyä': 'sat', 'mayä': 'water', 'ʾənəzä': 'then',
    'yəlaḥu': 'went up', 'mäqədäsə': 'holy', 'ḥäge': 'spirit', 'wäzäkarəyasə': 'grieved',
    'näbiyatə': 'prophet', 'laʿəlä': 'to', 'ʾäyəhudə': 'judah', 'bäsəmä': 'in',
    'ʾəməlakä': 'city', 'mänəgəśətä': 'reign', 'mänəgəśət': 'reign',
    'lädarəyosə': 'of darius', 'tänäbäyu': 'was grieved', 'zärubabelə': 'zerubbabel',
    'säbəʾə': 'hundred', 'mäkwanənətä': 'degrees', 'medonə': 'between',
    'wämägäbətə': 'appearance', 'kwəlu': 'man', 'hənədäke': 'going',
    'mäfarəsə': 'babylon', 'mäṣəʾä': 'moses', 'məsəlä': 'like', 'räbänatä': 'lord',
    'gäbrä': 'entered', 'wälomuni': 'all', 'ʾəgəziʾomu': 'priest', 'mäläk': 'kingdom',
    'yəmäwəʾə': 'and', 'ʾänətəmu': 'said', 'ʿədäwə': 'said', 'ʾäkonu': 'him',
    'yəmäwəʿəwa': 'said', 'lämədərə': 'arose', 'wäyəkwenənəwa': 'arose',
    'mäqədäsə': 'holy', 'yona': 'jonathan', 'wäbä': 'and', 'bä': 'and',
    'lä': 'the', 'mä': 'the', 'nə': 'the', 'qä': 'the', 'wä': 'and', 'wa': 'and',
}

TOKEN = re.compile(r"[a-zA-Zäöüəʾʿɨʹ]+")


def eth_hints(abbr, chapter, n=45):
    j = json.load(open('/tmp/chapters/%s/%d.json' % (abbr, chapter), encoding='utf-8'))
    tr = ' '.join(w.get('t', '') for vs in j['verses'] for w in vs.get('words', []))
    out = []
    for w in TOKEN.findall(tr)[:n]:
        g = G.get(w.lower())
        if g:
            out.extend(g.split())
    return out


def build_english():
    """ordered list of (page, position_hint, text) for the whole 4 Ezra section"""
    rows = []
    for pi, pg in enumerate(PAGES):
        for li, l in enumerate(pg['lines']):
            rows.append((pi, li, l))
    return rows


def score_window(hints, words, start, width=170):
    seg = words[start:start + width]
    low = ' '.join(seg)
    h = [x for x in hints]
    # fraction of hint words present in the window
    hit = sum(1 for x in h if x in low)
    order = 0
    pos = -1
    for x in h:
        i = low.find(x, pos + 1)
        if i > 0:
            order += 1
            pos = i
    return hit, order


def main():
    rows = build_english()
    words = [w for _, _, l in rows for w in l.split()]
    # index from word position back to (page, line)
    widx = []
    for pi, li, l in rows:
        for w in l.split():
            widx.append((pi, li))
    for ch in range(1, 11):
        h = eth_hints('ApEz', ch)
        if not h:
            print('cap%-3d (fara indicii)' % ch)
            continue
        best = []
        for s in range(0, max(1, len(words) - 60), 12):
            hit, order = score_window(h, words, s)
            best.append((order, hit, s))
        best.sort(reverse=True)
        o, h2, s = best[0]
        pi, li = widx[min(s, len(widx) - 1)]
        print('cap%-3d hints=%2d -> pag %d lin %d | ordine=%d potriviri=%d | %r'
              % (ch, len(h), PAGES[pi]['idx'], li, o, h2, ' '.join(h[:7])))


if __name__ == '__main__':
    main()
