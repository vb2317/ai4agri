# Demo spec

*The artifact we're building in the 4-week sprint — what it is, what it isn't, and where the labels come from.*

---

## Shape

One AOI. One narrative. One screen.

**AOI:** a 5×5 km patch in Chhattisgarh — Rajnandgaon, Mahasamund, or Bastar — paddy-dominant, with a public flood or drought event in the last two seasons we can anchor the story to.

**Data:** Sentinel-2 + Sentinel-1 time series across one Kharif and one Rabi. Real parcel polygons from Bhuvan / Chhattisgarh DLR if accessible; auto-segmented from a clear-day composite otherwise.

**Screen:** map on the left, parcel inspector on the right, time slider on the bottom.

---

## The two-minute walkthrough

1. **Open the AOI.** Parcel polygons over a recent Sentinel-2 RGB. Each parcel coloured by classified crop, opacity modulated by confidence. *"This is what one block of Rajnandgaon looks like to the system on Oct 15, 2024."*
2. **Click a parcel.** Inspector opens — crop class, confidence, area, NDVI time series, SAR-derived moisture signal where optical was cloudy. *"This parcel: paddy, 0.87 confidence, 1.2 ha. Here's its season."*
3. **Drag the slider to early September.** NDVI curve highlights the healthy inflection. Drag forward — NDVI drops mid-September. Map shifts to Sentinel-1 backscatter showing standing water across the area for two weeks. *"This is what the flood looked like to satellites, before anyone filed a claim."*
4. **Click "explain this parcel."** A side card shows the model's reasoning trace — phenology fit, NDVI deviation from cohort, SAR water signal, confidence breakdown. Plain language, not a confusion matrix. *"This is what the system would tell a claims officer to look at."*
5. **Click "API view."** A code panel shows the GeoJSON + REST call that produces the same answer programmatically. *"This is what a trader or insurer would integrate against."*
6. **Click the "RFP traceability" tab.** A sidebar maps every capability shown back to a Section 12 clause. *"And this is how every piece of what you just saw answers a specific line of the Chhattisgarh tender."*

Three minutes if I'm crisp.

---

## What gets built

Four layers, ordered by what already exists:

1. **The model.** Reuse the AI4Agri Subtask 1 + Subtask 2 work. Pixel-level ordinal output and crop classification are already what we're tuning for the competition. Repackage as a per-parcel aggregator with confidence.
2. **The data.** One AOI, pulled from Sentinel Hub or Earth Engine. ~12 Kharif dates, ~10 Rabi dates. SAR for known cloud-cover weeks. Parcel polygons via Bhuvan / state DLR or SAM-style auto-segmentation. **Budget half the sprint here** — it's the most likely time sink.
3. **The UI.** Build on the existing `app/` scaffold. MapLibre or Leaflet, parcel inspector, time slider, NDVI sparkline, "explain" card, "API" code panel, "RFP" sidebar. Clarity over polish.
4. **The narrative wrapper.** A 5-page leave-behind and a talk track. The talk track is the same Tuesday-morning-in-Raipur story from the deck, acted out in the live app.

---

## What it explicitly is not

- Not multi-state. One AOI. Resist scope creep.
- Not real-time. Pre-baked tiles, pre-run inference. The "live" feel is a UI illusion.
- Not production accuracy. Header reads "demonstration; production accuracy requires licensed imagery and operational GT."
- Not a mobile app. Web only.
- Not a confusion-matrix dashboard. One matrix on a methodology page is enough.

---

## Three audiences, one demo

Same screens, different opening sentence in the talk track:

| Audience | What they should remember | What they click on |
|---|---|---|
| State agri secretary | "I could see crop loss before a claim is filed" | Flood time-slider, explain card |
| Commodity trader | "I could see acreage two weeks before the bulletin" | Acreage summary, API panel |
| Insurer / reinsurer | "I could auto-settle PMFBY at scale" | Confidence panel, RFP traceability tab |

That's the whole personalization.

---

## Where the labels come from

This is the hardest part of the demo and the place we'll be most tempted to hand-wave. Two distinct label problems, two distinct answers.

### Problem 1 — labels for the technical proof

The "show me the model actually works" piece doesn't have to be Chhattisgarh. AI4Agri's competition provides labeled training and test patches for both subtasks. Labels are clean, public, free.

**Use the competition AOI for the methodology slide and the confusion matrix.** This is what gets shown to a sophisticated reviewer who wants numbers.

### Problem 2 — labels for the narrative AOI in Chhattisgarh

The Tuesday-morning story needs a Chhattisgarh AOI where nobody has handed us labels. Four layers, in increasing effort:

**Layer 1 — Weak global / national labels (free, day one)**
- ESA **WorldCereal** — global crop maps including India, ~10 m. Coarse but real.
- **Bhuvan / NRSC** seasonal crop maps — ISRO publishes these. Mediocre at parcel level, useful as priors.
- **Dynamic World / WorldCover** — for cropland masks.
- **OSM `landuse=farmland`** — cropland-vs-not only.

Rough per-pixel label across the AOI in an afternoon. Not parcel-grade, not crop-specific enough on its own.

**Layer 2 — Phenology rules (one week, surprisingly powerful)**
Crops have signature time-series:
- **Paddy:** SAR backscatter drop + NDWI spike during transplanting (standing water), then rapid NDVI rise. Distinctive signature in Chhattisgarh; rule-labels paddy with 80%+ accuracy alone.
- **Wheat / Rabi:** different phenological window, different NDVI shape.
- **Fallow / failed:** flat NDVI.
- **Sugarcane:** long season, no Kharif harvest signal.

Phenology rules turn ~60–70% of parcels into rule-labeled training data with stated confidence. The remaining 30–40% are the hard cases — exactly the ones a real GT survey would target.

**Layer 3 — Manual visual inspection (one weekend)**
For 150–300 parcels, open Google Earth high-res historical imagery, eyeball the crop, label by hand. This becomes the **held-out validation set** — not enough to train, enough to compute a real (small) confusion matrix and not lie.

**Layer 4 — Optional DIY ground truth trip (one weekend, ~₹30K)**
If we want field photos in the demo for credibility — and we probably do for the state-secretary audience — drive to the AOI, two people, rented car, KoboCollect or ODK on a phone. Collect 200–400 geotagged photos with crop type and growth stage. Buys us:
- Real photos in the parcel inspector
- A defensible "we did fieldwork" story
- A second small validation set

Not production GT. But the difference between a demo someone trusts and one they don't.

### Label provenance is part of the UI

Every parcel in the demo gets a label-provenance tag visible in the inspector:

- 🛰️ *Rule-labeled* (phenology match)
- 👁️ *Visually verified* (manual inspection)
- 📍 *Field-verified* (DIY GT photo)
- ❓ *Inferred only* (model prediction without label support)

When the state secretary clicks a parcel, they see where the label evidence came from. The demo tells the truth about its own foundations. That's the credibility move most teams skip.

### The honest framing

For production this label stack would not be enough. The RFP specifies 1–2% stratified GT for a reason; we can't fake that in four weeks.

For a demo whose purpose is to show capability and start a pilot conversation, the four-layer stack is defensible, transparent, and reproducible. The pitch becomes:

> *"This is what we can show you in four weeks with public data and one weekend of fieldwork. Imagine what we can show you with your GT operation behind us."*

That framing makes the GT operation **the buyer's contribution**, not our cost center. Which is exactly where we want it.

---

## Four-week sprint plan

**Week 1 — Data and labels**
- D1–2: Download WorldCereal + Bhuvan + Sentinel-2/1 stack for chosen AOI
- D3–5: Write phenology rules (paddy water signature first)
- Weekend: 150–200 manual visual labels for held-out set

**Week 2 — Model and inference**
- Repackage competition model for parcel-level aggregation with confidence
- Run inference across full AOI for all dates
- Build the rule-vs-model-vs-visual confusion comparison
- Pre-bake tiles

**Week 3 — UI**
- Map, parcel inspector, time slider, NDVI chart
- Explain card, API view, RFP traceability sidebar
- Label-provenance tags
- Optional: weekend GT trip if we're doing Layer 4

**Week 4 — Story + polish**
- 5-page leave-behind
- Talk track per audience (state / trader / insurer)
- Dry-run the demo five times
- Deploy somewhere shareable (Vercel / Render / Fly)

---

## What to flag honestly when showing it

A sophisticated state buyer will ask: *"show me a different district I didn't pick."* We won't have that. The honest answer:

> *"The methodology generalizes. The pilot is where we prove it on your district. Four weeks for the demo, one season for the pilot."*

That's true, and it forces a real next conversation. Feature, not bug.

---

## What this demo serves, regardless of company outcome

Even if no company emerges, the demo is:

- The **technical artifact** that restates my professional seriousness as I enter the India market.
- The **State Overflow case study** — applied statistics, label provenance, measurement under uncertainty in a real domain.
- The **conversation opener** for the customer-discovery interviews (state secretaries, traders, insurers) that I want to do anyway.
- The **portfolio piece** for advisor / board / licensing conversations with Cropin, SatSure, RMSI.

It serves all five shapes from the deck. Build it. Decide on shape after.
