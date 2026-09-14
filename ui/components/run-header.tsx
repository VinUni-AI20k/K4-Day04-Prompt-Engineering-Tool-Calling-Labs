"use client"

import { Download, Hash } from "lucide-react"
import type { ArtifactVersion } from "@/lib/api"

interface RunHeaderProps {
  artifact: ArtifactVersion | null
  model: string
  provider: string
  turnCount: number
  onDownload: () => void
}

/**
 * What is running, and which artifacts produced it.
 *
 * The version and both hashes are computed server-side from the files on disk,
 * so this cannot claim a version the deployment is not actually running. That
 * is the whole point of showing them: a screenshot of a result is only evidence
 * if it names the prompt and tool declarations that produced it.
 */
export function RunHeader({ artifact, model, provider, turnCount, onDownload }: RunHeaderProps) {
  return (
    <header className="border-border bg-card/60 sticky top-0 z-10 border-b backdrop-blur">
      <div className="mx-auto flex w-full max-w-5xl flex-wrap items-center gap-x-4 gap-y-2 px-4 py-3">
        <div className="min-w-0">
          <h1 className="text-foreground text-sm leading-tight font-medium">
            IT Helpdesk Agent
          </h1>
          <p className="text-muted-foreground font-mono text-[11px] leading-tight">
            {provider ? `${provider} / ` : ""}
            {model || "not connected"}
          </p>
        </div>

        <div className="flex min-w-0 flex-wrap items-center gap-x-3 gap-y-1.5 sm:ml-auto">
          {artifact ? (
            <>
              <span className="border-border text-foreground/85 rounded-md border px-2 py-1 font-mono text-[11px] whitespace-nowrap">
                {artifact.artifact_version}
              </span>
              <HashChip label="prompt" value={artifact.prompt_hash} />
              <HashChip label="tools" value={artifact.tools_hash} />
            </>
          ) : (
            <span className="text-muted-foreground font-mono text-[11px]">
              artifact version unavailable
            </span>
          )}

          <button
            type="button"
            onClick={onDownload}
            disabled={turnCount === 0}
            className="border-border text-foreground hover:bg-muted focus-visible:ring-ring inline-flex items-center gap-1.5 rounded-md border px-2.5 py-1.5 text-xs font-medium whitespace-nowrap outline-none focus-visible:ring-2 disabled:cursor-not-allowed disabled:opacity-40"
          >
            <Download aria-hidden="true" className="size-3.5" />
            Transcript
          </button>
        </div>
      </div>
    </header>
  )
}

function HashChip({ label, value }: { label: string; value: string }) {
  if (!value) return null
  return (
    <span
      // The full hash is what gets pasted into a report, so it stays reachable
      // on hover even though only the first 12 characters are shown.
      title={`${label}: ${value}`}
      className="text-muted-foreground inline-flex items-center gap-1 font-mono text-[11px] whitespace-nowrap"
    >
      <Hash aria-hidden="true" className="size-3" />
      {label} {value.slice(0, 12)}
    </span>
  )
}
