#!/usr/bin/env python3
"""Audit HSK1 vocabulary against PPTX content."""
import json

# Load database
with open("hsk1_vocabulary.json", "r", encoding="utf-8") as f:
    db = json.load(f)

db_words = {}
for lesson in db["lessons"]:
    lesson_num = lesson["lesson"]
    db_words[lesson_num] = set()
    for word in lesson["words"]:
        db_words[lesson_num].add(word["hanzi"])

# Read extracted text
with open("hsk1_extracted.txt", "r", encoding="utf-8") as f:
    text = f.read()

# Now let me manually define the vocabulary from each lesson based on the PPTX slides
# This is based on the actual "new word" slides in the PPTX files

lesson_vocab = {
    1: ["你", "您", "你们", "好", "很", "我", "呢", "对不起", "没关系"],
    2: ["谢谢", "不客气", "再见", "请", "问", "姓", "贵姓", "叫", "什么", "名字", "先生", "小姐", "老师", "吗", "不"],
    3: ["是", "学生", "也", "人", "中国", "北京", "美国", "朋友", "他", "她", "哪", "国"],
    5: ["家", "有", "口", "女儿", "岁", "今年", "几", "多", "大", "了", "哥哥", "姐姐", "弟弟", "妹妹", "爷爷", "奶奶", "爸爸", "妈妈"],
    6: ["会", "说", "汉语", "菜", "好吃", "做", "写", "汉字", "字", "读", "怎么", "英语", "法语", "日语"],
    7: ["今天", "月", "号", "星期", "昨天", "明天", "学校", "看", "书", "去", "日", "生日"],
    8: ["想", "吃", "商店", "茶", "下午", "个", "杯子", "多少", "那", "喝", "米饭", "钱", "买", "这", "块", "上午", "中午", "晚上"],
}

# Check each lesson
for lesson_num, expected_words in lesson_vocab.items():
    print(f"\n{'='*60}")
    print(f"Lesson {lesson_num}")
    print(f"{'='*60}")
    
    db_lesson_words = db_words.get(lesson_num, set())
    
    print(f"Expected words ({len(expected_words)}): {sorted(expected_words)}")
    print(f"DB words ({len(db_lesson_words)}): {sorted(db_lesson_words)}")
    
    # Words in expected but not in DB
    missing = set(expected_words) - db_lesson_words
    if missing:
        print(f"\n❌ MISSING from DB: {sorted(missing)}")
    
    # Words in DB but not in expected
    extra = db_lesson_words - set(expected_words)
    if extra:
        print(f"\n⚠️ EXTRA in DB (not in expected): {sorted(extra)}")
    
    if not missing and not extra:
        print(f"\n✅ Perfect match!")

# Also check for words that appear in lessons but might belong to a different lesson
print(f"\n\n{'='*60}")
print("CROSS-LESSON CHECK")
print(f"{'='*60}")

# Check if words assigned to one lesson actually first appear in another
all_db_words = {}
for lesson in db["lessons"]:
    for word in lesson["words"]:
        all_db_words[word["hanzi"]] = lesson["lesson"]

# Check for duplicates (words appearing in multiple lessons)
from collections import Counter
word_lessons = {}
for lesson in db["lessons"]:
    for word in lesson["words"]:
        hanzi = word["hanzi"]
        if hanzi not in word_lessons:
            word_lessons[hanzi] = []
        word_lessons[hanzi].append(lesson["lesson"])

duplicates = {k: v for k, v in word_lessons.items() if len(v) > 1}
if duplicates:
    print("\n⚠️ Words appearing in multiple lessons:")
    for word, lessons in duplicates.items():
        print(f"  {word}: lessons {lessons}")
else:
    print("\n✅ No duplicates found")
