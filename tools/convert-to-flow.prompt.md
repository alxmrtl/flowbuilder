# Convert source material into a Flow Builder map

You are a process-mapping analyst. Read the SOURCE MATERIAL at the end and produce ONE JSON object
that Flow Builder can import to render a value-stream / process map. Flow Builder shows how work
flows to a customer through steps and queues, rates each step for value, and analyses
speed / capacity / quality.

## Task
1. Read every source. Identify the real end-to-end flow: the ordered steps work passes through, who
   does each, where work waits, and how steps connect — including branches, rework loops and
   parallel paths.
2. If several sources are given, RECONCILE them (see "Multiple sources").
3. Emit the flow as ONE JSON object matching the schema below.
4. Obey the FIDELITY setting for how much you may add beyond what the sources literally say.
5. After the JSON, write a short REPORT of what you inferred vs. read verbatim, plus any conflicts.

## Output format (strict)
Return exactly two parts, in order:
1. A single fenced ```json block containing ONLY the model object — valid JSON, no comments, no
   trailing commas. The top-level object IS the model (do not nest it under any key).
2. A "## Report" section in plain markdown (NOT imported).

## FIDELITY = <STRICT | BALANCED | ENRICHED>
- STRICT — Mirror the source exactly. Include only steps, connections, owners, numbers and wording
  that appear in the source. Do NOT infer value ratings, do NOT group, do NOT add notes, do NOT
  rename beyond fixing obvious typos. Omit any field the source doesn't state.
- BALANCED (default) — STRICT, plus: normalise step names to short consistent verb-phrases; merge
  obvious duplicates; add groups where the source clearly signals phases / systems / swimlanes; set
  `classification` only where the source's own language makes it unambiguous
  (e.g. "approval required for compliance" → NNVA). Invent no numbers.
- ENRICHED — BALANCED, plus: infer `classification` for every work step from its purpose (value to
  the customer), add a one-line `valueNote` for each step, and capture stated pains as `comments`.
  Still invent NOTHING numeric and add nothing the source doesn't support — enrichment is
  interpretation of what's present, not fabrication. Flag every inferred item in the Report.

Hard rule (all levels): never fabricate quantitative data (times, volumes, headcount, rework %).
Include a number only if a source states it.

## Schema
```
{
  "name": string,                          // the flow's name
  "settings": {                            // optional
    "timeUnit": "hrs" | "days" | "mins",   // default "hrs" — match the source
    "demand": number,                      // cases arriving per day, if stated
    "bottleneckMode": "absolute",
    "bottleneckThreshold": 0.8
  },
  "nodes": [ {                             // REQUIRED
    "id": string,                          // unique; referenced by edges/groups/comments
    "type": "start" | "end" | "touch" | "wait",
    "label": string,                       // the card title
    "x": number, "y": number,              // logical px — see Layout
    // touch steps:
    "performer": "human" | "bot",          // default human
    "owner": string,                       // team/role (for bots, the bot/system name)
    "tool": "uipath" | "copilot" | "excel",// optional automation tool
    "classification": "VA" | "NNVA" | "NVA",// value rating (see below)
    "valueNote": string,                   // details — what happens in this step
    "stepId": string,                      // data key (usually = id)
    "touchTimeManual": number, "people": number, "hoursPerDay": number,
    "reworkPct": number, "throughputManual": number, "capacityManual": number,
    // wait steps:
    "wip": number,                         // items in the queue
    "waitTimeManual": number               // avg wait
  } ],
  "edges": [ {                             // REQUIRED (may be empty)
    "id": string, "from": nodeId, "to": nodeId,
    "fromSide": "right", "toSide": "left", // default sides; keep unless a branch needs otherwise
    "splitPct": number,                    // branch share (outgoing edges sum ~100)
    "label": string                        // e.g. "rejected", "rework"
  } ],
  "groups": [ { "id": string, "label": string, "members": [nodeId], "collapsed": false,
                "valueNote": string } ],
  "comments": [ {                          // notes/pains
    "id": string,
    "type": "note" | "frustration" | "waste" | "idea",
    "subtype": "waiting"|"rework"|"overprocessing"|"handoffs"|"inventory"|"motion", // waste only
    "text": string, "nodeId": nodeId       // nodeId attaches the note to a step
  } ]
}
```

## Node rules
- Exactly one "start" (the request/trigger that begins the flow). "end" = value delivered to the
  customer (one, or one per terminal branch).
- "touch" = a step where a person or bot actively does work. "wait" = a queue/delay where work sits
  between steps ("waiting for approval", "sits in the inbox", a backlog). Model waiting explicitly —
  queues are first-class and usually alternate with touch steps along the main line.

## Connecting the pieces
- No orphans: every node but start has ≥1 incoming edge; every node but end has ≥1 outgoing edge.
- Branch: split → multiple outgoing edges; set splitPct if proportions are stated; label them.
- Rework: work bounces back → an edge from the later step to the earlier one, labelled "rework".
- Parallel: several edges from one step that later rejoin.

## Grouping (BALANCED / ENRICHED)
Wrap steps that the source organises into a phase / department / system / swimlane in a group. Group
for meaning, only when the source supports it.

## Value rating (classification)
- VA (Valued) — the customer would pay for it / it directly advances their outcome.
- NNVA (Necessary) — required for compliance / risk / control, not valued by the customer directly.
- NVA (Could remove) — adds no value; a candidate to cut (duplicate entry, avoidable waiting, chasing).
Set only per the fidelity rules.

## Numbers (any level — only if stated)
touch: touchTimeManual, people, hoursPerDay, reworkPct; bots: throughputManual / capacityManual.
wait: wip, waitTimeManual. Give every metric-bearing step a stepId (= its id) for later data matching.

## Layout (so it reads before "Tidy")
- Columns advance along the main line: x = 40 + column*300 (snap to nearest 20).
- Main line at y = 220; branch/parallel lanes at y = 220 ± 200. Match a node's column to its distance
  from start; just avoid overlaps — the app's Tidy will perfect the geometry.

## Multiple sources
- Build the UNION of steps; treat differently-worded steps describing the same work as one (note
  merges in the Report).
- Prefer the most authoritative/specific source for names and sequence; prefer whichever source
  gives measured numbers for numeric fields.
- On CONFLICT (order, owner, contradictory numbers) pick the most defensible reading, use it in the
  JSON, and list the conflict in the Report.

## Example (shape reference)
```json
{ "name": "Invoice approval",
  "settings": { "timeUnit": "hrs", "demand": 20 },
  "nodes": [
    { "id":"start","type":"start","label":"Invoice received","x":40,"y":220 },
    { "id":"q1","type":"wait","label":"In AP inbox","stepId":"q1","x":340,"y":220,"wip":12 },
    { "id":"t1","type":"touch","label":"Code & match PO","owner":"AP","stepId":"t1","x":640,"y":220,
      "touchTimeManual":0.5,"people":2,"hoursPerDay":7,"classification":"NNVA",
      "valueNote":"Match invoice to PO and GL code." },
    { "id":"t2","type":"touch","label":"Approve","owner":"Finance","stepId":"t2","x":940,"y":220,
      "touchTimeManual":0.2,"people":1,"hoursPerDay":6,"reworkPct":10,"classification":"NNVA" },
    { "id":"end","type":"end","label":"Paid","x":1240,"y":220 } ],
  "edges": [
    { "id":"e1","from":"start","to":"q1" },
    { "id":"e2","from":"q1","to":"t1" },
    { "id":"e3","from":"t1","to":"t2" },
    { "id":"e4","from":"t2","to":"end","splitPct":90 },
    { "id":"e5","from":"t2","to":"t1","label":"rework","splitPct":10 } ],
  "comments": [
    { "id":"c1","type":"frustration","text":"Approvals stall when Finance is out.","nodeId":"t2" } ] }
```

---
SOURCE MATERIAL (label each source):
<paste transcripts / exported Visio text / Excel rows / job-aids here>
