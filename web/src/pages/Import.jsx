import { useState, useRef, useEffect } from 'react'
import { Link } from 'react-router-dom'
import {
  loadCustomLessons,
  deleteCustomLesson,
  validateLesson,
  importLesson,
} from '../utils/customLessons'
import { refreshLessons } from '../utils/vocabularyLoader'
import { QuizIcon, XIcon, InboxIcon } from '../components/Icons'

const SAMPLE = `{
  "lesson": 12,
  "title": "我能坐这儿吗 (Can I sit here)",
  "words": [
    {
      "hanzi": "能",
      "pinyin": "néng",
      "english": "can; to be able to",
      "vietnamese": "có thể"
    },
    {
      "hanzi": "坐",
      "pinyin": "zuò",
      "english": "to sit"
    }
  ]
}`

export default function Import() {
  const [lessons, setLessons] = useState([])
  const [jsonText, setJsonText] = useState('')
  const [fileName, setFileName] = useState('')
  const [errors, setErrors] = useState([])
  const [success, setSuccess] = useState('')
  const [dragOver, setDragOver] = useState(false)
  const fileRef = useRef(null)

  const reload = () => setLessons(loadCustomLessons())
  useEffect(reload, [])

  const handleData = (text, name) => {
    setSuccess('')
    let data
    try {
      data = JSON.parse(text)
    } catch (e) {
      setErrors([`Invalid JSON${name ? ` in ${name}` : ''}: ${e.message}`])
      return
    }
    const { ok, errors: errs, lesson } = validateLesson(data)
    if (!ok) {
      setErrors(errs)
      return
    }
    const result = importLesson(lesson)
    if (!result.ok) {
      setErrors([result.error])
      return
    }
    refreshLessons()
    setErrors([])
    setSuccess(`Lesson ${lesson.lesson} "${lesson.title}" imported — ${lesson.words.length} words.`)
    setJsonText('')
    setFileName('')
    reload()
  }

  const handleFile = (file) => {
    if (!file) return
    setFileName(file.name)
    const reader = new FileReader()
    reader.onload = (e) => handleData(e.target.result, file.name)
    reader.readAsText(file)
  }

  const handleDelete = (num) => {
    if (!window.confirm(`Delete custom lesson ${num}? Progress stats for its words remain but it won't be quiz-able.`)) return
    deleteCustomLesson(num)
    refreshLessons()
    reload()
  }

  return (
    <div className="max-w-lg mx-auto px-4 py-6">
      <h1 className="text-2xl font-bold text-gray-900 mb-2">Import a Lesson</h1>
      <p className="text-sm text-gray-500 mb-6">
        Add your own vocabulary lessons as JSON. They appear in the lesson selector and work in
        Quiz and Flashcards like built-in lessons. Your imports stay on this device.
      </p>

      {/* Drop zone / file picker */}
      <div
        onDragOver={(e) => { e.preventDefault(); setDragOver(true) }}
        onDragLeave={() => setDragOver(false)}
        onDrop={(e) => { e.preventDefault(); setDragOver(false); handleFile(e.dataTransfer.files[0]) }}
        onClick={() => fileRef.current?.click()}
        className={`border-2 border-dashed rounded-2xl p-8 text-center cursor-pointer transition-colors mb-4 ${
          dragOver ? 'border-red-400 bg-red-50' : 'border-gray-300 bg-white hover:border-red-300 hover:bg-red-50'
        }`}
      >
        <input
          ref={fileRef}
          type="file"
          accept=".json,application/json"
          className="hidden"
          onChange={(e) => handleFile(e.target.files[0])}
        />
        <div className="text-gray-500">
          <div className="text-lg font-medium">Drop a .json lesson here</div>
          <div className="text-sm mt-1">or tap to browse</div>
          {fileName && <div className="text-sm mt-2 text-red-600 font-medium">📄 {fileName}</div>}
        </div>
      </div>

      {/* Paste JSON */}
      <div className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 mb-4">
        <label className="block text-sm font-medium text-gray-700 mb-2">
          …or paste the lesson JSON
        </label>
        <textarea
          value={jsonText}
          onChange={(e) => setJsonText(e.target.value)}
          rows={8}
          spellCheck={false}
          placeholder={SAMPLE}
          className="w-full px-3 py-2 border border-gray-300 rounded-xl text-xs font-mono focus:outline-none focus:ring-2 focus:ring-red-500 focus:border-transparent"
        />
        <div className="flex gap-2 mt-3">
          <button
            onClick={() => handleData(jsonText)}
            disabled={!jsonText.trim()}
            className="px-4 py-2 bg-red-600 hover:bg-red-700 disabled:bg-gray-300 text-white text-sm font-semibold rounded-xl transition-colors"
          >
            Validate & Import
          </button>
          <button
            onClick={() => setJsonText(SAMPLE)}
            className="px-4 py-2 bg-gray-100 hover:bg-gray-200 text-gray-700 text-sm font-semibold rounded-xl transition-colors"
          >
            Fill sample
          </button>
        </div>
      </div>

      {/* Feedback */}
      {errors.length > 0 && (
        <div className="bg-red-50 border border-red-200 rounded-xl p-4 mb-4 fade-in">
          <h3 className="text-sm font-semibold text-red-800 mb-2">Import failed:</h3>
          <ul className="list-disc list-inside space-y-1">
            {errors.map((e, i) => (
              <li key={i} className="text-sm text-red-700">{e}</li>
            ))}
          </ul>
        </div>
      )}
      {success && (
        <div className="bg-green-50 border border-green-200 rounded-xl p-4 mb-4 fade-in">
          <p className="text-sm font-semibold text-green-800">✓ {success}</p>
        </div>
      )}

      {/* Format docs */}
      <details className="bg-white rounded-2xl shadow-sm border border-gray-200 p-4 mb-6">
        <summary className="text-sm font-semibold text-gray-700 cursor-pointer">
          Expected JSON format
        </summary>
        <pre className="mt-3 text-xs font-mono bg-gray-50 rounded-lg p-3 overflow-x-auto">{SAMPLE}</pre>
        <ul className="mt-3 text-xs text-gray-600 space-y-1 list-disc list-inside">
          <li><b>lesson</b>: positive integer — must not collide with built-ins (1–9, 11). Use 12+ or 101+.</li>
          <li><b>title</b>: shown in the lesson selector.</li>
          <li><b>words[]</b>: hanzi, pinyin, english required per word. vietnamese + example_sentences optional.</li>
          <li>Output of <code>scripts/pdf_extract.py</code> / <code>scripts/auto_extract.py</code> is compatible — import <code>extracted_L12.json</code> directly.</li>
        </ul>
      </details>

      {/* Imported lessons */}
      <h2 className="text-lg font-semibold text-gray-800 mb-3">Imported Lessons ({lessons.length})</h2>
      {lessons.length === 0 ? (
        <div className="text-center py-8 bg-white rounded-2xl shadow-sm border border-gray-200">
          <div className="inline-flex items-center justify-center w-14 h-14 rounded-full bg-gray-100 text-gray-400 mb-3">
            <InboxIcon className="w-7 h-7" />
          </div>
          <p className="text-sm text-gray-500">No custom lessons yet</p>
        </div>
      ) : (
        <div className="space-y-3">
          {lessons.map((l) => (
            <div key={l.lesson} className="bg-white rounded-xl shadow-sm border border-gray-200 p-4 flex items-center justify-between">
              <div className="flex items-center gap-3">
                <span className="inline-flex items-center justify-center w-10 h-10 rounded-full bg-purple-100 text-purple-600">
                  <QuizIcon className="w-5 h-5" />
                </span>
                <div>
                  <div className="font-semibold text-gray-800">
                    L{l.lesson}: {l.title}
                  </div>
                  <div className="text-xs text-gray-500">{l.words.length} words</div>
                </div>
              </div>
              <button
                onClick={() => handleDelete(l.lesson)}
                aria-label={`Delete lesson ${l.lesson}`}
                className="p-2 rounded-full text-gray-400 hover:text-red-600 hover:bg-red-50 transition-colors"
              >
                <XIcon className="w-4 h-4" />
              </button>
            </div>
          ))}
        </div>
      )}

      <div className="mt-6 text-center">
        <Link to="/" className="text-sm text-red-600 hover:text-red-700 font-medium">
          ← Back to Home
        </Link>
      </div>
    </div>
  )
}
