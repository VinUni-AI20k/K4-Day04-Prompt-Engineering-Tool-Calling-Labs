"use client"

import * as React from "react"
import { CornerDownLeft, Loader2 } from "lucide-react"
import { RunHeader } from "@/components/run-header"
import { TurnCard, type Turn } from "@/components/turn-card"
import {
  ApiError,
  fetchMeta,
  sendChat,
  type ArtifactVersion,
  type ChatHistoryItem,
  type MetaResponse,
} from "@/lib/api"
import {
  buildTranscript,
  downloadTranscript,
  nowIso,
  transcriptId,
  type TranscriptTurn,
} from "@/lib/transcript"

/** Starting points that exercise the four flows the lab asks for evidence on. */
const EXAMPLES = [
  "VPN production co dang bi loi khong?",
  "Laptop LT-318 khong vao duoc VPN, kiem tra giup minh.",
  "May in tang 3 bi ket lenh in, mo ticket giup minh.",
  "Kiem tra thiet bi giup minh.",
]

export default function Page() {
  const [turns, setTurns] = React.useState<Turn[]>([])
  const [meta, setMeta] = React.useState<MetaResponse | null>(null)
  const [metaError, setMetaError] = React.useState<string | null>(null)
  const [input, setInput] = React.useState("")
  const [sending, setSending] = React.useState(false)

  // Transcript identity is fixed when the session starts, so every download
  // from this session is the same run rather than a new one each time.
  const sessionRef = React.useRef({ createdAt: nowIso(), id: "" })
  const recordsRef = React.useRef<TranscriptTurn[]>([])
  const bottomRef = React.useRef<HTMLDivElement>(null)
  const inputRef = React.useRef<HTMLTextAreaElement>(null)

  React.useEffect(() => {
    const controller = new AbortController()
    fetchMeta(controller.signal)
      .then((value) => {
        setMeta(value)
        sessionRef.current.id = transcriptId(value.artifact, value.provider)
      })
      .catch((error: unknown) => {
        if (error instanceof DOMException && error.name === "AbortError") return
        setMetaError(error instanceof ApiError ? error.message : String(error))
      })
    return () => controller.abort()
  }, [])

  React.useEffect(() => {
    bottomRef.current?.scrollIntoView({ behavior: "smooth", block: "end" })
  }, [turns])

  const artifact: ArtifactVersion | null = meta?.artifact ?? null

  async function submit(text: string) {
    const message = text.trim()
    if (!message || sending) return

    // Only settled turns are context. A turn still in flight has no answer to
    // carry, and a failed one would teach the model from an empty reply.
    const history: ChatHistoryItem[] = turns.flatMap((turn) =>
      turn.response?.reply
        ? [
            { role: "user" as const, content: turn.user },
            { role: "assistant" as const, content: turn.response.reply },
          ]
        : []
    )

    const index = turns.length + 1
    const id = `turn-${index}-${Date.now()}`
    const startedAt = nowIso()

    setTurns((previous) => [...previous, { id, index, user: message }])
    setInput("")
    setSending(true)

    try {
      const response = await sendChat(message, history)
      setTurns((previous) =>
        previous.map((turn) => (turn.id === id ? { ...turn, response } : turn))
      )
      recordsRef.current.push({
        turn_index: index,
        started_at: startedAt,
        ended_at: nowIso(),
        user: message,
        status: response.status,
        assistant_text: response.assistant_text,
        reply: response.reply,
        rounds: response.rounds,
        tool_events: response.tool_events,
        spans: response.spans,
        duration_ms: response.duration_ms,
        retries: response.retries,
        error: response.error,
      })
      if (!sessionRef.current.id) {
        sessionRef.current.id = transcriptId(response.artifact, response.provider)
      }
    } catch (error: unknown) {
      const detail = error instanceof ApiError ? error.message : String(error)
      setTurns((previous) =>
        previous.map((turn) => (turn.id === id ? { ...turn, transportError: detail } : turn))
      )
      recordsRef.current.push({
        turn_index: index,
        started_at: startedAt,
        ended_at: nowIso(),
        user: message,
        status: "transport_error",
        assistant_text: "",
        reply: "",
        rounds: [],
        tool_events: [],
        spans: [],
        duration_ms: 0,
        retries: 0,
        error: detail,
      })
    } finally {
      setSending(false)
      inputRef.current?.focus()
    }
  }

  function onDownload() {
    downloadTranscript(
      buildTranscript(
        recordsRef.current,
        artifact,
        meta?.provider ?? "gemini",
        meta?.model ?? "",
        sessionRef.current.createdAt,
        sessionRef.current.id || transcriptId(artifact, meta?.provider ?? "gemini")
      )
    )
  }

  return (
    <div className="flex min-h-dvh flex-col">
      <RunHeader
        artifact={artifact}
        model={meta?.model ?? ""}
        provider={meta?.provider ?? ""}
        // Driven by state, not the ref: a ref mutation would not re-enable the
        // download button until something else happened to re-render.
        turnCount={turns.length}
        onDownload={onDownload}
      />

      <main className="mx-auto w-full max-w-5xl flex-1 px-4 py-6">
        {metaError && (
          <div className="border-destructive/40 bg-destructive/5 mb-6 rounded-lg border p-3">
            <p className="text-destructive text-xs font-medium">Agent API not reachable</p>
            <p className="text-foreground/80 mt-1 text-xs leading-relaxed">{metaError}</p>
            <p className="text-muted-foreground mt-2 font-mono text-[11px]">
              Local development needs the Python server too: python scripts/local_api.py
            </p>
          </div>
        )}

        {turns.length === 0 ? (
          <EmptyState onPick={submit} disabled={sending} />
        ) : (
          <div className="space-y-8">
            {turns.map((turn) => (
              <TurnCard key={turn.id} turn={turn} />
            ))}
          </div>
        )}
        <div ref={bottomRef} />
      </main>

      <footer className="border-border bg-card/60 sticky bottom-0 border-t backdrop-blur">
        <form
          onSubmit={(event) => {
            event.preventDefault()
            void submit(input)
          }}
          className="mx-auto flex w-full max-w-5xl items-end gap-2 px-4 py-3"
        >
          <textarea
            ref={inputRef}
            value={input}
            onChange={(event) => setInput(event.target.value)}
            onKeyDown={(event) => {
              // Enter sends, Shift+Enter adds a line: this is a chat box, and a
              // multi-turn lab flow means a lot of short consecutive messages.
              if (event.key === "Enter" && !event.shiftKey) {
                event.preventDefault()
                void submit(input)
              }
            }}
            rows={1}
            disabled={sending}
            placeholder="Ask the helpdesk agent something"
            aria-label="Message to the helpdesk agent"
            className="border-border bg-background text-foreground placeholder:text-muted-foreground focus-visible:ring-ring max-h-40 min-h-[2.5rem] flex-1 resize-y rounded-lg border px-3 py-2 text-sm outline-none focus-visible:ring-2 disabled:opacity-60"
          />
          <button
            type="submit"
            disabled={sending || !input.trim()}
            className="bg-primary text-primary-foreground focus-visible:ring-ring inline-flex h-10 shrink-0 items-center gap-1.5 rounded-lg px-4 text-sm font-medium outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-40"
          >
            {sending ? (
              <Loader2 aria-hidden="true" className="size-3.5 animate-spin" />
            ) : (
              <CornerDownLeft aria-hidden="true" className="size-3.5" />
            )}
            {sending ? "Running" : "Send"}
          </button>
        </form>
      </footer>
    </div>
  )
}

function EmptyState({
  onPick,
  disabled,
}: {
  onPick: (text: string) => void
  disabled: boolean
}) {
  return (
    <div className="py-10">
      <h2 className="text-foreground text-lg font-medium">Start a conversation</h2>
      <p className="text-muted-foreground mt-2 max-w-xl text-sm leading-relaxed">
        Every turn shows the tools the agent chose, the arguments it passed, what each tool
        returned, and how long each step took.
      </p>

      <div className="mt-6 grid gap-2 sm:grid-cols-2">
        {EXAMPLES.map((example) => (
          <button
            key={example}
            type="button"
            disabled={disabled}
            onClick={() => onPick(example)}
            className="border-border hover:bg-muted focus-visible:ring-ring rounded-lg border px-3 py-2.5 text-left text-sm outline-none focus-visible:ring-2 disabled:opacity-50"
          >
            {example}
          </button>
        ))}
      </div>
    </div>
  )
}
