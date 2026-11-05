import { SquarePenIcon } from "lucide-react"

import { ConfirmDeleteDialog } from "@/components/confirm-delete-dialog"
import { PersonaAvatar } from "@/components/persona-avatar"
import { Button } from "@/components/ui/button"
import type { Persona } from "@/lib/api"

export function PersonaHeader({
  persona,
  onNewChat,
  onDelete,
}: {
  persona: Persona
  onNewChat: () => void
  onDelete: () => Promise<void>
}) {
  return (
    <header className="flex items-center gap-3 border-b p-4">
      <PersonaAvatar name={persona.name} className="size-10" />
      <div className="min-w-0 flex-1">
        <h2 className="truncate font-medium">{persona.name}</h2>
        <p className="truncate text-xs text-muted-foreground">
          Born {persona.birthdate} · {persona.lived_place}
        </p>
      </div>
      <Button variant="outline" size="sm" onClick={onNewChat}>
        <SquarePenIcon />
        New chat
      </Button>
      <ConfirmDeleteDialog
        label={`Delete ${persona.name}`}
        title={`Delete ${persona.name}?`}
        description="This removes the persona and all of its chats permanently."
        onConfirm={onDelete}
      />
    </header>
  )
}
