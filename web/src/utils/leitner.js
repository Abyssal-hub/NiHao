/**
 * Progress persistence layer.
 * localStorage schema:
 * {
 *   "sessions": [{ date, mode, lessonStart, lessonEnd, totalWords, correct,
 *                  wrongWords: [{hanzi, pinyin, english, lesson}] }],
 *   "wordStats": { "<hanzi>": { seen, correct, wrong } }
 * }
 */

export const STORAGE_KEY = 'nihao_progress'

const emptyProgress = () => ({ sessions: [], wordStats: {} })

export function loadProgress() {
  try {
    const raw = window.localStorage.getItem(STORAGE_KEY)
    if (!raw) return emptyProgress()
    const parsed = JSON.parse(raw)
    return {
      sessions: Array.isArray(parsed.sessions) ? parsed.sessions : [],
      wordStats: parsed.wordStats && typeof parsed.wordStats === 'object' ? parsed.wordStats : {},
    }
  } catch {
    return emptyProgress()
  }
}

export function saveProgress(progress) {
  try {
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(progress))
  } catch {
    // storage unavailable — ignore
  }
}

export function bumpWord(progress, word, correct) {
  const stats = progress.wordStats[word.hanzi] || { seen: 0, correct: 0, wrong: 0 }
  stats.seen += 1
  if (correct) stats.correct += 1
  else stats.wrong += 1
  progress.wordStats[word.hanzi] = stats
  return stats
}

/**
 * Record a completed session: bumps per-word stats and prepends the
 * session entry. `results` is [{ word, correct }] for every word seen.
 */
export function recordSession({ mode, lessonStart, lessonEnd, totalWords, correct, wrongWords, results }) {
  const progress = loadProgress()
  for (const r of results) bumpWord(progress, r.word, r.correct)
  progress.sessions.unshift({
    date: new Date().toISOString(),
    mode,
    lessonStart,
    lessonEnd,
    totalWords,
    correct,
    wrongWords: wrongWords.map((w) => ({
      hanzi: w.hanzi,
      pinyin: w.pinyin,
      english: w.english,
      lesson: w.lesson,
    })),
  })
  // Cap stored history
  if (progress.sessions.length > 200) progress.sessions.length = 200
  saveProgress(progress)
  return progress
}

export function clearHistory() {
  const progress = loadProgress()
  progress.sessions = []
  saveProgress(progress)
  return progress
}

/**
 * Simple Leitner-style box helper: word moves up a box on correct,
 * down to box 1 on wrong. Boxes 1..5 (higher = better known).
 * Boxes are stored inside wordStats entries as `box`.
 */
export function nextBox(currentBox, correct) {
  const box = currentBox || 1
  if (correct) return Math.min(5, box + 1)
  return 1
}

export function updateBox(progress, hanzi, correct) {
  const stats = progress.wordStats[hanzi] || { seen: 0, correct: 0, wrong: 0 }
  stats.box = nextBox(stats.box, correct)
  progress.wordStats[hanzi] = stats
  return stats
}

/** Get all recorded sessions (newest first). */
export function getSessions() {
  return loadProgress().sessions
}

/** Get all word stats as an object keyed by hanzi. */
export function getWordStats() {
  return loadProgress().wordStats
}
