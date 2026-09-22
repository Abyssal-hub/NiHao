import { Routes, Route, Link, useLocation } from 'react-router-dom'
import { useState } from 'react'
import Home from './pages/Home'
import Quiz from './pages/Quiz'
import Flashcard from './pages/Flashcard'
import History from './pages/History'
import Stats from './pages/Stats'
import { SpeakerIcon } from './components/Icons'
import { isMuted, setMuted } from './hooks/useSpeech'

function MuteToggle() {
  const [muted, setMutedState] = useState(isMuted)

  const toggle = () => {
    const next = !muted
    setMutedState(next)
    setMuted(next)
  }

  return (
    <button
      onClick={toggle}
      aria-label={muted ? 'Unmute pronunciation' : 'Mute pronunciation'}
      title={muted ? 'Unmute pronunciation' : 'Mute pronunciation'}
      className={`p-2 rounded-full transition-colors ${
        muted ? 'bg-gray-200 text-gray-500' : 'bg-red-50 text-red-600 hover:bg-red-100'
      }`}
    >
      <SpeakerIcon className="w-5 h-5" muted={muted} />
    </button>
  )
}

function NavBar() {
  const location = useLocation()
  const isActive = (path) => location.pathname === path

  return (
    <nav className="bg-white shadow-sm border-b border-gray-200 sticky top-0 z-50">
      <div className="max-w-lg mx-auto px-4">
        <div className="flex items-center justify-between h-14">
          <Link to="/" className="flex items-center gap-2">
            <span className="text-2xl font-bold text-red-700">你好</span>
            <span className="text-sm text-gray-500 hidden sm:inline">NiHao</span>
          </Link>
          <div className="flex items-center gap-2">
            <MuteToggle />
            <Link
              to="/"
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/') ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              Home
            </Link>
            <Link
              to="/history"
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/history') ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              History
            </Link>
            <Link
              to="/stats"
              className={`px-3 py-2 rounded-lg text-sm font-medium transition-colors ${
                isActive('/stats') ? 'bg-red-50 text-red-700' : 'text-gray-600 hover:bg-gray-50'
              }`}
            >
              Stats
            </Link>
          </div>
        </div>
      </div>
    </nav>
  )
}

export default function App() {
  return (
    <div className="min-h-screen bg-gray-50">
      <NavBar />
      <main className="pb-8">
        <Routes>
          <Route path="/" element={<Home />} />
          <Route path="/quiz" element={<Quiz />} />
          <Route path="/flashcard" element={<Flashcard />} />
          <Route path="/history" element={<History />} />
          <Route path="/stats" element={<Stats />} />
        </Routes>
      </main>
    </div>
  )
}
