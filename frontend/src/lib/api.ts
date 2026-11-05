import type { UIMessage } from "ai"

export const API_URL =
  import.meta.env.VITE_API_URL ?? "http://localhost:8000/api"

export type Persona = {
  id: string
  name: string
  birthdate: string
  lived_place: string
  details: string
  gender: "male" | "female" | "other"
}

export type PersonaInput = Omit<Persona, "id">

export type ConversationSummary = {
  id: string
  persona_id: string
  title: string
  updated_at: string
}

export type Conversation = ConversationSummary & { messages: UIMessage[] }

type FieldError = { field: string; message: string }

type ApiResponse<T> = {
  success: boolean
  data: T
  error: { code: string; message: string; details: FieldError[] | null } | null
}

export class ApiError extends Error {
  readonly fields: FieldError[]

  constructor(message: string, fields: FieldError[] = []) {
    super(message)
    this.fields = fields
  }
}

async function request<T>(path: string, init?: RequestInit): Promise<T> {
  let response: Response
  try {
    response = await fetch(`${API_URL}${path}`, init)
  } catch {
    throw new ApiError("Cannot reach the server. Is the backend running?")
  }

  if (response.status === 204) {
    return undefined as T
  }

  const body = (await response.json()) as ApiResponse<T>
  if (!body.success) {
    throw new ApiError(
      body.error?.message ?? "Something went wrong",
      body.error?.details ?? []
    )
  }
  return body.data
}

export function listPersonas(signal?: AbortSignal) {
  return request<Persona[]>("/personas", { signal })
}

export function createPersona(input: PersonaInput) {
  return request<Persona>("/personas", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  })
}

export function deletePersona(id: string) {
  return request<void>(`/personas/${id}`, { method: "DELETE" })
}

export function listConversations(personaId: string, signal?: AbortSignal) {
  return request<ConversationSummary[]>(
    `/personas/${personaId}/conversations`,
    { signal }
  )
}

export function getConversation(id: string) {
  return request<Conversation>(`/conversations/${id}`)
}

export function deleteConversation(id: string) {
  return request<void>(`/conversations/${id}`, { method: "DELETE" })
}
