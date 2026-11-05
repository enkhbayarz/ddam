import { useChat } from "@ai-sdk/react"
import { Streamdown } from "streamdown"

import { ChatInput } from "@/components/chat-input"
import { Bubble, BubbleContent } from "@/components/ui/bubble"
import { Button } from "@/components/ui/button"
import { Message, MessageContent } from "@/components/ui/message"
import {
  MessageScroller,
  MessageScrollerButton,
  MessageScrollerContent,
  MessageScrollerItem,
  MessageScrollerProvider,
  MessageScrollerViewport,
} from "@/components/ui/message-scroller"
import type { Persona } from "@/lib/api"
import { getChat, getChatErrorMessage, getMessageText } from "@/lib/chat"

type ChatPanelProps = {
  persona: Persona
  conversationId: string
  onMessageSent: (text: string) => void
}

export function ChatPanel({
  persona,
  conversationId,
  onMessageSent,
}: ChatPanelProps) {
  const { messages, sendMessage, regenerate, stop, status, error } = useChat({
    chat: getChat(conversationId, persona.id),
  })

  function handleSend(text: string) {
    sendMessage({ text })
    onMessageSent(text)
  }

  const busy = status === "submitted" || status === "streaming"
  const lastMessage = messages.at(-1)
  const replyStarted =
    lastMessage?.role === "assistant" && getMessageText(lastMessage) !== ""

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div className="min-h-0 flex-1">
        {messages.length === 0 ? (
          <div className="mx-auto flex h-full max-w-prose flex-col justify-center gap-2 p-6 text-center text-sm">
            <p className="font-medium">Say hello to {persona.name}</p>
            <p className="leading-relaxed text-muted-foreground">
              {persona.details}
            </p>
          </div>
        ) : (
          <MessageScrollerProvider autoScroll defaultScrollPosition="end">
            <MessageScroller>
              <MessageScrollerViewport>
                <MessageScrollerContent className="mx-auto w-full max-w-3xl gap-6 p-4">
                  {messages.map((message) => {
                    const text = getMessageText(message)
                    if (!text) return null

                    return (
                      <MessageScrollerItem
                        key={message.id}
                        messageId={message.id}
                        scrollAnchor={message.role === "user"}
                      >
                        {message.role === "user" ? (
                          <Message align="end">
                            <MessageContent>
                              <Bubble align="end" variant="muted">
                                <BubbleContent className="whitespace-pre-wrap">
                                  {text}
                                </BubbleContent>
                              </Bubble>
                            </MessageContent>
                          </Message>
                        ) : (
                          <Message>
                            <MessageContent>
                              <Streamdown
                                isAnimating={busy && message === lastMessage}
                              >
                                {text}
                              </Streamdown>
                            </MessageContent>
                          </Message>
                        )}
                      </MessageScrollerItem>
                    )
                  })}
                  {busy && !replyStarted && (
                    <p
                      role="status"
                      className="animate-pulse text-sm text-muted-foreground"
                    >
                      {persona.name} is thinking...
                    </p>
                  )}
                </MessageScrollerContent>
              </MessageScrollerViewport>
              <MessageScrollerButton />
            </MessageScroller>
          </MessageScrollerProvider>
        )}
      </div>

      <div className="mx-auto grid w-full max-w-3xl gap-2 p-4 pt-2">
        {error && (
          <div
            role="alert"
            className="flex items-center justify-between gap-3 rounded-lg bg-destructive/10 px-3 py-2 text-sm text-destructive"
          >
            {getChatErrorMessage(error)}
            <Button variant="outline" size="sm" onClick={() => regenerate()}>
              Try again
            </Button>
          </div>
        )}
        <ChatInput
          personaName={persona.name}
          busy={busy}
          onSend={handleSend}
          onStop={stop}
        />
      </div>
    </div>
  )
}
