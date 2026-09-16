#!/usr/bin/env python3
"""Merge grammar points and measure words into the vocabulary database."""
import json

# Load vocabulary database
with open('/root/.openclaw/workspace/vocabulary.json', 'r', encoding='utf-8') as f:
    db = json.load(f)

# Load grammar points
with open('/root/.openclaw/workspace/grammar_points.json', 'r', encoding='utf-8') as f:
    grammar = json.load(f)

# Load measure words
with open('/root/.openclaw/workspace/measure_words.json', 'r', encoding='utf-8') as f:
    measure = json.load(f)

# Merge grammar points into lessons
grammar_by_lesson = {}
for gp in grammar['grammar_points']:
    lesson_num = gp['lesson']
    if lesson_num not in grammar_by_lesson:
        grammar_by_lesson[lesson_num] = []
    grammar_by_lesson[lesson_num].append({
        'pattern': gp['pattern'],
        'title': gp['title'],
        'explanation': gp['explanation'],
        'examples': gp['examples']
    })

# Add grammar points to each lesson
for lesson in db['lessons']:
    lesson_num = lesson.get('lesson')
    if isinstance(lesson_num, int) and lesson_num in grammar_by_lesson:
        lesson['grammar_points'] = grammar_by_lesson[lesson_num]
        print(f"Added {len(grammar_by_lesson[lesson_num])} grammar points to Lesson {lesson_num}")

# Add top-level measure words
db['measure_words'] = measure['measure_words']
print(f"Added {len(measure['measure_words'])} measure words to database")

# Update metadata
db['metadata']['last_updated'] = '2026-09-15'
db['metadata']['format_version'] = '2.0'

# Save
with open('/root/.openclaw/workspace/vocabulary.json', 'w', encoding='utf-8') as f:
    json.dump(db, f, ensure_ascii=False, indent=2)

print(f"\n✅ Merged! Total lessons: {len(db['lessons'])}, measure words: {len(db['measure_words'])}")
