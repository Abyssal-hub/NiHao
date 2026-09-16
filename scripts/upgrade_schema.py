#!/usr/bin/env python3
"""Upgrade vocabulary database schema from v1.0 to v2.0.

Reads:  hsk1_vocabulary.json  (v1.0)
Writes: vocabulary.json      (v2.0, universal name)

Changes:
- metadata.format_version -> "2.0"
- metadata.last_updated  -> "2026-09-15"
- + metadata.level  = "HSK1"
- + metadata.hsk_level = 1
- + top-level "grammar_points" array (empty, populated separately)
- + top-level "measure_words"  array (empty, populated separately)
- Each word gains:
    leitner_box: 1   (int 1-4, default 1 = new)
    stroke_order: None  (populated later)
    audio_url: None     (populated later)
    hsk_level: 1
- All existing word fields preserved (hanzi, pinyin, english,
  example_sentences, tags; lesson stays implied from parent).
"""

import json
from pathlib import Path

SRC = Path(__file__).parent / "hsk1_vocabulary.json"
DST = Path(__file__).parent / "vocabulary.json"


def upgrade(src_path: Path) -> dict:
    with open(src_path, encoding="utf-8") as f:
        data = json.load(f)

    meta = data["metadata"]

    # --- metadata upgrades ---
    meta["format_version"] = "2.0"
    meta["last_updated"] = "2026-09-15"
    meta["level"] = "HSK1"
    meta["hsk_level"] = 1
    # Keep existing metadata keys (course, total_lessons, fields) untouched.

    # --- top-level new arrays ---
    data["grammar_points"] = []
    data["measure_words"] = []

    # --- per-word upgrades ---
    for lesson in data["lessons"]:
        for word in lesson["words"]:
            word.setdefault("leitner_box", 1)   # default: new card
            word.setdefault("stroke_order", None)
            word.setdefault("audio_url", None)
            word.setdefault("hsk_level", 1)

    return data


def main() -> None:
    upgraded = upgrade(SRC)

    word_count = sum(len(lesson["words"]) for lesson in upgraded["lessons"])
    lesson_count = len(upgraded["lessons"])

    with open(DST, "w", encoding="utf-8") as f:
        json.dump(upgraded, f, ensure_ascii=False, indent=2)

    # --- summary ---
    new_word_fields = ["leitner_box", "stroke_order", "audio_url", "hsk_level"]
    print("Schema upgrade complete: v1.0 -> v2.0")
    print(f"  Source:      {SRC.name}")
    print(f"  Destination: {DST.name}")
    print(f"  Lessons:     {lesson_count}")
    print(f"  Words:       {word_count}")
    print(f"  New word fields:     {', '.join(new_word_fields)}")
    print(f"  New top-level keys:  grammar_points, measure_words")
    print(f"  Metadata: format_version={upgraded['metadata']['format_version']}, "
          f"level={upgraded['metadata']['level']}, "
          f"hsk_level={upgraded['metadata']['hsk_level']}, "
          f"last_updated={upgraded['metadata']['last_updated']}")

    # --- verify: print first word entry ---
    first_lesson = upgraded["lessons"][0]
    first_word = first_lesson["words"][0]
    print(f"\nFirst word entry (lesson {first_lesson['lesson']}):")
    print(json.dumps(first_word, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
