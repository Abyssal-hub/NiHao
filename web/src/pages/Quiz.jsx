import { useState, useEffect } from 'react'
import { useSearchParams, useNavigate } from 'react-router-dom'
import { useQuiz } from '../hooks/useQuiz'
import { useSpeech } from '../hooks/useSpeech'

function AudioButton({ text, size = 'md' }) {
  const { speak, speaking, supported } = useSpeech()
  if (!supported) return null

  const sizeClass = size === 'lg' ? 'p-3 text-xl' : 'p-2 text-base'

  return (
    <button
      onClick={(e) => {
        e.stopPropagation()
        speak(text)
      }}
      className={`${sizeClass} rounded-full bg-gray-100 hover:bg-gray-200 transition-colors ${speaking ? 'animate-pulse bg-red-100' : ''}`}
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

function StrokeOrderDisplay({ hanzi }) {
  const [strokes, setStrokes] = useState([])
  const [currentStroke, setCurrentStroke] = useState(0)
  const [showStroke, setShowStroke] = useState(false)

  useEffect(() => {
    setStrokes([])
    setCurrentStroke(0)
    setShowStroke(false)
  }, [hanzi])

  const loadStrokeOrder = async () => {
    if (showStroke) {
      setShowStroke(false)
      return
    }

    if (hanzi.length === 1) {
      try {
        // Use a simple stroke count approximation
        setStrokes([1, 2, 3, 4, 5])
        setShowStroke(true)
      } catch (e) {
        console.log('Stroke order not available')
      }
    } else {
      // For multi-char words, show each char's stroke count
      setShowStroke(true)
    }
  }

  return (
    <div className="mt-3">
      <button
        onClick={loadStrokeOrder}
        className="text-xs text-gray-400 hover:text-gray-600 underline"
      >
        {showStroke ? 'Hide stroke info' : 'Show stroke info'}
      </button>
      {showStroke && (
        <div className="mt-2 p-3 bg-gray-50 rounded-xl">
          {hanzi.split('').map((char, idx) => (
            <div key={idx} className="flex items-center gap-3 mb-2 last:mb-0">
              <span className="text-2xl hanzi-display">{char}</span>
              <span className="text-sm text-gray-500">
                {getStrokeCount(char)} strokes
              </span>
            </div>
          ))}
        </div>
      )}
    </div>
  )
}

// Approximate stroke counts for common HSK1 characters
function getStrokeCount(char) {
  const counts = {
    '一': 1, '二': 2, '三': 3, '十': 2, '人': 2, '口': 3, '日': 4, '月': 4,
    '你': 7, '好': 6, '我': 7, '他': 5, '她': 6, '是': 9, '不': 4, '了': 2,
    '在': 6, '有': 6, '家': 10, '学': 8, '校': 10, '老': 6, '师': 6, '吗': 6,
    '呢': 8, '很': 9, '大': 3, '小': 3, '中': 4, '国': 8, '年': 6,
    '号': 5, '星': 9, '期': 12, '今': 4, '天': 4, '明': 8, '昨': 9, '去': 5,
    '来': 7, '吃': 6, '喝': 12, '说': 9, '看': 9, '见': 4, '买': 6, '卖': 8,
    '钱': 10, '块': 7, '杯': 8, '茶': 9, '饭': 7, '菜': 11, '水': 4, '水果': 8,
  }
  return counts[char] || '?'
}

function ExampleSentences({ examples }) {
  if (!examples || examples.length === 0) return null

  return (
    <div className="mt-4 p-4 bg-amber-50 rounded-xl border border-amber-100">
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
          className="h-full bg-red-500 rounded-full transition-all duration-300"
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
        <h2 className="text-2xl font-bold text-gray-900 mb-2">Quiz Complete!</h2>
        <p className="text-gray-500 mb-6">
          You got {correct} out of {total} correct ({pct}%)
        </p>

        <div className="grid grid-cols-2 gap-4 mb-6">
          <div className="bg-green-50 rounded-xl p-4">
            <div className="text-3xl font-bold text-green-600">{correct}</div>
            <div className="text-sm text-green-600">Correct</div>
          </div>
          <div className="bg-red-50 rounded-xl p-4">
            <div className="text-3xl font-bold text-red-600">{total - correct}</div>
            <div className="text-sm text-red-600">Wrong</div>
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
              className="w-full py-3 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-colors"
            >
              Retry Wrong Words ({wrongWords.length})
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

export default function Quiz() {
  const [searchParams] = useSearchParams()
  const navigate = useNavigate()
  const start = parseInt(searchParams.get('start') || '1')
  const end = parseInt(searchParams.get('end') || '9')

  const {
    question,
    index,
    total,
    selected,
    answered,
    correctCount,
    wrongWords,
    complete,
    answer,
    next,
    retryWrong,
  } = useQuiz({ start, end })

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

  if (!question) {
    return (
      <div className="max-w-lg mx-auto px-4 py-8 text-center">
        <p className="text-gray-500">No words found in this range.</p>
        <button
          onClick={() => navigate('/')}
          className="mt-4 px-4 py-2 bg-red-600 text-white rounded-lg"
        >
          Go Home
        </button>
      </div>
    )
  }

  const isCorrect = selected?.hanzi === question.word.hanzi

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      <ProgressBar current={index} total={total} />

      {/* Score */}
      <div className="flex justify-between items-center mb-4">
        <div className="text-sm text-gray-500">
          Score: <span className="font-semibold text-green-600">{correctCount}</span>
        </div>
        <AudioButton text={question.word.hanzi} />
      </div>

      {/* Question Card */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-6 mb-6">
        <div className="text-center mb-6">
          <p className="text-sm text-gray-400 mb-3">What does this mean?</p>
          <div className="hanzi-display text-7xl font-bold text-gray-900 mb-2">
            {question.word.hanzi}
          </div>
          <div className="text-xl">
            <PinyinDisplay pinyin={question.word.pinyin} />
          </div>
        </div>

        {/* Answer Options */}
        <div className="space-y-3">
          {question.options.map((opt, i) => {
            let btnClass = 'w-full p-4 text-left rounded-xl border-2 transition-all '
            
            if (answered) {
              if (opt.hanzi === question.word.hanzi) {
                btnClass += 'border-green-500 bg-green-50 text-green-800'
              } else if (selected?.hanzi === opt.hanzi) {
                btnClass += 'border-red-500 bg-red-50 text-red-800'
              } else {
                btnClass += 'border-gray-200 bg-white text-gray-400'
              }
            } else {
              btnClass += 'border-gray-200 bg-white hover:border-red-300 hover:bg-red-50 text-gray-700 active:scale-95'
            }

            return (
              <button
                key={i}
                onClick={() => answer(opt)}
                disabled={answered}
                className={btnClass}
              >
                <span className="font-medium">{opt.english}</span>
              </button>
            )
          })}
        </div>

        {/* Feedback */}
        {answered && (
          <div className={`mt-6 p-4 rounded-xl fade-in ${isCorrect ? 'feedback-correct' : 'feedback-wrong'}`}>
            <div className="flex items-center gap-2 mb-2">
              <span className="text-xl">{isCorrect ? '✅' : '❌'}</span>
              <span className={`font-semibold ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                {isCorrect ? 'Correct!' : `Wrong. The answer is "${question.word.english}"`}
              </span>
            </div>
            <ExampleSentences examples={question.word.example_sentences} />
            <StrokeOrderDisplay hanzi={question.word.hanzi} />
          </div>
        )}
      </div>

      {/* Next Button */}
      {answered && (
        <button
          onClick={next}
          className="w-full py-4 bg-red-600 hover:bg-red-700 text-white font-semibold rounded-xl transition-colors active:scale-95 fade-in"
        >
          {index + 1 >= total ? 'See Results' : 'Next Word →'}
        </button>
      )}
    </div>
  )
}
