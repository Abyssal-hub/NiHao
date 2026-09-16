#!/usr/bin/env python3
"""Enhanced HSK vocabulary PDF generator with tone colors, handwriting grids,
stroke order, Leitner markers, and audio QR codes.

Usage:
    python3 gen_vocab_pdf_v2.py              # full database
    python3 gen_vocab_pdf_v2.py 1 3          # lessons 1-3
    python3 gen_vocab_pdf_v2.py 5            # lesson 5 only
"""
import json
import sys
import subprocess
import os
import re

DB_PATH = "/root/.openclaw/workspace/vocabulary.json"
DB_FALLBACK = "/root/.openclaw/workspace/hsk1_vocabulary.json"
OUTPUT_DIR = "/root/.openclaw/workspace"

# Tone color mapping
TONE_COLORS = {
    1: '180, 30, 30',    # 1st tone: red
    2: '200, 100, 20',   # 2nd tone: orange
    3: '30, 130, 30',    # 3rd tone: green
    4: '30, 60, 180',    # 4th tone: blue
    0: '100, 100, 100',  # neutral: gray
}

# Tone-marked characters to tone number mapping
TONE_MAP = {
    'ā': 1, 'ē': 1, 'ī': 1, 'ō': 1, 'ū': 1, 'ǖ': 1,
    'á': 2, 'é': 2, 'í': 2, 'ó': 2, 'ú': 2, 'ǘ': 2,
    'ǎ': 3, 'ě': 3, 'ǐ': 3, 'ǒ': 3, 'ǔ': 3, 'ǚ': 3,
    'à': 4, 'è': 4, 'ì': 4, 'ò': 4, 'ù': 4, 'ǜ': 4,
}


def load_db():
    """Load vocabulary database, preferring v2.0."""
    if os.path.exists(DB_PATH):
        with open(DB_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    elif os.path.exists(DB_FALLBACK):
        with open(DB_FALLBACK, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        raise FileNotFoundError("No vocabulary database found")


def get_tone_number(char):
    """Get tone number for a pinyin character."""
    return TONE_MAP.get(char, 0)


def colorize_pinyin(pinyin):
    """Convert pinyin string to LaTeX with tone-colored syllables.
    
    Splits pinyin into syllables and wraps each in the appropriate tone color.
    Example: "nǐ hǎo" → "\\toneB{nǐ} \\toneB{hǎo}"
    """
    if not pinyin:
        return ""
    
    # Map tone numbers to LaTeX command names
    tone_cmds = {
        1: 'toneO',   # 1st tone: red
        2: 'toneA',   # 2nd tone: orange
        3: 'toneB',   # 3rd tone: green
        4: 'toneC',   # 4th tone: blue
        0: 'toneN',   # neutral: gray
    }
    
    result = []
    for syllable in pinyin.split():
        # Find the tone-marked character
        tone = 0
        for char in syllable:
            if char in TONE_MAP:
                tone = TONE_MAP[char]
                break
        
        cmd = tone_cmds.get(tone, 'toneN')
        result.append(f"\\{cmd}{{{syllable}}}")
    
    return ' '.join(result)


def generate_latex_header():
    """Generate the LaTeX header with all custom commands."""
    header = r"""\usepackage{xeCJK}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{framed}
\usepackage{enumitem}
\usepackage{amssymb}
\usepackage{pifont}

% Colors
\definecolor{hanzicolor}{RGB}{180, 30, 30}
\definecolor{pinyincolor}{RGB}{60, 60, 60}
\definecolor{examplebg}{RGB}{250, 248, 245}
\definecolor{rulecolor}{RGB}{200, 200, 200}

% Tone colors
\definecolor{tone1color}{RGB}{180, 30, 30}    % 1st tone: red
\definecolor{tone2color}{RGB}{200, 100, 20}   % 2nd tone: orange
\definecolor{tone3color}{RGB}{30, 130, 30}    % 3rd tone: green
\definecolor{tone4color}{RGB}{30, 60, 180}    % 4th tone: blue
\definecolor{tone0color}{RGB}{100, 100, 100}  % neutral: gray

% Tone coloring commands
\newcommand{\toneO}[1]{{\color{tone1color}#1}}   % 1st tone
\newcommand{\toneA}[1]{{\color{tone2color}#1}}   % 2nd tone
\newcommand{\toneB}[1]{{\color{tone3color}#1}}   % 3rd tone
\newcommand{\toneC}[1]{{\color{tone4color}#1}}   % 4th tone
\newcommand{\toneN}[1]{{\color{tone0color}#1}}   % neutral

% Aliases for numeric tones
\newcommand{\toneOcmd}[1]{\toneO{#1}}
\newcommand{\toneAcmd}[1]{\toneA{#1}}
\newcommand{\toneBcmd}[1]{\toneB{#1}}
\newcommand{\toneCcmd}[1]{\toneC{#1}}
\newcommand{\toneNcmd}[1]{\toneN{#1}}

% Large hanzi display
\newcommand{\wordhanzi}[1]{%
  \begin{center}
    \vspace{4pt}
    {\fontsize{42}{50}\selectfont\color{hanzicolor}\textbf{#1}}
    \vspace{4pt}
  \end{center}
}

% Practice grid (米字格) - 4x4 grid of squares with diagonal guidelines
\newcommand{\practicegrid}{%
  \begin{center}
  \begin{tikzpicture}[scale=0.35]
    \foreach \x in {0,1,2,3} {
      \foreach \y in {0,1,2,3} {
        % Square border (dotted)
        \draw[gray!50, dotted, line width=0.3pt] (\x,\y) rectangle (\x+1,\y+1);
        % Diagonal lines
        \draw[gray!30, dashed, line width=0.2pt] (\x,\y) -- (\x+1,\y+1);
        \draw[gray!30, dashed, line width=0.2pt] (\x,\y+1) -- (\x+1,\y);
        % Center lines
        \draw[gray!30, dashed, line width=0.2pt] (\x+0.5,\y) -- (\x+0.5,\y+1);
        \draw[gray!30, dashed, line width=0.2pt] (\x,\y+0.5) -- (\x+1,\y+0.5);
      }
    }
  \end{tikzpicture}
  \end{center}
  \vspace{2pt}
}

% Stroke order indicator
\newcommand{\strokeorder}[1]{%
  \vspace{2pt}
  \noindent\small\color{pinyincolor}\textit{Strokes: #1}
  \vspace{2pt}
}

% Leitner box indicator
\newcommand{\leitnerbox}[1]{%
  \ifnum#1=1 \textcolor{red!70!black}{\rule{8pt}{8pt}}%       Box 1: new (red)
  \else\ifnum#1=2 \textcolor{orange!80!black}{\rule{8pt}{8pt}}% Box 2: learning (orange)
  \else\ifnum#1=3 \textcolor{yellow!70!black}{\rule{8pt}{8pt}}% Box 3: review (yellow)
  \else\ifnum#1=4 \textcolor{green!60!black}{\rule{8pt}{8pt}}%  Box 4: mastered (green)
  \else\textcolor{red!70!black}{\rule{8pt}{8pt}}%               Default: new (red)
  \fi\fi\fi\fi
  \hspace{3pt}
}

% Example sentences block
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

% Audio QR code placeholder
\newcommand{\audioqr}[1]{%
  \vspace{2pt}
  \noindent\footnotesize\color{pinyincolor}\textit{Audio: #1}
  \vspace{2pt}
}

% Word separator
\newcommand{\wordseparator}{%
  \vspace{8pt}
  \noindent\textcolor{rulecolor}{\rule{\linewidth}{0.4pt}}
  \vspace{12pt}
}

% Grammar section
\newenvironment{grammarsection}{%
  \section*{Grammar Points}
  \begin{itemize}[leftmargin=1.5em, itemsep=4pt]
}{%
  \end{itemize}
}

% Measure word table
\newenvironment{measuretable}{%
  \section*{Measure Word Reference}
  \begin{tabular}{|l|l|p{5cm}|p{5cm}|}
  \hline
  \textbf{MW} & \textbf{Pinyin} & \textbf{Usage} & \textbf{Examples} \\\hline
}{%
  \end{tabular}
}
"""
    return header


def generate_markdown(data, lessons, lesson_start=None, lesson_end=None):
    """Generate markdown content for PDF."""
    lines = []
    
    # Title
    if lesson_start is None:
        title = "HSK1 Vocabulary — Complete Database"
        subtitle = "All Lessons"
    elif lesson_start == lesson_end:
        title = f"HSK1 Vocabulary — Lesson {lesson_start}"
        subtitle = f"{lessons[0]['title']}"
    else:
        title = f"HSK1 Vocabulary — Lessons {lesson_start}–{lesson_end}"
        lesson_titles = [f"L{l['lesson']}: {l['title']}" for l in lessons]
        subtitle = " | ".join(lesson_titles)
    
    lines.append(f"# {title}")
    lines.append("")
    lines.append(f"*{subtitle}*")
    lines.append("")
    
    total_words = sum(len(l["words"]) for l in lessons)
    lines.append(f"**Total Words: {total_words}**")
    lines.append("")
    lines.append("---")
    lines.append("")
    
    for lesson in lessons:
        lines.append(f"## Lesson {lesson['lesson']}: {lesson['title']}")
        lines.append("")
        
        for i, word in enumerate(lesson["words"], 1):
            # Word heading with Leitner box indicator and English
            leitner = word.get('leitner_box', 1)
            lines.append(f"### \\leitnerbox{{{leitner}}}{i}. {word['english']}")
            lines.append("")
            
            # Big hanzi
            lines.append(f"\\wordhanzi{{{word['hanzi']}}}")
            lines.append("")
            
            # Pinyin with tone colors
            colored_pinyin = colorize_pinyin(word['pinyin'])
            lines.append(f"**Pinyin:** {colored_pinyin}")
            lines.append("")
            lines.append(f"**Meaning:** {word['english']}")
            lines.append("")
            
            # Stroke order (if available)
            stroke_count = word.get('stroke_count')
            if stroke_count:
                lines.append(f"\\strokeorder{{{stroke_count}}}")
                lines.append("")
            
            # Examples
            if word.get("example_sentences"):
                lines.append("\\begin{wordexamples}")
                for ex in word["example_sentences"]:
                    lines.append(f"  \\item {ex}")
                lines.append("\\end{wordexamples}")
                lines.append("")
            
            # Category/Tags
            if word.get("tags"):
                lines.append(f"**Category:** {', '.join(word['tags'])}")
                lines.append("")
            
            # Audio QR placeholder
            audio_url = word.get('audio_url')
            if audio_url:
                lines.append(f"\\audioqr{{{audio_url}}}")
                lines.append("")
            
            # Practice grid (handwriting practice)
            lines.append("\\practicegrid")
            lines.append("")
            
            # Separator
            lines.append("\\wordseparator")
            lines.append("")
        
        # Grammar points for this lesson
        grammar_points = lesson.get('grammar_points', [])
        if grammar_points:
            lines.append("\\begin{grammarsection}")
            for gp in grammar_points:
                pattern = gp.get('pattern', '')
                explanation = gp.get('explanation', '')
                examples = gp.get('examples', [])
                
                lines.append(f"  \\item \\textbf{{{pattern}}}")
                if explanation:
                    lines.append(f"  \\\\\\  {explanation}")
                if examples:
                    lines.append("  \\begin{itemize}")
                    for ex in examples:
                        lines.append(f"    \\item {ex}")
                    lines.append("  \\end{itemize}")
            lines.append("\\end{grammarsection}")
            lines.append("")
        
        lines.append("\\newpage")
        lines.append("")
    
    # Measure word reference table (only for full database)
    if lesson_start is None and data.get('measure_words'):
        lines.append("\\begin{measuretable}")
        for mw in data['measure_words']:
            hanzi = mw.get('hanzi', '')
            pinyin = mw.get('pinyin', '')
            usage = mw.get('usage', '')
            examples = ' | '.join(mw.get('examples', []))
            lines.append(f"{hanzi} & {pinyin} & {usage} & {examples} \\\\")
            lines.append("\\hline")
        lines.append("\\end{measuretable}")
    
    return "\n".join(lines)


def generate_pdf(md_content, output_pdf):
    """Generate PDF from markdown content."""
    md_path = output_pdf.replace(".pdf", ".md")
    header_path = output_pdf.replace(".pdf", "_header.tex")
    
    # Write markdown
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # Write LaTeX header
    header = generate_latex_header()
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(header)
    
    # Build pandoc command
    cmd = [
        "pandoc", md_path,
        "-o", output_pdf,
        "--pdf-engine=xelatex",
        "-H", header_path,
        "-V", "CJKmainfont=Noto Serif CJK SC",
        "-V", "geometry:margin=0.9in",
        "--toc",
        "--toc-depth=2"
    ]
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    if result.returncode != 0:
        print(f"PDF generation failed:\n{result.stderr[:2000]}")
        return False
    
    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"Generated: {os.path.basename(output_pdf)} ({size_kb:.1f} KB)")
    return True


def slugify(text):
    """Convert lesson title to filename slug."""
    match = re.search(r'\(([^)]+)\)', text)
    if match:
        english = match.group(1)
    else:
        english = text
    english = re.sub(r'[^\w\s-]', '', english)
    english = re.sub(r'[-\s]+', '-', english).strip('-')
    return english


def build_filename(lessons, lesson_start=None, lesson_end=None):
    """Build output filename based on lesson range."""
    if lesson_start is None and lesson_end is None:
        return os.path.join(OUTPUT_DIR, "HSK1-Vocabulary-Full-All-Lessons.pdf")
    if lesson_start == lesson_end:
        lesson = lessons[0]
        title_slug = slugify(lesson['title'])
        return os.path.join(OUTPUT_DIR, f"HSK1-Vocabulary-L{lesson_start:02d}-{title_slug}.pdf")
    else:
        first_title = slugify(lessons[0]['title'])
        last_title = slugify(lessons[-1]['title'])
        if len(lessons) <= 3:
            return os.path.join(OUTPUT_DIR, f"HSK1-Vocabulary-L{lesson_start:02d}-{lesson_end:02d}-{first_title}-to-{last_title}.pdf")
        else:
            return os.path.join(OUTPUT_DIR, f"HSK1-Vocabulary-L{lesson_start:02d}-{lesson_end:02d}.pdf")


def main():
    data = load_db()
    
    lesson_start = None
    lesson_end = None
    
    if len(sys.argv) >= 2:
        lesson_start = int(sys.argv[1])
        lesson_end = lesson_start
    if len(sys.argv) >= 3:
        lesson_end = int(sys.argv[2])
    
    lessons = data["lessons"]
    
    # Filter by lesson range (handle both int and string lesson numbers)
    def get_lesson_num(lesson):
        l = lesson.get("lesson", 0)
        return l if isinstance(l, int) else 0
    
    if lesson_start is not None:
        lessons = [l for l in lessons if get_lesson_num(l) >= lesson_start]
    if lesson_end is not None:
        lessons = [l for l in lessons if get_lesson_num(l) <= lesson_end]
    
    if not lessons:
        print("No lessons found in that range.")
        sys.exit(1)
    
    output_pdf = build_filename(lessons, lesson_start, lesson_end)
    md = generate_markdown(data, lessons, lesson_start, lesson_end)
    success = generate_pdf(md, output_pdf)
    
    if success:
        print(f"Done: {output_pdf}")
    else:
        sys.exit(1)


if __name__ == "__main__":
    main()
