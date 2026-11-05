import { useEffect, useState } from "react"

import {
  deleteConversation,
  listConversations,
  type ConversationSummary,
} from "@/lib/api"

const TITLE_LENGTH = 60

type LoadedList = {
  personaId: string
  items: ConversationSummary[]
  error: string
}

export function useConversations(personaId: string | undefined) {
  const [list, setList] = useState<LoadedList | null>(null)

  useEffect(() => {
    if (!personaId) return
    const controller = new AbortController()

    listConversations(personaId, controller.signal)
      .then((items) => setList({ personaId, items, error: "" }))
      .catch((cause: Error) => {
        if (controller.signal.aborted) return
        setList({ personaId, items: [], error: cause.message })
      })

    return () => controller.abort()
  }, [personaId])

  // A list loaded for the previous persona is ignored, not shown by mistake.
  const current = list?.personaId === personaId ? list : null

  function touch(id: string, text: string) {
    setList((previous) => {
      if (!previous) return previous
      const item = previous.items.find((entry) => entry.id === id) ?? {
        id,
        persona_id: previous.personaId,
        title: text.slice(0, TITLE_LENGTH),
        updated_at: new Date().toISOString(),
      }
      const others = previous.items.filter((entry) => entry.id !== id)
      return { ...previous, items: [item, ...others] }
    })
  }

  async function remove(id: string) {
    await deleteConversation(id)
    setList(
      (previous) =>
        previous && {
          ...previous,
          items: previous.items.filter((entry) => entry.id !== id),
        }
    )
  }

  return {
    conversations: current?.items ?? [],
    loading: !current,
    error: current?.error ?? "",
    touch,
    remove,
  }
}
