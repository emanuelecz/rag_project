import type { Lang } from '@/lib/types'
import type { Strings } from '@/lib/i18n'
import Icon from './Icon'

interface Props {
  lang: Lang
  setLang: (l: Lang) => void
  onNew: () => void
  str: Strings
}

export default function TopBar({ lang, setLang, onNew, str }: Props) {
  return (
    <div className="flex items-center gap-3 px-4 py-3.5 md:px-7 md:py-4 border-b border-border bg-bg z-10 relative shrink-0">
      {/* Logo + title */}
      <div className="flex items-center gap-2.5 flex-1 min-w-0">
        <div
          className="w-7 h-7 md:w-8 md:h-8 rounded-[7px] flex items-center justify-center text-bg shrink-0"
          style={{
            background: 'linear-gradient(135deg, #c89968 0%, #8b6f47 100%)',
            boxShadow: '0 1px 0 rgba(255,255,255,.08) inset, 0 2px 8px rgba(200,153,104,.15)',
          }}
        >
          <Icon name="book" size={15} stroke={2} />
        </div>
        <div className="min-w-0">
          <div className="font-serif text-[15px] md:text-base font-medium text-tx leading-tight tracking-[-0.01em] truncate">
            {str.title}
          </div>
          <div className="hidden md:block text-[11px] text-tx-faint font-mono tracking-[0.03em] mt-0.5 truncate">
            {str.subtitle}
          </div>
        </div>
      </div>

      {/* Lang toggle */}
      <div
        className="inline-flex rounded-md p-0.5 border border-border shrink-0"
        style={{ background: '#14181f' }}
      >
        {(['es', 'en'] as Lang[]).map((l) => (
          <button
            key={l}
            onClick={() => setLang(l)}
            className="px-2.5 py-1 rounded text-[11px] font-semibold font-mono tracking-[0.05em] uppercase transition-colors"
            style={{
              background: lang === l ? '#222a35' : 'transparent',
              color: lang === l ? '#e8e6e0' : '#9098a5',
              border: 'none',
              cursor: 'pointer',
            }}
          >
            {l}
          </button>
        ))}
      </div>

      {/* New chat */}
      <button
        onClick={onNew}
        title={str.newChat}
        className="flex items-center gap-1.5 px-2 py-1.5 md:px-3 rounded-md border border-border text-tx-dim text-xs font-medium transition-colors hover:bg-elev hover:text-tx shrink-0"
        style={{ background: 'transparent' }}
      >
        <Icon name="plus" size={14} />
        <span className="hidden md:inline">{str.newChat}</span>
      </button>
    </div>
  )
}
