# Flow Builder — Lean Value-Stream Visualizer

A single self-contained HTML tool for building and visualizing the **flow of value** to the
customer, analysed through three pillars — **Speed** (hands-on time, waiting, turnaround, flow
efficiency), **Capacity** (people × hours vs incoming work) and **Quality** (rework, right first
time) — fed from a few plain-language inputs and/or Excel/CSV, with a **Value** rating on every
step. Holds **many flows** in one place.

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
2. Fill in the numbers (hands-on time, wait time, queue sizes).
3. **⬆ Import sheet** — load it back. The numbers populate the cards/analysis and are **saved with
   the flow** (and travel into a shared copy). Re-import any time to refresh.

If no sheet is imported, cards fall back to the values typed into the inspector, so a
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
grows** to fit. Every work step carries a **Value** section — a short *Details* description plus a
*Value to customer* rating — and unrated steps show a ⚠.

**Snapping & Tidy:** dragging snaps to a **20px grid**, and dashed **alignment guides** flash when
a box lines up with a neighbour's edge or centre (hold **Alt** to drag freely). **✨ Tidy** lays
the flow out as neat left-to-right columns — it repositions boxes but **never re-routes your
arrows** (custom top/bottom loop routings survive).

**Sub-steps (granularity control):** a step like *"Underwrite deal"* can hold **sub-steps**
(*Review docs → Rate risk → Refer*). Add them in the inspector's **Sub-steps** section. The
collapsed card shows a **▸ N SUB-STEPS** chip and **rolls the numbers up** (touch = sum,
pace/capacity = the slowest sub-step); clicking the chip **expands the card in place** into a
dashed frame of child cards — everything downstream slides over to make room, and slides back on
collapse. Arrows always attach to the parent, so expanding can never break the flow. (This is
different from a **Group**, which is a visual overlay for sectioning the map.)

**Undo & shortcuts:** **⌘Z / Ctrl+Z** undo · **⇧⌘Z / Ctrl+Y** redo · **⌘D** duplicate ·
**Delete** removes the selection · **+ / −** zoom · **Esc** cancels tools/menus ·
**V** cursor · **C** connect · **G** group · **N** note · hold **Space** to grab-pan.

**One cursor does most of it:** the default **Cursor** tool selects (click / shift-click / drag a
box on empty canvas), moves steps, and wires arrows from the hover dots — a **filled dot** means
the port already carries an arrow and dragging adds **another branch**. Drop a port drag on empty
canvas to **create the next step right there** (Human / Bot / Queue picker, pre-connected), or use
the **+ on a card's right edge**. Drag a **lone box over an arrow** and hold ~half a second — the
arrow lights up, and dropping **splices the box into the flow** (downstream steps slide over to
make room). Deleting a mid-chain step **heals the arrow** around it. Connect / Group / Note remain
as smaller specialist tools.

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

## Value

Every work step has a **Details** free-text (what happens in this step) and a **Value to
customer** rating. The three choices and their definitions are shown right in the inspector:

| Choice | Meaning | Color |
|---|---|---|
| **Valued** | Customers would pay for this | green |
| **Necessary** | Required — compliance or risk — but not valued directly | blue |
| **Could remove** | Adds no value; a candidate to cut | red |

## Card views (lenses)

The header **View** switcher changes what every card shows — card size and edge anchors adapt
automatically (hit **✨ Tidy** to re-space for the active view). The active view is saved with the
flow and is what PNG/PDF/share exports show:

- **Metrics** (default) — split-column cards: pace + load scale (derived from people × hours when
  set) and wait/hands-on time with each node's share of the lead time; estimated queue waits show
  with a ≈.
- **People** — owner as the headline plus the **tool** used (UiPath / Copilot / Excel / manual)
  and the step's staffing (N ppl × H h): the handoff-and-automation conversation.
- **Value** — the classification band, glyph and the step's details; queues
  read "WAITING — NO VALUE ADDED": the waste-hunting view.
- **Compact** — small icon+name pills; the whole flow fits on a slide.

## Seeing how work is distributed

- **Load** is shown on each queue card's **cell grid** (more filled cells = bigger backlog) and
  each step's **capacity scale**, so cards stay a uniform size.
- **Bottom panel: the time-contribution ribbon** — one proportional bar of the whole turnaround,
  now fully **interactive**: hover a band for a tooltip (time, % of turnaround, avg passes) and
  its card lights up on the map (and vice-versa); **click** a band to select the step and glide
  the canvas to it. Back-to-back same-colour bands alternate brightness with hairline cuts, so
  neighbours stay distinguishable. A **Type / Severity** toggle recolours the bands by node type
  or by how heavy each band is (green/amber/red) — exports follow the chosen mode.

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
| `Throughput` / `Capacity` | cases/day done vs. possible — overrides the modelled numbers |
| `People` / `HoursPerDay` | staffing on the step — exported for context |
| `ReworkPct` | share of cases that come back — feeds the Quality pillar |
| `ParentStep` | for a sub-step, its parent's name — for humans; ignored on import |

Leave a cell blank where it doesn't apply. If a step has no data row, the node falls back to the
values typed into Build mode, or shows "no data" — it never breaks. A step **with sub-steps** is
not listed (its numbers are derived); the sheet lists its sub-steps instead.

## The metric web (Speed · Capacity · Quality)

The analysis strip groups its stats under three pillars, all fed by a handful of plain-language
inputs — **incoming work** (cases/day, on the Start step), each step's **hands-on time**,
**people** and **hours/day**, an optional **rework %**, and each queue's **in-queue** count.
Everything else is derived, and the derivations link the pillars:

- **Capacity** = people × hours/day ÷ hands-on time — the most a step can do per day
  (availability dictates potential pace). Rework **eats** capacity: effective = capacity × (1 −
  rework %). Observed pace/capacity (inspector "Observed numbers" or a data sheet) override the
  model: *measured > observed > modelled*.
- **Load** = the step's demand (incoming × passes) ÷ effective capacity — the card's load scale;
  over 100 % reads OVERLOADED.
- **Keeping up?** = incoming work vs what the whole flow can deliver per day (the most loaded
  step sets the ceiling). **Load by owner** compares each owner's demand-hours to their staffed
  hours.
- **Queue wait** (when not typed) ≈ in-queue ÷ the next step's pace — "time to clear at today's
  pace" (Little's Law), shown with a ≈.
- **Speed**: hands-on = Σ active work · wait = Σ time in backlogs · turnaround = the two added ·
  **flow efficiency** = hands-on ÷ turnaround (the headline Lean number).
- **Quality**: **right first time** = the chance a case sails through with no rework ·
  **lost to rework** = hands-on hours spent redoing work each day.
- **Bottleneck** = a genuinely hot step (load ≥ 80 %) if there is one, else the longest queue —
  one flag, consistent across the map, the stats and exports.

## Roadmap (not yet built)

- Split % on branches, side-by-side segment comparison, turnaround trend / cumulative flow diagram.
- SharePoint auto-refresh via Power Automate, optional Power BI companion.
