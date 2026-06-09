'use client'
import { useState, Fragment } from 'react'
import type { ParsedSource } from '@/lib/types'
import type { Strings } from '@/lib/i18n'
import RoseTrailLoader from './RoseTrailLoader'
import SourceCard from './SourceCard'
import Icon from './Icon'

function CiteChip({ n, src }: { n: number; src?: ParsedSource }) {
  const [hover, setHover] = useState(false)
  return (
    <span className="relative inline-block">
      <button
        onMouseEnter={() => setHover(true)}
        onMouseLeave={() => setHover(false)}
        className="inline-flex items-center justify-center min-w-[18px] h-[18px] px-[5px] rounded font-mono text-[11px] font-semibold transition-colors hover:bg-cite hover:text-bg"
        style={{
          background: 'rgba(123,168,214,0.13)',
          color: '#7ba8d6',
          border: '1px solid rgba(123,168,214,0.35)',
          lineHeight: 1,
          verticalAlign: 'baseline',
          position: 'relative',
          top: -2,
          cursor: 'pointer',
        }}
      >
        {n}
      </button>
      {hover && src && (
        <span
          className="absolute z-30 pointer-events-none text-left animate-fadeUp"
          style={{
            bottom: 'calc(100% + 6px)',
            left: '50%',
            transform: 'translateX(-50%)',
            width: 260,
            padding: '10px 12px',
            background: '#222a35',
            border: '1px solid #2e3744',
            borderRadius: 8,
            boxShadow: '0 8px 24px rgba(0,0,0,.4)',
            fontSize: 12,
            lineHeight: 1.5,
            color: '#9098a5',
          }}
        >
          <div className="font-mono text-[10px] text-cite mb-1 tracking-wide">
            {src.label} · p. {src.page}
          </div>
          <div className="text-tx font-medium text-[12px]">{src.filename}</div>
        </span>
      )}
    </span>
  )
}

function BlinkingCaret() {
  return (
    <span
      className="inline-block w-[7px] h-[14px] ml-0.5 align-bottom animate-blink"
      style={{ background: '#c89968' }}
    />
  )
}

function DotPulse() {
  return (
    <span className="inline-block w-[18px]">
      <span className="animate-dotp1 opacity-30">.</span>
      <span className="animate-dotp2 opacity-30">.</span>
      <span className="animate-dotp3 opacity-30">.</span>
    </span>
  )
}

function renderInline(text: string, sources: ParsedSource[]): React.ReactNode[] {
  const re = /(\*\*[^*]+\*\*|\[\^?(\d+)\])/g
  const parts: React.ReactNode[] = []
  let last = 0, k = 0
  let m: RegExpExecArray | null
  while ((m = re.exec(text)) !== null) {
    if (m.index > last) parts.push(<Fragment key={k++}>{text.slice(last, m.index)}</Fragment>)
    if (m[0].startsWith('**')) {
      parts.push(<strong key={k++}>{m[0].slice(2, -2)}</strong>)
    } else {
      const n = parseInt(m[2])
      parts.push(<CiteChip key={k++} n={n} src={sources.find((s) => s.n === n)} />)
    }
    last = re.lastIndex
  }
  if (last < text.length) parts.push(<Fragment key={k++}>{text.slice(last)}</Fragment>)
  return parts
}

function MarkdownRenderer({ text, sources, isStreaming }: {
  text: string
  sources: ParsedSource[]
  isStreaming: boolean
}) {
  const blocks = text.split(/\n(?=\n)|\n(?=## )/).map((b) => b.trim()).filter(Boolean)
  return (
    <div className="ntp-md">
      {blocks.map((b, i) => {
        if (b.startsWith('## ')) {
          return <h2 key={i}>{renderInline(b.slice(3).trim(), sources)}</h2>
        }
        if (/^\d+\.\s/.test(b)) {
          const items = b.split(/\n(?=\d+\.\s)/)
          return (
            <ol key={i}>
              {items.map((it, j) => (
                <li key={j}>{renderInline(it.replace(/^\d+\.\s*/, ''), sources)}</li>
              ))}
            </ol>
          )
        }
        return (
          <p key={i}>
            {b.split('\n').map((line, j, arr) => (
              <Fragment key={j}>
                {renderInline(line, sources)}
                {j < arr.length - 1 && <br />}
              </Fragment>
            ))}
          </p>
        )
      })}
      {isStreaming && <BlinkingCaret />}
    </div>
  )
}

function ActionBtn({ icon, label, onClick, iconOnly }: {
  icon: string; label?: string; onClick?: () => void; iconOnly?: boolean
}) {
  return (
    <button
      onClick={onClick}
      title={label}
      className="inline-flex items-center gap-1.5 rounded-[5px] text-xs font-medium text-tx-dim transition-colors hover:bg-elev hover:text-tx"
      style={{
        padding: iconOnly ? 6 : '5px 9px',
        background: 'transparent',
        border: 'none',
        cursor: 'pointer',
      }}
    >
      <Icon name={icon} size={13} />
      {!iconOnly && label && <span>{label}</span>}
    </button>
  )
}

interface Props {
  status: 'thinking' | 'streaming' | 'done'
  text: string
  sources: ParsedSource[]
  str: Strings
  onCopy?: () => void
  onRegen?: () => void
}

export default function AssistantMessage({ status, text, sources, str, onCopy, onRegen }: Props) {
  const [sourcesOpen, setSourcesOpen] = useState(status === 'done')
  const [copied, setCopied] = useState(false)

  const handleCopy = () => {
    navigator.clipboard.writeText(text).catch(() => {})
    setCopied(true)
    setTimeout(() => setCopied(false), 1500)
    onCopy?.()
  }

  if (status === 'thinking') {
    return (
      <div className="flex items-center gap-2.5 py-3 mb-2 animate-fadeUp">
        <span className="text-accent inline-flex">
          <RoseTrailLoader size={20} color="#c89968" />
        </span>
        <span className="font-mono text-[12px] text-tx-dim tracking-[0.03em]">
          {str.thinking}<DotPulse />
        </span>
      </div>
    )
  }

  return (
    <div className="mb-2 animate-fadeUp">
      {status === 'streaming' && (
        <div className="flex items-center gap-2.5 mb-3">
          <span className="text-accent inline-flex">
            <RoseTrailLoader size={18} color="#c89968" />
          </span>
          <span className="font-mono text-[11px] text-tx-dim tracking-[0.03em]">
            {str.streamingLabel}<DotPulse />
          </span>
        </div>
      )}

      <MarkdownRenderer text={text} sources={sources} isStreaming={status === 'streaming'} />

      {status === 'done' && (
        <>
          <div className="flex items-center gap-1 mt-4 pt-3.5 border-t border-border flex-wrap">
            <ActionBtn icon="copy"      label={copied ? '✓' : str.copy}  onClick={handleCopy} />
            <ActionBtn icon="share"     label={str.share} />
            <ActionBtn icon="refresh"   label={str.regen}                 onClick={onRegen} />
            <div className="flex-1" />
            <span className="text-[11px] text-tx-faint mr-1 hidden sm:inline">{str.helpful}</span>
            <ActionBtn icon="thumbsup"   iconOnly />
            <ActionBtn icon="thumbsdown" iconOnly />
          </div>

          {sources.length > 0 && (
            <div className="mt-4">
              <button
                onClick={() => setSourcesOpen((o) => !o)}
                className="flex items-center gap-2 font-mono text-[11px] text-tx-dim tracking-[0.05em] uppercase py-1.5 transition-colors hover:text-tx"
                style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
              >
                <Icon name={sourcesOpen ? 'chevron-up' : 'chevron-down'} size={13} />
                {str.sources} · {sources.length}
              </button>
              {sourcesOpen && (
                <div className="mt-2.5 flex flex-col gap-2 animate-fadeUp">
                  {sources.map((src) => (
                    <SourceCard key={src.n} src={src} />
                  ))}
                </div>
              )}
            </div>
          )}
        </>
      )}
    </div>
  )
}
