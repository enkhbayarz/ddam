import { useEffect, useState } from "react"

import {
  createPersona,
  deletePersona,
  listPersonas,
  type Persona,
  type PersonaInput,
} from "@/lib/api"

type Status = "loading" | "ready" | "error"

export function usePersonas() {
  const [personas, setPersonas] = useState<Persona[]>([])
  const [status, setStatus] = useState<Status>("loading")
  const [error, setError] = useState("")
  const [attempt, setAttempt] = useState(0)

  useEffect(() => {
    // Aborting stops a stale request from overwriting newer state, for example
    // the double run of effects in React StrictMode.
    const controller = new AbortController()

    listPersonas(controller.signal)
      .then((data) => {
        setPersonas(data)
        setStatus("ready")
      })
      .catch((cause: Error) => {
        if (controller.signal.aborted) return
        setError(cause.message)
        setStatus("error")
      })

    return () => controller.abort()
  }, [attempt])

  function retry() {
    setStatus("loading")
    setAttempt((current) => current + 1)
  }

  async function create(input: PersonaInput) {
    const persona = await createPersona(input)
    setPersonas((current) => [...current, persona])
    return persona
  }

  async function remove(id: string) {
    await deletePersona(id)
    setPersonas((current) => current.filter((persona) => persona.id !== id))
  }

  return { personas, status, error, retry, create, remove }
}
