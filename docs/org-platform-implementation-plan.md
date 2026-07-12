# Org Platform — Implementation Plan (Rev A)

**Date:** 2026-07-11 · **Input:** `docs/org-platform-plan.html` reviewed by Alex (all 8 recommendations accepted; comments folded in below).
This is the working plan implementation sessions execute against. The architecture rationale lives in the HTML plan; this document is the *what and in which order*.

---

## 1 · Decision record (locked)

| # | Decision | Choice | Reviewer comment → how it's honored |
|---|----------|--------|--------------------------------------|
| D1 | Storage connection | **Local folder first (File System Access), Graph API later** | "Draw up a high-level Graph plan that is compatible, keep for future." → § 3.2 forward-compat contract; Graph build deferred to Phase 5. |
| D2 | Index location | **Shared `.flowbuilder/` sidecar in the library + IndexedDB cache** | — |
| D3 | Metadata model | **Core fields + org-defined `schema.json`** | — |
| D4 | Decomposition | **Groups ⇄ maps with linked steps, digest roll-ups** | — |
| D5 | Dashboard scoping | **Metadata query + pins** | "All 4 templates serve a role — develop all 4." → all four ship in Phase 4. |
| D6 | Concurrency | **Etag/version check + soft presence** | "Very little simultaneous editing." → presence marker is the low-effort variant; no escalation path needed. |
| D7 | Build order | **As proposed (foundations → workspace → hierarchy → dashboards)** | New requirements inserted as Phases 2/2.5 without reordering the spine. |
| D8 | Code packaging | **Evolve inside `index.html`, single file** | Question answered in § 2.1. |

---

## 2 · Answers to open questions from the review

### 2.1 D8 — "Is there a legitimacy risk to staying one file?"

**No user-facing or architectural risk.** The single file is a *deployment artifact* question, not an app-quality one:

- **Runtime:** browsers parse a 1–2 MB HTML file without measurable startup difference at this scale; Vercel serves and caches it identically. Users can't tell.
- **Correctness/testing:** the headless-verify recipe already drives the real file; nothing about testing requires modules.
- **The real costs are developer-experience costs**, and they only bite under conditions that don't currently hold: (a) multiple contributors editing concurrently (merge conflicts in one file) — you commit solo to main; (b) a unit-test framework wanting importable modules; (c) editor sluggishness on very large files — noticeable around ~2 MB, we're at ~0.4 MB.
- **No lock-in by deferring:** the file is already organized in banner-delimited sections. A later migration is mechanical — split at banners into modules, `esbuild`-concat back to one emitted file (same shipped artifact, same deploy). Nothing built now would be thrown away.

**Triggers to revisit** (any one): a second regular contributor · file crosses ~1.5 MB · we want TypeScript · section discipline visibly decays. Until then: stay as-is, keep section banners strict, and maintain a short file-map comment at the top of `index.html` as the Workspace sections land.

### 2.2 D1 — Graph API forward-compatibility contract

Everything in Phases 0–4 is built against a 5-method storage adapter. The Mode B (local folder) implementation is the only one built now; the Graph mapping is recorded so nothing drifts incompatible:

| Adapter method | Mode B (File System Access) | Mode A (Graph, future) |
|---|---|---|
| `list()` | recurse directory handle | `GET /drives/{id}/root:/…:/children` |
| `read(path)` | `getFileHandle().getFile()` | `GET …/content` |
| `write(path, blob, expectedRev)` | write via handle; `expectedRev` = lastModified | `PUT …/content` with `If-Match: eTag` |
| `changedSince(cursor)` | mtime scan vs catalog | delta query (`/delta?token=`) — cursor = delta link |
| `rev(path)` | `lastModified` | `eTag`/`cTag` |

Rules that keep compatibility: all stored paths are **relative to the library root**; identity is `mapId`, never path; revs are opaque strings; the catalog/digests never embed absolute paths or drive ids. Future IT ask (documented, not built): SPA app registration, `Sites.Selected` scope, MSAL.js — one page in onboarding docs when the time comes.

---

## 3 · New requirements from the review

### 3.1 R1 — Segments (per-case-type stats) — *"I know this will be a need"*

**Concept:** a flow serves different case types ("Simple" vs "Complex" claims); a triage step routes them; users must view the map's stats for one segment at a time, and dashboards must compare segments across maps.

**Format (reserved in Phase 0, engine in Phase 2):**

```jsonc
// map level
"segments": {
  "dimension": "Case type",          // display name; may reference a shared dimension id from schema.json
  "list": [
    { "id": "seg_simple",  "label": "Simple",  "share": 0.7 },
    { "id": "seg_complex", "label": "Complex", "share": 0.3 }
  ]
}
// per node — sparse overrides, base values are the fallback
"seg": {
  "seg_simple":  { "touch": 5 },
  "seg_complex": { "touch": 25, "reworkPct": 12 },
  "seg_fast":    { "skip": true }    // this segment bypasses the step entirely (routing)
}
```

**Semantics:**
- A segment = (a) a **route** — the subset of steps it passes through (`skip` flags), and (b) optional **per-step overrides** (touch, wait, rework, wip…) at shared steps. Absent override → base value.
- `share` = fraction of incoming demand. **"All cases" = share-weighted blend**, which must reproduce today's numbers when no segments are defined (zero-regression rule).
- Derived per segment, reusing the existing engine unchanged: lead time along *its* path, flow efficiency, capacity consumed, RFT. Bottleneck flag stays whole-flow (a segment view can *show* its own constraint, but the unified `r.flag` semantics don't change).

**CSV:** optional `Segment` column. Rows carrying a segment feed `measured` per-segment values; rows without apply to all. Export sheet grows the column when segments exist.

**UI (Phase 2):** a segment switcher (chip row: `All · Simple · Complex`) beside the lens controls. Selecting a segment: cards show segment numbers, steps/edges not on its route dim (same visual grammar as lens dimming), analysis strip recomputes. Segment editing lives in the step inspector (per-segment value rows) + a "segments" editor on the map details panel.

**Digest & dashboards:** digest carries `metricsBySegment` (same headline fields as `metrics`, keyed by segment id). `schema.json` can declare **shared dimensions** (e.g. org-wide "Case type": Simple/Complex) so segment labels are comparable across maps; dashboards can then slice org metrics by segment.

### 3.2 R2 — Output by role (people-level splits) — *plan for, build later*

Same slicing idea, different axis: not *which cases*, but *which people* (junior vs senior adjusters at the same steps). Two facts shape the plan:

1. **Partial support already exists**: `ownerLoad` ("Load by role") already computes per-role load from step owners. The request extends a real metric, not a blank.
2. **Semantics differ from segments**: roles don't route (all roles share the path); they *partition staffing* at a step (`people`, `hoursPerDay`, `touch` per role). Blending is capacity-additive rather than share-weighted.

**Plan:** the segment engine is built as a generic *dimension* mechanism internally (`resolve(node, field, dimKey, memberId)`), with `seg` as its first client. Role splits (`n.role = { r_senior: { people: 2, touch: 4 }, … }`) become its second client in Phase 5, when the build/inspection UX for it is designed properly. Format key `role` is reserved in the Phase 0 validator so files that anticipate it never get stripped.

### 3.3 R3 — Standardized vocabulary (org-editable, FB standard by default)

**The hook already exists.** `METRICS_SPEC` is a canonical registry — term ids (`touch`, `wait`, `turnaround`, `eff`, `capacity`, `rft`, `wip`, `load`, `flowCap`, `ownerLoad`, …) each with default label, unit, plain-language definition, and derivation relations — and every metric label in the UI renders through `ML(id)`. So:

- **Flow Builder standard lexicon = `METRICS_SPEC` as shipped** (already simple/non-jargon). Phase 0 adds a coverage audit: any label string not routed through `ML()`/the spec (canvas drawers, analysis prose, CSV headers, export sheets, insights text) gets routed. This is the census of "base tracking data fields" the review asked for — the registry *is* the census, extended with the input fields (`people`, `hoursPerDay`, `demand`, `wip`, value ratings) and map-level fields as first-class entries.
- **Workspace overrides:** `.flowbuilder/vocabulary.json` — `{ "terms": { "touch": "Time to action", … } }`. `ML(id)` becomes `vocab[id] ?? METRICS_SPEC…l`. Loaded with the workspace; standalone (no workspace) uses defaults. Overrides apply everywhere labels render: cards, lenses, analysis, insights, exports, CSV headers, dashboards.
- **Aliases on import:** each term keeps an alias list (FB default + workspace override + common synonyms, e.g. "time to action" → `touch`), so CSV/Convert-docs imports recognize org language.
- **Glossary surface:** the existing "Metrics explained" overlay becomes workspace-aware (shows the org's chosen labels with FB definitions) — the shared-language artifact for onboarding. Editing UI: a two-column term editor in Workspace settings (FB standard → org term), Phase 1.

### 3.4 R4 — Onboarding & migration of existing map estates (PDF / Visio)

Three tiers, honest about what each can achieve:

- **Tier 1 — AI prompt conversion (exists; harden in Phase 1).** The Convert-docs flow covers PDFs, transcripts, documents — anything that is *prose or a picture*. There is no deterministic path for these; AI is the only route, output always needs human review. Hardening: test against real artifacts, add provenance to imported maps (`meta.importedFrom: { type:"ai-doc", source, date, fidelity }`), and a governance flag ("AI-imported, unreviewed") so converted maps enter the estate as visible drafts, not silent truth.
- **Tier 2 — native `.vsdx` importer (Phase 2.5, deterministic, no AI).** Visio's `.vsdx` is an OPC package — a zip of XML — parseable fully in-browser (one small zip lib into `vendor/`). Mapping: shape masters → step types (process/decision/start-end heuristics), connectors (`Connects` XML) → edges, containers/swimlanes → groups, geometry → x/y (scaled; optional Tidy after), shape text → labels, Visio *Shape Data* rows → step details where recognizable (some orgs store cycle times there — alias matching via R3). Unmapped shapes → generic steps with an attached note listing what was skipped. **UX:** drop a `.vsdx` into the Workspace → conversion preview (counts: N shapes → N steps, M connectors → M edges, unmapped list) → accept → saved as a draft map with provenance. Structure imports faithfully; timing/people data usually won't exist in the source — imported maps are *structurally complete, metrically empty*, which the confidence system already expresses honestly.
- **Tier 3 — bulk onboarding sequence (later, with/without API).** Workspace scans the connected folder for `.vsdx`/`.pdf`, queues conversions (Tier 2 deterministic for Visio; Tier 1 AI for documents — via the Convert-docs API per `docs/convert-docs-api-plan.md` when it exists, or as a guided one-by-one prompt workflow meanwhile), and feeds a human review queue. Not MVP; the queue UI is cheap once Tiers 1–2 exist.

**Recommendation for orgs with big Visio estates:** Tier 2 is the credible answer and is worth pulling relatively early (hence Phase 2.5) — "drop your Visio files in, they become live maps" is likely the single strongest adoption lever after search.

### 3.5 R5 — Swimlane view (noted 2026-07-11, build later)

A layout mode toggle, sibling of Tidy: switch a map back and forth between the current **one-line** arrangement and a **swimlane** arrangement (lanes by role/owner — the natural lane key given steps already carry owners; segment lanes are a possible second mode via the R1 dimension engine). Like Tidy it's a *placement* operation over the same model — no format change needed, positions are just recomputed per mode — so nothing in Phases 0–4 has to anticipate it beyond keeping owner/role data clean. Also relevant to R4: Visio imports are usually swimlane diagrams, so lane detection there (containers → owners) feeds this view for free. Scheduled Phase 5.

---

## 4 · Format specifications (frozen by Phase 0)

**Map file `*.flow.json` — v2 additions** (all optional; migrate-on-load fills defaults; unknown-key policy in validator changes from *strip* to *preserve-listed*):

```jsonc
{
  "schemaVersion": 2,
  "mapId": "m_<uuid>",              // minted at creation; survives rename/move; duplicate mints new
  "meta": {
    "owner": "", "area": "", "team": "",
    "status": "draft",              // draft | active | under-review | retired
    "reviewedAt": null, "reviewCadenceDays": null,
    "tags": [], "custom": {},
    "importedFrom": null            // provenance (R4)
  },
  "segments": { … },                // R1 (may be absent)
  "nodes": [ { …, "seg": { … }, "role": { … }, "linksTo": { "mapId": "…", "nodeId": null } } ]
}
```

**Digest v1** (`.flowbuilder/digests/<mapId>.json`): as specced in the HTML plan § 3, plus `metricsBySegment`, `meta.importedFrom`, and `vocabVersion`. Built by a pure function `buildDigest(model, results)` so it's testable headlessly before any workspace exists.

**Workspace sidecar** (`.flowbuilder/`): `catalog.json`, `digests/`, `search/`, `aggregates/`, `dashboards/`, `schema.json` (metadata fields **+ shared segment dimensions**), `vocabulary.json` (R3).

---

## 5 · Phase plan

Spine unchanged per D7; new requirements slot in as 2/2.5. Each phase ends with the headless-verify recipe green plus its own acceptance check.

| Phase | Scope | Contents | Acceptance |
|---|---|---|---|
| **0** | Format foundations + registry | `mapId`, `schemaVersion:2`, `meta`, `linksTo`/`seg`/`role` preserved by validator; `buildDigest()` + golden test; `ML()` vocabulary-override hook + label-routing audit; migrations (old flows load silently) | Every saved flow carries id/meta/v2; digest of a sample flow matches golden; zero visual regression |
| **1** | Workspace: connect · browse · search | FS-Access adapter (§ 2.2 contract); catalog + reconcile loop; home gallery → Workspace (folder-backed); faceted browse; MiniSearch full-text; meta-editing panel (schema-driven); vocabulary editor + glossary; localStorage migration wizard; Tier-1 provenance/flags | A 1,000-map folder browses/searches without perceptible lag; localStorage flows migrate in |
| **2** | Segments | Dimension engine (`seg` client); segment switcher + dimmed routing view; per-segment inspector rows + map-level segment editor; CSV `Segment` column in/out; `metricsBySegment` in digest | With no segments defined, every number identical to today; segment view reproduces hand-checked fixture |
| **2.5** | Visio onboarding | `.vsdx` parser (vendor zip lib); master/connector/container mapping; Shape-Data → details via aliases; preview-accept flow; provenance + governance flag | Reference Visio files render faithfully with only positional tweaks |
| **3** | Links, hierarchy, roll-ups | Linked steps + drill-in/breadcrumb; promote/demote group ⇄ map; digest roll-ups (segment-aware where dimensions match); backlinks; tombstones + cycle flags | Parent shows live child metrics; rename/move/delete never breaks links |
| **4** | Dashboards + governance | Aggregates; **all four** templates (per D5): My processes / Ops health / Compare teams / Portfolio; governance panel + widgets; `aggregates/*.csv` for Excel/Power BI; etag save-check + presence (D6) | VP-view renders from aggregates only; confidence + governance visible |
| **5** | Later | Dashboard builder; **role dimension** (R2) on the dimension engine; **swimlane view** (R5); Graph adapter + IT one-pager (D1); connector descriptors; Tier-3 bulk onboarding; thin service only if the ceiling is hit | — |

**Sequencing note:** Phase 2 (segments) lands before hierarchy because it touches the metric engine's resolution layer — better to stabilize that before roll-ups consume it. Phases 2 and 2.5 are independent of each other and can swap if a Visio-heavy org shows up first.

---

## 6 · Risk register additions (beyond HTML plan § 12)

| Risk | Mitigation |
|---|---|
| Segment engine perturbs existing numbers | Zero-regression rule: no segments defined ⇒ resolution path is byte-identical to today; golden-number tests on sample flows before/after |
| Vocabulary overrides create cross-org babel in shared artifacts | Exports/digests store term **ids**; labels resolve at render time from the viewing workspace; FB-standard labels used when no workspace |
| Visio estates use wild custom stencils | Unmapped-shape → generic-step fallback guarantees nothing is dropped; preview shows exactly what needs hand-mapping |
| Segment/role data multiplies CSV complexity | Segment column optional; export pre-fills current shape so round-tripping stays copy-paste simple |

---

## 7 · Next action

**Phase 0** is fully specified above and has no open questions: mint `mapId`, add `schemaVersion`/`meta`, switch validator to preserve `linksTo`/`seg`/`role`/`segments`, implement `buildDigest()` with a golden test, hook `ML()` for vocabulary overrides, audit label routing. Zero visible UI change; verified headlessly.
