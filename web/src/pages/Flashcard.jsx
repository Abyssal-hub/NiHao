import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useFlashcard } from '../hooks/useFlashcard'
import { useSpeech } from '../hooks/useSpeech'

function AudioButton({ text, size = 'md', autoPlay = false }) {
  const { speak, speaking, supported } = useSpeech()

  // Auto-play when word changes
  useEffect(() => {
    if (autoPlay && supported && text) {
      const timer = setTimeout(() => speak(text), 300)
      return () => clearTimeout(timer)
    }
  }, [text, autoPlay, supported, speak])

  if (!supported) return null

  const sizeClass = size === 'lg' ? 'p-4 text-2xl' : 'p-2 text-base'

  return (
    <button
      onClick={(e) => {
        e.stopPropagation()
        speak(text)
      }}
      className={`${sizeClass} rounded-full bg-blue-50 hover:bg-blue-100 text-blue-600 transition-colors ${speaking ? 'animate-pulse bg-blue-200' : ''}`}
      title="Listen to pronunciation"
    >
      🔊
    </button>
  )
}

function PinyinDisplay({ pinyin }) {
  const toneMap = {
    'ā': 1, 'ē': 1, 'ī': 1, 'ō': 1, 'ū': 1, 'ǖ': 1,
    'á': 2, 'é': 2, 'í': 2, 'ó': 2, 'ú': 2, 'ǘ': 2,
    'ǎ': 3, 'ě': 3, 'ǐ': 3, 'ǒ': 3, 'ǔ': 3, 'ǚ': 3,
    'à': 4, 'è': 4, 'ì': 4, 'ò': 4, 'ù': 4, 'ǜ': 4,
  }

  const syllables = pinyin.split(' ')

  return (
    <span>
      {syllables.map((syl, i) => {
        let tone = 0
        for (const ch of syl) {
          if (toneMap[ch]) {
            tone = toneMap[ch]
            break
          }
        }
        return (
          <span key={i} className={`tone-${tone}`}>
            {syl}
            {i < syllables.length - 1 ? ' ' : ''}
          </span>
        )
      })}
    </span>
  )
}

function ExampleSentences({ examples }) {
  if (!examples || examples.length === 0) return null

  return (
    <div className="mt-4 p-4 bg-amber-50 rounded-xl border border-amber-100 text-left">
      <h4 className="text-sm font-semibold text-amber-800 mb-2">Example Sentences</h4>
      <ul className="space-y-2">
        {examples.map((ex, idx) => (
          <li key={idx} className="text-sm text-amber-900">
            {ex}
          </li>
        ))}
      </ul>
    </div>
  )
}

function ProgressBar({ current, total }) {
  const pct = total > 0 ? Math.round(((current + 1) / total) * 100) : 0
  return (
    <div className="mb-4">
      <div className="flex justify-between text-sm text-gray-500 mb-1">
        <span>{current + 1} / {total}</span>
        <span>{pct}%</span>
      </div>
      <div className="w-full h-2 bg-gray-200 rounded-full overflow-hidden">
        <div
          className="h-full bg-blue-500 rounded-full transition-all duration-300"
          style={{ width: `${pct}%` }}
        />
      </div>
    </div>
  )
}

function ResultScreen({ correct, total, wrongWords, onRetry, onHome }) {
  const pct = total > 0 ? Math.round((correct / total) * 100) : 0

  return (
    <div className="max-w-lg mx-auto px-4 py-8 fade-in">
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 text-center">
        <div className="text-6xl mb-4">
          {pct >= 90 ? '🎉' : pct >= 70 ? '👍' : pct >= 50 ? '📚' : '💪'}
        </div>
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Flashcards Complete!</h2>
        <p className="text-gray-500 mb-6">
          You knew {correct} out of {total} words ({pct}%)
        </p>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-green-50 rounded-xl p-4">
            <div className="text-3xl font-bold text-green-600">{correct}</div>
            <div className="text-sm text-green-600">Knew</div>
          </div>
          <div className="bg-red-50 rounded-xl p-4">
            <div className="text-3xl font-bold text-red-600">{total - correct}</div>
            <div className="text-sm text-red-600">Forgot</div>
          </div>
        </div>

        {wrongWords.length > 0 && (
          <div className="mb-6 text-left">
            <h3 className="text-sm font-semibold text-gray-700 mb-3">Words to Review:</h3>
            <div className="flex flex-wrap gap-2">
              {wrongWords.map((w, i) => (
                <span
                  key={i}
                  className="inline-flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-700 rounded-full text-sm"
                >
                  <span className="hanzi-display font-medium">{w.hanzi}</span>
                  <span className="text-red-500">{w.pinyin}</span>
                </span>
              ))}
            </div>
          </div>
        )}

        <div className="space-y-3">
          {wrongWords.length > 0 && (
            <button
              onClick={onRetry}
              className="w-full py-3 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors"
            >
              Review Forgotten Words ({wrongWords.length})
            </button>
          )}
          <button
            onClick={onHome}
            className="w-full py-3 bg-gray-100 hover:bg-gray-200 text-gray-700 font-semibold rounded-xl transition-colors"
          >
            Back to Home
          </button>
        </div>
      </div>
    </div>
  )
}

export default function Flashcard() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const start = parseInt(searchParams.get('start') || '1')
  const end = parseInt(searchParams.get('end') || '9')

  const {
    current: word,
    index,
    total,
    flipped,
    correctCount,
    wrongWords,
    complete,
    flip,
    grade,
    retryWrong,
  } = useFlashcard({ start, end })

  const [touchStart, setTouchStart] = useState(null)
  const [touchEnd, setTouchEnd] = useState(null)

  // Swipe detection
  const minSwipeDistance = 50

  const onTouchStart = (e) => {
    setTouchEnd(null)
    setTouchStart(e.targetTouches[0].clientX)
  }

  const onTouchMove = (e) => {
    setTouchEnd(e.targetTouches[0].clientX)
  }

  const onTouchEnd = () => {
    if (!touchStart || !touchEnd) return
    const distance = touchStart - touchEnd
    const isLeftSwipe = distance > minSwipeDistance
    const isRightSwipe = distance < -minSwipeDistance

    if (flipped) {
      if (isLeftSwipe) {
        // Swipe left = forgot
        grade(false)
      } else if (isRightSwipe) {
        // Swipe right = knew
        grade(true)
      }
    }
  }

  if (complete) {
    return (
      <ResultScreen
        correct={correctCount}
        total={total}
        wrongWords={wrongWords}
        onRetry={retryWrong}
        onHome={() => navigate('/')}
      />
    )
  }

  if (!word) {
    return (
      <div className="max-w-lg mx-auto px-4 py-8 text-center">
        <p className="text-gray-500">No words found in this range.</p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 px-4 py-2 bg-blue-600 text-white rounded-lg"
        >
          Go Home
        </button>
      </div>
    )
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      <ProgressBar current={index} total={total} />

      {/* Score */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-sm text-gray-500">
          Knew: <span className="font-semibold text-green-600">{correctCount}</span>
          {' | '}
          Forgot: <span className="font-semibold text-red-600">{wrongWords.length}</span>
        </div>
      </div>

      {/* Flashcard */}
      <div
        className="flashcard-container h-80 mb-6 cursor-pointer select-none"
        onClick={() => !flipped && flip()}
        onTouchStart={onTouchStart}
        onTouchMove={onTouchMove}
        onTouchEnd={onTouchEnd}
      >
        <div className={`flashcard-inner ${flipped ? 'flipped' : ''}`}>
          {/* Front */}
          <div className="flashcard-front bg-white rounded-2xl shadow-sm border border-gray-200 flex flex-col items-center justify-center p-6">
            <div className="flex items-center gap-4 mb-4">
              <div className="hanzi-display text-8xl font-bold text-gray-900">
                {word.hanzi}
              </div>
              <AudioButton text={word.hanzi} size="lg" autoPlay={true} />
            </div>
            <p className="text-gray-400 text-sm">Tap to reveal answer</p>
          </div>

          {/* Back */}
          <div className="flashcard-back bg-white rounded-2xl shadow-sm border border-gray-200 flex flex-col items-center justify-center p-6 overflow-y-auto">
            <div className="flex items-center gap-3 mb-3">
              <div className="hanzi-display text-5xl font-bold text-gray-900">
                {word.hanzi}
              </div>
              <AudioButton text={word.hanzi} />
            </div>
            <div className="text-2xl mb-2">
              <PinyinDisplay pinyin={word.pinyin} />
            </div>
            <div className="text-lg font-semibold text-gray-700 mb-1">
              🇬🇧 {word.english}
            </div>
            {word.vietnamese && (
              <div className="text-base text-gray-600 mb-2">
                🇻🇳 {word.vietnamese}
              </div>
            )}
            <ExampleSentences examples={word.example_sentences} />
          </div>
        </div>
      </div>

      {/* Grading buttons (show after flip) */}
      {flipped ? (
        <div className="grid grid-cols-2 gap-4 fade-in">
          <button
            onClick={() => grade(false)}
            className="py-4 bg-red-100 hover:bg-red-200 text-red-700 font-semibold rounded-xl transition-colors active:scale-95"
          >
            ❌ Forgot
          </button>
          <button
            onClick={() => grade(true)}
            className="py-4 bg-green-100 hover:bg-green-200 text-green-700 font-semibold rounded-xl transition-colors active:scale-95"
          >
            ✅ Knew It
          </button>
        </div>
      ) : (
        <button
          onClick={flip}
          className="w-full py-4 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-xl transition-colors active:scale-95"
        >
          Flip Card
        </button>
      )}

      {/* Swipe hint */}
      {flipped && (
        <p className="text-center text-xs text-gray-400 mt-4">
          Swipe right = Knew it • Swipe left = Forgot
        </p>
      )}
    </div>
  )
}
