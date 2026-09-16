#!/usr/bin/env python3
"""Fully automated PPTX vocabulary extraction engine.

Usage:
    python3 auto_extract.py <pptx_file> [--lesson N] [--title "Title"] [--output OUTPUT.json]

Identifies vocabulary slides, extracts pinyin-English-hanzi triplets,
auto-tags each word, and outputs in v2.0 schema format.
"""
import json
import re
import sys
import argparse
from pptx import Presentation
from pptx.util import Inches


def is_pinyin_text(text):
    """Check if text looks like pinyin (has tone marks or spaced syllables)."""
    tone_marks = 'āáǎàēéěèīíǐìōóǒòūúǔùǖǘǚǜ'
    if any(c in tone_marks for c in text):
        return True
    # Spaced syllables without tone marks (rare but possible)
    parts = text.strip().split()
    if len(parts) >= 2 and all(len(p) <= 6 and p.isascii() and not p[0].isupper() for p in parts):
        return True
    return False


def is_english_text(text):
    """Check if text looks like English translation."""
    # Mostly ASCII, 1-5 words, no CJK
    if re.search(r'[\u4e00-\u9fff]', text):
        return False
    words = text.strip().split()
    if not 1 <= len(words) <= 5:
        return False
    # Allow apostrophes and hyphens
    cleaned = re.sub(r"[\s\-'/.,!?()]", '', text)
    return cleaned.isascii() and bool(cleaned)


def is_hanzi_text(text):
    """Check if text is purely Chinese characters."""
    cleaned = text.strip()
    if not cleaned:
        return False
    # Remove punctuation that might accompany hanzi
    cleaned = re.sub(r'[，。！？；：、·…\s]', '', cleaned)
    return all('\u4e00' <= c <= '\u9fff' for c in cleaned) and len(cleaned) >= 1


def extract_tone_number(pinyin_char):
    """Determine tone number from a pinyin character with tone mark."""
    tone_map = {
        'ā': 1, 'ē': 1, 'ī': 1, 'ō': 1, 'ū': 1, 'ǖ': 1,
        'á': 2, 'é': 2, 'í': 2, 'ó': 2, 'ú': 2, 'ǘ': 2,
        'ǎ': 3, 'ě': 3, 'ǐ': 3, 'ǒ': 3, 'ǔ': 3, 'ǚ': 3,
        'à': 4, 'è': 4, 'ì': 4, 'ò': 4, 'ù': 4, 'ǜ': 4,
    }
    return tone_map.get(pinyin_char, 0)


def normalize_pinyin(pinyin):
    """Normalize spaced pinyin to standard form."""
    parts = pinyin.strip().split()
    if len(parts) <= 1:
        return pinyin.strip()
    # Join syllables that were space-separated
    # e.g., "duì bu qǐ" → "duìbùqǐ", "nǐ men" → "nǐmen"
    return ''.join(parts)


def auto_tag(english, hanzi, pinyin):
    """Auto-generate tags based on English meaning and hanzi patterns."""
    eng = english.lower()
    tags = []

    # Question words
    question_words = {'what', 'which', 'who', 'where', 'when', 'why', 'how',
                      'how many', 'how much', 'how old'}
    if any(q in eng for q in question_words):
        tags.append('question')

    # Pronouns
    pronouns = {'you', 'i', 'me', 'he', 'him', 'she', 'her', 'it', 'we', 'us',
                'they', 'them', 'this', 'that', 'these', 'those'}
    if eng.strip() in pronouns or any(p in eng.split() for p in pronouns if len(p) > 1):
        tags.append('pronoun')

    # Numbers
    number_chars = set('一二三四五六七八九十两零百千万亿')
    if any(c in hanzi for c in number_chars) and len(hanzi) <= 3:
        tags.append('number')

    # Measure words
    measure_words = {'个', '口', '岁', '块', '杯', '本', '只', '张', '件',
                     '把', '条', '瓶', '双', '层', '顿', '家', '些'}
    if hanzi in measure_words:
        tags.append('measure_word')

    # Particles
    particles = {'吗', '呢', '了', '的', '吧', '啊', '呀', '嘛', '么', '地', '得'}
    if hanzi in particles:
        tags.append('particle')

    # Expressions
    expressions = {'sorry', 'thank', 'please', 'excuse', 'goodbye', 'hello',
                   'welcome', "it's okay", 'no problem', "you're welcome",
                   'not at all', 'good bye', 'bye', 'thanks'}
    if any(e in eng for e in expressions):
        tags.append('expression')

    # Negation
    if 'not' in eng or 'no ' in eng or eng.startswith('no') or '不' in hanzi:
        tags.append('negation')

    # Verbs (action words)
    verb_patterns = [
        r'\bto (be|have|go|eat|drink|buy|speak|write|read|see|look|watch|work|want|think|call|ask|say|learn|study|teach|live|like|love|need|give|take|come|sit|stand|walk|run|sleep|rest|play|do|make|use)',
        r'\bcan\b', r'\bmay\b', r'\bwant\b', r'\blike\b', r'\bneed\b',
    ]
    if any(re.search(p, eng) for p in verb_patterns):
        tags.append('verb')

    # Time words
    time_words = {'today', 'tomorrow', 'yesterday', 'year', 'month', 'day',
                  'week', 'morning', 'afternoon', 'evening', 'noon', 'night',
                  'now', 'this year', "o'clock", 'date', 'birthday', 'spring',
                  'summer', 'autumn', 'fall', 'winter', 'season', 'monday',
                  'tuesday', 'wednesday', 'thursday', 'friday', 'saturday', 'sunday'}
    if any(t in eng for t in time_words):
        tags.append('time')

    # Family
    family_words = {'father', 'mother', 'dad', 'mom', 'brother', 'sister',
                    'son', 'daughter', 'grandfather', 'grandmother', 'grandpa',
                    'grandma', 'family', 'home', 'older brother', 'younger brother',
                    'older sister', 'younger sister'}
    if any(f in eng for f in family_words):
        tags.append('family')

    # Food and drink
    food_words = {'eat', 'drink', 'tea', 'rice', 'food', 'dish', 'delicious',
                  'cup', 'glass', 'water', 'coffee', 'milk', 'juice', 'beer',
                  'wine', 'restaurant', 'meal', 'breakfast', 'lunch', 'dinner',
                  'hungry', 'thirsty'}
    if any(f in eng for f in food_words):
        tags.append('food')

    # Shopping / money
    shopping_words = {'buy', 'money', 'yuan', 'dollar', 'kuai', 'store', 'shop',
                      'how much', 'expensive', 'cheap', 'price', 'pay', 'sell',
                      'market', 'mall'}
    if any(s in eng for s in shopping_words):
        tags.append('shopping')

    # Language
    lang_words = {'chinese', 'english', 'french', 'japanese', 'korean', 'spanish',
                  'language', 'speak', 'write', 'read', 'character', 'word',
                  'hanzi', 'pinyin', 'pronounce', 'learn', 'study'}
    if any(l in eng for l in lang_words):
        tags.append('language')

    # Places
    place_words = {'china', 'beijing', 'shanghai', 'america', 'usa', 'school',
                   'hospital', 'bank', 'store', 'shop', 'restaurant', 'home',
                   'here', 'there', 'where', 'place', 'country', 'city', 'in',
                   'on', 'at', 'up', 'down', 'inside', 'outside'}
    if any(p in eng for p in place_words):
        tags.append('place')

    # People / professions
    profession_words = {'teacher', 'student', 'doctor', 'nurse', 'worker',
                        'farmer', 'driver', 'cook', 'seller', 'clerk', 'manager',
                        'engineer', 'lawyer', 'writer', 'artist', 'musician',
                        'professor', 'mr.', 'miss', 'mrs.', 'ms.', 'sir', 'madam'}
    if any(p in eng for p in profession_words):
        tags.append('person')

    # Adjectives
    adj_words = {'good', 'bad', 'big', 'small', 'many', 'much', 'few', 'little',
                 'hot', 'cold', 'warm', 'cool', 'new', 'old', 'young', 'tall',
                 'short', 'long', 'fast', 'slow', 'easy', 'hard', 'difficult',
                 'delicious', 'nice', 'beautiful', 'pretty', 'ugly', 'happy',
                 'sad', 'tired', 'busy', 'free', 'interesting', 'boring'}
    if eng.strip() in adj_words or any(f' {a}' in eng or eng.startswith(a) for a in adj_words):
        tags.append('adjective')

    # Adverbs
    adv_words = {'very', 'also', 'too', 'not', 'no', 'just', 'only', 'already',
                 'still', 'always', 'usually', 'often', 'sometimes', 'never',
                 'quickly', 'slowly', 'well', 'here', 'there'}
    if eng.strip() in adv_words:
        tags.append('adverb')

    # Countries / nationalities
    country_words = {'china', 'chinese', 'america', 'american', 'japan', 'japanese',
                     'france', 'french', 'korea', 'korean', 'england', 'english',
                     'country', 'nation'}
    if any(c in eng for c in country_words):
        tags.append('country')

    # Default tag if nothing matched
    if not tags:
        tags.append('vocabulary')

    # Add 'basic' for common everyday words
    basic_words = {'you', 'i', 'me', 'good', 'hello', 'sorry', 'thank', 'yes',
                   'no', 'not', 'very', 'is', 'are', 'am', 'be', 'have', 'go',
                   'come', 'eat', 'drink', 'see', 'want', 'can', 'may'}
    if any(b in eng for b in basic_words):
        tags.append('basic')

    return list(dict.fromkeys(tags))  # Deduplicate, preserve order


def is_vocab_slide(slide, prs):
    """Determine if a slide is a vocabulary slide."""
    slide_width = prs.slide_width / 914400  # EMU to inches

    pinyin_shapes = []
    english_shapes = []
    hanzi_shapes = []
    all_texts = []

    for shape in slide.shapes:
        if not hasattr(shape, 'text') or not shape.text.strip():
            continue
        text = shape.text.strip()
        all_texts.append(text)
        left = shape.left / 914400 if shape.left else 0
        top = shape.top / 914400 if shape.top else 0

        # Check for exclusion keywords (non-vocab slides)
        exclusion_keywords = [
            '拼音', '声调', '笔画', '笔顺', '规则', '儿化', '发音',
            '辨音', '音节', '变调', '轻声', '录音', '跟读', '连读',
            '隔音', '省写', '标调', '练习', '复习', '汉字', '独体字',
            '声母', '韵母', '整体认读'
        ]
        if any(kw in text for kw in exclusion_keywords) and len(text) > 10:
            return False, [], [], []

        if shape.shape_type == 1:  # AUTO_SHAPE
            if is_pinyin_text(text):
                pinyin_shapes.append({'left': left, 'top': top, 'text': text})
            elif is_hanzi_text(text):
                hanzi_shapes.append({'left': left, 'top': top, 'text': text})
        elif shape.shape_type == 17:  # TEXT_BOX
            if is_english_text(text) and len(text) < 40:
                english_shapes.append({'left': left, 'top': top, 'text': text})

    # Need at least 3 pinyin shapes (English may be 0 for some lessons)
    if len(pinyin_shapes) < 3:
        return False, [], [], []

    return True, pinyin_shapes, english_shapes, hanzi_shapes


def extract_vocab_slide(slide, prs):
    """Extract vocabulary pairs from a slide."""
    slide_width = prs.slide_width / 914400
    mid_point = slide_width / 2

    pinyin_list = []
    english_list = []

    for shape in slide.shapes:
        if not hasattr(shape, 'text') or not shape.text.strip():
            continue
        text = shape.text.strip()
        left = shape.left / 914400 if shape.left else 0
        top = shape.top / 914400 if shape.top else 0
        col = 1 if left < mid_point else 2

        if shape.shape_type == 1:  # AUTO_SHAPE
            if is_pinyin_text(text):
                pinyin_list.append({'col': col, 'top': top, 'text': text, 'left': left})
        elif shape.shape_type == 17:  # TEXT_BOX
            if is_english_text(text) and len(text) < 40:
                english_list.append({'col': col, 'top': top, 'text': text, 'left': left})

    # Sort within columns by vertical position
    for lst in [pinyin_list, english_list]:
        lst.sort(key=lambda x: (x['col'], x['top']))

    # Pair pinyin with English by column + vertical proximity
    # If no English found, create pairs with just pinyin + hanzi
    pairs = []
    for col in [1, 2]:
        col_pinyin = [p for p in pinyin_list if p['col'] == col]
        col_english = [e for e in english_list if e['col'] == col]

        if col_english:
            # Normal case: pair pinyin with English
            for p in col_pinyin:
                best = None
                best_dist = float('inf')
                for e in col_english:
                    dist = abs(p['top'] - e['top'])
                    if dist < best_dist:
                        best_dist = dist
                        best = e
                
                if best and best_dist < 2.5:
                    pairs.append({
                        'pinyin_raw': p['text'],
                        'pinyin': normalize_pinyin(p['text']),
                        'english': best['text'],
                        'hanzi': None,
                        'col': col,
                        'top': p['top'],
                        'left': p['left'],
                    })
                    col_english.remove(best)
        else:
            # No English on this slide — just extract pinyin for hanzi matching
            for p in col_pinyin:
                pairs.append({
                    'pinyin_raw': p['text'],
                    'pinyin': normalize_pinyin(p['text']),
                    'english': None,  # Will try to infer from hanzi
                    'hanzi': None,
                    'col': col,
                    'top': p['top'],
                    'left': p['left'],
                })

    return pairs


def find_hanzi_for_pairs(slides, vocab_slide_idx, prs, pairs):
    """Match hanzi to pinyin pairs using known HSK1 vocabulary and positional hints."""
    # Collect all hanzi candidates from nearby slides
    candidates = []
    for offset in range(0, 4):
        idx = vocab_slide_idx + offset
        if idx >= len(slides):
            break
        slide = slides[idx]
        for shape in slide.shapes:
            if hasattr(shape, 'text') and shape.text.strip():
                text = shape.text.strip()
                clean = re.sub(r'[，。！？；：、·…\s\*]', '', text)
                if is_hanzi_text(clean) and 1 <= len(clean) <= 4:
                    left = shape.left / 914400 if shape.left else 0
                    top = shape.top / 914400 if shape.top else 0
                    candidates.append({'text': clean, 'slide': idx, 'left': left, 'top': top})
    
    # Build a lookup: pinyin_normalized → hanzi from known HSK1 vocab
    hsk1_pinyin_to_hanzi = {
        'nǐ': '你', 'nín': '您', 'nǐmen': '你们', 'hǎo': '好', 'hěn': '很',
        'wǒ': '我', 'ne': '呢', 'duìbuqǐ': '对不起', 'méiguānxi': '没关系',
        'xièxie': '谢谢', 'búkèqi': '不客气', 'zàijiàn': '再见',
        'bù': '不', 'qǐng': '请', 'wèn': '问', 'xìng': '姓',
        'guìxìng': '贵姓', 'jiào': '叫', 'shénme': '什么', 'míngzi': '名字',
        'xiānsheng': '先生', 'xiǎojiě': '小姐', 'lǎoshī': '老师', 'ma': '吗',
        'shì': '是', 'xuésheng': '学生', 'yě': '也', 'rén': '人',
        'zhōngguó': '中国', 'běijīng': '北京', 'měiguó': '美国',
        'péngyou': '朋友', 'tā': '他', 'nǎ': '哪', 'guó': '国',
        'jiā': '家', 'yǒu': '有', 'kǒu': '口', 'nǚér': '女儿',
        'suì': '岁', 'jīnnián': '今年', 'jǐ': '几', 'duō': '多',
        'dà': '大', 'le': '了', 'yéye': '爷爷', 'nǎinai': '奶奶',
        'bàba': '爸爸', 'māma': '妈妈', 'gēge': '哥哥', 'jiějie': '姐姐',
        'dìdi': '弟弟', 'mèimei': '妹妹',
        'huì': '会', 'shuō': '说', 'hànyǔ': '汉语', 'cài': '菜',
        'hǎochī': '好吃', 'zuò': '做', 'xiě': '写', 'hànzì': '汉字',
        'zì': '字', 'dú': '读', 'zěnme': '怎么', 'yīngyǔ': '英语',
        'fǎyǔ': '法语', 'rìyǔ': '日语',
        'jīntiān': '今天', 'yuè': '月', 'hào': '号', 'xīngqī': '星期',
        'zuótiān': '昨天', 'míngtiān': '明天', 'xuéxiào': '学校',
        'kàn': '看', 'shū': '书', 'qù': '去', 'rì': '日', 'shēngrì': '生日',
        'xiǎng': '想', 'chī': '吃', 'shāngdiàn': '商店', 'chá': '茶',
        'xiàwǔ': '下午', 'gè': '个', 'bēizi': '杯子', 'duōshao': '多少',
        'nà': '那', 'hē': '喝', 'mǐfàn': '米饭', 'qián': '钱',
        'mǎi': '买', 'zhè': '这', 'kuài': '块',
        'shàngwǔ': '上午', 'zhōngwǔ': '中午', 'wǎnshàng': '晚上',
        'zài': '在', 'xiǎo': '小', 'yǐzi': '椅子', 'gōngzuò': '工作',
        'érzi': '儿子', 'yīshēng': '医生', 'yīyuàn': '医院',
        'māo': '猫', 'gǒu': '狗', 'nàr': '那儿', 'xiàmiàn': '下面',
        'nǎr': '哪儿', 'zhèr': '这儿', 'shuìjiào': '睡觉',
        'xiūxi': '休息', 'zúqiú': '足球', 'lánqiú': '篮球', 'xǐzǎo': '洗澡',
    }
    
    used = set()
    for pair in pairs:
        if pair.get('hanzi'):
            continue
        
        pinyin_clean = pair['pinyin'].lower().replace(' ', '')
        
        # Strategy 1: Direct lookup from known HSK1 vocabulary
        if pinyin_clean in hsk1_pinyin_to_hanzi:
            hanzi = hsk1_pinyin_to_hanzi[pinyin_clean]
            if hanzi not in used and hanzi in [c['text'] for c in candidates]:
                pair['hanzi'] = hanzi
                used.add(hanzi)
                continue
        
        # Strategy 2: Match by syllable count and position
        syllables = len(pair['pinyin_raw'].split())
        best = None
        best_score = -1
        
        for c in candidates:
            if c['text'] in used:
                continue
            
            hanzi_len = len(c['text'])
            score = 0
            
            # Syllable count match
            if hanzi_len == syllables:
                score += 100
            elif hanzi_len == 1 and syllables == 1:
                score += 80
            elif abs(hanzi_len - syllables) <= 1:
                score += 40
            else:
                continue
            
            # Position bonus: same general area
            pair_col_x = pair.get('left', 0)
            if abs(c['left'] - pair_col_x) < 3:
                score += 15
            
            if score > best_score:
                best_score = score
                best = c
        
        if best and best_score > 40:
            pair['hanzi'] = best['text']
            used.add(best['text'])
    
    return pairs


def infer_english(hanzi, pinyin):
    """Infer English meaning from well-known HSK1 vocabulary."""
    hsk1_dict = {
        '你': 'you', '您': 'you (polite)', '你们': 'you (plural)',
        '好': 'good / fine / OK', '很': 'very', '我': 'I / me',
        '呢': 'question particle (and you?)', '对不起': 'sorry',
        '没关系': "it's okay / no problem",
        '谢谢': 'thank you', '不客气': "you're welcome", '再见': 'goodbye',
        '不': 'not / no', '请': 'please', '问': 'to ask',
        '姓': 'surname / to be surnamed', '贵姓': 'your surname (polite)',
        '叫': 'to be called / to call', '什么': 'what', '名字': 'name',
        '先生': 'Mr. / husband', '小姐': 'Miss / young lady', '老师': 'teacher',
        '吗': 'question particle',
        '是': 'to be / am / is / are', '学生': 'student', '也': 'also / too',
        '人': 'person / people', '中国': 'China', '北京': 'Beijing',
        '美国': 'America / USA', '朋友': 'friend', '他': 'he / him',
        '她': 'she / her', '哪': 'which', '国': 'country / nation',
        '家': 'home / family', '有': 'to have / there is/are',
        '口': 'mouth / measure word for people', '女儿': 'daughter',
        '岁': 'year (of age)', '今年': 'this year', '几': 'how many / several',
        '多': 'many / much / how', '大': 'big / old (age)',
        '了': 'particle indicating change', '爷爷': 'grandfather (paternal)',
        '奶奶': 'grandmother (paternal)', '爸爸': 'father / dad',
        '妈妈': 'mother / mom', '哥哥': 'older brother',
        '姐姐': 'older sister', '弟弟': 'younger brother',
        '妹妹': 'younger sister',
        '会': 'can / to be able to', '说': 'to speak', '汉语': 'Chinese language',
        '菜': 'dish / cuisine', '好吃': 'delicious / tasty', '做': 'to do / to make',
        '写': 'to write', '汉字': 'Chinese characters', '字': 'character',
        '读': 'to read', '怎么': 'how', '英语': 'English language',
        '法语': 'French language', '日语': 'Japanese language',
        '今天': 'today', '月': 'month', '号': 'date / number',
        '星期': 'week', '昨天': 'yesterday', '明天': 'tomorrow',
        '学校': 'school', '看': 'to look / to watch / to read', '书': 'book',
        '去': 'to go', '日': 'sun / day', '生日': 'birthday',
        '想': 'to want / to think', '吃': 'to eat', '商店': 'shop / store',
        '茶': 'tea', '下午': 'afternoon', '个': 'measure word (general)',
        '杯子': 'cup / glass / mug', '多少': 'how much / how many',
        '那': 'that', '喝': 'to drink', '米饭': 'cooked rice',
        '钱': 'money', '买': 'to buy', '这': 'this', '块': 'yuan / dollar',
        '上午': 'morning', '中午': 'noon', '晚上': 'evening / night',
        '在': 'at / in / on', '小': 'small', '椅子': 'chair',
        '工作': 'to work / job', '儿子': 'son', '医生': 'doctor',
        '医院': 'hospital', '猫': 'cat', '狗': 'dog', '那儿': 'there',
        '下面': 'below / under', '哪儿': 'where', '这儿': 'here',
        '售货员': 'shop assistant / sales clerk', '银行职员': 'bank clerk',
        '睡觉': 'to sleep', '休息': 'to rest', '足球': 'football / soccer',
        '篮球': 'basketball', '洗澡': 'to take a shower / bath',
    }
    return hsk1_dict.get(hanzi)


def extract_from_pptx(pptx_path, lesson_num=None, title=None):
    """Main extraction function."""
    prs = Presentation(pptx_path)
    all_pairs = []
    vocab_slide_indices = []

    # Pass 1: Identify vocab slides
    for i, slide in enumerate(prs.slides):
        is_vocab, pinyin_shapes, english_shapes, hanzi_shapes = is_vocab_slide(slide, prs)
        if is_vocab and len(pinyin_shapes) >= 3:
            vocab_slide_indices.append(i)

    # Pass 2: Extract from each vocab slide
    for idx in vocab_slide_indices:
        slide = prs.slides[idx]
        pairs = extract_vocab_slide(slide, prs)

        # Match hanzi to pairs using nearby slides
        pairs = find_hanzi_for_pairs(prs.slides, idx, prs, pairs)

        all_pairs.extend(pairs)

    # Build word entries
    words = []
    for pair in all_pairs:
        if pair['hanzi'] is None:
            print(f"  ⚠️ Skipping unmatched: {pair['pinyin']} → {pair.get('english', '?')}")
            continue

        # Infer English from common HSK1 knowledge if missing
        english = pair.get('english')
        if english is None:
            english = infer_english(pair['hanzi'], pair['pinyin'])
            if english is None:
                print(f"  ⚠️ No English for: {pair['hanzi']} ({pair['pinyin']})")
                continue

        tags = auto_tag(english, pair['hanzi'], pair['pinyin'])
        words.append({
            'hanzi': pair['hanzi'],
            'pinyin': pair['pinyin'],
            'english': english,
            'example_sentences': [],
            'tags': tags,
            'leitner_box': 1,
            'stroke_order': None,
            'audio_url': None,
            'hsk_level': 1
        })

    return words


def main():
    parser = argparse.ArgumentParser(description='Extract vocabulary from HSK PPTX file')
    parser.add_argument('pptx_file', help='Path to PPTX file')
    parser.add_argument('--lesson', type=int, help='Lesson number')
    parser.add_argument('--title', help='Lesson title')
    parser.add_argument('--output', help='Output JSON file path')
    parser.add_argument('--merge', help='Merge into existing vocabulary.json')
    args = parser.parse_args()

    print(f"Extracting vocabulary from: {args.pptx_file}")

    # Infer lesson number from filename if not provided
    lesson_num = args.lesson
    if lesson_num is None:
        fname = args.pptx_file
        match = re.search(r'第(\d+)课', fname)
        if match:
            lesson_num = int(match.group(1))
        else:
            match = re.search(r'hsk1-(\d+)', fname)
            if match:
                lesson_num = int(match.group(1))

    title = args.title
    if title is None and lesson_num:
        # Try to extract from first slide
        prs = Presentation(args.pptx_file)
        first_slide = prs.slides[0]
        for shape in first_slide.shapes:
            if hasattr(shape, 'text') and shape.text.strip():
                text = shape.text.strip()
                if re.search(r'[\u4e00-\u9fff]', text) and '\n' in text:
                    lines = text.split('\n')
                    if len(lines) >= 2:
                        title = lines[1].strip()
                        break
                elif re.search(r'[\u4e00-\u9fff]', text) and len(text) > 2 and len(text) < 30:
                    title = text
                    break

    words = extract_from_pptx(args.pptx_file, lesson_num, title)
    print(f"\nExtracted {len(words)} words from Lesson {lesson_num}")

    for w in words:
        print(f"  {w['hanzi']:8s} {w['pinyin']:15s} {w['english']:25s} [{', '.join(w['tags'][:3])}]")

    # Output
    lesson_data = {
        'lesson': lesson_num,
        'title': title or f'Lesson {lesson_num}',
        'words': words
    }

    output_path = args.output
    if output_path is None:
        output_path = f'extracted_L{lesson_num:02d}.json'

    with open(output_path, 'w', encoding='utf-8') as f:
        json.dump(lesson_data, f, ensure_ascii=False, indent=2)
    print(f"\nWritten to: {output_path}")

    # Merge mode
    if args.merge:
        merge_path = args.merge
        with open(merge_path, 'r', encoding='utf-8') as f:
            db = json.load(f)

        # Check if lesson already exists
        existing_lessons = {l['lesson'] for l in db.get('lessons', [])}
        if lesson_num in existing_lessons:
            # Replace existing lesson
            db['lessons'] = [l for l in db['lessons'] if l['lesson'] != lesson_num]
            print(f"Replaced existing Lesson {lesson_num}")

        # Add new lesson in order
        db['lessons'].append(lesson_data)
        db['lessons'].sort(key=lambda x: x['lesson'])
        db['metadata']['total_lessons'] = len(db['lessons'])

        with open(merge_path, 'w', encoding='utf-8') as f:
            json.dump(db, f, ensure_ascii=False, indent=2)
        print(f"Merged into: {merge_path}")

    return words


if __name__ == '__main__':
    main()
