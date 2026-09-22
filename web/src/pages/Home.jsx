import { useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { getLessonList } from '../utils/vocabularyLoader'
import { QuizIcon, CardsIcon } from '../components/Icons'

export default function Home() {
  const navigate = useNavigate()
  const lessons = getLessonList()
  const numericLessons = lessons.filter((l) => typeof l.lesson === 'number')
  const [startLesson, setStartLesson] = useState(1)
  const [endLesson, setEndLesson] = useState(numericLessons.length ? numericLessons[numericLessons.length - 1].lesson : 9)

  const startQuiz = () => {
    navigate(`/quiz?start=${startLesson}&end=${endLesson}`)
  }

  const startFlashcard = () => {
    navigate(`/flashcard?start=${startLesson}&end=${endLesson}`)
  }

  const selectAll = () => {
    if (numericLessons.length) {
      setStartLesson(numericLessons[0].lesson)
      setEndLesson(numericLessons[numericLessons.length - 1].lesson)
    }
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      {/* Header */}
      <div className="text-center mb-8">
        <h1 className="text-4xl font-bold text-gray-900 mb-2">Learn Chinese</h1>
        <p className="text-gray-500">HSK1 Vocabulary Practice</p>
      </div>

      {/* Lesson Range Selector */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-5 mb-6">
        <h2 className="text-lg font-semibold text-gray-800 mb-4">Select Lesson Range</h2>

        <div className="flex items-center gap-3 mb-4">
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-600 mb-1">From</label>
            <select
              value={startLesson}
              onChange={(e) => setStartLesson(Number(e.target.value))}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white"
            >
              {numericLessons.map((l) => (
                <option key={l.lesson} value={l.lesson}>
                  L{l.lesson}: {l.title.split(' ')[0]}
                </option>
              ))}
            </select>
          </div>
          <div className="text-gray-400 mt-6">→</div>
          <div className="flex-1">
            <label className="block text-sm font-medium text-gray-600 mb-1">To</label>
            <select
              value={endLesson}
              onChange={(e) => setEndLesson(Number(e.target.value))}
              className="w-full px-3 py-2.5 border border-gray-300 rounded-xl text-sm focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent bg-white"
            >
              {numericLessons
                .filter((l) => l.lesson >= startLesson)
                .map((l) => (
                  <option key={l.lesson} value={l.lesson}>
                    L{l.lesson}: {l.title.split(' ')[0]}
                  </option>
                ))}
            </select>
          </div>
        </div>

        <button
          onClick={selectAll}
          className="text-sm text-red-600 hover:text-red-700 font-medium mb-4"
        >
          Select All Lessons
        </button>

        <div className="bg-gray-50 rounded-xl p-3 text-sm text-gray-600">
          {(() => {
            const words = numericLessons
              .filter((l) => l.lesson >= startLesson && l.lesson <= endLesson)
              .reduce((sum, l) => sum + l.wordCount, 0)
            return `${words} words in selected range`
          })()}
        </div>
      </div>

      {/* Mode Selection */}
      <div className="grid grid-cols-2 gap-4">
        <button
          onClick={startQuiz}
          className="bg-red-600 hover:bg-red-700 text-white rounded-2xl p-5 text-center transition-colors active:scale-95"
        >
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-red-100 text-red-600 mb-3">
            <QuizIcon className="w-6 h-6" />
          </div>
          <div className="font-semibold">Quiz</div>
          <div className="text-xs text-red-200 mt-1">Multiple choice</div>
        </button>

        <button
          onClick={startFlashcard}
          className="bg-white hover:bg-gray-50 text-gray-800 border-2 border-gray-200 rounded-2xl p-5 text-center transition-colors active:scale-95"
        >
          <div className="inline-flex items-center justify-center w-12 h-12 rounded-full bg-blue-50 text-blue-600 mb-3">
            <CardsIcon className="w-6 h-6" />
          </div>
          <div className="font-semibold">Flashcards</div>
          <div className="text-xs text-gray-400 mt-1">Self-graded</div>
        </button>
      </div>

      {/* Quick Stats */}
      <div className="mt-8 bg-white rounded-2xl shadow-sm border border-gray-200 p-5">
        <h3 className="text-sm font-semibold text-gray-700 mb-3">Database Overview</h3>
        <div className="grid grid-cols-3 gap-4 text-center">
          <div>
            <div className="text-2xl font-bold text-red-600">
              {numericLessons.reduce((sum, l) => sum + l.wordCount, 0)}
            </div>
            <div className="text-xs text-gray-500">Words</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">{numericLessons.length}</div>
            <div className="text-xs text-gray-500">Lessons</div>
          </div>
          <div>
            <div className="text-2xl font-bold text-red-600">10</div>
            <div className="text-xs text-gray-500">Measure Words</div>
          </div>
        </div>
      </div>
    </div>
  )
}
