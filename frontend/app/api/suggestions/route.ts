import { NextResponse } from 'next/server'

export const runtime = 'nodejs'
export const dynamic = 'force-dynamic'

export async function GET() {
  const backendUrl = process.env.BACKEND_URL || 'http://localhost:8000'

  try {
    const upstream = await fetch(`${backendUrl}/suggestions`)
    if (!upstream.ok) return NextResponse.json({ es: [], en: [] })
    const data = await upstream.json()
    return NextResponse.json(data)
  } catch {
    return NextResponse.json({ es: [], en: [] })
  }
}
