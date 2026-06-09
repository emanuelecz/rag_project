import type { Metadata } from 'next'
import './globals.css'

export const metadata: Metadata = {
  title: 'NTP Assistant',
  description: 'Asistente de normativa NTP española de prevención en construcción',
}

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="es">
      <body className="bg-bg font-sans text-tx">{children}</body>
    </html>
  )
}
