import { useState, useEffect } from 'react'
import { Link } from 'react-router-dom'
import { getSessions } from '../utils/leitner'
import { QuizIcon, CardsIcon, InboxIcon } from '../components/Icons'

function ModeIcon({ mode, className = 'w-6 h-6' }) {
  return mode === 'quiz' ? (
    <QuizIcon className={className} />
  ) : (
    <CardsIcon className={className} />
  )
}

function SessionCard({ session, index }) {
  const [expanded, setExpanded] = useState(false)
  const date = new Date(session.date)
  const pct = session.totalWords > 0
    ? Math.round((session.correct / session.totalWords) * 100)
    : 0

  const modeLabel = session.mode === 'quiz' ? 'Quiz' : 'Flashcard'

  return (
    <div className="bg-white rounded-xl shadow-sm border border-gray-200 overflow-hidden">
      <button
        onClick={() => setExpanded(!expanded)}
        className="w-full p-4 text-left hover:bg-gray-50 transition-colors"
      >
        <div className="flex items-center justify-between">
          <div className="flex items-center gap-3">
            <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-gray-100 text-gray-600">
              <ModeIcon mode={session.mode} />
            </span>
            <div>
              <div className="font-semibold text-gray-800">
                {modeLabel} — L{session.lessonStart} to L{session.lessonEnd}
              </div>
              <div className="text-sm text-gray-500">
                {date.toLocaleDateString()} {date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
              </div>
            </div>
          </div>
          <div className="text-right">
            <div className={`text-lg font-bold ${pct >= 70 ? 'text-green-600' : pct >= 50 ? 'text-amber-600' : 'text-red-600'}`}>
              {pct}%
            </div>
            <div className="text-xs text-gray-400">
              {session.correct}/{session.totalWords}
            </div>
          </div>
        </div>
      </button>

      {expanded && session.wrongWords && session.wrongWords.length > 0 && (
        <div className="px-4 pb-4 border-t border-gray-100">
          <h4 className="text-sm font-semibold text-gray-600 mt-3 mb-2">
            Words to Review ({session.wrongWords.length}):
          </h4>
          <div className="flex flex-wrap gap-2">
            {session.wrongWords.map((w, i) => (
              <span
                key={i}
                className="inline-flex items-center gap-1 px-3 py-1.5 bg-red-50 text-red-700 rounded-full text-sm"
              >
                <span className="hanzi-display font-medium">{w.hanzi}</span>
                <span className="text-red-400 text-xs">{w.pinyin}</span>
                <span className="text-red-500 text-xs">= {w.english}</span>
              </span>
            ))}
          </div>
        </div>
      )}
    </div>
  )
}

export default function History() {
  const [sessions, setSessions] = useState([])
  const [filter, setFilter] = useState('all') // all, quiz, flashcard

  useEffect(() => {
    setSessions(getSessions())
  }, [])

  const filtered = sessions.filter((s) => {
    if (filter === 'all') return true
    return s.mode === filter
  })

  const totalSessions = sessions.length
  const avgScore = sessions.length > 0
    ? Math.round(
        sessions.reduce((sum, s) => sum + (s.totalWords > 0 ? (s.correct / s.totalWords) * 100 : 0), 0) / sessions.length
      )
    : 0

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-6">Practice History</h1>

      {/* Summary */}
      <div className="grid grid-cols-2 gap-4 mb-6">
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-3xl font-bold text-gray-800">{totalSessions}</div>
          <div className="text-sm text-gray-500">Total Sessions</div>
        </div>
        <div className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 text-center">
          <div className="text-3xl font-bold text-gray-800">{avgScore}%</div>
          <div className="text-sm text-gray-500">Average Score</div>
        </div>
      </div>

      {/* Filter */}
      <div className="flex gap-2 mb-4">
        {['all', 'quiz', 'flashcard'].map((f) => (
          <button
            key={f}
            onClick={() => setFilter(f)}
            className={`px-4 py-2 rounded-lg text-sm font-medium transition-colors ${
              filter === f
                ? 'bg-red-100 text-red-700'
                : 'bg-gray-100 text-gray-600 hover:bg-gray-200'
            }`}
          >
            {f === 'all' ? 'All' : f === 'quiz' ? 'Quiz' : 'Flashcard'}
          </button>
        ))}
      </div>

      {/* Session List */}
      {filtered.length === 0 ? (
        <div className="text-center py-12">
          <div className="inline-flex items-center justify-center w-16 h-16 rounded-full bg-gray-100 text-gray-400 mb-4">
            <InboxIcon className="w-8 h-8" />
          </div>
          <p className="text-gray-500 mb-4">No sessions yet</p>
          <Link
            to="/"
            className="inline-block px-6 py-3 bg-red-600 text-white font-semibold rounded-xl hover:bg-red-700 transition-colors"
          >
            Start Practicing
          </Link>
        </div>
      ) : (
        <div className="space-y-3">
          {filtered.map((session, i) => (
            <SessionCard key={i} session={session} index={i} />
          ))}
        </div>
      )}
    </div>
  )
}
