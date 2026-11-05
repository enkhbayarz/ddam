import { cn } from "@/lib/utils"

export function PersonaAvatar({
  name,
  className,
}: {
  name: string
  className?: string
}) {
  const initials = name
    .split(/\s+/)
    .slice(0, 2)
    .map((word) => word[0])
    .join("")
    .toUpperCase()

  return (
    <span
      aria-hidden
      className={cn(
        "flex size-9 shrink-0 items-center justify-center rounded-full bg-muted text-xs font-medium text-muted-foreground",
        className
      )}
    >
      {initials}
    </span>
  )
}
