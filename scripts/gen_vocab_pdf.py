#!/usr/bin/env python3
"""Generate HSK1 vocabulary PDF from JSON database.

Usage:
    python3 gen_vocab_pdf.py              # full database
    python3 gen_vocab_pdf.py 1 3          # lessons 1-3 only
    python3 gen_vocab_pdf.py 5            # lesson 5 only
"""
import json
import sys
import subprocess
import os
import re

DB_PATH = "/root/.openclaw/workspace/hsk1_vocabulary.json"
OUTPUT_DIR = "/root/.openclaw/workspace"

def load_db():
    with open(DB_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def slugify(text):
    match = re.search(r'\(([^)]+)\)', text)
    if match:
        english = match.group(1)
    else:
        english = text
    english = re.sub(r'[^\w\s-]', '', english)
    english = re.sub(r'[-\s]+', '-', english).strip('-')
    return english

def build_filename(lessons, lesson_start=None, lesson_end=None):
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

def generate_markdown(data, lessons, lesson_start=None, lesson_end=None):
    lines = []
    
    if lesson_start is None:
        title = "HSK1 Vocabulary — Complete Database"
        subtitle = "All Lessons (1, 2, 3, 5, 6, 7, 8)"
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
        # Lesson heading — clean, no hanzi in TOC
        lines.append(f"## Lesson {lesson['lesson']}: {lesson['title']}")
        lines.append("")
        
        for i, word in enumerate(lesson["words"], 1):
            # Use raw LaTeX for the hanzi display — outside heading so TOC stays clean
            # The word entry number + English goes in heading (appears in TOC mini)
            # Hanzi appears large in body only
            lines.append(f"### {i}. {word['english']}")
            lines.append("")
            
            # Big hanzi — raw LaTeX, NOT in heading
            lines.append(f"\\wordhanzi{{{word['hanzi']}}}")
            lines.append("")
            lines.append(f"**Pinyin:** {word['pinyin']}")
            lines.append("")
            lines.append(f"**Meaning:** {word['english']}")
            lines.append("")
            
            if word["example_sentences"]:
                lines.append("\\begin{wordexamples}")
                for ex in word["example_sentences"]:
                    lines.append(f"  \\item {ex}")
                lines.append("\\end{wordexamples}")
                lines.append("")
            
            if word["tags"]:
                lines.append(f"**Category:** {', '.join(word['tags'])}")
                lines.append("")
            
            # Visual separator between words
            lines.append("\\wordseparator")
            lines.append("")
        
        lines.append("\\newpage")
        lines.append("")
    
    return "\n".join(lines)

def generate_pdf(md_content, output_pdf):
    md_path = output_pdf.replace(".pdf", ".md")
    header_path = output_pdf.replace(".pdf", "_header.tex")
    
    with open(md_path, "w", encoding="utf-8") as f:
        f.write(md_content)
    
    # LaTeX header with custom environment for vocabulary cards
    header = r"""\usepackage{xeCJK}
\usepackage{xcolor}
\usepackage{tikz}
\usepackage{framed}
\usepackage{enumitem}

% Colors
\definecolor{hanzicolor}{RGB}{180, 30, 30}
\definecolor{pinyincolor}{RGB}{60, 60, 60}
\definecolor{examplebg}{RGB}{250, 248, 245}
\definecolor{rulecolor}{RGB}{200, 200, 200}

% Large hanzi display — NOT in headings/TOC
\newcommand{\wordhanzi}[1]{%
  \begin{center}
    \vspace{4pt}
    {\fontsize{42}{50}\selectfont\color{hanzicolor}\textbf{#1}}
    \vspace{4pt}
  \end{center}
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

% Word separator
\newcommand{\wordseparator}{%
  \vspace{8pt}
  \noindent\textcolor{rulecolor}{\rule{\linewidth}{0.4pt}}
  \vspace{12pt}
}
"""
    with open(header_path, "w", encoding="utf-8") as f:
        f.write(header)
    
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
        print(f"PDF generation failed:\n{result.stderr}")
        return False
    
    size_kb = os.path.getsize(output_pdf) / 1024
    print(f"Generated: {os.path.basename(output_pdf)} ({size_kb:.1f} KB)")
    return True

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
    if lesson_start is not None:
        lessons = [l for l in lessons if l["lesson"] >= lesson_start]
    if lesson_end is not None:
        lessons = [l for l in lessons if l["lesson"] <= lesson_end]
    
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
