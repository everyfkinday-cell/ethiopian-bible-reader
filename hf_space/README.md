---
title: Ethiopian Bible Reader
emoji: 📖
colorFrom: yellow
colorTo: red
sdk: docker
app_port: 7860
pinned: false
---

# Ethiopian Orthodox Tewahedo Bible Reader

An offline-style HTML reader for the 81-book Ethiopian Orthodox Tewahedo (Ge'ez) canon.

**Features**
- 81 Ge'ez books, 1,806 chapters, 37,123 verses (Beta Masaheft / `cpradmin/ethiopian-bible`)
- Manuscript gallery (Wikimedia images + Archive.org full-reader links)
- Translations: **World English Bible** (EN), **Lutherbibel 1912** (DE),
  **Romanian** (machine translation of the WEB via Google Translate)
- Text-to-speech "audio book" player with per-language voice selection
- **7 neural Romanian voices** (Piper TTS): Mihai, Lili, Sanda, Raluca, Liana (medium & high quality)

**Credits**
- Ge'ez corpus: cpradmin/ethiopian-bible (Beta Masaheft, University of Hamburg)
- EN: World English Bible (public domain)
- DE: Lutherbibel 1912 (public domain)
- RO: machine translation — may contain errors; the Ge'ez original is always shown
- Neural voices: Piper (rhasspy/piper-voices, eduardem Romanian voices)
