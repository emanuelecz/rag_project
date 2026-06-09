'use client'
import { useState } from 'react'
import type { ParsedSource } from '@/lib/types'
import Icon from './Icon'

interface Props {
  src: ParsedSource
}

export default function SourceCard({ src }: Props) {
  const [open, setOpen] = useState(false)

  return (
    <div
      className="rounded-lg border border-border overflow-hidden transition-colors hover:bg-elev2 hover:border-border-hi"
      style={{ background: '#14181f' }}
    >
      <button
        onClick={() => setOpen((o) => !o)}
        className="flex items-center gap-3 w-full px-4 py-3.5 text-left"
        style={{ background: 'transparent', border: 'none', cursor: 'pointer' }}
      >
        <span
          className="shrink-0 w-6 h-6 rounded-[5px] flex items-center justify-center font-mono text-xs font-semibold text-cite border"
          style={{ background: 'rgba(123,168,214,0.13)', borderColor: 'rgba(123,168,214,0.35)' }}
        >
          {src.n}
        </span>
        <span className="flex-1 min-w-0">
          <span className="block font-mono text-[11px] text-cite tracking-[0.04em] uppercase mb-0.5">
            {src.label}
          </span>
          <span className="block text-sm text-tx-dim">
            p. {src.page}
          </span>
        </span>
        <span className="text-tx-faint shrink-0">
          <Icon name={open ? 'chevron-up' : 'chevron-down'} size={15} />
        </span>
      </button>

      {open && (
        <div
          className="px-4 pb-4 pt-3 border-t border-border animate-fadeUp"
          style={{ paddingLeft: '3.25rem' }}
        >
          <div className="font-mono text-xs text-tx-faint">
            {src.filename}
          </div>
        </div>
      )}
    </div>
  )
}
