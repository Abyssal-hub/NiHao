import { useState, useEffect, useCallback } from 'react'

/**
 * Web Speech API helper for Chinese (zh-CN) text-to-speech.
 */
export function useSpeech() {
  const supported = typeof window !== 'undefined' && 'speechSynthesis' in window
  const [speaking, setSpeaking] = useState(false)

  const speak = useCallback(
    (text, { rate = 0.85 } = {}) => {
      if (!supported || !text) return
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

  return { speak, cancel, speaking, supported }
}
