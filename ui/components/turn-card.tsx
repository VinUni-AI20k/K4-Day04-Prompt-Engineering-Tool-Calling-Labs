"use client"

import * as React from "react"
import { TriangleAlert, User } from "lucide-react"
import { AgentTrace } from "@/components/ui/agent-trace"
import { JsonViewer } from "@/components/json-viewer"
import { ToolEventList } from "@/components/tool-event-list"
import { STATUS_LABEL, type ChatResponse, type RunStatus } from "@/lib/api"
import { cn } from "@/lib/utils"

export interface Turn {
  id: string
  index: number
  user: string
  /** Absent while the turn is still in flight. */
  response?: ChatResponse
  /** Set when the request itself failed, as opposed to the run failing. */
  transportError?: string
}

const STATUS_STYLE: Record<RunStatus, string> = {
  answered: "border-primary/40 text-primary",
  waiting_for_user: "border-border text-foreground/80",
  max_tool_rounds: "border-border text-foreground/80",
  provider_error: "border-destructive/50 text-destructive",
}

export function TurnCard({ turn }: { turn: Turn }) {
  return (
    <article className="space-y-3">
      <UserMessage text={turn.user} />

      {turn.transportError ? (
        <FailureNotice title="Could not reach the agent" detail={turn.transportError} />
      ) : turn.response ? (
        <AgentAnswer turn={turn} response={turn.response} />
      ) : (
        <PendingAnswer />
      )}
    </article>
  )
}

function UserMessage({ text }: { text: string }) {
  return (
    <div className="flex items-start gap-2.5">
      <span className="border-border text-muted-foreground mt-0.5 flex size-6 shrink-0 items-center justify-center rounded-full border">
        <User aria-hidden="true" className="size-3" />
      </span>
      <p className="text-foreground min-w-0 flex-1 text-sm leading-relaxed whitespace-pre-wrap">
        {text}
      </p>
    </div>
  )
}

function AgentAnswer({ turn, response }: { turn: Turn; response: ChatResponse }) {
  const rounds = response.rounds?.length ?? 0
  // The envelope is only worth showing when it carried something the reply did
  // not, which is exactly when a grader wants to see it.
  const showEnvelope =
    response.structured_output != null && response.assistant_text !== response.reply

  return (
    <div className="border-border bg-card space-y-3 rounded-xl border p-3 sm:p-4">
      <div className="flex flex-wrap items-center gap-x-3 gap-y-1.5">
        <span
          className={cn(
            "rounded-full border px-2 py-0.5 font-mono text-[11px] leading-4",
            STATUS_STYLE[response.status]
          )}
        >
          {STATUS_LABEL[response.status]}
        </span>
        <span className="text-muted-foreground font-mono text-[11px]">
          {rounds} round{rounds === 1 ? "" : "s"}
        </span>
        <span className="text-muted-foreground font-mono text-[11px] tabular-nums">
          {(response.duration_ms / 1000).toFixed(2)}s
        </span>
        {response.retries > 0 && (
          <span className="text-muted-foreground font-mono text-[11px]">
            {response.retries} retr{response.retries === 1 ? "y" : "ies"}
          </span>
        )}
      </div>

      {response.error && (
        <FailureNotice title="The run did not finish" detail={response.error} />
      )}

      {response.reply && (
        <p className="text-foreground text-sm leading-relaxed whitespace-pre-wrap">
          {response.reply}
        </p>
      )}

      {response.spans.length > 0 && (
        <AgentTrace
          spans={response.spans}
          duration={response.duration_ms}
          runId={`turn_${turn.index}`}
          model={response.model}
          autoPlay={false}
          // A finished run is the useful resting state here: this is evidence to
          // read, not a loop to watch, so the playhead starts at the end.
          defaultTime={response.duration_ms}
          rowHeight={32}
          labelWidth={180}
        />
      )}

      {response.tool_events.length > 0 ? (
        <ToolEventList events={response.tool_events} />
      ) : (
        <p className="text-muted-foreground font-mono text-[11px]">
          No tools were called on this turn.
        </p>
      )}

      {showEnvelope && (
        <details className="group/env">
          <summary className="text-muted-foreground hover:text-foreground focus-visible:ring-ring marker:content-[''] inline-flex cursor-pointer rounded font-mono text-[11px] underline underline-offset-2 outline-none focus-visible:ring-2">
            Raw model output
          </summary>
          <div className="mt-2">
            <JsonViewer value={response.structured_output} />
          </div>
        </details>
      )}
    </div>
  )
}

/** Skeleton shaped like the answer it replaces, so nothing jumps when it lands. */
function PendingAnswer() {
  return (
    <div
      role="status"
      aria-label="Running the agent"
      className="border-border bg-card space-y-3 rounded-xl border p-3 sm:p-4"
    >
      <div className="flex items-center gap-3">
        <span className="bg-muted h-4 w-20 animate-pulse rounded-full" />
        <span className="bg-muted h-3 w-14 animate-pulse rounded-full" />
      </div>
      <div className="space-y-2">
        <span className="bg-muted block h-3 w-full animate-pulse rounded" />
        <span className="bg-muted block h-3 w-4/5 animate-pulse rounded" />
      </div>
      <div className="border-border space-y-2 rounded-lg border p-3">
        <span className="bg-muted block h-2.5 w-2/3 animate-pulse rounded-full" />
        <span className="bg-muted block h-2.5 w-1/2 animate-pulse rounded-full" />
      </div>
      <p className="text-muted-foreground font-mono text-[11px]">
        Calling the model and its tools. This usually takes 5 to 15 seconds.
      </p>
    </div>
  )
}

function FailureNotice({ title, detail }: { title: string; detail: string }) {
  return (
    <div className="border-destructive/40 bg-destructive/5 flex items-start gap-2.5 rounded-lg border p-3">
      <TriangleAlert aria-hidden="true" className="text-destructive mt-0.5 size-4 shrink-0" />
      <div className="min-w-0">
        <p className="text-destructive text-xs font-medium">{title}</p>
        <p className="text-foreground/80 mt-1 text-xs leading-relaxed">{detail}</p>
      </div>
    </div>
  )
}
