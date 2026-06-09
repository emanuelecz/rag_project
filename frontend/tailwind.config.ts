import type { Config } from 'tailwindcss'

const config: Config = {
  content: ['./app/**/*.{ts,tsx}', './components/**/*.{ts,tsx}'],
  theme: {
    extend: {
      colors: {
        bg:      '#0d1014',
        panel:   '#14181f',
        elev:    '#1c222b',
        elev2:   '#222a35',
        border:  { DEFAULT: '#232a35', hi: '#2e3744' },
        tx:      { DEFAULT: '#e8e6e0', dim: '#9098a5', faint: '#5f6772' },
        accent:  '#c89968',
        cite:    '#7ba8d6',
      },
      fontFamily: {
        sans:  ['"IBM Plex Sans"', 'system-ui', 'sans-serif'],
        serif: ['"Newsreader"', 'Georgia', 'serif'],
        mono:  ['"IBM Plex Mono"', 'ui-monospace', 'monospace'],
      },
      keyframes: {
        blink:   { '50%': { opacity: '0' } },
        dotp:    { '0%,80%,100%': { opacity: '0.3' }, '40%': { opacity: '1' } },
        shimmer: { '0%': { backgroundPosition: '200% 0' }, '100%': { backgroundPosition: '-200% 0' } },
        fadeUp:  { from: { opacity: '0', transform: 'translateY(4px)' }, to: { opacity: '1', transform: 'none' } },
      },
      animation: {
        blink:   'blink 1s steps(2) infinite',
        dotp1:   'dotp 1.2s infinite',
        dotp2:   'dotp 1.2s 0.2s infinite',
        dotp3:   'dotp 1.2s 0.4s infinite',
        shimmer: 'shimmer 1.6s linear infinite',
        fadeUp:  'fadeUp 0.35s ease-out',
      },
    },
  },
  plugins: [],
}
export default config
