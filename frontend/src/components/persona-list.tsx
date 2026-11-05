import { PersonaAvatar } from "@/components/persona-avatar"
import { Button } from "@/components/ui/button"
import type { Persona } from "@/lib/api"
import { cn } from "@/lib/utils"

type PersonaListProps = {
  personas: Persona[]
  status: "loading" | "ready" | "error"
  error: string
  selectedId: string | null
  onSelect: (id: string) => void
  onRetry: () => void
}

export function PersonaList({
  personas,
  status,
  error,
  selectedId,
  onSelect,
  onRetry,
}: PersonaListProps) {
  if (status === "loading") {
    return <p className="p-2 text-sm text-muted-foreground">Loading...</p>
  }

  if (status === "error") {
    return (
      <div className="grid gap-2 p-2">
        <p role="alert" className="text-sm text-destructive">
          {error}
        </p>
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      </div>
    )
  }

  if (personas.length === 0) {
    return (
      <p className="p-2 text-sm text-muted-foreground">
        No personas yet. Create the first one.
      </p>
    )
  }

  return (
    <ul className="flex flex-col gap-1">
      {personas.map((persona) => (
        <li key={persona.id}>
          <button
            type="button"
            aria-current={persona.id === selectedId}
            onClick={() => onSelect(persona.id)}
            className={cn(
              "flex w-full items-center gap-3 rounded-lg p-2 text-left transition-colors hover:bg-accent focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-inset",
              persona.id === selectedId && "bg-accent"
            )}
          >
            <PersonaAvatar name={persona.name} />
            <span className="min-w-0">
              <span className="block truncate text-sm font-medium">
                {persona.name}
              </span>
              <span className="block truncate text-xs text-muted-foreground">
                {persona.lived_place}
              </span>
            </span>
          </button>
        </li>
      ))}
    </ul>
  )
}
