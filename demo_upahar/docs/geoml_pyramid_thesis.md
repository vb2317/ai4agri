# Geo ML Platform — The Pyramid Thesis

We are a **decision-making platform**. Everything below is about one move: take the two layers of work that sit *beneath* a decision and commoditize them so completely that the customer spends all their energy on the decision itself.

## The pyramid, recapped

Data science is a pyramid with three layers: data engineering at the base, statistics in the middle, and at the top the layer I used to call domain knowledge — but the sharpest name for it is *the decision*. Each rests on the one below. I've written about this separately ([data_science_pyramid.md](./data_science_pyramid.md)) — the short version is that the base is what compounds, the middle is what protects you from fooling yourself, and the top is the call that makes the work matter and that only the customer can make.

The order has held across every team I've worked on. What's changed in the last few years is *how much of each layer can be commoditized*.

## What's commoditizing, and what isn't

**The base — data engineering — is increasingly automatable with good software engineering.** Modern data tooling (STAC catalogs, COG / Parquet / GeoParquet formats, dbt-style pipelines, lineage tools) has compressed work that used to take quarters into work that takes weeks. The boring parts — schema management, freshness checks, idempotent jobs, lineage tracking — can be built once and reused indefinitely. A team that adopts the right primitives stops rebuilding this layer for every project.

**The middle — statistics and ML — has been transformed by AI.** Foundation models, AutoML, embedding-based retrieval, and standardized training loops have absorbed enormous amounts of what used to be bespoke modeling work. A regression head over pre-computed features is now a thirty-line script. A change-detection routine across a Sentinel-2 stack is a library call. The marginal cost of trying a model has collapsed; the modeler's value-add has moved upstream (problem framing) and downstream (interpretation).

**The top — the decision — has not moved.** This is by design. The decision is irreducibly specific to the problem, the customer, the regulatory environment, the geography, the crop, the failure mode. A model can rank a claim's risk; only the underwriter decides to pay it. A pipeline can produce a kharif paddy estimate; only the state department decides what it means for their procurement plan. The top of the pyramid is where the judgment — and the accountability — lives, and it always will. That is why we frame the product as a decision-making platform, not an ML platform: ML is the means; the decision is the point.

## The product thesis

We provide the two layers beneath the decision. The customer makes the decision.

```
              [   The decision   ]      ← customer makes
                                          (their labels, their framing, their call)

          [        Statistics        ]   ← platform provides
                                          (formulations, auto-training, eval, provenance)

    [         Data engineering          ] ← platform provides
                                            (features catalog, compute, lineage)
```

This is the cleanest way to describe the platform. Not "another ML tool." Not "yet another EO platform." It is a decision-making platform: *we take the two layers that have become commoditizable, and we commoditize them so completely for the geo domain that you can focus all your energy on the decision that actually requires you*.

> **[Diagram slot — Pyramid view of the platform]**
> *A clean three-tier pyramid with the bottom two layers shaded as "platform-provided" and the apex labeled "the decision — customer's." Inside each layer, list the concrete things the platform delivers (features catalog, formulations, compute, lineage) versus what the customer brings to the decision (labels, framing, the call). The visual should make immediately obvious that the platform shrinks two layers to zero customer-effort while leaving the decision untouched.*

## What each layer looks like in the platform

### Data engineering — the features catalog

A three-tier catalog of geo features ready to be joined to anything:

- **Tier A** — static vector base: admin boundaries, electoral, census, forest, soil, watershed, infrastructure. Modeled on the [india-geodata](https://yashveeeeeeer.github.io/india-geodata/) curation discipline.
- **Tier B** — open dynamic rasters and aggregates: NDVI / EVI / SAVI / LSWI / NDWI / fAPAR composites, IMD gridded weather, SMAP soil moisture, DEM derivatives — pre-computed across India, refreshed on schedule.
- **Tier C** — premium feeds: high-resolution aerial (Pléiades Neo, SkySat), high-cadence PlanetScope, SAR backscatter — pooled across customers, amortized across use cases.

All exposed through a single STAC + Parquet interface. No customer ever has to wrangle a CRS, build a tile cache, or write a Sentinel-2 ingestion loop. That work has already been done.

### Statistics and ML — the problem formulations

A small set of standardized formulations covers most geo workflows:

- Spatio-temporal regression (yield, biomass, density, price)
- Parcel or pixel classification (crop type, land cover, damage class)
- Change and anomaly detection (flood extent, fire scar, stress, encroachment)
- Forecasting (yield, rainfall, demand)

Each formulation has a canonical data shape, canonical evaluation metrics, and canonical output schema. The customer picks a formulation, uploads labels, picks a feature bundle, and the platform handles spatial-holdout splits, baseline training, evaluation, and provenance manifest generation. AI absorbs the parts of stats and ML work that no longer benefit from being bespoke.

The notebook surface exists for when the customer wants to extend — write a custom model, add a feature, run a distributed job. The contract is: anything you build that uses platform features and emits a standard output manifest gets free distributed compute, free caching, free lineage.

### The decision — what the customer brings

This is the layer we deliberately do not own — the decision and everything that feeds the customer's judgment of it:

- **Their labels.** CCE points, claim histories, parcel polygons, ground-truth surveys, expert annotations. Versioned, validated, and joined to features by the platform — but always owned by the customer.
- **Their code.** When the standard formulations don't fit, the customer extends via SDK or notebook. Custom features, custom models, custom evaluation logic.
- **Their framing.** What question to ask, which loss to optimize, what counts as a good answer, what regulator needs to be satisfied. This is the layer where their competitive advantage lives.

The platform's job is to make this the only layer the customer's best people have to think about.

## Why this wins

Three things follow from the framing:

1. **Customers stop wasting senior talent on plumbing.** Today the typical Indian insurer's data team spends most of its cycles on ingestion, cleaning, format conversion, and re-implementing the same indices their last project used. A platform that takes those two layers off their plate frees up their domain experts to actually do domain work.

2. **The platform compounds across customers in a way bespoke work cannot.** Every customer's investment in the bottom two layers benefits the next customer. A new feature added for the insurance demo becomes available to the agritech customer. A new formulation tested with a state govt becomes one the hedge fund can use. The top layer — domain knowledge — stays customer-specific by design, and that's correct.

3. **The decision frame defends against the "yet another platform" critique.** Buyers in this space have seen many vendors pitch undifferentiated ML platforms. Positioning around the decision sharpens the pitch: *we are not your data science team, and we are not another model vendor. We are the infrastructure beneath your decisions — we make them fast, scaled, and defensible. You make the call that was always yours to make.*

## How the insurance demo proves it

The 45-day demo described in the [two-pager](./geoml_platform_twopager.md) is a concrete instance of this thesis:

- **Data engineering layer** — STAC catalog on Indian-region hosting, Chhattisgarh feature bundle pre-computed, one Pléiades strip ingested. The insurer touches none of this.
- **Statistics / ML layer** — three pipelines (yield, loss, CHF) built as instances of standard formulations. The insurer picks parameters; doesn't write modeling code.
- **The decision layer** — the insurer brings their CCE points, their portfolio polygons, their event windows, their underwriting framing, and the calls themselves. They tell us what "severe damage" means for *their* policy and decide which parcels to pay; the platform runs the change-detection that surfaces those parcels and arms the decision.

At the end of the demo, the insurer's analyst has produced a regulator-grade output without writing a join, ingesting a Sentinel-2 tile, or implementing an ensemble model. The work she *did* do — define the question, supply the ground truth, interpret the result — is exactly the work only she could do.

## Scope discipline for v1

The pyramid framing doesn't change what we build first; it sharpens why:

- **Vector labels only** in v1 — enough to demonstrate the BYO-labels surface across regression and classification formulations. Raster labels are in the roadmap for v2; the principle (customer brings the labels, platform handles the join and training) is the same.
- **Three reference pipelines** in v1 — yield, loss, CHF — chosen because they collectively exercise both feature tiers, both label types we support, and the provenance surface that regulated buyers need.
- **One state, one premium strip, single-tenant** for the demo. The platform shape is general; the demo scope is deliberately narrow.

## The one-line version

The insurance demo is the proof. The pyramid is the thesis. Together they describe a decision-making platform: it takes the parts of geo data science that have become commoditizable and commoditizes them — leaving the customer's best people free to make the only call that was ever uniquely theirs.
