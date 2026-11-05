import { ConfirmDeleteDialog } from "@/components/confirm-delete-dialog"
import type { ConversationSummary } from "@/lib/api"
import { cn } from "@/lib/utils"

type ConversationListProps = {
  personaName: string
  conversations: ConversationSummary[]
  loading: boolean
  error: string
  activeId: string
  onOpen: (id: string) => void
  onDelete: (id: string) => Promise<void>
}

export function ConversationList({
  personaName,
  conversations,
  loading,
  error,
  activeId,
  onOpen,
  onDelete,
}: ConversationListProps) {
  return (
    <section aria-label="Chat history" className="mt-4 flex flex-col gap-1">
      <h2 className="truncate px-2 text-xs font-medium text-muted-foreground">
        Chats with {personaName}
      </h2>

      {error && (
        <p role="alert" className="px-2 text-sm text-destructive">
          {error}
        </p>
      )}

      {!loading && !error && conversations.length === 0 && (
        <p className="px-2 text-sm text-muted-foreground">No chats yet.</p>
      )}

      <ul className="flex flex-col gap-0.5">
        {conversations.map((conversation) => (
          <li
            key={conversation.id}
            className={cn(
              "group flex items-center rounded-lg transition-colors hover:bg-accent",
              conversation.id === activeId && "bg-accent"
            )}
          >
            <button
              type="button"
              aria-current={conversation.id === activeId}
              onClick={() => onOpen(conversation.id)}
              className="min-w-0 flex-1 truncate rounded-lg px-2 py-1.5 text-left text-sm focus-visible:ring-2 focus-visible:ring-ring focus-visible:outline-none focus-visible:ring-inset"
            >
              {conversation.title}
            </button>
            <ConfirmDeleteDialog
              label={`Delete chat: ${conversation.title}`}
              title="Delete this chat?"
              description={`"${conversation.title}" will be removed permanently.`}
              triggerClassName="size-7 shrink-0 focus-visible:opacity-100 md:opacity-0 md:group-hover:opacity-100"
              onConfirm={() => onDelete(conversation.id)}
            />
          </li>
        ))}
      </ul>
    </section>
  )
}
