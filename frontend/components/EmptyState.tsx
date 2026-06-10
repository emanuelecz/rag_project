import type { Lang } from '@/lib/types'
import type { Strings, Suggestion } from '@/lib/i18n'
import { SUGGESTIONS } from '@/lib/i18n'
import Icon from './Icon'

interface Props {
  lang: Lang
  str: Strings
  onPick: (q: string) => void
  suggestions?: Suggestion[]
}

export default function EmptyState({ lang, str, onPick, suggestions: dynamicSuggestions }: Props) {
  const suggestions = dynamicSuggestions && dynamicSuggestions.length > 0
    ? dynamicSuggestions
    : SUGGESTIONS[lang]

  return (
    <div className="flex flex-col items-center justify-center min-h-full px-4 py-10 md:px-8 md:py-12 w-full max-w-2xl mx-auto">
      <div
        className="w-12 h-12 md:w-14 md:h-14 rounded-xl flex items-center justify-center text-accent mb-4 md:mb-5 border border-border-hi"
        style={{
          background: 'radial-gradient(circle at 30% 30%, rgba(200,153,104,.3), #1c222b 70%)',
          boxShadow: '0 1px 0 rgba(255,255,255,.04) inset',
        }}
      >
        <svg width="24" height="24" viewBox="0 0 24 24" fill="none"
          stroke="currentColor" strokeWidth="1.4" strokeLinecap="round" strokeLinejoin="round">
          <path d="M4 4h11a3 3 0 0 1 3 3v14H7a3 3 0 0 1-3-3z"/>
          <path d="M4 18a3 3 0 0 1 3-3h11"/>
          <path d="M8 9h6M8 12h6"/>
        </svg>
      </div>

      <h1 className="font-serif font-normal text-3xl md:text-4xl text-tx tracking-[-0.02em]">
        {str.greeting}<span className="text-accent">.</span>
      </h1>
      <p className="text-sm md:text-[15px] text-tx-dim mt-2 mb-7 md:mb-8 text-center max-w-sm">
        {str.sub}
      </p>

      <div className="w-full flex items-center gap-3 mb-3">
        <div className="flex-1 h-px bg-border" />
        <span className="text-[10px] text-tx-faint font-mono tracking-[0.12em] uppercase">{str.sugg}</span>
        <div className="flex-1 h-px bg-border" />
      </div>

      <div className="w-full grid grid-cols-1 sm:grid-cols-2 gap-2.5">
        {suggestions.map((s, i) => (
          <button
            key={i}
            onClick={() => onPick(s.q)}
            className="flex items-start gap-3 p-3.5 text-left rounded-xl border border-border bg-panel transition-all hover:bg-elev hover:border-border-hi hover:-translate-y-px"
          >
            <span
              className="shrink-0 w-8 h-8 rounded-lg flex items-center justify-center mt-0.5 text-accent"
              style={{ background: 'rgba(200,153,104,0.14)' }}
            >
              <Icon name={s.icon} size={16} stroke={1.5} />
            </span>
            <span className="flex-1 min-w-0">
              <span className="block text-[13.5px] leading-snug text-tx font-[450]">{s.q}</span>
              <span className="block font-mono text-[10px] text-tx-faint mt-1 tracking-[0.04em] uppercase">{s.tag}</span>
            </span>
          </button>
        ))}
      </div>
    </div>
  )
}
