# Geo ML Platform — Two-Pager

---

## Page 1 — The Platform

### What it is

A **decision-making platform** for land. It lets a domain user go from data to a defensible spatio-temporal *decision* — what to insure, what to pay, where to send a surveyor — without building any of the infrastructure between. The platform ships a curated catalog of generic features (admin vector layers, satellite indices, weather, soil, DEM), accepts the user's labels and optionally their code, and standardizes the rest of the pipeline — data joining, splitting, training, evaluation, provenance — so the only thing left for the customer is the call itself.

The framing matters: we are not another ML tool or EO viewer. ML is the means; the decision is the point. We commoditize the two layers beneath the decision (data engineering, statistics/ML) and leave the apex — the judgment, the accountability, the regulator to satisfy — with the customer, where it belongs.

The mental model is closer to a managed feature store + training service for geo than to a hosted notebook product. The notebook surface exists, but the primary experience is structured: pick features, upload labels, pick a problem formulation, get a decision-ready output with full lineage.

### Why this, why now

Three things have converged:

- **Open geospatial data for India has matured.** Admin and vector layers (Survey of India, ECI, Census, FSI), satellite archives (Sentinel, Landsat, MODIS), and government rasters (NRSC crop masks, IMD gridded weather) are all accessible — but stitching them is still a multi-week engineering exercise for every team that needs them.
- **The managed geo-ML platforms that exist today are built for global, foreign-hosted workloads.** Indian buyers want sovereignty (data resident in India), predictable INR pricing, no egress to overseas clouds, and Indian datasets pre-bundled. Current options force them to give up at least one of these.
- **Regulated buyers need provenance.** Insurers under YES-TECH, govts under e-governance audits, multilaterals under MRV frameworks — all need to explain how a number was produced. Most ML platforms ship models; few ship lineage.

### The three primitives

| Primitive | What the user brings | What the platform provides |
|---|---|---|
| Features | Nothing in the common path | Curated three-tier catalog: static vector base, open dynamic rasters and aggregates, premium feeds |
| Labels | Points, polygons, tables, or rasters | Validation, schema inference, spatial join to features, versioning, holdout splits |
| Code | Optional — Python via SDK or notebook | Distributed compute on Dask/K8s, caching, lineage, scheduling |

### Problem formulations

Above the primitives sits a small set of standardized formulations — spatio-temporal regression, parcel or pixel classification, change and anomaly detection, forecasting. Most real workflows reduce to one of these. Standardizing the formulation lets us standardize the plumbing without limiting the modeler.

### Architecture

> **[Diagram slot — Architecture]**
> *Style reference: a stacked-layer system view in the idiom of Figure 1 of the Trinity paper (arXiv 2106.11756). Data sources at the bottom, the feature catalog and transform engine in the middle, problem formulation and serving at the top, with BYO Labels and BYO Code entering from the side. Mark the three feature tiers (A/B/C), the label management subsystem, the formulation and compute layer, and the lineage graph that connects every output back to its inputs.*

### What makes it defensible

- **A curated Indian features catalog** that compounds with every customer engagement — open-data tier modeled on the [india-geodata](https://yashveeeeeeer.github.io/india-geodata/) collection, extended with pre-computed satellite indices and weather aggregates.
- **Premium-feed reuse economics.** One high-resolution aerial strip serves multiple customers and multiple use cases. This is the gross-margin story.
- **First-class provenance.** Every output carries a lineage manifest tying back to source features, label versions, code commits, and (where relevant) the regulatory SOP section that justified the modeling choice.
- **Sovereignty.** Indian-region hosting (Yotta, CtrlS, AWS Mumbai), no data egress, on-prem option for government workloads.

### Customer surface

| Customer type | What they buy |
|---|---|
| Private insurers | Yield, loss, parametric index pipelines on their portfolio |
| Agritech companies | Feature backbone + training compute, BYO models |
| State governments | UPAHAR-style RFP execution with audit-grade outputs |
| Hedge funds, commodities | Production estimates and supply signals |
| Multilaterals (WB, IMF, UN) | Reproducible methodology bundles for development indicators |

The platform shape is constant across these. The demo proves it on one; the rest are pull-led expansion.

### Scope discipline for v1

- **Vector labels only.** Tabular targets joined to vector geometries — points, polygons, parcels. Covers regression and classification over administrative or parcel units. Enough for the insurance demo and for most agritech and govt workflows.
- **Raster labels (segmentation masks) deferred to v2.** Damage maps, land cover, and CV-style workflows need raster handling — same primitives, roughly 3x the engineering. Listed in the roadmap so customers see where it goes.
- One state (Chhattisgarh), one premium aerial strip, three reference pipelines, single-tenant.

---

## Page 2 — The Demo: Insurance

### The wedge

The 45-day demo proves the platform on a hard, regulated, well-funded use case: a private Indian insurer running YES-TECH-aligned crop pipelines on our infrastructure instead of their current mix — in-house attempts, NRSC engagements, or imported tools running on overseas cloud.

I'm picking insurance because the buyer has budget, the pain is acute, and the regulatory frame (YES-TECH, WINDS) forces investment in technology they don't have internally. Warm intros are in hand. The demo doubles as a credible reference for adjacent buyers (agritech, govts) without rebuilding anything.

### The customer profile

A mid-tier private general insurer — ICICI Lombard, HDFC Ergo, Bajaj Allianz, Tata AIG, or Reliance General — running either:

- A PMFBY portfolio (YES-TECH compliance pressure), or
- A parametric weather or yield-indexed product portfolio (differentiation pressure).

I'm biasing toward parametric products in the first conversation: shorter sales cycle, value-led not compliance-led, no procurement gauntlet.

### The three pipelines shown

Each is an instance of a platform primitive — not bespoke code.

1. **IU-level yield estimate** — `RegressionTask` over a kharif paddy feature bundle (NDVI / EVI / LSWI 8-day composites + IMD weather + soil tier-A) with an ML ensemble head trained on CCE points the insurer provides. YES-TECH SOP-aligned.
2. **Parcel-level loss assessment** — `ChangeDetection` over the Pléiades strip and Sentinel-2 stack, classifying parcels into no / partial / severe / failure damage categories around an event window.
3. **CHF-style parametric index** — `WeightedComposite` over NDVI + LSWI + rainfall + SAR backscatter with entropy-derived weights. The insurer prices a parametric product against the index.

All three share features. The premium Pléiades strip is reused across pipelines (2) and (3). Each output ships with a provenance bundle that cites the YES-TECH SOP sections justifying the methodology — surfaced through a doc2llm knowledge pack queryable from the report.

### Demo flow

> **[Diagram slot — Demo flow]**
> *Style reference: a horizontal data → compute → output flow in the visual idiom common to modern geospatial platform landing pages. Left column: insurer uploads CCE labels and portfolio polygons. Middle column: platform joins them to the pre-computed Chhattisgarh feature bundle, then runs the three pipelines in parallel on Dask/K8s. Right column: outputs render as PDF report, interactive map, and JSON API; every output has a "view methodology" link that opens the cited SOP sections. Annotate the single Pléiades strip reused across pipelines (2) and (3).*

### What the insurer's analyst sees

- A web app with three forms — one per pipeline — with dropdowns for district, season, crop, event window.
- A label upload screen with validation feedback.
- Reports as PDF and Excel, a map view in the browser, a JSON API for downstream integration.
- A "view methodology" link on every output that opens the YES-TECH SOP at the cited section.
- A gated notebook environment for the insurer's data science team to extend the pipelines.

### 45-day plan

| Week | Build | Outside-build |
|---|---|---|
| 1 | STAC catalog on Yotta, Sentinel-2 and Landsat ingestion for Chhattisgarh | Confirm insurer contact, scope conversation |
| 2 | Tier A vector layers (india-geodata), Tier B index pre-computation | Procure Pléiades strip for chosen tehsil |
| 3 | Regression pipeline (yield), label upload + validation | First insurer call — confirm CCE data shape |
| 4 | Change-detection pipeline (loss), CHF composite pipeline | Begin shaping the demo narrative |
| 5 | Web app, report rendering, provenance manifests | Internal dry-run with a friendly reviewer |
| 6 | doc2llm SOP integration, polish, cost comparison sheet | First insurer demo |
| Buffer | Bug fixes, second insurer demo | Outreach to customers 2 and 3 |

Build is roughly 30 days; customer conversations are the remaining 15. If I build for the full 45 and start selling on day 46, the demo goes stale before it gets seen.

### What we learn from the demo

- **Is the cost wedge real?** A side-by-side comparison: our stack versus the insurer's current or candidate alternative for the same workload. If we're not at 40–60% of the comparable cost, the price story is weak and we need a different angle.
- **Does the provenance story matter?** I think it does for regulated buyers, but the demo is where I find out whether it's a nice-to-have or a "we will sign for this."
- **Which pipeline lands hardest?** Yield, loss, and CHF appeal to different teams inside the insurer. The one that gets a buying signal tells us which adjacent customer to pursue next.

### What's deliberately not in the demo

- Multi-tenancy, billing, SLAs, self-serve onboarding.
- Raster labels and segmentation workflows (in the platform roadmap, not built).
- Custom pipeline registration via SDK (notebook BYO code only).
- Anything beyond Chhattisgarh and the three reference pipelines.

The platform vision is what gets the second meeting. The demo is what closes the first one.
