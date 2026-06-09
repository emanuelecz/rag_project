'use client'
import { useState, useRef, useEffect } from 'react'
import type { Message, Lang } from '@/lib/types'
import { parseSourceString } from '@/lib/types'
import { STR } from '@/lib/i18n'
import type { Suggestion } from '@/lib/i18n'
import TopBar from './TopBar'
import EmptyState from './EmptyState'
import UserMessage from './UserMessage'
import AssistantMessage from './AssistantMessage'
import Composer from './Composer'

export default function NTPChat() {
  const [lang, setLang] = useState<Lang>('es')
  const [messages, setMessages] = useState<Message[]>([])
  const [input, setInput] = useState('')
  const [busy, setBusy] = useState(false)
  const [dynamicSuggestions, setDynamicSuggestions] = useState<Record<Lang, Suggestion[]>>({ es: [], en: [] })
  const abortRef = useRef<AbortController | null>(null)
  const scrollRef = useRef<HTMLDivElement>(null)
  const str = STR[lang]

  useEffect(() => {
    fetch('/api/suggestions')
      .then((r) => r.json())
      .then((data) => {
        if (data.es?.length || data.en?.length) setDynamicSuggestions(data)
      })
      .catch(() => {})
  }, [])

  useEffect(() => {
    const el = scrollRef.current
    if (!el) return
    el.scrollTop = el.scrollHeight
  }, [messages])

  const ask = async (q: string) => {
    if (!q.trim() || busy) return
    abortRef.current?.abort()
    const ac = new AbortController()
    abortRef.current = ac

    setInput('')
    setBusy(true)

    setMessages((ms) => [
      ...ms,
      { role: 'user', text: q },
      { role: 'assistant', status: 'thinking', text: '', sources: [] },
    ])

    try {
      const res = await fetch('/api/ask', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({ question: q, candidates: 20, top_k: 8, lang }),
        signal: ac.signal,
      })

      if (!res.ok || !res.body) throw new Error(`HTTP ${res.status}`)

      const reader = res.body.getReader()
      const decoder = new TextDecoder()
      let buffer = ''

      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        buffer += decoder.decode(value, { stream: true })
        const lines = buffer.split('\n')
        buffer = lines.pop() ?? ''

        for (const line of lines) {
          if (!line.startsWith('data: ')) continue
          let payload: { type: string; content?: string; sources?: string[] }
          try { payload = JSON.parse(line.slice(6)) } catch { continue }

          if (payload.type === 'token') {
            setMessages((ms) => {
              const last = ms[ms.length - 1]
              if (!last || last.role !== 'assistant') return ms
              return [
                ...ms.slice(0, -1),
                { ...last, status: 'streaming' as const, text: last.text + (payload.content ?? '') },
              ]
            })
          } else if (payload.type === 'sources' && payload.sources) {
            const parsed = payload.sources.map(parseSourceString)
            setMessages((ms) => {
              const last = ms[ms.length - 1]
              if (!last || last.role !== 'assistant') return ms
              return [...ms.slice(0, -1), { ...last, sources: parsed }]
            })
          } else if (payload.type === 'done') {
            setMessages((ms) => {
              const last = ms[ms.length - 1]
              if (!last || last.role !== 'assistant') return ms
              return [...ms.slice(0, -1), { ...last, status: 'done' as const }]
            })
            setBusy(false)
          }
        }
      }
    } catch (err) {
      if ((err as Error).name === 'AbortError') return
      setMessages((ms) => {
        const last = ms[ms.length - 1]
        if (!last || last.role !== 'assistant') return ms
        return [
          ...ms.slice(0, -1),
          {
            ...last,
            status: 'done' as const,
            text: last.text || str.errorMsg,
          },
        ]
      })
      setBusy(false)
    }
  }

  const stop = () => {
    abortRef.current?.abort()
    setMessages((ms) => {
      const last = ms[ms.length - 1]
      if (!last || last.role !== 'assistant') return ms
      return [...ms.slice(0, -1), { ...last, status: 'done' as const }]
    })
    setBusy(false)
  }

  const reset = () => {
    abortRef.current?.abort()
    setMessages([])
    setBusy(false)
    setInput('')
  }

  return (
    <div className="w-full h-full flex flex-col bg-bg overflow-hidden">
      <TopBar lang={lang} setLang={setLang} onNew={reset} str={str} />

      <div
        ref={scrollRef}
        className="flex-1 overflow-y-auto overflow-x-hidden scroll-smooth"
      >
        {messages.length === 0 ? (
          <EmptyState lang={lang} str={str} onPick={ask} suggestions={dynamicSuggestions[lang]} />
        ) : (
          <div className="max-w-[760px] mx-auto px-4 pt-6 pb-6 md:px-7 md:pt-9">
            {messages.map((m, i) =>
              m.role === 'user' ? (
                <UserMessage key={i} text={m.text} />
              ) : (
                <AssistantMessage
                  key={i}
                  status={m.status}
                  text={m.text}
                  sources={m.sources}
                  str={str}
                  onRegen={() => {
                    const prev = messages[i - 1]
                    if (prev?.role === 'user') ask(prev.text)
                  }}
                />
              )
            )}
          </div>
        )}
      </div>

      <Composer
        value={input}
        setValue={setInput}
        onSend={() => ask(input)}
        onStop={stop}
        busy={busy}
        str={str}
      />
    </div>
  )
}
