# Before the Demo — The Story the Deck Tells

*Precursor to the deck. The deck is shown first, the live demo second. This doc is the narrative the slides are built from: what we're showing, why it's framed this way, and how the three parts of the demo each stand on a different idea in machine learning. It ends by handing off to the demo.*

The one thing to hold through the whole deck: **we are a decision-making platform.** Not an ML tool, not an imagery viewer. The output that matters is a *decision* — what to insure, what to pay, where to send a surveyor — made faster, at scale, and defensibly. Machine learning is the means; the decision is the end.

The shape is deliberate: **What → Why → How**, then the demo proves the How.

---

## 1. What

An insurer makes thousands of decisions a season — *which fields to insure, at what premium, which claims to pay and how much, which fields are worth a surveyor's visit.* Today those decisions rest on thin, slow, disputable evidence: sparse ground samples, manual surveys, numbers nobody can fully reconstruct.

We've built a decision-making platform for that work, and an insurer-facing demo on top of it. The demo is an agriculture command surface for a Madhya Pradesh crop insurer: you draw the insured fields from satellite imagery, read each field's crop and risk across the season, and review the fields the model is unsure about against fields that look like them. Every screen is a decision being armed.

The durable claim underneath: **a domain user goes from data to a defensible decision without building any of the infrastructure between.** The insurer never wrangles a coordinate system, ingests a satellite tile, or hand-implements a model. They bring the part that's actually theirs — what the policy covers, what "loss" means, which fields matter — and make the call. We arm the call.

One line: *we don't make the insurer's decisions; we make them fast, scaled, and auditable.*

---

## 2. Why

### The pyramid — and where the decision sits

Across fifteen years of data work the same shape has held. Data science is a pyramid:

```
              [ The decision ]          ← the call only the customer can make
          [        Statistics        ]   ← signal vs. noise, honest uncertainty
    [         Data engineering          ] ← reliable, fresh, reproducible data
```

The base is what compounds. The middle is what keeps you from fooling yourself. The apex is the part that was ever uniquely the customer's — and the sharpest way to name it is not "domain knowledge" in the abstract but *the decision*: which question to ask, which answer would change what they do. Most teams build this inverted and wonder why nothing compounds.

### What changed

What's new is *how much of each layer can be commoditized*:

- **The base — data engineering — is now mostly a software problem.** STAC catalogs, cloud-optimized formats, scheduled pipelines, lineage. Build it once, reuse it forever.
- **The middle — statistics and ML — has been reshaped by AI.** A classifier over pre-computed features is a short script. Change detection over a satellite stack is a library call. The marginal cost of trying a model has collapsed.
- **The apex — the decision — has not moved, and won't.** A model can rank a claim's risk; only the underwriter decides to pay it. No tooling replaces the judgment, the accountability, or the regulator who has to be satisfied.

So the product thesis is one sentence: **we commoditize the two layers beneath the decision so completely that the customer spends all their energy on the decision itself.**

### Why now

Three things converged: open geospatial data for India matured; foundation models, embeddings, and AutoML collapsed the cost of the middle layer; and the buyers whose decisions carry the most weight — regulated buyers — now demand two things from any system they decide on.

- **Provenance** — the full, reconstructable trail behind a decision. For any output ("severe loss on this parcel," "2.1 t/ha for this unit"), you can trace back to which imagery, which weather, which label version, which model and code commit, which methodology clause justified each choice. This matters *because decisions get challenged*: a farmer disputes a payout, an auditor samples ten claims, a regulator asks why the index was weighted that way. A decision-making platform has to defend its decisions — so the trail is first-class, not retrofitted. Most ML platforms ship the answer; few ship the trail.
- **Sovereignty** — the data and compute stay inside India (Indian-region cloud or on-prem, no egress). Government data often can't legally leave; procurement increasingly requires it; and buyers are wary of sending portfolio data overseas. Global platforms are foreign-hosted by default and fail this test out of the box.

Regulation creates the budget; provenance and sovereignty are exactly the two things the incumbent, foreign, model-only tools are worst at. That's a stronger *why now* than "AI is hot": mandated demand, pointed at a gap competitors structurally can't fill.

> **[Diagram slot — the pyramid]** Three-tier pyramid. Bottom two layers shaded "platform-provided," apex labeled "the decision — yours." The visual should make obvious that two layers shrink to near-zero customer effort while the decision is left untouched.

---

## 3. How — three stepping stones, three decisions

Here's the part that earns the demo. The work splits into three machine-learning ideas. None is exotic; the point is that each is now a *building block* rather than a research project, each maps to a layer of the pyramid, and **each answers a specific decision the insurer has to make.** The demo walks through them in order.

### Stepping stone 1 — Human-in-the-loop with a foundation model

**The decision it serves:** *What is my exposure?* — which fields are actually in the book.

**The idea.** Before you can decide anything about a field, you need the field — its boundary. Hand-digitizing thousands of parcels is the slow, expensive work that quietly kills these projects. Instead, a segmentation foundation model (SAM) proposes every field boundary in the image; a person keeps the good ones. The machine traces; the human decides what's in.

**Why it matters.** This is how the portfolio gets defined cheaply. Boundaries are the customer's to own, but owning them shouldn't mean drawing them by hand. Human-in-the-loop is the bridge from "we have imagery" to "we have a book of insured fields we trust."

**In the demo.** *Field Boundaries.* Tap **Detect fields**; the model outlines every field in view, each with a confidence; you click the ones that matter and save them. Boundaries out as plain GeoJSON, ready for analysis.

### Stepping stone 2 — Supervised learning

**The decision it serves:** *Underwrite, price, or pay?* — crop, loss, payout.

**The idea.** The familiar one. Given labeled examples — this field was soybean, that one was stressed — and a season of satellite features, fit a model that predicts crop type and stress for fields you haven't labeled, *with a confidence on every call.*

**Why it matters.** This is the middle of the pyramid feeding the decision directly: features become an underwriting or claims input, with the uncertainty made explicit so a human can weigh it. It's a standard formulation now — parcel classification over temporal features — not bespoke code. The platform handles the holdout split, the evaluation, the provenance; the insurer brings the labels and makes the call.

**In the demo.** *Crop & Risk.* Run analysis on the saved fields and each fills in: crop type, a confidence bar, stress level, expected yield. The honest framing is on the surface — confidence, not certainty.

### Stepping stone 3 — Unsupervised learning, via embeddings search

**The decision it serves:** *Where do I spend scarce human attention?* — which fields to investigate versus auto-clear.

**The idea.** Labels are expensive and never cover the whole portfolio. Embeddings sidestep that: every patch of imagery becomes a vector, and similar-looking fields land near each other — no labels required. So you can ask, "show me fields that look like this flagged one," and triage at the scale of a portfolio instead of a sample.

**Why it matters.** This is how a few labels stretch across thousands of fields, and how a human reviewer stays in the loop without re-labeling everything. It turns "we can't look at every field" into "we look at the right ones." And it closes the cycle: the fields the model is least sure about are exactly the ones worth a human look — and a new label — which feeds back into stone 1.

**In the demo.** *Similar Field Review.* For a flagged field, the platform surfaces the closest-looking fields from an indexed library; the analyst confirms or dismisses. (The indexed library here is real Sentinel-2 over France — the technique is the point; the geography is incidental.)

### The three together — a decision loop

They form a loop, not a list:

```
   define exposure (HITL + SAM)  →  assess each field (supervised)  →  triage (embeddings search)
   "what's in the book"             "crop / loss / payout"             "who gets a human look"
                ↑___________________________________________________________|
                          the uncertain fields become the next label
```

That loop is the platform's operating model in miniature, and it's exactly the sequence the demo follows.

> **[Diagram slot — the decision loop]** Three nodes in a cycle, each tagged with its demo surface (Field Boundaries / Crop & Risk / Similar Field Review), its ML idea, and the decision it serves.

---

## 4. The demo is the proof

Each part of the demo is a concrete instance of the thesis — a decision being armed:

| Demo part | ML idea | Decision it serves |
|---|---|---|
| Field Boundaries (SAM) | Human-in-the-loop + foundation model | *What is my exposure?* |
| Crop & Risk | Supervised learning | *Underwrite / price / pay?* |
| Similar Field Review | Unsupervised / embeddings | *Where do I spend scarce attention?* |

By the end, the analyst has gone from raw imagery to a reviewed, insured portfolio and a set of defensible calls — without writing a join, ingesting a tile, or implementing a model. The work she *did* do — decide which fields matter, judge the predictions, confirm the look-alikes — is the work only she can do. That's the pyramid, proven on one screen: we armed every decision; she made them.

A note on honesty, because the room will be skeptical: the current models are demonstrators, not production claims. The confidence numbers, the validation, the "this is illustrative" labels stay visible. The point of the demo is the *shape* of the decision workflow and the fact that the plumbing is gone — not a benchmark we're not ready to defend.

### One positioning discipline

Lead with the decisions; close with the platform. Decisions are why the room leans in — insurers buy better loss ratios and faster claims, not ML formulations. But the platform underneath — the Indian features catalog, the provenance, the sovereignty — is *why the decisions are trustworthy and the margins compound*, and it's the part competitors can't copy. Decisions get the first meeting; the infrastructure is why it's defensible and yours.

---

## 5. Suggested deck flow

The slides fall out of the sections above. A tight version:

1. **Title** — "a decision-making platform for land," in one line.
2. **The decisions** — the calls an insurer makes every season, on thin evidence today. (Sets the stakes before any tech.)
3. **What you'll see** — one sentence per demo part, each named as the decision it serves.
4. **The pyramid** — three layers; the apex is *the decision*, and it's yours.
5. **What's commoditizing** — base = software, middle = AI, apex = the decision, unchanged.
6. **The thesis** — we commoditize the two layers beneath the decision so you spend everything on the decision.
7. **Why now** — open data matured, modeling cost collapsed, regulated buyers demand provenance + sovereignty (and that's where incumbents are weakest).
8. **How: stepping stone 1** — HITL + SAM → *what's my exposure?*
9. **How: stepping stone 2** — supervised learning → *underwrite / pay?*
10. **How: stepping stone 3** — embeddings search → *where to spend attention?*
11. **The decision loop** — the three as a cycle.
12. **Hand-off** — "Now let me show you." → live demo.
13. *(After the demo)* **What this proves** — the proof table; we armed the decisions, she made them; the honest caveat.

Keep slides 8–10 visually parallel — same layout, three times: *the decision → the idea → what you're about to see* — so the audience feels the rhythm, then watches it happen.
