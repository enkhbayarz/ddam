import { useState, type FormEvent, type KeyboardEvent } from "react"
import { ArrowUpIcon, SquareIcon } from "lucide-react"

import {
  InputGroup,
  InputGroupAddon,
  InputGroupButton,
  InputGroupTextarea,
} from "@/components/ui/input-group"

type ChatInputProps = {
  personaName: string
  busy: boolean
  onSend: (text: string) => void
  onStop: () => void
}

// The draft lives here, not in the parent, so that typing re-renders only this
// small component and not the whole message list.
export function ChatInput({
  personaName,
  busy,
  onSend,
  onStop,
}: ChatInputProps) {
  const [draft, setDraft] = useState("")
  const text = draft.trim()

  function send() {
    if (!text || busy) return
    onSend(text)
    setDraft("")
  }

  function handleSubmit(event: FormEvent) {
    event.preventDefault()
    send()
  }

  function handleKeyDown(event: KeyboardEvent) {
    // isComposing: Enter is confirming IME text here, not sending the message.
    if (
      event.key === "Enter" &&
      !event.shiftKey &&
      !event.nativeEvent.isComposing
    ) {
      event.preventDefault()
      send()
    }
  }

  return (
    <form onSubmit={handleSubmit}>
      {/* The disabled Send button must not dim the whole input. */}
      <InputGroup className="has-disabled:bg-transparent has-disabled:opacity-100 dark:has-disabled:bg-input/30">
        <InputGroupTextarea
          autoFocus
          value={draft}
          maxLength={8000}
          onChange={(event) => setDraft(event.target.value)}
          onKeyDown={handleKeyDown}
          placeholder={`Message ${personaName}...`}
          aria-label="Message"
          className="max-h-40 min-h-12"
        />
        <InputGroupAddon align="block-end" className="justify-end pt-1">
          {busy ? (
            <InputGroupButton
              type="button"
              size="icon-sm"
              variant="default"
              aria-label="Stop reply"
              onClick={onStop}
            >
              <SquareIcon className="fill-current" />
            </InputGroupButton>
          ) : (
            <InputGroupButton
              type="submit"
              size="icon-sm"
              variant="default"
              aria-label="Send message"
              disabled={!text}
            >
              <ArrowUpIcon />
            </InputGroupButton>
          )}
        </InputGroupAddon>
      </InputGroup>
    </form>
  )
}
