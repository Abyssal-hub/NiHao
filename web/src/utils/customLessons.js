// Custom lesson store — imported lessons persisted in localStorage.
// Built-in lessons ship with the app; these live alongside them.

const STORAGE_KEY = 'nihao_custom_lessons'

export function loadCustomLessons() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return []
    const parsed = JSON.parse(raw)
    return Array.isArray(parsed) ? parsed : []
  } catch {
    return []
  }
}

export function saveCustomLessons(lessons) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(lessons))
  } catch {
    // storage unavailable — ignore
  }
}

const BUILTIN_LESSONS = [1, 2, 3, 4, 5, 6, 7, 8, 9, 11]

function isHanzi(text) {
  return typeof text === 'string' && [...text].some((c) => c >= '\u4e00' && c <= '\u9fff')
}

/**
 * Validate and normalize an imported lesson object.
 * Accepts {lesson, title, words:[{hanzi, pinyin, english, ...}]}.
 * Returns { ok, errors, lesson } — lesson is normalized to v2.0 word schema.
 */
export function validateLesson(data) {
  const errors = []

  if (!data || typeof data !== 'object') {
    return { ok: false, errors: ['Not a JSON object'], lesson: null }
  }
  if (typeof data.lesson !== 'number' || !Number.isInteger(data.lesson) || data.lesson < 1) {
    errors.push('"lesson" must be a positive integer (e.g. 12)')
  } else if (BUILTIN_LESSONS.includes(data.lesson)) {
    errors.push(
      `Lesson ${data.lesson} is built-in — built-in lessons cannot be overridden. ` +
      'Renumber your import (e.g. 101+) or ask for the source to be updated.'
    )
  }
  if (typeof data.title !== 'string' || !data.title.trim()) {
    errors.push('"title" is required (e.g. "我能坐这儿吗 (Can I sit here)")')
  }
  if (!Array.isArray(data.words) || data.words.length === 0) {
    errors.push('"words" must be a non-empty array')
  }

  const words = []
  if (Array.isArray(data.words)) {
    const seen = new Set()
    data.words.forEach((w, i) => {
      const where = `words[${i}]`
      if (!w || typeof w !== 'object') {
        errors.push(`${where}: not an object`)
        return
      }
      if (typeof w.hanzi !== 'string' || !isHanzi(w.hanzi)) {
        errors.push(`${where}.hanzi: missing or no Chinese characters`)
        return
      }
      if (seen.has(w.hanzi)) {
        errors.push(`${where}.hanzi: duplicate "${w.hanzi}" in this lesson`)
        return
      }
      seen.add(w.hanzi)
      if (typeof w.pinyin !== 'string' || !w.pinyin.trim()) {
        errors.push(`${where}.pinyin: required`)
        return
      }
      if (typeof w.english !== 'string' || !w.english.trim()) {
        errors.push(`${where}.english: required`)
        return
      }
      words.push({
        hanzi: w.hanzi.trim(),
        pinyin: w.pinyin.trim(),
        english: w.english.trim(),
        vietnamese: typeof w.vietnamese === 'string' && w.vietnamese.trim()
          ? w.vietnamese.trim() : null,
        example_sentences: Array.isArray(w.example_sentences)
          ? w.example_sentences.filter((s) => typeof s === 'string') : [],
        tags: Array.isArray(w.tags) && w.tags.length
          ? w.tags.filter((t) => typeof t === 'string')
          : ['vocabulary', 'custom'],
        leitner_box: 1,
        stroke_order: null,
        audio_url: null,
        hsk_level: 1,
        custom: true,
      })
    })
  }

  if (errors.length) return { ok: false, errors, lesson: null }

  return {
    ok: true,
    errors: [],
    lesson: {
      lesson: data.lesson,
      title: data.title.trim(),
      words,
      grammar_points: Array.isArray(data.grammar_points) ? data.grammar_points : [],
      custom: true,
    },
  }
}

/** Import a validated lesson; returns {ok, error} handling number collisions. */
export function importLesson(lesson) {
  const lessons = loadCustomLessons()
  const collision = lessons.find((l) => l.lesson === lesson.lesson)
  if (collision) {
    return {
      ok: false,
      error: `Custom lesson ${lesson.lesson} ("${collision.title}") already exists. Delete it first to replace.`,
    }
  }
  lessons.push(lesson)
  lessons.sort((a, b) => a.lesson - b.lesson)
  saveCustomLessons(lessons)
  return { ok: true }
}

export function deleteCustomLesson(lessonNumber) {
  const lessons = loadCustomLessons().filter((l) => l.lesson !== lessonNumber)
  saveCustomLessons(lessons)
}
