# NiHao (你好)

**Automated Chinese Vocabulary Extraction & Study Material Generation**

NiHao is a toolchain that extracts vocabulary from HSK1 Standard Course PPTX files, builds a structured database, and generates professionally formatted study PDFs with tone colors, handwriting practice grids, grammar points, and spaced repetition markers.

## Features

- **Automated PPTX Extraction** — Drop a PPTX file, get structured vocabulary
- **Tone-Colored Pinyin** — Each syllable colored by tone (1st=red, 2nd=orange, 3rd=green, 4th=blue, neutral=gray)
- **Handwriting Practice Grids** (米字格) — Dotted squares with diagonal guidelines for character practice
- **Grammar Points** — Sentence patterns with explanations and examples per lesson
- **Measure Word Reference** — Complete index of HSK1 measure words with usage rules
- **Leitner Box Markers** — Spaced repetition tracking (red→orange→yellow→green)
- **Audio QR Placeholders** — Ready for future audio integration
- **Multiple Output Formats** — Full database PDFs, single-lesson PDFs, or custom ranges

## Quick Start

### Extract vocabulary from a new PPTX lesson

```bash
python3 scripts/auto_extract.py source-pptx/your_lesson.pptx --lesson 4 --merge data/vocabulary.json
```

### Generate PDFs

```bash
# Full database (all lessons)
python3 scripts/gen_vocab_pdf_v2.py

# Single lesson
python3 scripts/gen_vocab_pdf_v2.py 5

# Lesson range
python3 scripts/gen_vocab_pdf_v2.py 1 3
```

## Project Structure

```
nihao/
├── data/                  # Vocabulary databases
│   ├── vocabulary.json       # Master database (v2.0, 118 words)
│   ├── hsk1_vocabulary.json  # Legacy v1.0 format
│   ├── grammar_points.json   # 15 grammar patterns
│   └── measure_words.json    # 10 measure words
├── scripts/               # Processing pipeline
│   ├── auto_extract.py       # PPTX → vocabulary (automated)
│   ├── gen_vocab_pdf_v2.py   # Enhanced PDF generator
│   ├── gen_vocab_pdf.py      # Original PDF generator
│   ├── extract_pptx.py       # Raw PPTX text extraction
│   ├── build_vocab.py        # Legacy DB builder
│   ├── upgrade_schema.py     # v1.0 → v2.0 migration
│   ├── merge_extensions.py   # Merge grammar/measure words
│   └── audit_vocab.py        # Database validation
├── output/                # Generated PDFs
├── reference/             # Documentation
│   └── HSK1-PDF-FORMAT-REFERENCE.md
└── source-pptx/           # Source PPTX files
```

## Database Schema (v2.0)

```json
{
  "metadata": {
    "course": "HSK1 Standard Course",
    "level": "HSK1",
    "hsk_level": 1,
    "format_version": "2.0",
    "total_lessons": 9,
    "last_updated": "2026-09-15"
  },
  "lessons": [{
    "lesson": 1,
    "title": "你好 (Hello)",
    "words": [{
      "hanzi": "你",
      "pinyin": "nǐ",
      "english": "you",
      "example_sentences": ["你好！Nǐ hǎo! (Hello!)"],
      "tags": ["pronoun", "basic"],
      "leitner_box": 1,
      "stroke_order": null,
      "audio_url": null,
      "hsk_level": 1
    }],
    "grammar_points": [{
      "pattern": "Sub + 很 + Adj",
      "title": "很 as degree adverb",
      "explanation": "...",
      "examples": ["我很好。Wǒ hěn hǎo."]
    }]
  }],
  "measure_words": [...]
}
```

## Current Status

| Lesson | Words | Grammar Points | Status |
|--------|-------|---------------|--------|
| L1 你好 | 9 | 2 | ✅ Complete |
| L2 谢谢 | 15 | 1 | ✅ Complete |
| L3 你叫什么名字 | 12 | 2 | ✅ Complete |
| L4 | — | — | 🔴 PPTX missing |
| L5 她女儿今年二十岁 | 18 | 3 | ✅ Complete |
| L6 我会说汉语 | 14 | 2 | ✅ Complete |
| L7 今天几号 | 12 | 2 | ✅ Complete |
| L8 我想喝茶 | 18 | 2 | ✅ Complete |
| L9 你儿子在哪儿工作 | 15 | 1 | ✅ Complete |
| L10 | 5 (placeholder) | 0 | 🟡 Pending real PPTX |
| Appendix | 5 | 0 | ✅ Supplementary |

**Total: 118 words, 15 grammar points, 10 measure words**

## Dependencies

- Python 3.10+
- `python-pptx` — PPTX file parsing
- `pandoc` — Markdown → PDF conversion
- `xelatex` (TeX Live) — PDF typesetting with CJK support
- `Noto Serif CJK SC` font — Chinese character rendering

```bash
# Ubuntu/Debian
sudo apt install pandoc texlive-xetex texlive-lang-chinese fonts-noto-cjk
pip3 install python-pptx
```

## Roadmap

- [ ] Lesson 4 PPTX (when available)
- [ ] Lesson 10 real vocabulary (replace placeholder)
- [ ] Stroke order diagrams (SVG rendering)
- [ ] Audio QR codes (TTS integration)
- [ ] HSK2 support (schema ready)
- [ ] Web-based flashcard UI
- [ ] Anki deck export

## License

MIT
