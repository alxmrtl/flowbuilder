# Convert docs → API integration plan

**Status:** design only. The shipped feature is prompt-only (copy prompt → paste into any LLM →
paste the JSON back). This doc specs the "Run with AI" upgrade that removes the round-trip: the same
**Convert docs** modal gains a file-drop zone and a **Build map** button that calls Claude and drops
the result straight into `validateImportModel` → `importFlowFromObj`.

> When building this, load the `claude-api` Claude Code skill for exact model ids, params and
> pricing — do not hardcode numbers from memory.

---

## 1. What stays the same

- The **Convert-to-Flow prompt** (`tools/convert-to-flow.prompt.md`, embedded as `#convert-prompt`)
  is the single source of truth. In the API path it becomes the **system prompt**, with the chosen
  fidelity paragraph selected exactly as the copy button does today.
- The **fidelity control** (Strict / Balanced / Enriched) and the **`validateImportModel`** hardening
  step are shared with the prompt-only path — the API path only replaces "user pastes JSON" with
  "app receives JSON".
- On any API failure the modal **falls back** to the copy-paste flow, so the feature degrades
  gracefully and the app stays useful offline.

---

## 2. The Claude request

Messages API, one turn.

- **model** — default `claude-opus-4-8` (best structure inference); offer `claude-sonnet-5` as a
  cheaper/faster option in the modal. (Confirm ids/pricing via the `claude-api` skill at build time.)
- **system** — the assembled Convert prompt (fidelity spliced in).
- **messages** — one `user` message whose `content` is an array of blocks, one per source file plus a
  short lead-in ("Here are the sources; label them Source A, B, …"):
  - **PDF** → `document` block, base64.
  - **Image** (photo of a whiteboard, screenshot of a Visio map) → `image` block, base64. Claude reads
    the diagram directly.
  - **`.xlsx` / `.csv`** → parse to text in-browser with the bundled `vendor/xlsx.full.min.js` +
    existing `readDataFile` / `parseCSV` (index.html:4494) and send as a `text` block (a labelled
    table). Do not send the raw binary.
  - **`.docx` / Visio `.vsdx`** → best-effort text extraction; if we can't extract, ask the user to
    paste text or export to PDF (note the limitation in the UI). Plain `.txt` / transcript → `text`.
  - Multiple files → multiple blocks in the one message; this is how multi-source reconciliation
    happens natively.

### Structured output (preferred over fence-parsing)
Define a single tool `create_flow` whose `input_schema` is the model schema (nodes/edges/groups/
comments as in the prompt), and set `tool_choice: { type: "tool", name: "create_flow" }`. Claude then
returns the model as a `tool_use` input — already JSON, no markdown-fence extraction. The prompt's
"Report" becomes an optional `report` string field on the tool input (shown read-only in the modal).
Always still run `validateImportModel` on the result before `importFlowFromObj`.

If tool-forcing is undesirable, keep the prompt's `” ```json ` + `## Report`" contract and reuse the
same fence-extractor the paste path uses.

### Response handling
- Parse `tool_use.input` (or the fenced JSON) → `validateImportModel` → `importFlowFromObj` → open
  the new flow. Toast "Built N steps, M connections".
- **Stream** the request so the modal can show progress ("Reading sources… building map…"); the model
  JSON only applies once complete.
- **Size guard** — cap total input (page/file count + bytes) and warn before large/expensive calls;
  show an estimated token/cost figure.

---

## 3. Two architectures

The app is currently a **pure static** page (no backend, Vercel static). That is the crux: an API key
cannot live in shipped HTML. Two ways to bridge.

### A. Serverless proxy (recommended for a shared/hosted deployment)
- Add a Vercel Function `POST /api/convert`. It holds `ANTHROPIC_API_KEY` (env var, never shipped),
  receives the files + fidelity, builds the Messages request, calls Claude, streams the result back.
- **Pros** — users need no key; central rate/cost control; key stays server-side; can add
  auth/logging/quotas.
- **Cons** — introduces a backend to a static app (deploy config, cold starts, a bill you own); needs
  abuse controls (rate limit, max size, maybe a simple auth token).
- **Deploy notes** — document the function + env var in `README` and Vercel project settings; the
  static build calls a same-origin `/api/convert` so there's no CORS.

### B. Bring-your-own key (recommended to ship first / for the local build)
- The user pastes their own Anthropic API key into the modal; store in `localStorage`
  (`flowbuilder.anthropicKey`), never included in Design-file / library / HTML exports.
- The browser calls the Messages API directly with `anthropic-dangerous-direct-browser-access: true`.
- **Pros** — app stays 100% static; nothing for us to run or pay for; ships fastest.
- **Cons** — each user needs a key; a browser-held key is user-owned and user-visible (make this
  explicit in the UI: only ever your own key, stored locally on this device); direct-browser access
  must be enabled.

### Decision matrix

| | Serverless proxy | BYO key |
|---|---|---|
| App stays static | no | yes |
| User needs own key | no | yes |
| Who pays | us | user |
| Key exposure | server-side | user's browser (own key) |
| Effort to ship | higher | lower |
| Best for | hosted, shared, non-technical users | local build, technical users, quick ship |

A reasonable path: ship **BYO key** first (no backend), add the **proxy** when the hosted version
needs keyless UX.

---

## 4. UI delta from the prompt-only modal

- Add a **drop zone** (accept `.pdf,.png,.jpg,.xlsx,.csv,.docx,.txt`) listing attached files.
- Add a **Build map** button next to "Copy prompt". If no key/endpoint is configured, Build map is
  disabled and the copy-paste flow remains the primary path.
- Add a small **settings** row: model choice, and (BYO) an API-key field with a "stored locally only"
  note; (proxy) nothing user-facing.
- Progress + error states; on error, surface "Copy prompt instead" as the fallback.

---

## 5. Build checklist (when we do it)

1. Load the `claude-api` skill; confirm model ids, the document/image block shapes, tool-use schema,
   streaming, and `anthropic-dangerous-direct-browser-access`.
2. File → content-block converters (reuse `readDataFile`/`parseCSV`; add PDF/image base64).
3. `create_flow` tool schema mirroring the model; `validateImportModel` already exists.
4. Pick architecture (A or B); wire the request; stream progress.
5. Guards: size cap, cost estimate, rate limit (proxy), key handling (BYO).
6. Verify end-to-end on a transcript, a Visio image, and an Excel sheet; confirm fallback works.
