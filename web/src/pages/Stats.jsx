import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getWordStats } from '../utils/leitner'

function WordRow({ hanzi, stats }) {
  const total = stats.seen || 0
  const correct = stats.correct || 0
  const wrong = stats.wrong || 0
  const accuracy = total > 0 ? Math.round((correct / total) * 100) : 0

  const getAccuracyColor = () => {
    if (accuracy >= 80) return 'text-green-600'
    if (accuracy >= 60) return 'text-amber-600'
    return 'text-red-600'
  }

  const getBarColor = () => {
    if (accuracy >= 80) return 'bg-green-500'
    if (accuracy >= 60) return 'bg-amber-500'
    return 'bg-red-500'
  }

  return (
    <div className="flex items-center gap-4 py-3 border-b border-gray-100 last:border-0">
      <span className="hanzi-display text-2xl font-bold text-gray-800 w-12 text-center">
        {hanzi}
      </span>
      <div className="flex-1">
        <div className="flex justify-between text-sm mb-1">
          <span className="text-gray-600">
            Seen {total}× • Wrong {wrong}×
          </span>
          <span className={`font-semibold ${getAccuracyColor()}`}>
            {accuracy}%
          </span>
        </div>
        <div className="w-full h-2 bg-gray-100 rounded-full overflow-hidden">
          <div
            className={`h-full ${getBarColor()} rounded-full transition-all`}
            style={{ width: `${accuracy}%` }}
          />
        </div>
      </div>
    </div>
  )
}

export default function Stats() {
  const [wordStats, setWordStats] = useState({})
  const [sortBy, setSortBy] = useState('worst') // worst, mostSeen, best

  useEffect(() => {
    setWordStats(getWordStats())
  }, [])

  const entries = Object.entries(wordStats)

  const sorted = entries.sort((a, b) => {
    const [, statsA] = a
    const [, statsB] = b

    if (sortBy === 'worst') {
      const accA = statsA.seen > 0 ? statsA.correct / statsA.seen : 0
      const accB = statsB.seen > 0 ? statsB.correct / statsB.seen : 0
      return accA - accB
    } else if (sortBy === 'mostSeen') {
      return (statsB.seen || 0) - (statsA.seen || 0)
    } else {
      const accA = statsA.seen > 0 ? statsA.correct / statsA.seen : 0
      const accB = statsB.seen > 0 ? statsB.correct / statsB.seen : 0
      return accB - accA
    }
  })

  const totalWords = entries.length
  const masteredWords = entries.filter(([, s]) => {
    const acc = s.seen > 0 ? s.correct / s.seen : 0
    return acc >= 80 && s.seen >= 3
  }).length
  const strugglingWords = entries.filter(([, s]) => {
    const acc = s.seen > 0 ? s.correct / s.seen : 0
    return acc < 60 && s.seen >= 2
  }).length

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Statistics</h1>

      {/* Overview Cards */}
      <div className="grid grid-cols-3 gap-3 mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-3 text-center">
          <div className="text-2xl font-bold text-gray-800">{totalWords}</div>
          <div className="text-xs text-gray-500">Words Practiced</div>
        </div>
        <div className="bg-green-50 rounded-xl shadow-sm border border-green-200 p-3 text-center">
          <div className="text-2xl font-bold text-green-600">{masteredWords}</div>
          <div className="text-xs text-green-600">Mastered</div>
        </div>
        <div className="bg-red-50 rounded-xl shadow-sm border border-red-200 p-3 text-center">
          <div className="text-2xl font-bold text-red-600">{strugglingWords}</div>
          <div className="text-xs text-red-600">Struggling</div>
        </div>
      </div>

      {/* Sort Options */}
      <div className="flex gap-2 mb-4">
        {[
          { id: 'worst', label: '🔴 Needs Work' },
          { id: 'mostSeen', label: '📊 Most Seen' },
          { id: 'best', label: '🟢 Best' },
        ].map((opt) => (
          <button
            key={opt.id}
            onClick={() => setSortBy(opt.id)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              sortBy === opt.id
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {opt.label}
          </button>
        ))}
      </div>

      {/* Word Stats List */}
      {sorted.length === 0 ? (
        <div className="text-center py-12">
          <div className="text-5xl mb-4">📊</div>
          <p className="text-gray-500 mb-4">No practice data yet</p>
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 transition-colors"
          >
            Start Practicing
          </Link>
        </div>
      ) : (
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4">
          <h3 className="text-sm font-semibold text-gray-700 mb-3">
            {sorted.length} Words Tracked
          </h3>
          {sorted.slice(0, 50).map(([hanzi, stats]) => (
            <WordRow key={hanzi} hanzi={hanzi} stats={stats} />
          ))}
          {sorted.length > 50 && (
            <p className="text-center text-sm text-gray-400 mt-4">
              Showing top 50 of {sorted.length} words
            </p>
          )}
        </div>
      )}
    </div>
  )
}
