export interface ParsedSource {
  n: number
  filename: string
  page: string
  label: string
}

export type MessageStatus = 'thinking' | 'streaming' | 'done'

export interface UserMsg {
  role: 'user'
  text: string
}

export interface AssistantMsg {
  role: 'assistant'
  status: MessageStatus
  text: string
  sources: ParsedSource[]
}

export type Message = UserMsg | AssistantMsg

export type Lang = 'es' | 'en'

export function parseSourceString(s: string): ParsedSource {
  const m = s.match(/^\[(\d+)\]\s+(.+?)\s+[—\-]+\s+page\s+(.+)$/)
  if (m) {
    const filename = m[2]
    return {
      n: parseInt(m[1]),
      filename,
      page: m[3],
      label: filename.replace(/\.[^.]+$/, '').replace(/_/g, ' '),
    }
  }
  return { n: 0, filename: s, page: '?', label: s }
}
