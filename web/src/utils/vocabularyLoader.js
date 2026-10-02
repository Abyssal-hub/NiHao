import vocab from '../data/vocabulary.json'
import { loadCustomLessons } from './customLessons'

let cachedLessons = null

/**
 * Normalize raw JSON: every word gets a `lesson` field (the data file
 * does not include it on individual words). Lesson ids are numbers for
 * L1-L9 plus the string "appendix" for supplementary vocabulary.
 * Note: lesson 4 does not exist in this dataset (L1,L2,L3,L5..L9).
 * Custom imported lessons (localStorage) are merged in by lesson number.
 */
function normalize() {
  if (cachedLessons) return cachedLessons
  const builtin = vocab.lessons.map((l) => ({
    lesson: l.lesson,
    title: l.title,
    words: l.words.map((w) => ({ ...w, lesson: l.lesson })),
    grammar_points: l.grammar_points || [],
  }))
  const custom = loadCustomLessons().map((l) => ({
    lesson: l.lesson,
    title: l.title,
    words: l.words.map((w) => ({ ...w, lesson: l.lesson })),
    grammar_points: l.grammar_points || [],
    custom: true,
  }))
  cachedLessons = [...builtin, ...custom].sort((a, b) => {
    const na = typeof a.lesson === 'number' ? a.lesson : 999
    const nb = typeof b.lesson === 'number' ? b.lesson : 999
    return na - nb
  })
  return cachedLessons
}

/** Rebuild the merged cache (call after importing/deleting custom lessons). */
export function refreshLessons() {
  cachedLessons = null
  return normalize()
}

/** All lessons (numeric + appendix), unsorted order as in the file. */
export function getLessons() {
  return normalize()
}

/** Numeric lessons only (1,2,3,5,6,7,8,9), sorted ascending. */
export function getNumericLessons() {
  return normalize()
    .filter((l) => typeof l.lesson === 'number')
    .sort((a, b) => a.lesson - b.lesson)
}

/** Sorted list of numeric lesson ids present in the data. */
export function getLessonNumbers() {
  return getNumericLessons().map((l) => l.lesson)
}

export function getFirstLessonNumber() {
  return getLessonNumbers()[0]
}

export function getLastLessonNumber() {
  const n = getLessonNumbers()
  return n[n.length - 1]
}

/**
 * All words whose lesson number falls within [start, end] (inclusive).
 * Non-existent lessons in the range (e.g. L4) are simply skipped.
 * Pass { includeAppendix: true } to also include appendix vocabulary.
 */
export function getWordsForRange(start, end, { includeAppendix = false } = {}) {
  const lessons = normalize().filter(
    (l) => typeof l.lesson === 'number' && l.lesson >= start && l.lesson <= end
  )
  let words = lessons.flatMap((l) => l.words)
  if (includeAppendix) {
    const app = normalize().find((l) => l.lesson === 'appendix')
    if (app) words = words.concat(app.words)
  }
  return words
}

export function countWordsForRange(start, end, opts) {
  return getWordsForRange(start, end, opts).length
}

export function getWordByHanzi(hanzi) {
  for (const l of normalize()) {
    const w = l.words.find((w) => w.hanzi === hanzi)
    if (w) return w
  }
  return null
}

/** List of all lessons with word counts (for the Home page selector). */
export function getLessonList() {
  return normalize().map((l) => ({
    lesson: l.lesson,
    title: l.title,
    wordCount: l.words.length,
  }))
}
