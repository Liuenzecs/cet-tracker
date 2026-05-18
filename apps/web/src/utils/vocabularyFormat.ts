/** Frontend formatting utilities for vocabulary display.

 * Ensures no raw markdown (**, |---|, ###, etc.) leaks into the UI.
 * Always returns clean, displayable strings.
 */

/** Format any value into a displayable string. Handles objects, arrays, nulls. */
export function formatText(value: unknown): string {
  if (value === null || value === undefined) return ''
  if (typeof value === 'string') return value
  if (typeof value === 'number' || typeof value === 'boolean') return String(value)
  if (Array.isArray(value)) return value.map(formatText).filter(Boolean).join('; ')
  if (typeof value === 'object') {
    // For {en, zh} objects, render as "en — zh"
    const obj = value as Record<string, unknown>
    const en = obj.en ? String(obj.en) : ''
    const zh = obj.zh ? String(obj.zh) : ''
    if (en) return zh ? `${en} — ${zh}` : en
    // For comparison-like objects
    const left = obj.left || obj.word1 || obj.term_a || ''
    const right = obj.right || obj.word2 || obj.term_b || ''
    if (left && right) return `${left} vs ${right}`
    if (left) return String(left)
    // General fallback for objects
    return Object.values(obj).filter(v => v !== null && v !== undefined && v !== '').join('; ')
  }
  return ''
}

/** Format a list of items, each cleaned through formatText. */
export function formatTextList(list: unknown[]): string[] {
  if (!Array.isArray(list)) return []
  return list.map(formatText).filter(s => s.length > 0)
}

/** Format an example object {en, zh} into a display pair. */
export function formatExample(example: unknown): { en: string; zh: string } {
  if (!example || typeof example !== 'object') return { en: '', zh: '' }
  const ex = example as Record<string, unknown>
  return {
    en: typeof ex.en === 'string' ? ex.en : '',
    zh: typeof ex.zh === 'string' ? ex.zh : '',
  }
}

/** Format a comparison object into displayable fields. */
export function formatComparison(comp: unknown): {
  left: string
  right: string
  leftMeaning: string
  rightMeaning: string
} {
  if (!comp || typeof comp !== 'object') {
    return { left: '', right: '', leftMeaning: '', rightMeaning: '' }
  }
  const c = comp as Record<string, unknown>
  const left =
    (typeof c.left === 'string' && c.left) ||
    (typeof c.word1 === 'string' && c.word1) ||
    (typeof c.term_a === 'string' && c.term_a) ||
    ''
  const right =
    (typeof c.right === 'string' && c.right) ||
    (typeof c.word2 === 'string' && c.word2) ||
    (typeof c.term_b === 'string' && c.term_b) ||
    ''
  const leftMeaning =
    (typeof c.left_meaning === 'string' && c.left_meaning) ||
    (typeof c.meaning1 === 'string' && c.meaning1) ||
    (typeof c.description === 'string' && c.description) ||
    (typeof c.note === 'string' && c.note) ||
    ''
  const rightMeaning =
    (typeof c.right_meaning === 'string' && c.right_meaning) ||
    (typeof c.meaning2 === 'string' && c.meaning2) ||
    ''

  return { left, right, leftMeaning, rightMeaning }
}

/** Check if a string looks like raw markdown noise. */
export function looksLikeMarkdownNoise(text: string): boolean {
  if (!text) return false
  if (/^\|\s*[-:]+\s*\|/.test(text)) return true   // |---|---|
  if (/^\|[\s|\-:]*$/.test(text)) return true      // pipes and dashes
  if (/^\*{2,3}\s*$/.test(text)) return true       // ***
  if (/^[-_]{3,}$/.test(text)) return true          // --- or ___
  if (/^#{1,6}\s*$/.test(text)) return true         // just heading markers
  if (text.trim() === '|') return true
  return false
}
