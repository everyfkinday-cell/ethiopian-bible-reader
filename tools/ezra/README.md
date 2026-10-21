# Apocalypse of Ezra (ApEz) — translation work-in-progress

## Status

**English shipped** (`reader/data/books/en/ApEz.js`, 10 chapters / 451 verses,
aligned verse-for-verse with the Ge'ez). Romanian and German are machine
translations of that English.

## Why it is hard (the real reason)

The Ethiopic `ApEz` (ራእየ፡ዕዝራ, 10 chapters / 451 verses) is a **literal
translation of the Greek 4 Esdras**, divided by the Ethiopic editors into
**10 chapters** (the Greek and Latin text has 16). The available English
translations are of the **Latin** recension, which differs and even omits
passages the Ethiopic has:

| Passage | Greek / Ethiopic | Latin-based English (KJV, Douay-Rheims) |
|---|---|---|
| 4 Esdras 3:1 | "In the thirtieth year **of the king** in Babylon" | "after the **ruin of the city**" |
| 4 Esdras 9:19 | "a great **earthquake in all the land of Judah**" | *absent* |
| 4 Esdras 12:2ff | "And I **saw Daniel**…" | *absent* |
| 4 Esdras 14:1 | "I Ezra was in the **holy temple** at Babylon, in the house of **Jonathan son of Nason**" | *absent* |

Verified by searching the Douay-Rheims JSON (`kjva_2esdras.json`): none of
`Azariah`, `Jonathan the son of Nason`, `all the land of Juda`, `I saw Daniel`
occur in the Latin-based text. Aligning the English to the Ethiopic by
chapter number alone would therefore produce **wrong scripture**.

The Ethiopic chapter order is also **non-monotonic** (it is a compilation of
excerpts): cap.2 = 4 Esdras 9:19, cap.3 = 3:1, cap.4 = 12:2, cap.6 = 13:1,
cap.8 = 13:57, cap.10 = 14:1.

## Sources already secured

| Source | Where | Use |
|---|---|---|
| Charles, *The Apocrypha and Pseudepigrapha of the Old Testament* vol. II (1913) | `charles2.pdf` / `charles2_djvu.xml` | **primary** — English translation of the **Greek** 4 Ezra, with the Greek chapter/verse in the running heads |
| van der Vlis, *Disputatio critica de Ezrae libro apocrypho* (1839) | `/tmp/vlis.txt` | Latin translation **of the Ethiopic** (cross-check) |
| Dillmann, *Veteris testamenti aethiopici tomus quintus* (1894) | `/tmp/dillmann.txt` | Ethiopic text (OCR unusable) |
| Douay-Rheims 4 Esdras (getbible `kjva/68`) | `/tmp/kjva_2esdras.json` | clean JSON, Latin recension — **proved insufficient** |

## What is already done

* `charles2_djvu.xml` (61 MB) downloaded; the two-column layout (Greek left,
  English right) separated **by content**, not by coordinates
  → `charles_4ezra_lines.json` (2364 lines, English column, noise stripped)
* `charles_4ezra_dump.txt` — the same text as a flat, greppable line list
* `extract_charles_4ezra.py` — PDF extraction with a font-size filter that
  removes Charles's critical notes (notes are 7.4–8.9 pt, main text 9.5–10.3 pt)
* `index_greek_verses.py` — rebuilds a Greek-numbered verse index
* `build_apez.py` — builds `data/books/en/ApEz.js`

## How the alignment was done

The English was taken as a **line range** per Ethiopic chapter (not a verse
index — the OCR interleaves Charles's notes with the text, which corrupts any
verse numbering).  The ranges were fixed by two independent checks:

1. **content** — the Ethiopic opening of each chapter matched a specific
   passage of the English (e.g. cap. 3 “In the thirtieth year, the king in
   Babylon, I was lying, troubled in his spirit” = 4 Esdras 3:1);
2. **length** — the Ethiopic chapter length (transliteration ÷ ~1.7) predicted
   the English length to within 8–46 characters out of 1 000–5 000 for seven of
   the ten chapters.

Final ranges (flat line numbers in `charles_4ezra_dump.txt`):

| Ge'ez | English | Greek |
|---|---|---|
| cap. 1 | title | — |
| cap. 2 | 1807–1868 | 4 Esdras 9:19 – 10:9 |
| cap. 3 | 893–921 | 4 Esdras 3:1–18 |
| cap. 4 | 2076–2092 | 4 Esdras 12:1–13 |
| cap. 5 | 2240–2318 | 4 Esdras 13:47 – 14:17 |
| cap. 6 | 2171–2224 | 4 Esdras 13:1–24 |
| cap. 7 | 2079–2115 | 4 Esdras 12:36–51 |
| cap. 8 | 2260–2277 | 4 Esdras 13:57 – 14:3 |
| cap. 9 | 2268–2363 | 4 Esdras 14:3–50 (the Ezra legend) |
| cap. 10 | 2264–2270 + DR 15:1–9 | 4 Esdras 14:1–2 + the conclusion |

**Known limitation:** the Ethiopic text follows the Ethiopic recension (E²/S),
Charles's English follows the Greek (M).  At the opening of some chapters the
two recensions differ (e.g. 14:1: the Ethiopic has “Ezra was in the holy temple
at Babylon, in the house of Jonathan son of Nason”, the Greek “after the third
day, while I sat under the oak”).  The English shipped is Charles's Greek text;
the Ethiopic original is shown side by side in the reader, so the reader can see
both recensions.  The same applies to 4 Esdras 3:1 (“of the king” vs “after the
ruin of the city”) and 9:19 (the earthquake, which the Latin text omits).

## Anchors already confirmed

| Ge'ez chapter | Greek passage | Confirmation |
|---|---|---|
| cap. 3 | 4 Esdras 3:1 ff. | "In the thirtieth year, the king in Babylon, I was lying, troubled in his spirit, and there arose a great vision" |
| cap. 6 | 4 Esdras 13:1 ff. | "And it came to pass after these things, when the earth was quiet, and the mountains were still, and the air not stirred" |
| cap. 8 | 4 Esdras 13:57 ff. | "And I went forth and walked in the field, greatly magnifying and praising the Most High" |
| cap. 10 | 4 Esdras 14:1 ff. | "And Ezra was in the holy temple in Babylon, in the house of Jonathan the son of Nason" |
| cap. 2 | 4 Esdras 9:19 ff. | "a great earthquake in all the land of Judah, and great terror round about it" |
| cap. 4 | 4 Esdras 12:2 ff. | "And I saw Daniel…" |

## Done

1. ✅ The 10 chapter ranges determined and verified (content + length).
2. ✅ Charles's English split into the Ethiopic verse counts
   (1 / 58 / 31 / 24 / 63 / 72 / 34 / 15 / 97 / 56).
3. ✅ `reader/data/books/en/ApEz.js` written in the app format
   `window.__EBT["en"]["ApEz"]=[[chapter,[[verse,"text"],…]],…]`.
4. ✅ Credit added to `reader/data/lang.js`.
5. ✅ Romanian and German: machine translation of that English (same method as
   the rest of the Romanian translation).

## License note

The Ge'ez text and the upstream corpus are **CC BY-NC-SA 4.0** (attribution,
non-commercial, share-alike). Charles's APOTP is public domain (1913). The
reader is a free, non-commercial project, so this is compatible — attribution
is added in `lang.js`.
