#!/usr/bin/env python3
"""PDF vocabulary extraction engine for the NiHao project.

Usage:
    python3 pdf_extract.py <pdf_file> --lesson N [--title "Title"] [--merge vocabulary.json]

Supports born-digital PDFs (text layer present). Two extraction strategies:

  A) TABLE — HSK textbook vocab tables (生词 | 拼音 | 词性 | 注释 columns).
     pdfplumber's table extraction handles ruled tables; a text-strategy
     fallback catches tables without ruling lines.

  B) LIST  — line-clustered vocab lists: hanzi + pinyin + meaning per line.

Scanned (image-only) PDFs are rejected with a clear message — OCR is not
supported.

Output word schema matches vocabulary.json v2.0 (vietnamese left null —
fill separately or ask the assistant to translate).
"""
import argparse
import json
import re
import sys

try:
    import pdfplumber
except ImportError:
    sys.exit("pdfplumber is required: pip install pdfplumber")

TONE_CHARS = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'
CJK_RE = re.compile(r'[\u4e00-\u9fff]')

POS_MAP = {
    '名': 'noun', '动': 'verb', '形': 'adjective', '代': 'pronoun',
    '副': 'adverb', '介': 'preposition', '量': 'measure_word',
    '助': 'particle', '叹': 'expression', '连': 'conjunction',
    '数': 'number', '词': 'particle',
}

TAG_WORDS = {
    'pronoun': {'you', 'i', 'me', 'he', 'him', 'she', 'her', 'we', 'us', 'they', 'them',
                'this', 'that', 'these', 'those', 'it'},
    'question': {'what', 'which', 'who', 'where', 'when', 'why', 'how', 'how many',
                 'how much', 'how old'},
    'time': {'today', 'tomorrow', 'yesterday', 'now', 'morning', 'afternoon', 'evening',
             'noon', 'night', 'year', 'month', 'week', 'day', 'hour', 'minute', 'o\'clock',
             'date', 'birthday', 'time', 'moment'},
    'family': {'father', 'mother', 'dad', 'mom', 'brother', 'sister', 'son', 'daughter',
               'grandfather', 'grandmother', 'grandpa', 'grandma', 'wife', 'husband',
               'family', 'home', 'older', 'younger', 'paternal'},
    'food': {'eat', 'drink', 'tea', 'rice', 'food', 'dish', 'delicious', 'meal', 'noodle',
             'fruit', 'apple', 'banana', 'coffee', 'water', 'milk', 'restaurant', 'cook'},
    'place': {'china', 'beijing', 'america', 'school', 'hospital', 'bank', 'store', 'shop',
              'here', 'there', 'in', 'on', 'at', 'front', 'back', 'above', 'below', 'under',
              'country', 'city'},
    'profession': {'teacher', 'student', 'doctor', 'worker', 'clerk', 'seller', 'profession',
                   'job', 'work'},
    'money': {'money', 'buy', 'sell', 'yuan', 'dollar', 'expensive', 'cheap', 'price', 'pay',
              'much'},
    'language': {'chinese', 'english', 'french', 'japanese', 'language', 'speak', 'write',
                 'read', 'character', 'word', 'book', 'learn', 'study'},
    'travel': {'go', 'come', 'return', 'travel', 'train', 'car', 'bus', 'plane', 'ticket'},
    'number': {'one', 'two', 'three', 'four', 'five', 'six', 'seven', 'eight', 'nine', 'ten'},
}

MEASURE_WORDS = {'个', '口', '岁', '块', '杯', '本', '只', '张', '件', '把', '条', '瓶',
                 '双', '层', '顿', '家', '些', '点', '分'}

MAX_WORD_LEN = 4  # longest HSK1 words (银行职员); guards against dialogue lines

ENGLISH_STOP = {'the', 'to', 'of', 'a', 'an', 'and', 'or', 'in', 'on', 'at', 'is', 'are',
                'am', 'be', 'it', 'this', 'that', 'with', 'for', 's', 't', 'd'}

SYLLABLE_RE = re.compile(r'^[a-zü]{1,6}$')


def is_lenient_pinyin(token):
    """Toneless pinyin like 'ba' or 'zhèr' (letters valid in pinyin)."""
    token = token.lower().replace(':', '').replace(';', '').strip('.')
    if not token or token in ENGLISH_STOP:
        return False
    syllables = re.split(r"[ '\-\u2019]+", token)
    return all(SYLLABLE_RE.match(s) for s in syllables if s)


def is_pinyin(text):
    return any(c in TONE_CHARS for c in text)


def is_hanzi(text):
    cleaned = re.sub(r'[，。！？；：、·…\s\*\[\]（）()【】]', '', text)
    return bool(cleaned) and all('\u4e00' <= c <= '\u9fff' for c in cleaned)


def is_english(text):
    if CJK_RE.search(text):
        return False
    cleaned = re.sub(r"[\s\-'/.,!?()0-9]", '', text)
    return bool(cleaned) and cleaned.isascii()


def auto_tag(english, hanzi):
    eng = english.lower()
    tags = []
    words = set(eng.split())
    if any(q in eng for q in TAG_WORDS['question']):
        tags.append('question')
    if words & TAG_WORDS['pronoun']:
        tags.append('pronoun')
    if any(w in TAG_WORDS['number'] for w in words) or any(
            '\u4e00' <= c <= '\u4e09' for c in hanzi) and len(hanzi) <= 2:
        tags.append('number')
    if hanzi in MEASURE_WORDS:
        tags.append('measure_word')
    if any(t in eng for t in TAG_WORDS['time']):
        tags.append('time')
    if any(f in eng for f in TAG_WORDS['family']):
        tags.append('family')
    if any(f in eng for f in TAG_WORDS['food']):
        tags.append('food')
    if any(p in eng for p in TAG_WORDS['place']):
        tags.append('place')
    if any(p in eng for p in TAG_WORDS['profession']):
        tags.append('profession')
    if any(m in eng for m in TAG_WORDS['money']):
        tags.append('money')
    if any(l in eng for l in TAG_WORDS['language']):
        tags.append('language')
    if any(t in eng for t in TAG_WORDS['travel']):
        tags.append('travel')
    if not tags:
        tags.append('noun')
    return list(dict.fromkeys(tags))


def make_word(hanzi, pinyin, english, pos=None):
    tags = []
    if pos and pos in POS_MAP.values():
        tags.append(pos)
    else:
        mapped = POS_MAP.get(pos or '', None)
        tags.append(mapped if mapped else auto_tag(english, hanzi)[0])
    tags.extend(t for t in auto_tag(english, hanzi) if t not in tags)
    tags.append('core')
    return {
        'hanzi': hanzi,
        'pinyin': pinyin.strip(),
        'english': english.strip(),
        'vietnamese': None,
        'example_sentences': [],
        'tags': list(dict.fromkeys(tags)),
        'leitner_box': 1,
        'stroke_order': None,
        'audio_url': None,
        'hsk_level': 1,
    }


# ---------- Strategy A: tables ----------

POS_CHARS = set('名动形代副介量助叹连数')  # single-char POS column values


def english_from_lines(lines, pinyin_first, table_english=''):
    """Rebuild a row's English from raw token lines (complete, unwrapped text).

    Table cells often truncate wrapped text; the token lines hold everything.
    Falls back to the table's own english when the line can't be located.
    """
    for line in lines:
        texts = [t['text'] for t in line]
        if not any(pinyin_first in t for t in texts):
            continue
        ordered = sorted(line, key=lambda t: t['x0'])
        px1 = None
        for t in ordered:
            if pinyin_first in t['text']:
                px1 = t['x1']
        if px1 is None:
            continue
        eng = [t['text'] for t in ordered if t['x0'] > px1 + 30 and is_english(t['text'])]
        joined = ' '.join(eng)
        if len(joined) >= len(table_english):
            return joined
    return table_english


def extract_from_tables(page, lines=None):
    """Try line-based then text-based table extraction; return word dicts."""
    words = []
    tables = []
    try:
        tables = page.extract_tables() or []
    except Exception:
        pass
    if not tables:
        try:
            settings = {'vertical_strategy': 'text', 'horizontal_strategy': 'text',
                        'snap_tolerance': 3, 'join_tolerance': 3}
            tables = page.extract_tables(settings) or []
        except Exception:
            pass

    for table in tables:
        rows = [[(c or '').strip() for c in row] for row in table if row]
        rows = [r for r in rows if any(r)]
        if len(rows) < 2:
            continue
        header = rows[0]
        # Identify columns by header content, else by content shape
        col_role = {}
        for idx, cell in enumerate(header):
            if '生词' in cell or cell == '词':
                col_role['hanzi'] = idx
            elif '拼音' in cell:
                col_role['pinyin'] = idx
            elif '词性' in cell or cell == 'POS':
                col_role['pos'] = idx
            elif '注释' in cell or '英文' in cell or '意思' in cell or cell == 'English':
                col_role['english'] = idx
        # Fallback: detect by scanning data rows
        if 'hanzi' not in col_role or 'pinyin' not in col_role:
            best = None
            for row in rows[1:]:
                roles = {}
                for idx, cell in enumerate(row):
                    if is_hanzi(cell) and 'hanzi' not in roles:
                        roles['hanzi'] = idx
                    elif is_pinyin(cell) and 'pinyin' not in roles:
                        roles['pinyin'] = idx
                    elif is_english(cell) and 'english' not in roles:
                        roles['english'] = idx
                if 'hanzi' in roles and 'pinyin' in roles:
                    best = roles
                    break
            if best:
                col_role = {**best, **col_role}
        if 'hanzi' not in col_role or 'pinyin' not in col_role:
            continue
        pos_idx = col_role.get('pos')
        eng_idx = col_role.get('english')
        data_rows = rows[1:] if ('生词' in ''.join(header) or '拼音' in ''.join(header)) else rows
        for row in data_rows:
            def cell(i):
                return row[i] if i is not None and i < len(row) else ''
            hanzi = re.sub(r'[（(].*?[)）]', '', cell(col_role['hanzi'])).strip()
            pinyin = re.sub(r'\s+', ' ', cell(col_role['pinyin'])).strip()
            english = re.sub(r'\s+', ' ', cell(eng_idx)).strip() if eng_idx is not None else ''
            pos_raw = cell(pos_idx).strip() if pos_idx is not None else ''
            if not (is_hanzi(hanzi) and (is_pinyin(pinyin) or is_lenient_pinyin(pinyin))):
                continue
            pos = POS_MAP.get(pos_raw[:1], None)
            if not english:
                continue
            if lines:
                rebuilt = english_from_lines(lines, pinyin.split()[0], english)
                english = rebuilt if rebuilt else english
            words.append(make_word(hanzi, pinyin, english, pos))
    return words


# ---------- Strategy B: line clustering ----------

def get_lines(page):
    """Cluster a page's words into visually-grouped lines."""
    try:
        tokens = page.extract_words(x_tolerance=1.5, y_tolerance=3)
    except Exception:
        return []
    if not tokens:
        return []
    tokens = sorted(tokens, key=lambda t: (round((t['top'] + t['bottom']) / 2 / 4), t['x0']))
    lines, current, last_y = [], [], None
    for t in tokens:
        cy = (t['top'] + t['bottom']) / 2
        if last_y is None or abs(cy - last_y) <= 4:
            current.append(t)
        else:
            lines.append(current)
            current = [t]
        last_y = cy
    if current:
        lines.append(current)
    return lines


def extract_from_lines(page):
    """A vocab line has hanzi + pinyin + english; cluster and filter."""
    words_out = []
    lines = get_lines(page)

    for idx, line in enumerate(lines):
        line.sort(key=lambda t: t['x0'])
        # Identify hanzi tokens and their x-extent
        hanzi_parts, hanzi_x1 = [], None
        for t in line:
            if is_hanzi(t['text']) and not is_pinyin(t['text']):
                # Skip single-char POS column values (名/动/助...) after a hanzi
                if (len(t['text']) == 1 and t['text'] in POS_CHARS
                        and len(re.sub(r'[^一-鿿]', '', t['text'])) == 1
                        and hanzi_parts):
                    continue
                hanzi_parts.append(t['text'])
                hanzi_x1 = t['x1'] if hanzi_x1 is None else max(hanzi_x1, t['x1'])
        hanzi = ''.join(re.sub(r'[^一-鿿]', '', p) for p in hanzi_parts)
        if not is_hanzi(hanzi) or len(hanzi) > MAX_WORD_LEN:
            continue

        # Pinyin: strict (tone-marked) anywhere; lenient only near hanzi block
        pinyin_parts, pinyin_x1 = [], None
        for t in line:
            txt = t['text']
            if CJK_RE.search(txt):
                continue
            if is_pinyin(txt):
                pinyin_parts.append(txt)
                pinyin_x1 = t['x1'] if pinyin_x1 is None else max(pinyin_x1, t['x1'])
            elif (hanzi_x1 is not None and t['x0'] - hanzi_x1 <= 60
                  and is_lenient_pinyin(txt)):
                pinyin_parts.append(txt)
                pinyin_x1 = t['x1'] if pinyin_x1 is None else max(pinyin_x1, t['x1'])
        pinyin = ' '.join(pinyin_parts)
        if not pinyin:
            continue

        # English: tokens after the pinyin block (or after hanzi if no pinyin)
        boundary = pinyin_x1 if pinyin_x1 is not None else hanzi_x1
        eng_parts = [t['text'] for t in line
                     if boundary is not None and t['x0'] > boundary + 30 and is_english(t['text'])]
        english = ' '.join(eng_parts)
        if not english:
            continue

        # Wrapped cell: if the NEXT line is English-only, it's the continuation
        if idx + 1 < len(lines):
            nxt = sorted(lines[idx + 1], key=lambda t: t['x0'])
            nxt_eng = [t['text'] for t in nxt if is_english(t['text'])]
            nxt_other = [t['text'] for t in nxt
                         if not is_english(t['text']) and not is_pinyin(t['text'])]
            if nxt_eng and not nxt_other and len(' '.join(nxt_eng)) <= 25:
                english = (english + ' ' + ' '.join(nxt_eng)).strip()

        words_out.append(make_word(hanzi, pinyin, english))
    return words_out


def extract_from_pdf(pdf_path):
    all_words = []
    seen = set()
    with pdfplumber.open(pdf_path) as pdf:
        total_chars = 0
        for page in pdf.pages:
            text = page.extract_text() or ''
            total_chars += len(text.strip())
        if total_chars < 20:
            sys.exit(
                "ERROR: This PDF has no extractable text — it is a scanned/image PDF.\n"
                "OCR is not supported. Please use a born-digital PDF (e.g. exported\n"
                "from the textbook's digital edition) or provide a PPTX/JSON instead."
            )
        for page in pdf.pages:
            lines = get_lines(page)
            page_words = extract_from_tables(page, lines=lines)
            if not page_words:
                page_words = extract_from_lines(page)
            for w in page_words:
                key = w['hanzi']
                if key in seen:
                    continue
                seen.add(key)
                all_words.append(w)
    return all_words


def main():
    ap = argparse.ArgumentParser(description='Extract vocabulary from a lesson PDF')
    ap.add_argument('pdf_file')
    ap.add_argument('--lesson', type=int, required=True)
    ap.add_argument('--title', default=None)
    ap.add_argument('--output', default=None)
    ap.add_argument('--merge', default=None, help='Merge into existing vocabulary.json')
    args = ap.parse_args()

    print(f"Extracting vocabulary from: {args.pdf_file}")
    words = extract_from_pdf(args.pdf_file)

    if not words:
        print("No vocabulary found. The PDF layout may not match known patterns.")
        print("Try the PPTX source or a JSON word list instead.")
        sys.exit(1)

    print(f"\nExtracted {len(words)} words:")
    for w in words:
        print(f"  {w['hanzi']:10s} {w['pinyin']:18s} {w['english']:35s} [{', '.join(w['tags'][:3])}]")

    title = args.title or f'Lesson {args.lesson}'
    lesson_data = {'lesson': args.lesson, 'title': title, 'words': words}

    out = args.output or f'extracted_pdf_L{args.lesson:02d}.json'
    with open(out, 'w', encoding='utf-8') as f:
        json.dump(lesson_data, f, ensure_ascii=False, indent=2)
    print(f"\nWritten to: {out}")

    if args.merge:
        with open(args.merge, encoding='utf-8') as f:
            db = json.load(f)
        existing = {l.get('lesson') for l in db.get('lessons', [])}
        if args.lesson in existing:
            db['lessons'] = [l for l in db['lessons'] if l.get('lesson') != args.lesson]
            print(f"Replaced existing Lesson {args.lesson}")
        db['lessons'].append(lesson_data)
        db['lessons'].sort(key=lambda x: x.get('lesson') if isinstance(x.get('lesson'), int) else 999)
        db['metadata']['total_lessons'] = len(
            [l for l in db['lessons'] if isinstance(l.get('lesson'), int)])
        with open(args.merge, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"Merged into: {args.merge}")


if __name__ == '__main__':
    main()
