import type { Lang } from './types'

export interface Strings {
  title: string
  subtitle: string
  greeting: string
  sub: string
  placeholder: string
  sugg: string
  sources: string
  newChat: string
  thinking: string
  streamingLabel: string
  stop: string
  copy: string
  share: string
  regen: string
  helpful: string
  disclaimer: string
  errorMsg: string
}

export const STR: Record<Lang, Strings> = {
  es: {
    title: 'Asistente NTP',
    subtitle: 'Normativa española de prevención · Construcción',
    greeting: 'Buenos días',
    sub: '¿En qué normativa de prevención puedo ayudarte hoy?',
    placeholder: 'Pregunta sobre NTPs, RD, prevención…',
    sugg: 'Consultas frecuentes',
    sources: 'Fuentes',
    newChat: 'Nueva consulta',
    thinking: 'Buscando en normativa NTP',
    streamingLabel: 'Generando respuesta',
    stop: 'Detener',
    copy: 'Copiar',
    share: 'Compartir',
    regen: 'Regenerar',
    helpful: '¿Te ha sido útil?',
    disclaimer: 'Las respuestas se basan en NTPs del INSST y normativa vigente. Verifica siempre con el RD aplicable.',
    errorMsg: 'Error al conectar con el servidor. Asegúrate de que el backend está activo.',
  },
  en: {
    title: 'NTP Assistant',
    subtitle: 'Spanish workplace safety regulations · Construction',
    greeting: 'Good morning',
    sub: 'Which prevention regulation can I help with today?',
    placeholder: 'Ask about NTPs, RDs, prevention…',
    sugg: 'Suggested questions',
    sources: 'Sources',
    newChat: 'New chat',
    thinking: 'Searching NTP regulations',
    streamingLabel: 'Generating response',
    stop: 'Stop',
    copy: 'Copy',
    share: 'Share',
    regen: 'Regenerate',
    helpful: 'Was this helpful?',
    disclaimer: 'Answers draw on INSST NTPs and active regulations. Always verify against the applicable RD.',
    errorMsg: 'Could not connect to the server. Make sure the backend is running.',
  },
}

export interface Suggestion {
  icon: string
  q: string
  tag: string
}

export const SUGGESTIONS: Record<Lang, Suggestion[]> = {
  es: [
    { icon: 'hardhat',    q: '¿Qué EPI son obligatorios para trabajos en altura?',               tag: 'NTP 809 · EPI' },
    { icon: 'scaffold',   q: 'Requisitos de montaje de andamios tubulares según NTP 670',          tag: 'NTP 670 · Andamios' },
    { icon: 'excavation', q: 'Medidas preventivas en excavaciones y zanjas',                        tag: 'NTP 278 · Excavación' },
    { icon: 'crane',      q: '¿Cuándo se requiere coordinador de seguridad en obra?',              tag: 'RD 1627/1997' },
  ],
  en: [
    { icon: 'hardhat',    q: 'What PPE is mandatory for work at heights?',                         tag: 'NTP 809 · PPE' },
    { icon: 'scaffold',   q: 'Assembly requirements for tubular scaffolding (NTP 670)',             tag: 'NTP 670 · Scaffolding' },
    { icon: 'excavation', q: 'Preventive measures for excavations and trenches',                    tag: 'NTP 278 · Excavation' },
    { icon: 'crane',      q: 'When is a safety coordinator required on site?',                     tag: 'RD 1627/1997' },
  ],
}
