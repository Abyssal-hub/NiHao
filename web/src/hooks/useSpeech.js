import { useState, useEffect, useCallback } from 'react'

const MUTE_KEY = 'nihao_muted'
export const MUTE_EVENT = 'nihao:mute-changed'

export function isMuted() {
  try {
    return window.localStorage.getItem(MUTE_KEY) === '1'
  } catch {
    return false
  }
}

export function setMuted(muted) {
  try {
    window.localStorage.setItem(MUTE_KEY, muted ? '1' : '0')
  } catch {
    // storage unavailable — ignore
  }
  window.dispatchEvent(new Event(MUTE_EVENT))
}

/**
 * Web Speech API helper for Chinese (zh-CN) text-to-speech.
 * Honors the global mute flag (nav-bar toggle, persisted).
 */
export function useSpeech() {
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  const [speaking, setSpeaking] = useState(false)
  const [muted, setMutedState] = useState(isMuted)

  useEffect(() => {
    const sync = () => {
      const m = isMuted()
      setMutedState(m)
      if (m && supported) window.speechSynthesis.cancel()
    }
    window.addEventListener(MUTE_EVENT, sync)
    return () => window.removeEventListener(MUTE_EVENT, sync)
  }, [supported])

  const speak = useCallback(
    (text, { rate = 0.85 } = {}) => {
      if (!supported || !text || isMuted()) return
      window.speechSynthesis.cancel()
      const utterance = new SpeechSynthesisUtterance(text)
      utterance.lang = 'zh-CN'
      utterance.rate = rate
      utterance.onend = () => setSpeaking(false)
      utterance.onerror = () => setSpeaking(false)
      setSpeaking(true)
      window.speechSynthesis.speak(utterance)
    },
    [supported]
  )

  const cancel = useCallback(() => {
    if (supported) window.speechSynthesis.cancel()
    setSpeaking(false)
  }, [supported])

  // Clean up any in-flight speech on unmount
  useEffect(() => () => {
    if (supported) window.speechSynthesis.cancel()
  }, [supported])

  return { speak, cancel, speaking, supported, muted }
}
