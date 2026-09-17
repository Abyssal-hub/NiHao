# Vocabulary Category System Design

## Two-Layer Tagging Approach

### Layer 1: Part of Speech (POS) — What type of word is it?
| Tag | Description | Examples |
|-----|-------------|----------|
| `noun` | Things, people, places | 茶， 老师， 中国 |
| `verb` | Actions | 吃， 喝， 去， 买 |
| `adjective` | Descriptions | 好， 大， 小， 热闹 |
| `adverb` | Modifies verbs/adjectives | 很， 也， 不 |
| `pronoun` | Replaces nouns | 我， 你， 他， 这， 那 |
| `particle` | Grammar particles | 的， 了， 吗， 呢 |
| `measure_word` | Counting words | 个， 口， 岁， 块 |
| `question_word` | Asks questions | 什么， 哪， 谁， 几 |
| `number` | Numbers | 一， 二， 三 |
| `expression` | Fixed phrases | 谢谢， 对不起， 没关系 |

### Layer 2: Topic Category — What is it about?
| Tag | Description | Examples |
|-----|-------------|----------|
| `time` | Time & date | 今天， 明天， 月， 号， 星期 |
| `family` | Family members | 爸爸， 妈妈， 哥哥， 姐姐 |
| `food` | Food & drink | 茶， 米饭， 菜， 杯子 |
| `place` | Places & locations | 家， 学校， 商店， 医院 |
| `profession` | Jobs & roles | 老师， 医生， 学生， 售货员 |
| `language` | Languages & learning | 汉语， 英语， 字， 书 |
| `body` | Body parts | 口， 手， 鼻 |
| `money` | Money & shopping | 钱， 块， 买， 商店 |
| `travel` | Travel & transport | 去， 上车， 出差， 长城 |
| `daily_life` | Daily activities | 吃饭， 睡觉， 洗澡， 工作 |
| `people` | People & relationships | 朋友， 同学， 人 |
| `country` | Countries & nationalities | 中国， 美国， 国 |
| `grammar` | Grammar concepts | 的， 是， 不 |
| `pronunciation` | Pronunciation drills | 知识， 厨师， 超人 |

### Layer 3: Difficulty / Source — Where did it come from?
| Tag | Description |
|-----|-------------|
| `core` | HSK1 core vocabulary (L1-L9) |
| `supplementary` | Appendix / extra words |
| `basic` | Essential survival words |

## Tagging Rules

1. Every word gets **1 POS tag** (required)
2. Every word gets **1-3 topic tags** (as relevant)
3. Every word gets **1 source tag** (core or supplementary)
4. Example: 茶 = `noun` + `food` + `core`
5. Example: 的 = `particle` + `grammar` + `core`

## Category Filter UI (Future)

Users can filter by:
- **POS**: "Show me all verbs"
- **Topic**: "Show me all food words"
- **Combined**: "Show me all food nouns from Lessons 1-5"

## Current Tag Migration

Old tags → New tags:
- `noun` → keep as POS
- `verb` → keep as POS
- `time` → keep as topic
- `family` → keep as topic
- `food` → keep as topic
- `basic` → keep as source
- `supplementary` → keep as source
- `pronunciation` → keep as topic
- `polite` → merge into `expression`
- `question` → `question_word`
- `measure_word` → keep as POS
- etc.
