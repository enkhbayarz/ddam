import { useState, type FormEvent, type ReactNode } from "react"
import { PlusIcon } from "lucide-react"

import { Button } from "@/components/ui/button"
import {
  Dialog,
  DialogContent,
  DialogDescription,
  DialogFooter,
  DialogHeader,
  DialogTitle,
  DialogTrigger,
} from "@/components/ui/dialog"
import { Input } from "@/components/ui/input"
import { Label } from "@/components/ui/label"
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select"
import { Textarea } from "@/components/ui/textarea"
import { ApiError, type PersonaInput } from "@/lib/api"

function Field({
  id,
  label,
  error,
  children,
}: {
  id: string
  label: string
  error?: string
  children: ReactNode
}) {
  return (
    <div className="grid gap-1.5">
      <Label htmlFor={id}>{label}</Label>
      {children}
      {error && <p className="text-xs text-destructive">{error}</p>}
    </div>
  )
}

export function CreatePersonaDialog({
  onCreate,
}: {
  onCreate: (input: PersonaInput) => Promise<void>
}) {
  const [open, setOpen] = useState(false)
  const [submitting, setSubmitting] = useState(false)
  const [error, setError] = useState<ApiError | null>(null)

  const fieldError = (name: keyof PersonaInput) =>
    error?.fields.find((field) => field.field === name)?.message

  function handleOpenChange(next: boolean) {
    setOpen(next)
    setError(null)
  }

  async function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault()
    const input = Object.fromEntries(
      new FormData(event.currentTarget)
    ) as PersonaInput

    setSubmitting(true)
    setError(null)
    try {
      await onCreate(input)
      setOpen(false)
    } catch (cause) {
      setError(cause as ApiError)
    } finally {
      setSubmitting(false)
    }
  }

  return (
    <Dialog open={open} onOpenChange={handleOpenChange}>
      <DialogTrigger asChild>
        <Button className="w-full">
          <PlusIcon />
          New persona
        </Button>
      </DialogTrigger>
      <DialogContent className="max-h-[90svh] overflow-y-auto">
        <DialogHeader>
          <DialogTitle>New persona</DialogTitle>
          <DialogDescription>
            Who do you want to talk to? The more detail, the better they sound.
          </DialogDescription>
        </DialogHeader>

        {/* noValidate: the API schema is the single source of validation rules. */}
        <form onSubmit={handleSubmit} noValidate className="grid gap-4">
          <Field id="name" label="Name" error={fieldError("name")}>
            <Input
              id="name"
              name="name"
              placeholder="Marie Curie"
              aria-invalid={!!fieldError("name")}
            />
          </Field>

          <div className="grid gap-4 sm:grid-cols-2">
            <Field
              id="birthdate"
              label="Birthdate"
              error={fieldError("birthdate")}
            >
              <Input
                id="birthdate"
                name="birthdate"
                type="date"
                aria-invalid={!!fieldError("birthdate")}
              />
            </Field>

            <Field id="gender" label="Gender" error={fieldError("gender")}>
              <Select name="gender">
                <SelectTrigger
                  id="gender"
                  className="w-full"
                  aria-invalid={!!fieldError("gender")}
                >
                  <SelectValue placeholder="Select" />
                </SelectTrigger>
                <SelectContent>
                  <SelectItem value="female">Female</SelectItem>
                  <SelectItem value="male">Male</SelectItem>
                  <SelectItem value="other">Other</SelectItem>
                </SelectContent>
              </Select>
            </Field>
          </div>

          <Field
            id="lived_place"
            label="Lived place"
            error={fieldError("lived_place")}
          >
            <Input
              id="lived_place"
              name="lived_place"
              placeholder="Warsaw, Paris"
              aria-invalid={!!fieldError("lived_place")}
            />
          </Field>

          <Field id="details" label="Details" error={fieldError("details")}>
            <Textarea
              id="details"
              name="details"
              rows={4}
              placeholder="What they did, how they speak, what they care about."
              aria-invalid={!!fieldError("details")}
            />
          </Field>

          {error && error.fields.length === 0 && (
            <p role="alert" className="text-sm text-destructive">
              {error.message}
            </p>
          )}

          <DialogFooter>
            <Button type="submit" disabled={submitting}>
              {submitting ? "Creating..." : "Create persona"}
            </Button>
          </DialogFooter>
        </form>
      </DialogContent>
    </Dialog>
  )
}
