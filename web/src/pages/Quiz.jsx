import { useState, useEffect, useRef } from 'react'
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
  const [showStroke, setShowStroke] = useState(false)
  const canvasRefs = useRef([])
  const writersRef = useRef([])
  const hanziWriterLoaded = useRef(false)

  // Load Hanzi Writer script dynamically
  useEffect(() => {
    if (window.HanziWriter) {
      hanziWriterLoaded.current = true
      return
    }
    const script = document.createElement('script')
    script.src = 'https://cdn.jsdelivr.net/npm/hanzi-writer@3/dist/hanzi-writer.min.js'
    script.async = true
    script.onload = () => {
      hanziWriterLoaded.current = true
    }
    document.body.appendChild(script)
  }, [])

  // Cleanup writers when hanzi changes
  useEffect(() => {
    setShowStroke(false)
    writersRef.current.forEach((w) => {
      if (w && w.cancelAnimation) w.cancelAnimation()
    })
    writersRef.current = []
    canvasRefs.current = []
  }, [hanzi])

  const toggleStroke = () => {
    if (showStroke) {
      // Cancel any running animations
      writersRef.current.forEach((w) => {
        if (w && w.cancelAnimation) w.cancelAnimation()
      })
      writersRef.current = []
      setShowStroke(false)
      return
    }

    // Small delay to ensure DOM is ready
    setTimeout(() => {
      if (!window.HanziWriter) {
        console.warn('Hanzi Writer not loaded yet')
        return
      }

      const chars = hanzi.split('')
      writersRef.current = chars.map((char, idx) => {
        const canvas = canvasRefs.current[idx]
        if (!canvas) return null

        try {
          const writer = window.HanziWriter.create(canvas, char, {
            width: 80,
            height: 80,
            padding: 5,
            strokeAnimationSpeed: 1,
            delayBetweenStrokes: 150,
            radicalColor: '#168F16',
            strokeColor: '#333333',
            outlineColor: '#DDDDDD',
            showCharacter: false,
            showOutline: true,
          })

          // Animate the strokes
          writer.animateCharacter()
          return writer
        } catch (e) {
          console.warn(`Failed to create stroke animation for ${char}:`, e)
          return null
        }
      })
    }, 50)

    setShowStroke(true)
  }

  return (
    <div className="mt-3">
      <button
        onClick={toggleStroke}
        className="text-xs text-blue-500 hover:text-blue-700 font-medium"
      >
        {showStroke ? '▲ Hide stroke animation' : '▼ Show stroke animation'}
      </button>
      {showStroke && (
        <div className="mt-2 p-3 bg-gray-50 rounded-xl">
          <div className="flex justify-end mb-2">
            <button
              onClick={() => {
                writersRef.current.forEach((w) => {
                  if (w && w.animateCharacter) w.animateCharacter()
                })
              }}
              className="text-xs px-3 py-1 bg-blue-100 text-blue-700 rounded-full hover:bg-blue-200 transition-colors"
            >
              🔄 Replay
            </button>
          </div>
          <div className="flex flex-wrap justify-center gap-3">
            {hanzi.split('').map((char, idx) => (
              <div key={idx} className="flex flex-col items-center">
                <div
                  ref={(el) => (canvasRefs.current[idx] = el)}
                  className="bg-white rounded-lg shadow-sm"
                  style={{ width: 80, height: 80 }}
                />
                <span className="text-xs text-gray-400 mt-1">{char}</span>
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  )
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
            <div className="flex items-center gap-2 mb-3">
              <span className="text-xl">{isCorrect ? '✅' : '❌'}</span>
              <span className={`font-semibold ${isCorrect ? 'text-green-700' : 'text-red-700'}`}>
                {isCorrect ? 'Correct!' : 'Wrong!'}
              </span>
            </div>

            {/* Word Details */}
            <div className="bg-white rounded-xl p-4 mb-3">
              <div className="text-center">
                <div className="hanzi-display text-4xl font-bold text-gray-800 mb-1">
                  {question.word.hanzi}
                </div>
                <div className="text-lg mb-1">
                  <PinyinDisplay pinyin={question.word.pinyin} />
                </div>
                <div className="text-gray-700 font-medium mb-1">
                  🇬🇧 {question.word.english}
                </div>
                {question.word.vietnamese && (
                  <div className="text-gray-600">
                    🇻🇳 {question.word.vietnamese}
                  </div>
                )}
              </div>
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
