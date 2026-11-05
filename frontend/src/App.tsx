import { useState } from "react"

import { ChatPanel } from "@/components/chat-panel"
import { ConversationList } from "@/components/conversation-list"
import { CreatePersonaDialog } from "@/components/create-persona-dialog"
import { PersonaHeader } from "@/components/persona-header"
import { PersonaList } from "@/components/persona-list"
import { useConversations } from "@/hooks/use-conversations"
import { usePersonas } from "@/hooks/use-personas"
import type { PersonaInput } from "@/lib/api"
import { loadChat, removeChat } from "@/lib/chat"

export function App() {
  const { personas, status, error, retry, create, remove } = usePersonas()
  const [selectedId, setSelectedId] = useState<string | null>(null)
  // A new id means a new chat: no messages, so no context from earlier chats.
  const [conversationId, setConversationId] = useState<string>(() =>
    crypto.randomUUID()
  )
  const [openError, setOpenError] = useState("")

  const selected = personas.find((persona) => persona.id === selectedId)
  const history = useConversations(selected?.id)

  function startNewChat() {
    setConversationId(crypto.randomUUID())
    setOpenError("")
  }

  function selectPersona(id: string) {
    if (id === selectedId) return
    setSelectedId(id)
    startNewChat()
  }

  async function handleCreate(input: PersonaInput) {
    const persona = await create(input)
    selectPersona(persona.id)
  }

  async function handleDeletePersona(id: string) {
    await remove(id)
    history.conversations.forEach((conversation) => removeChat(conversation.id))
    removeChat(conversationId)
  }

  async function openConversation(id: string, personaId: string) {
    try {
      await loadChat(id, personaId)
      setConversationId(id)
      setOpenError("")
    } catch (cause) {
      setOpenError((cause as Error).message)
    }
  }

  async function handleDeleteConversation(id: string) {
    await history.remove(id)
    removeChat(id)
    if (id === conversationId) startNewChat()
  }

  return (
    <div className="flex h-svh flex-col md:flex-row">
      <aside className="flex max-h-[40svh] shrink-0 flex-col gap-3 border-b p-3 md:max-h-none md:w-72 md:border-r md:border-b-0">
        <h1 className="px-2 pt-1 font-medium">Persona Chat</h1>
        <CreatePersonaDialog onCreate={handleCreate} />
        <nav aria-label="Personas" className="min-h-0 flex-1 overflow-y-auto">
          <PersonaList
            personas={personas}
            status={status}
            error={error}
            selectedId={selectedId}
            onSelect={selectPersona}
            onRetry={retry}
          />
          {selected && (
            <ConversationList
              personaName={selected.name}
              conversations={history.conversations}
              loading={history.loading}
              error={history.error || openError}
              activeId={conversationId}
              onOpen={(id) => openConversation(id, selected.id)}
              onDelete={handleDeleteConversation}
            />
          )}
        </nav>
      </aside>

      <main className="flex min-h-0 min-w-0 flex-1 flex-col">
        {selected ? (
          <>
            <PersonaHeader
              persona={selected}
              onNewChat={startNewChat}
              onDelete={() => handleDeletePersona(selected.id)}
            />
            <ChatPanel
              key={conversationId}
              persona={selected}
              conversationId={conversationId}
              onMessageSent={(text) => history.touch(conversationId, text)}
            />
          </>
        ) : (
          <div className="flex flex-1 items-center justify-center p-6 text-center text-sm text-muted-foreground">
            Choose a persona to start chatting.
          </div>
        )}
      </main>
    </div>
  )
}

export default App
