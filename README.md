# Flow Builder — Lean Value-Stream Visualizer

A single self-contained HTML tool for building and visualizing the **flow of value** to the
customer: touch time (value-add work), wait time (backlogs), turnaround time, and **flow
efficiency** — fed from Excel/CSV, with a built-in prompt that forces the *"is this step
value-add?"* conversation on every step. Holds **many flows** in one place.

## Two versions

There are two builds of the same tool:

- **`FlowBuilder.html`** — the original **local** tool: double-click to open, with an *always-on*
  data layer (connect a spreadsheet, remember it, refresh live).
- **`index.html`** — a **hosted "snapshot"** build meant to live on a static site (Vercel via
  GitHub). Same builder and analysis, but tuned for *"build a flow now and then, drop in a sheet of
  numbers, read the analysis"*: no live data link, plus **PNG/PDF export** and full **theme**
  control. See **[Hosted version](#hosted-version-indexhtml-on-vercel)** below.

## Files

```
index.html               ← hosted "snapshot" build (served at the site root on Vercel)
FlowBuilder.html         ← original local build (open this in Microsoft Edge)
vendor/xlsx.full.min.js  ← reads .xlsx files, fully offline (no internet needed)
vendor/jspdf.umd.min.js  ← writes PDFs, fully offline (used by index.html's export)
samples/FlowData.csv     ← sample data so it works the moment you open it
```

Keep the folder together (the app needs `vendor/`). To share the local build, zip the folder or
drop it on SharePoint/OneDrive. Viewers just double-click `FlowBuilder.html`.

## Hosted version (`index.html` on Vercel)

`index.html` is a pure static page — no backend, no build step.

**Deploy:** push this repo to GitHub, import it in Vercel (framework preset **Other**, no build
command, output directory = repo root). Vercel serves `index.html` at the site URL automatically.
Make sure `vendor/` is committed.

**How flows are saved (persistence):**

- **In the browser** — every flow autosaves to `localStorage` as you edit, so it's there next time
  you visit the site. It's *per browser / per device* (not synced across machines), which is the
  right fit for an occasional-use snapshot tool.
- **Portable copy** — **Back up design** downloads a flow as JSON; re-add it anywhere via
  **Home → Import…**. **Share with team** exports a standalone read-only HTML copy.

**Stats are a snapshot, not a live feed:**

1. **⬇ Export sheet** — downloads a CSV with one row per step (its `StepID` + name, prefilled with
   whatever the cards currently show).
2. Fill in the numbers (touch time, wait time, WIP).
3. **⬆ Import sheet** — load it back. The numbers populate the cards/analysis and are **saved with
   the flow** (and travel into a shared copy). Re-import any time to refresh.

If no sheet is imported, cards fall back to the touch/wait/WIP values typed into the inspector, so a
flow analyses fine before any import.

**Export a picture:** **🖼 Export ▾ → PNG / PDF** renders the title + map + full analysis (stats +
time-contribution ribbon + legend) in the current theme. PDF is produced offline via `jsPDF`.

**Appearance / themes:** **🎨 Appearance** offers presets (**Dark / Light / Paper / Blueprint**)
plus per-colour pickers for background, surfaces, text, accent, the canvas grid, and the
Human/Bot/Queue hues. The theme is saved per flow and applied across the **whole UI — including the
menus and the exports** (Light/Paper are the print-friendly looks).

## Screens

- **Flows (home)** — a gallery of all your value streams. New / Open / Duplicate / Rename /
  Delete, plus Import / Export. Each card shows the flow's efficiency and biggest bottleneck.
- **Editor** — opening a flow lands you straight in the editor (there's no separate View/Build
  mode). The top **Add to flow** bar holds the building blocks, the canvas is the map, and the
  bottom **Analysis** area shows the live stats + the time-contribution bar.
- **Shared viewer** — *Share with team* exports a standalone, read-only copy (same layout, no
  editing).

Click **≣ Flows** (or the "Flow Builder" wordmark) any time to return to the gallery.

## Managing flows (start new / load existing)

- **+ New flow** — starts a blank flow (a Start and End node) ready to build.
- **Open** a card to view/edit it.
- **Duplicate / Rename / Delete** per card.
- **Export** a flow as a `.json` file; **Import…** adds a `.json` (single flow *or* a whole
  exported library) back in.
- **Export library** backs up *all* flows as one JSON.

Flows are saved automatically in the browser (localStorage) as you edit. `Save design` and
`Share with team` (below) are for sharing outside the browser.

## Building a flow

In **Build**: add nodes from the left palette — **🧑 Human Step**, **🤖 Bot Step**,
**Queue**, **Start**, **End** — and **drag** to arrange them. Node labels **wrap and the box
grows** to fit. For every work step you must set its **Customer value** and answer *"what value
does this add to the customer?"* — unrated steps show a ⚠.

**Connecting steps (Visio-style):** hover a box and **4 connection dots** appear (one per side).
**Drag from a dot to another box** (or onto one of its dots) to draw the arrow — it remembers
which sides it joins, so you can make **loops/rework** (e.g. drag from the *bottom* of a later
step back to an earlier one and it routes cleanly underneath). Select an arrow to change its
**From/To side**, split %, or delete it. (The inspector's **Draw arrow from here** still works as
a no-hover fallback.)

Every node is the **same uniform card**; its **type** is read from the card's **icon + colour**
(queue = indigo, human = teal, bot = violet) rather than its shape.

- **Human Step / Bot Step** — hands-on work. A Bot Step marks work done by automation (robot
  icon) vs a person (person icon); toggle Human ↔ Bot in the inspector.
- **Queue** — where items wait between steps (queue icon + indigo frame).

Each card carries the same slots: type icon + label, a **tank-fill gauge** (WIP for queues,
volume for steps), a **time · %** badge coloured by **severity** (green/amber/red), and a bottom
**icon row** that turns the categorical labels into glyphs — **state** (⏳ waiting), **owner**
(e.g. Ops / Underwriter / a system), and **value** (★ Valued · shield Necessary · ✂ Could remove).
The legend under the map decodes them. The single biggest backlog gets a **BOTTLENECK** flag.

- **💾 Save design** — downloads the current flow's design (boxes/arrows/ratings) as a backup JSON.
- **📤 Share with team** — produces a standalone, read-only HTML with this flow baked in; that's
  the file you hand to the team.

## Customer value (the forcing function)

Every work step must be rated. The three choices and their definitions are shown right in the
inspector:

| Choice | Meaning | Color |
|---|---|---|
| **Valued** | The customer values it / would pay for it | green |
| **Necessary** | Required (compliance, risk) but not valued by the customer | blue |
| **Could remove** | Adds no value — a candidate to eliminate | red |

## Seeing how work is distributed

- **Load** is shown on each card's **tank-fill gauge** (the fuller the tank, the bigger the
  backlog), so cards stay a uniform size. (The old "Size by load" toggle is retired.)
- **Bottom panel: Ribbon | Timeline**
  - **Ribbon** — one proportional bar of the whole turnaround, **coloured by type** so each band
    lines up with its card's hue.
  - **Timeline** — one bar per stage drawn to scale, so you can track where the time goes along
    the flow (long waits look long; the bottleneck is red).

## Connecting data (and keeping it "live")

A flow has **two layers**: the **design** (boxes/arrows/ratings — built once; *Share with team*,
*Back up design*) and the **numbers** (wait/touch/WIP per step — change constantly; *Data
template* → *Connect data* → *Refresh*). The toolbar separates them, and the **ℹ** button explains
it in-app.

**The data loop — the flow defines what data it needs:**

1. **Build** your flow. Each step has a `StepID` (its join key — editable in the inspector as
   "Data key").
2. **⬇ Data template** — downloads a CSV with the exact columns this flow needs and **one row per
   step** (its StepID + name, with the right metric column pre-filled). *This file is the spec.*
3. A teammate/programmer **fills that template** — or points a query/export at the same columns +
   StepIDs — and keeps it updated in a **OneDrive/SharePoint-synced folder**.
4. **🔌 Connect data** to that file once (it's **remembered**), then **⟳ Refresh** (or just reopen
   the flow) pulls the latest. The status shows `Source: … · updated Xm ago · N/N matched` so you
   know the file lines up — it turns amber and lists any steps with no data.

> **Back up design** downloads the flow's blueprint as JSON — for backup or moving the flow to
> another machine (re-add via Home → Import). It is *not* the data step.
>
> "Remember the file" uses the browser's File System Access API (Edge/Chromium). If it isn't
> available, **Refresh** simply re-opens the picker — still one click. Remembered sources are per
> browser/machine and are **not** included in a shared viewer.

### Data contract (what the template generates)

One row per **step × segment × period**:

| Column | Meaning |
|---|---|
| `StepID` | matches the node's data key on the map (the join key) |
| `StepName` | the step's label — for humans; ignored on import |
| `NodeType` | `Human` / `Bot` / `Queue` — for humans; ignored on import |
| `Segment` | item type, e.g. `New Business` / `Renewal` (or `ALL`) |
| `Period` | week/month for trends, e.g. `2026-06` |
| `TouchTimeAvg` | active work time — for **Human/Bot** steps |
| `WaitTimeAvg` | time-in-queue — for **Queue** nodes |
| `WIP` / `Volume` | queue size / throughput |

Leave a cell blank where it doesn't apply. If a step has no data row, the node falls back to the
values typed into Build mode, or shows "no data" — it never breaks.

## Metrics (computed automatically along the main path)

- **Touch time** = Σ active work on touch steps
- **Wait time** = Σ time in backlogs
- **Turnaround time** = touch + wait (start → delivered)
- **Flow efficiency** = touch ÷ turnaround (the headline Lean number)
- **Bottleneck** = the largest backlog on the path, or any backlog over its WIP limit

## Roadmap (not yet built)

- Split % on branches, side-by-side segment comparison, turnaround trend / cumulative flow diagram.
- SharePoint auto-refresh via Power Automate, optional Power BI companion.
