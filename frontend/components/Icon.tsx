interface Props { name: string; size?: number; stroke?: number }

export default function Icon({ name, size = 16, stroke = 1.6 }: Props) {
  const p = {
    width: size, height: size, viewBox: '0 0 24 24', fill: 'none',
    stroke: 'currentColor', strokeWidth: stroke,
    strokeLinecap: 'round' as const, strokeLinejoin: 'round' as const,
  }
  switch (name) {
    case 'book':        return <svg {...p}><path d="M4 4h11a3 3 0 0 1 3 3v14H7a3 3 0 0 1-3-3z"/><path d="M4 18a3 3 0 0 1 3-3h11"/></svg>
    case 'arrow-up':   return <svg {...p}><path d="M12 19V5M5 12l7-7 7 7"/></svg>
    case 'stop':       return <svg viewBox="0 0 24 24" width={size} height={size} fill="currentColor"><rect x="7" y="7" width="10" height="10" rx="1.5"/></svg>
    case 'attach':     return <svg {...p}><path d="M21 12l-8.5 8.5a5 5 0 0 1-7-7L14 5a3.5 3.5 0 0 1 5 5l-8.5 8.5a2 2 0 0 1-3-3L16 7"/></svg>
    case 'copy':       return <svg {...p}><rect x="9" y="9" width="11" height="11" rx="2"/><path d="M5 15V6a2 2 0 0 1 2-2h9"/></svg>
    case 'share':      return <svg {...p}><circle cx="18" cy="5" r="3"/><circle cx="6" cy="12" r="3"/><circle cx="18" cy="19" r="3"/><path d="M8.6 10.5l6.8-4M8.6 13.5l6.8 4"/></svg>
    case 'thumbsup':   return <svg {...p}><path d="M7 11v9H4v-9zM7 11l4-8a2 2 0 0 1 4 0v6h5.5a2 2 0 0 1 2 2.3l-1.4 6.5a2 2 0 0 1-2 1.7H7"/></svg>
    case 'thumbsdown': return <svg {...p}><path d="M17 13V4h3v9zM17 13l-4 8a2 2 0 0 1-4 0v-6H3.5a2 2 0 0 1-2-2.3L2.9 6.2A2 2 0 0 1 4.9 4.5H17"/></svg>
    case 'refresh':    return <svg {...p}><path d="M3 12a9 9 0 0 1 15.5-6.3L21 8M21 3v5h-5M21 12a9 9 0 0 1-15.5 6.3L3 16M3 21v-5h5"/></svg>
    case 'plus':       return <svg {...p}><path d="M12 5v14M5 12h14"/></svg>
    case 'chevron-down': return <svg {...p}><path d="M6 9l6 6 6-6"/></svg>
    case 'chevron-up':   return <svg {...p}><path d="M6 15l6-6 6 6"/></svg>
    case 'external':   return <svg {...p}><path d="M14 4h6v6M10 14L20 4M19 13v6a1 1 0 0 1-1 1H5a1 1 0 0 1-1-1V6a1 1 0 0 1 1-1h6"/></svg>
    case 'hardhat':    return <svg {...p}><path d="M3 17h18M5 17v-2a7 7 0 0 1 14 0v2"/><path d="M10 7V5h4v2"/></svg>
    case 'scaffold':   return <svg {...p}><path d="M4 4v16M20 4v16M4 9h16M4 15h16M9 4v16M15 4v16"/></svg>
    case 'excavation': return <svg {...p}><path d="M3 18h18M3 18l4-8h10l4 8M9 10V6M9 6h6M15 6v4"/></svg>
    case 'crane':      return <svg {...p}><path d="M5 21h6v-4H5zM3 17l5-5M8 12V4h12M20 4v6M14 4l-2 4"/></svg>
    default: return null
  }
}
