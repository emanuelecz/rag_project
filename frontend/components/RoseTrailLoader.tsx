'use client'
import { useEffect, useRef } from 'react'

interface Props {
  size?: number
  color?: string
  particleCount?: number
  trailSpan?: number
  durationMs?: number
  rotationDurationMs?: number
  pulseDurationMs?: number
  strokeWidth?: number
  baseRadius?: number
  detailAmplitude?: number
  petalCount?: number
  curveScale?: number
}

export default function RoseTrailLoader({
  size = 22,
  color = 'currentColor',
  particleCount = 48,
  trailSpan = 0.4,
  durationMs = 4600,
  rotationDurationMs = 24000,
  pulseDurationMs = 4200,
  strokeWidth = 5.5,
  baseRadius = 7,
  detailAmplitude = 3,
  petalCount = 7,
  curveScale = 3.9,
}: Props) {
  const groupRef = useRef<SVGGElement>(null)
  const pathRef = useRef<SVGPathElement>(null)
  const rafRef = useRef<number>(0)
  const startedAtRef = useRef<number>(0)

  useEffect(() => {
    const group = groupRef.current
    const path = pathRef.current
    if (!group || !path) return

    const SVG_NS = 'http://www.w3.org/2000/svg'
    const particles: SVGCircleElement[] = []
    for (let i = 0; i < particleCount; i++) {
      const c = document.createElementNS(SVG_NS, 'circle')
      c.setAttribute('fill', 'currentColor')
      group.appendChild(c)
      particles.push(c)
    }
    path.setAttribute('stroke-width', String(strokeWidth))

    const point = (progress: number, ds: number) => {
      const t = progress * Math.PI * 2
      return {
        x: 50 + (baseRadius * Math.cos(t) - detailAmplitude * ds * Math.cos(petalCount * t)) * curveScale,
        y: 50 + (baseRadius * Math.sin(t) - detailAmplitude * ds * Math.sin(petalCount * t)) * curveScale,
      }
    }
    const dsAt = (time: number) => {
      const p = (time % pulseDurationMs) / pulseDurationMs
      return 0.52 + ((Math.sin(p * Math.PI * 2 + 0.55) + 1) / 2) * 0.48
    }
    const rotAt = (time: number) => -((time % rotationDurationMs) / rotationDurationMs) * 360
    const buildPath = (ds: number) => {
      let d = ''
      for (let i = 0; i <= 240; i++) {
        const p = point(i / 240, ds)
        d += `${i === 0 ? 'M' : 'L'}${p.x.toFixed(2)} ${p.y.toFixed(2)} `
      }
      return d
    }
    const norm = (x: number) => ((x % 1) + 1) % 1

    startedAtRef.current = performance.now()

    const render = (now: number) => {
      const time = now - startedAtRef.current
      const progress = (time % durationMs) / durationMs
      const ds = dsAt(time)
      group.setAttribute('transform', `rotate(${rotAt(time)} 50 50)`)
      path.setAttribute('d', buildPath(ds))
      path.setAttribute('opacity', '0.1')
      for (let i = 0; i < particleCount; i++) {
        const tailOffset = i / (particleCount - 1)
        const p = point(norm(progress - tailOffset * trailSpan), ds)
        const fade = Math.pow(1 - tailOffset, 0.56)
        particles[i].setAttribute('cx', p.x.toFixed(2))
        particles[i].setAttribute('cy', p.y.toFixed(2))
        particles[i].setAttribute('r', (0.9 + fade * 2.7).toFixed(2))
        particles[i].setAttribute('opacity', (0.04 + fade * 0.96).toFixed(3))
      }
      rafRef.current = requestAnimationFrame(render)
    }
    rafRef.current = requestAnimationFrame(render)

    return () => {
      cancelAnimationFrame(rafRef.current)
      particles.forEach((p) => p.remove())
    }
  }, [particleCount, trailSpan, durationMs, rotationDurationMs, pulseDurationMs,
      strokeWidth, baseRadius, detailAmplitude, petalCount, curveScale])

  return (
    <svg
      width={size}
      height={size}
      viewBox="0 0 100 100"
      fill="none"
      aria-hidden="true"
      style={{ overflow: 'visible', color, display: 'inline-block', verticalAlign: 'middle' }}
    >
      <g ref={groupRef}>
        <path
          ref={pathRef}
          stroke="currentColor"
          strokeLinecap="round"
          strokeLinejoin="round"
          opacity="0.1"
        />
      </g>
    </svg>
  )
}
