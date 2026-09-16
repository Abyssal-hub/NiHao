import { useState, useEffect, useCallback } from 'react'
import { getWordsForRange } from '../utils/vocabularyLoader'
import { shuffle, buildQuestion } from '../utils/scoring'
import { recordSession } from '../utils/leitner'

function initQueue(start, end, includeAppendix) {
  return shuffle(getWordsForRange(start, end, { includeAppendix }))
}

/**
 * Multiple-choice quiz engine. Runs through every word in the range
 * exactly once (no repeats). Persists a session + word stats on completion.
 */
export function useQuiz({ start, end, includeAppendix = false }) {
  const [queue, setQueue] = useState(() => initQueue(start, end, includeAppendix))
  const [index, setIndex] = useState(0)
  const [question, setQuestion] = useState(() =>
    queue.length ? buildQuestion(queue[0], queue) : null
  )
  const [selected, setSelected] = useState(null)
  const [answered, setAnswered] = useState(false)
  const [correctCount, setCorrectCount] = useState(0)
  const [wrongWords, setWrongWords] = useState([])
  const [results, setResults] = useState([])
  const [complete, setComplete] = useState(false)
  const [saved, setSaved] = useState(false)

  // Reset when the lesson range changes
  useEffect(() => {
    const q = initQueue(start, end, includeAppendix)
    setQueue(q)
    setIndex(0)
    setQuestion(q.length ? buildQuestion(q[0], q) : null)
    setSelected(null)
    setAnswered(false)
    setCorrectCount(0)
    setWrongWords([])
    setResults([])
    setComplete(false)
    setSaved(false)
  }, [start, end, includeAppendix])

  const answer = useCallback(
    (option) => {
      if (answered || complete || !question) return
      const isCorrect = option.hanzi === question.word.hanzi
      setSelected(option)
      setAnswered(true)
      setCorrectCount((c) => c + (isCorrect ? 1 : 0))
      setWrongWords((w) => (isCorrect ? w : [...w, question.word]))
      setResults((r) => [...r, { word: question.word, correct: isCorrect }])
    },
    [answered, complete, question]
  )

  const next = useCallback(() => {
    if (!answered || complete) return
    if (index + 1 >= queue.length) {
      setComplete(true)
      return
    }
    const ni = index + 1
    setIndex(ni)
    setQuestion(buildQuestion(queue[ni], queue))
    setSelected(null)
    setAnswered(false)
  }, [answered, complete, index, queue])

  // Persist exactly once when the session completes
  useEffect(() => {
    if (complete && !saved) {
      recordSession({
        mode: 'quiz',
        lessonStart: start,
        lessonEnd: end,
        totalWords: queue.length,
        correct: correctCount,
        wrongWords,
        results,
      })
      setSaved(true)
    }
  }, [complete, saved, start, end, queue.length, correctCount, wrongWords, results])

  const retryWrong = useCallback(() => {
    if (!wrongWords.length) return
    const q = shuffle(wrongWords)
    setQueue(q)
    setIndex(0)
    setQuestion(buildQuestion(q[0], q))
    setSelected(null)
    setAnswered(false)
    setCorrectCount(0)
    setWrongWords([])
    setResults([])
    setComplete(false)
    setSaved(false) // the retry round saves its own session on completion
  }, [wrongWords])

  return {
    question,
    index,
    total: queue.length,
    selected,
    answered,
    correctCount,
    wrongWords,
    complete,
    answer,
    next,
    retryWrong,
  }
}
