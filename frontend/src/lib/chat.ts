import { Chat } from "@ai-sdk/react"
import { DefaultChatTransport, type UIMessage } from "ai"

import { API_URL, getConversation } from "@/lib/api"

// One Chat per conversation, kept outside React, so that switching chats lets
// a reply finish streaming in the background.
const chats = new Map<string, Chat<UIMessage>>()

export function getChat(
  conversationId: string,
  personaId: string,
  messages?: UIMessage[]
) {
  let chat = chats.get(conversationId)
  if (!chat) {
    chat = new Chat({
      id: conversationId,
      messages,
      transport: new DefaultChatTransport({
        api: `${API_URL}/chat`,
        body: { persona_id: personaId },
      }),
    })
    chats.set(conversationId, chat)
  }
  return chat
}

export async function loadChat(conversationId: string, personaId: string) {
  if (chats.has(conversationId)) return
  const { messages } = await getConversation(conversationId)
  getChat(conversationId, personaId, messages)
}

export function removeChat(conversationId: string) {
  chats.get(conversationId)?.stop()
  chats.delete(conversationId)
}

export function getMessageText(message: UIMessage) {
  return message.parts
    .map((part) => (part.type === "text" ? part.text : ""))
    .join("")
}

export function getChatErrorMessage(error: Error) {
  if (error instanceof TypeError) {
    return "Cannot reach the server. Is the backend running?"
  }
  try {
    // HTTP errors arrive as the raw API response body.
    return JSON.parse(error.message).error.message as string
  } catch {
    return error.message
  }
}
