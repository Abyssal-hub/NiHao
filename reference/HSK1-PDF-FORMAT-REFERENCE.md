# HSK1 Vocabulary PDF Format Reference

**Version:** 1.0  
**Last updated:** 2026-08-20  
**Purpose:** Document the visual layout and generation pipeline for HSK vocabulary PDFs.

---

## Design Philosophy

This format is optimized for **visual memorization** of Chinese characters while maintaining clean navigation (TOC, thumbnails). Key principles:

1. **Hanzi dominates the page** — large, centered, colored — the character is the focal point
2. **TOC stays readable** — headings contain English/pinyin, not hanzi, so thumbnails and table of contents remain scannable
3. **Card-like word blocks** — each entry is visually separated for focused study
4. **Examples are distinct** — shaded boxes separate examples from definitions
5. **Lessons are paginated** — page breaks between lessons for logical grouping

---

## Visual Layout (Per Word Entry)

```
┌─────────────────────────────────────┐
│  3. you                             │  ← Heading (TOC entry)
├─────────────────────────────────────┤
│                                     │
│           你                         │  ← 42pt hanzi, centered, red
│                                     │
├─────────────────────────────────────┤
│  Pinyin: nǐ                         │
│  Meaning: you                       │
├─────────────────────────────────────┤
│  ┌─────────────────────────────┐    │
│  │ Examples:                    │    │  ← Shaded framed box
│  │ • 你好！Nǐ hǎo!             │    │
│  │ • 你好吗？Nǐ hǎo ma?        │    │
│  └─────────────────────────────┘    │
│  Category: pronoun, basic           │
├─────────────────────────────────────┤
│  ─────────────────────────────────  │  ← Visual separator
└─────────────────────────────────────┘
```

---

## LaTeX Customization

The PDF is generated via **pandoc → xelatex** with a custom LaTeX header injected via `-H`.

### Header File (`*_header.tex`)

```latex
\usepackage{xeCJK}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{framed}
\usepackage{enumitem}

% Colors
\definecolor{hanzicolor}{RGB}{180, 30, 30}      % Dark red for hanzi
\definecolor{pinyincolor}{RGB}{60, 60, 60}       % Gray for examples
\definecolor{examplebg}{RGB}{250, 248, 245}      % Warm off-white box bg
\definecolor{rulecolor}{RGB}{200, 200, 200}      % Light gray separator

% \wordhanzi{字符} — large hanzi display (42pt, centered, red)
% ONLY used in body, NEVER in headings/TOC
\newcommand{\wordhanzi}[1]{%
  \begin{center}
    \vspace{4pt}
    {\fontsize{42}{50}\selectfont\color{hanzicolor}\textbf{#1}}
    \vspace{4pt}
  \end{center}
}

% wordexamples — shaded framed box for example sentences
\newenvironment{wordexamples}{%
  \begin{framed}
  \begin{minipage}{\linewidth}
  \small
  \color{pinyincolor}
  \textit{Examples:}
  \begin{itemize}[leftmargin=1em, itemsep=2pt]
}{%
  \end{itemize}
  \end{minipage}
  \end{framed}
  \vspace{4pt}
}

% \wordseparator — horizontal rule between entries
\newcommand{\wordseparator}{%
  \vspace{8pt}
  \noindent\textcolor{rulecolor}{\rule{\linewidth}{0.4pt}}
  \vspace{12pt}
}
```

### Pandoc Command

```bash
pandoc input.md \
  -o output.pdf \
  --pdf-engine=xelatex \
  -H header.tex \
  -V CJKmainfont="Noto Serif CJK SC" \
  -V geometry:margin=0.9in \
  --toc \
  --toc-depth=2
```

---

## Markdown Structure (Per Word)

```markdown
### 3. you              ← English in heading (appears in TOC)

\wordhanzi{你}         ← Raw LaTeX: 42pt hanzi in body only

**Pinyin:** nǐ

**Meaning:** you

\begin{wordexamples}   ← Raw LaTeX: shaded example box
  \item 你好！Nǐ hǎo! (Hello!)
  \item 你好吗？Nǐ hǎo ma? (How are you?)
\end{wordexamples}

**Category:** pronoun, basic

\wordseparator         ← Raw LaTeX: visual separator
```

**Critical rule:** Never put `\wordhanzi{}` inside a markdown heading (`###`). That would pollute the TOC with giant characters.

---

## PDF Naming Convention

| Type | Pattern | Example |
|------|---------|---------|
| Full database | `HSK1-Vocabulary-Full-All-Lessons.pdf` | — |
| Single lesson | `HSK1-Vocabulary-L{NN}-{Topic}.pdf` | `HSK1-Vocabulary-L05-Her-daughter-is-20-years-old-this-year.pdf` |
| Small range (≤3) | `HSK1-Vocabulary-L{NN}-{NN}-{First}-to-{Last}.pdf` | `HSK1-Vocabulary-L01-02-Hello-to-Thank-you.pdf` |
| Large range (>3) | `HSK1-Vocabulary-L{NN}-{NN}.pdf` | `HSK1-Vocabulary-L06-08.pdf` |

---

## Usage

### Generate full database
```bash
python3 gen_vocab_pdf.py
```

### Single lesson
```bash
python3 gen_vocab_pdf.py 5
```

### Lesson range
```bash
python3 gen_vocab_pdf.py 1 3
```

---

## How to Modify

### Change hanzi size
Edit `header.tex`, change this line:
```latex
{\fontsize{42}{50}\selectfont ...}   % 42pt font, 50pt line height
```

### Change hanzi color
Edit the RGB values:
```latex
\definecolor{hanzicolor}{RGB}{180, 30, 30}   % current: dark red
```

### Add tone colors
Extend the header with tone-specific commands:
```latex
\newcommand{\tonefirst}[1]{{\color{red}#1}}      % 1st tone: red
\newcommand{\tonesecond}[1]{{\color{orange}#1}}  % 2nd tone: orange
\newcommand{\tonethird}[1]{{\color{green}#1}}    % 3rd tone: green
\newcommand{\tonefourth}[1]{{\color{blue}#1}}    % 4th tone: blue
```

### Add stroke order
Requires external font or images. Not currently supported; would need:
1. Hanzi stroke order font (e.g., `TW-Kai`)
2. Or pre-generated SVGs inserted as images

---

## Files

| File | Purpose |
|------|---------|
| `gen_vocab_pdf.py` | Main generation script |
| `hsk1_vocabulary.json` | Source database |
| `*_header.tex` | Auto-generated LaTeX header per PDF |
| `*.md` | Auto-generated markdown intermediate |

---

## Source Database Schema (`hsk1_vocabulary.json`)

```json
{
  "metadata": {
    "course": "HSK1 Standard Course",
    "total_lessons": 8,
    "format_version": "1.0",
    "last_updated": "2026-08-17",
    "fields": ["hanzi", "pinyin", "english", "example_sentences", "lesson", "tags"]
  },
  "lessons": [
    {
      "lesson": 1,
      "title": "你好 (Hello)",
      "words": [
        {
          "hanzi": "你",
          "pinyin": "nǐ",
          "english": "you",
          "example_sentences": ["你好！Nǐ hǎo! (Hello!)"],
          "tags": ["pronoun", "basic"]
        }
      ]
    }
  ]
}
```

---

## Future Enhancements

- [ ] Tone color coding in pinyin
- [ ] Stroke order diagrams (SVG/PNG)
- [ ] Audio QR codes per word
- [ ] Spaced repetition markers (Leitner box)
- [ ] Handwriting practice grids (米字格)
