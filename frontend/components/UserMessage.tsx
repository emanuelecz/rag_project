interface Props { text: string }

export default function UserMessage({ text }: Props) {
  return (
    <div className="flex justify-end mb-6 animate-fadeUp">
      <div
        className="max-w-[78%] px-4 py-2.5 text-sm md:text-[14.5px] leading-relaxed text-tx border border-border rounded-[14px_14px_4px_14px]"
        style={{ background: '#1c222b' }}
      >
        {text}
      </div>
    </div>
  )
}
