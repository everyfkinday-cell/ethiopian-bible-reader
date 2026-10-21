# Apocalypse of Ezra (ApEz) — translation work-in-progress

## Status

**Not yet shipped.** The English translation of the Ethiopian `ApEz` book is
blocked by a *textual*, not a technical, problem. Everything needed to finish
it is already downloaded and extracted into this folder.

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
* `extract_charles_4ezra.py` — PDF extraction with a font-size filter that
  removes Charles's critical notes (notes are 7.4–8.9 pt, main text 9.5–10.3 pt)
* `index_greek_verses.py` — rebuilds a Greek-numbered verse index
* `align_geez_chapters.py` — locates the 10 Ethiopic chapters in the English

## Anchors already confirmed

| Ge'ez chapter | Greek passage | Confirmation |
|---|---|---|
| cap. 3 | 4 Esdras 3:1 ff. | "In the thirtieth year, the king in Babylon, I was lying, troubled in his spirit, and there arose a great vision" |
| cap. 6 | 4 Esdras 13:1 ff. | "And it came to pass after these things, when the earth was quiet, and the mountains were still, and the air not stirred" |
| cap. 8 | 4 Esdras 13:57 ff. | "And I went forth and walked in the field, greatly magnifying and praising the Most High" |
| cap. 10 | 4 Esdras 14:1 ff. | "And Ezra was in the holy temple in Babylon, in the house of Jonathan the son of Nason" |
| cap. 2 | 4 Esdras 9:19 ff. | "a great earthquake in all the land of Judah, and great terror round about it" |
| cap. 4 | 4 Esdras 12:2 ff. | "And I saw Daniel…" |

## Remaining work (well-defined, ~1–2 h)

1. Fix the 4 anchors above plus **cap. 5, 7, 9** in the English text
   (each needs a manual read of the English around the candidate position).
2. For each Ge'ez chapter take the Greek verse range and split Charles's
   English into the Ge'ez's verse count (1 / 58 / 31 / 24 / 63 / 72 / 34 / 15 / 97 / 56).
3. Write `reader/data/books/en/ApEz.js` in the app format
   `window.__EBT["en"]["ApEz"]=[[chapter,[[verse,"text"],…]],…]`.
4. Add the credit to `reader/data/lang.js`:
   "Apocalypse of Ezra — English translation of the Greek text after
   R. H. Charles, *The Apocrypha and Pseudepigrapha of the Old Testament* II (1913), PD;
   aligned with the Ethiopic (IAM corpus, CC BY-NC-SA 4.0)."

## License note

The Ge'ez text and the upstream corpus are **CC BY-NC-SA 4.0** (attribution,
non-commercial, share-alike). Charles's APOTP is public domain (1913). The
reader is a free, non-commercial project, so this is compatible — attribution
is added in `lang.js`.
