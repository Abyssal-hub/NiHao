/** Fisher–Yates shuffle (returns a new array). */
export function shuffle(arr) {
  const a = [...arr]
  for (let i = a.length - 1; i > 0; i--) {
    const j = Math.floor(Math.random() * (i + 1))
    ;[a[i], a[j]] = [a[j], a[i]]
  }
  return a
}

/**
 * Build a multiple-choice question: the target word plus 3 distractors
 * drawn from the SAME pool (lesson range), shuffled.
 */
export function buildQuestion(word, pool) {
  const distractors = shuffle(pool.filter((w) => w.hanzi !== word.hanzi)).slice(0, 3)
  const options = shuffle([word, ...distractors])
  return { word, options }
}

export function accuracyPercent(correct, total) {
  if (!total) return 0
  return Math.round((correct / total) * 100)
}
