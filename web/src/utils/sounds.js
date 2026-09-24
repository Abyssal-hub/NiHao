// Success sound for correct answers — synthesized via Web Audio API.
// No external audio assets needed; works offline.
// Respects the global mute flag (same toggle as pronunciation).

import { isMuted } from '../hooks/useSpeech'

let ctx = null

function getCtx() {
  if (typeof window === 'undefined') return null
  const AC = window.AudioContext || window.webkitAudioContext
  if (!AC) return null
  if (!ctx) ctx = new AC()
  if (ctx.state === 'suspended') ctx.resume()
  return ctx
}

function tone(freq, startTime, duration, peak = 0.16, type = 'sine') {
  const audio = getCtx()
  if (!audio) return
  const osc = audio.createOscillator()
  const gain = audio.createGain()
  osc.type = type
  osc.frequency.value = freq
  gain.gain.setValueAtTime(0, startTime)
  gain.gain.linearRampToValueAtTime(peak, startTime + 0.012)
  gain.gain.exponentialRampToValueAtTime(0.0001, startTime + duration)
  osc.connect(gain)
  gain.connect(audio.destination)
  osc.start(startTime)
  osc.stop(startTime + duration + 0.05)
}

/**
 * Pleasant two-note chime (E5 → A5) with a soft harmonic layer.
 * ~0.5s total. Call on correct answers only.
 */
export function playSuccessSound() {
  if (isMuted()) return
  const audio = getCtx()
  if (!audio) return
  const t = audio.currentTime

  // Main bell tones
  tone(659.25, t, 0.4)          // E5
  tone(880.0, t + 0.09, 0.55)   // A5

  // Soft harmonic shimmer for warmth
  tone(1318.5, t + 0.09, 0.35, 0.05)  // E6
  tone(1760.0, t + 0.18, 0.4, 0.04)   // A6
}
