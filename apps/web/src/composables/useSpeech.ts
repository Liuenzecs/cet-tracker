/** TTS pronunciation for vocabulary terms.

 *  Priority: Web Speech API (offline, free, no external dependency).
 *  Fallback: configurable TTS audio URL for environments where the
 *  browser's built-in speech synthesis has no English voice (e.g.
 *  some Chinese Windows installations).

 *  Youdao dictvoice is documented as a common free fallback.
 *  Set VITE_TTS_FALLBACK_URL to override the default.
 */
const DEFAULT_TTS_FALLBACK = 'https://dict.youdao.com/dictvoice'

let currentAudio: HTMLAudioElement | null = null

function getTtsFallbackUrl(): string {
  // Allow overriding via env var at build time, but don't expose in prod.
  return (import.meta as any).env?.VITE_TTS_FALLBACK_URL || DEFAULT_TTS_FALLBACK
}

export function useSpeech() {
  function speak(text: string) {
    if (!text) return

    // 1) Try Web Speech API (offline, no external calls)
    if (typeof window !== 'undefined' && 'speechSynthesis' in window) {
      const voices = window.speechSynthesis.getVoices()
      const enVoice = voices.find((v) => v.lang.startsWith('en'))
      if (enVoice) {
        window.speechSynthesis.cancel()
        const u = new SpeechSynthesisUtterance(text)
        u.voice = enVoice
        u.lang = enVoice.lang
        u.rate = 0.85
        window.speechSynthesis.speak(u)
        return
      }
    }

    // 2) Fallback: configurable TTS audio URL
    if (currentAudio) {
      currentAudio.pause()
      currentAudio = null
    }
    const base = getTtsFallbackUrl()
    const audio = new Audio(`${base}?audio=${encodeURIComponent(text)}&type=0`)
    currentAudio = audio
    audio.play().catch(() => {
      // Try UK pronunciation if US fails
      const audio2 = new Audio(`${base}?audio=${encodeURIComponent(text)}&type=1`)
      currentAudio = audio2
      audio2.play().catch(() => {
        currentAudio = null
      })
    })
    audio.addEventListener('ended', () => {
      currentAudio = null
    })
  }

  return { speak }
}
