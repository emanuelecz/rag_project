'use client'
import { useRef, useEffect } from 'react'
import type { Strings } from '@/lib/i18n'
import Icon from './Icon'

interface Props {
  value: string
  setValue: (v: string) => void
  onSend: () => void
  onStop: () => void
  busy: boolean
  str: Strings
}

export default function Composer({ value, setValue, onSend, onStop, busy, str }: Props) {
  const ref = useRef<HTMLTextAreaElement>(null)

  useEffect(() => {
    if (!ref.current) return
    ref.current.style.height = 'auto'
    ref.current.style.height = Math.min(140, ref.current.scrollHeight) + 'px'
  }, [value])

  return (
    <div
      className="px-4 pb-4 pt-3 md:px-7 md:pb-6 shrink-0"
      style={{ background: 'linear-gradient(180deg, transparent 0%, #0d1014 30%)' }}
    >
      <div className="max-w-[760px] mx-auto relative">
        <div
          className="rounded-xl md:rounded-2xl border px-3.5 pt-2.5 pb-2"
          style={{
            background: '#14181f',
            borderColor: '#2e3744',
            boxShadow: '0 8px 24px rgba(0,0,0,.18)',
          }}
        >
          <textarea
            ref={ref}
            value={value}
            onChange={(e) => setValue(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === 'Enter' && !e.shiftKey && !busy && value.trim()) {
                e.preventDefault()
                onSend()
              }
            }}
            placeholder={str.placeholder}
            rows={1}
            className="w-full resize-none bg-transparent border-none outline-none text-tx font-sans text-sm md:text-[14.5px] leading-relaxed placeholder:text-tx-faint overflow-y-auto"
            style={{ padding: '4px 0', maxHeight: 140, caretColor: '#c89968' }}
          />
          <div className="flex items-center mt-1">
            <button
              title="Adjuntar"
              className="p-1.5 text-tx-faint hover:text-tx-dim transition-colors rounded-md"
              style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
            >
              <Icon name="attach" size={15} />
            </button>
            <span className="flex-1 text-[11px] text-tx-faint font-mono ml-2 hidden md:inline">
              {!busy && 'Enter ↵  ·  Shift+Enter para nueva línea'}
            </span>
            {busy ? (
              <button
                onClick={onStop}
                title={str.stop}
                className="w-7 h-7 md:w-8 md:h-8 rounded-lg flex items-center justify-center text-tx transition-colors hover:bg-elev2"
                style={{ background: '#222a35', border: 'none', cursor: 'pointer' }}
              >
                <Icon name="stop" size={12} />
              </button>
            ) : (
              <button
                onClick={onSend}
                disabled={!value.trim()}
                title="Enviar"
                className="w-7 h-7 md:w-8 md:h-8 rounded-lg flex items-center justify-center text-bg transition-all hover:brightness-110 active:scale-95 disabled:opacity-35 disabled:cursor-not-allowed"
                style={{ background: '#c89968', border: 'none', cursor: value.trim() ? 'pointer' : 'not-allowed' }}
              >
                <Icon name="arrow-up" size={14} stroke={2.2} />
              </button>
            )}
          </div>
        </div>
        <p className="text-center text-[10.5px] text-tx-faint mt-2.5 leading-relaxed hidden md:block">
          {str.disclaimer}
        </p>
      </div>
    </div>
  )
}
