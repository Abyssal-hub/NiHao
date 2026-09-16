import { useState, useEffect, useCallback, useRef } from 'react'
import { getWordsForRange } from '../utils/vocabularyLoader'
import { shuffle } from '../utils/scoring'
import { recordSession } from '../utils/leitner'

const ADVANCE_DELAY_MS = 400

/**
 * Flashcard engine: show hanzi, tap to flip, self-grade knew/forgot.
 * Runs through every word in range once. Persists session + word stats
 * exactly as the quiz does (knew === correct).
 */
export function useFlashcard({ start, end, includeAppendix = false }) {
  const [queue, setQueue] = useState(() =>
    shuffle(getWordsForRange(start, end, { includeAppendix }))
  )
  const [index, setIndex] = useState(0)
  const [flipped, setFlipped] = useState(false)
  const [graded, setGraded] = useState(false)
  const [knewCount, setKnewCount] = useState(0)
  const [wrongWords, setWrongWords] = useState([])
  const [results, setResults] = useState([])
  const [complete, setComplete] = useState(false)
  const [saved, setSaved] = useState(false)
  const timerRef = useRef(null)

  const current = queue[index]

  const resetAll = useCallback((q) => {
    setQueue(q)
    setIndex(0)
    setFlipped(false)
    setGraded(false)
    setKnewCount(0)
    setWrongWords([])
    setResults([])
    setComplete(false)
  }, [])

  // Reset when the lesson range changes
  useEffect(() => {
    resetAll(shuffle(getWordsForRange(start, end, { includeAppendix })))
    setSaved(false)
  }, [start, end, includeAppendix, resetAll])

  // Clear any pending auto-advance on unmount
  useEffect(
    () => () => {
      if (timerRef.current) clearTimeout(timerRef.current)
    },
    []
  )

  const flip = useCallback(() => {
    if (graded || complete) return
    setFlipped((f) => !f)
  }, [graded, complete])

  const advance = useCallback(() => {
    if (index + 1 >= queue.length) {
      setComplete(true)
      return
    }
    setIndex((i) => i + 1)
    setFlipped(false)
    setGraded(false)
  }, [index, queue.length])

  const grade = useCallback(
    (knew) => {
      if (!flipped || graded || complete || !current) return
      setGraded(true)
      setKnewCount((c) => c + (knew ? 1 : 0))
      setWrongWords((w) => (knew ? w : [...w, current]))
      setResults((r) => [...r, { word: current, correct: knew }])
      timerRef.current = setTimeout(advance, ADVANCE_DELAY_MS)
    },
    [flipped, graded, complete, current, advance]
  )

  // Persist exactly once when the session completes
  useEffect(() => {
    if (complete && !saved) {
      recordSession({
        mode: 'flashcard',
        lessonStart: start,
        lessonEnd: end,
        totalWords: queue.length,
        correct: knewCount,
        wrongWords,
        results,
      })
      setSaved(true)
    }
  }, [complete, saved, start, end, queue.length, knewCount, wrongWords, results])

  const retryWrong = useCallback(() => {
    if (!wrongWords.length) return
    resetAll(shuffle(wrongWords))
    setSaved(false)
  }, [wrongWords, resetAll])

  return {
    current,
    index,
    total: queue.length,
    flipped,
    graded,
    knewCount,
    wrongWords,
    complete,
    flip,
    grade,
    retryWrong,
  }
}
