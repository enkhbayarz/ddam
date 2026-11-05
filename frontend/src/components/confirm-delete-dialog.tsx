import { useState, type MouseEvent } from "react"
import { Trash2Icon } from "lucide-react"

import {
  AlertDialog,
  AlertDialogAction,
  AlertDialogCancel,
  AlertDialogContent,
  AlertDialogDescription,
  AlertDialogFooter,
  AlertDialogHeader,
  AlertDialogTitle,
  AlertDialogTrigger,
} from "@/components/ui/alert-dialog"
import { Button } from "@/components/ui/button"

type ConfirmDeleteDialogProps = {
  label: string
  title: string
  description: string
  triggerClassName?: string
  onConfirm: () => Promise<void>
}

export function ConfirmDeleteDialog({
  label,
  title,
  description,
  triggerClassName,
  onConfirm,
}: ConfirmDeleteDialogProps) {
  const [open, setOpen] = useState(false)
  const [error, setError] = useState("")

  function handleOpenChange(next: boolean) {
    setOpen(next)
    setError("")
  }

  async function handleDelete(event: MouseEvent) {
    event.preventDefault() // Keep the dialog open so a failure stays visible.
    try {
      await onConfirm()
      setOpen(false)
    } catch (cause) {
      setError((cause as Error).message)
    }
  }

  return (
    <AlertDialog open={open} onOpenChange={handleOpenChange}>
      <AlertDialogTrigger asChild>
        <Button
          variant="ghost"
          size="icon"
          aria-label={label}
          className={triggerClassName}
        >
          <Trash2Icon />
        </Button>
      </AlertDialogTrigger>
      <AlertDialogContent>
        <AlertDialogHeader>
          <AlertDialogTitle>{title}</AlertDialogTitle>
          <AlertDialogDescription>{description}</AlertDialogDescription>
        </AlertDialogHeader>
        {error && (
          <p role="alert" className="text-sm text-destructive">
            {error}
          </p>
        )}
        <AlertDialogFooter>
          <AlertDialogCancel>Cancel</AlertDialogCancel>
          <AlertDialogAction variant="destructive" onClick={handleDelete}>
            Delete
          </AlertDialogAction>
        </AlertDialogFooter>
      </AlertDialogContent>
    </AlertDialog>
  )
}
