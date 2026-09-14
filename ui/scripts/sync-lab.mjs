#!/usr/bin/env node
/**
 * Copies the lab's Python package (starter_v0) into ui/.lab/ so the serverless
 * function can import the REAL run_model_tool_loop instead of a reimplementation.
 *
 * Why a copy: on Vercel the project Root Directory is `ui/`, so anything above it
 * is not uploaded with the function. This runs in the *install* command, which
 * Vercel executes strictly before it bundles functions — so ordering is
 * deterministic rather than incidental.
 *
 * .lab/ is gitignored. The lab code has exactly one home: starter_v0/.
 */
import { cp, rm, access, mkdir } from "node:fs/promises";
import { existsSync } from "node:fs";
import path from "node:path";
import { fileURLToPath } from "node:url";

const here = path.dirname(fileURLToPath(import.meta.url));
const uiRoot = path.resolve(here, "..");
const dest = path.join(uiRoot, ".lab");

// Local checkout: ../starter_v0. Vercel with "include files outside root": same.
const candidates = [
  path.resolve(uiRoot, "..", "starter_v0"),
  path.resolve(uiRoot, "..", "..", "starter_v0"),
];
const source = candidates.find((p) => existsSync(path.join(p, "chat.py")));

if (!source) {
  // A missing source is fatal: a silent skip would deploy a function that
  // imports nothing and fails at request time instead of at build time.
  console.error(
    "[sync-lab] FATAL: could not find starter_v0/chat.py. Looked in:\n  " +
      candidates.join("\n  ") +
      "\nOn Vercel, enable Settings -> Build -> 'Include source files outside of the Root Directory'."
  );
  process.exit(1);
}

// Never copy secrets or local scratch output into the bundle.
const EXCLUDE = new Set([
  ".venv", "__pycache__", ".env", ".pytest_cache",
  "tickets", "runs", "transcripts", "analysis",
]);

await rm(dest, { recursive: true, force: true });
await mkdir(dest, { recursive: true });
await cp(source, dest, {
  recursive: true,
  filter: (src) => {
    const base = path.basename(src);
    if (EXCLUDE.has(base)) return false;
    if (base.startsWith(".env")) return false;   // .env, .env.local, ...
    if (base.endsWith(".pyc")) return false;
    return true;
  },
});

console.log(`[sync-lab] ${path.relative(uiRoot, source)} -> .lab/`);
