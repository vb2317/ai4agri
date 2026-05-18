# Agriculture Intelligence Platform

*A discussion deck — what the Chhattisgarh RFP tells us we should build*

VB · for partner review · 2026-05

---

## The RFP is an accidental X-ray

I didn't go looking for this. I read the Chhattisgarh AI4Agri RFP closely because the work we're doing for the competition overlaps with it — and the document quietly turned out to be one of the most useful artifacts I've read this year.

It's not just a tender. It's a state government writing down, in 200 pages, its model of what agricultural intelligence infrastructure should look like in India for the next decade. The asks are specific enough to be a product spec, and the gaps are honest enough to be a market map.

This deck is what I see when I read it as an X-ray rather than as a tender. The question for us is whether we want to do anything about it.

---

## A Tuesday morning in Raipur

Imagine a PMFBY claims officer in the Chhattisgarh agriculture department.

It's late October. The Kharif season's just ended. A village in Bastar has filed a crop-loss claim — 600 hectares of paddy, they say, lost to late-season flooding. The file lands on his desk with a few geo-tagged photos and a hand-drawn map.

He has two weeks to approve, reject, or order a field inspection. Field inspection means a surveyor drives 14 hours, spends three days in the village, and files a report that may or may not match the photos. Approve means the state pays. Reject means a farmer suicide could be in tomorrow's newspaper.

He has no way, today, to look at that 600 hectares and *see* what actually happened week by week through the season.

The product we're talking about gives him that. One screen, parcel-level, temporally resolved, with confidence scores. He makes a decision in twenty minutes instead of three weeks.

There are roughly 200 of him across India's state ag departments. That's the buyer.

---

## What we'd be betting

> The decade-long bet is that **state-grade agricultural intelligence becomes operational infrastructure in India, the way GST or UPI did** — and the company that gets there first with a defensible product owns the layer.
>
> The shorter-horizon bet is that we can build a credible version of that product, in stages, starting from the demo we already have running.

The defensible part of the pitch — and I think this is the honest line — is:

> We can build the remote-sensing intelligence platform.
> Production accuracy and compliance depend on imagery access, GT data, and integration permissions.

That's the seam between what a product company can build and what only a state SI can deliver. We sit on the product side. We partner for the integration side.

---

## What would kill this

I want to say these out loud before we go further:

- **Sales cycle.** Indian state govt procurement runs 12–18 months per state. Three states deep, we've burned three years.
- **Political risk.** A state govt change can kill a contract overnight. Two have happened during PMFBY rollouts already.
- **GT operations cost.** 1–2% of sown area, stratified, photo-verified, 5-day rectification SLAs — this is field operations, not software. It may be the dominant line item.
- **Incumbents waking up.** Cropin, SatSure, RMSI have 80% of the pieces. The day they decide our specific angle is worth defending, they out-resource us.
- **Empanelment paperwork.** MeitY, ISO 27001, data sovereignty, state-specific cloud — the boring stuff that becomes a moat for whoever does it first, and a wall for everyone else.
- **The "everyone says yes, no one pays on time" problem.** State customers love the demo, sign the MoU, then take 18 months to clear the first invoice.

None of these is fatal. Two of them happening simultaneously is.

---

## What would prove it

If three of these are true in 90 days, we keep going:

1. **One state agri secretary asks us, unprompted, for a follow-up meeting** after seeing the demo.
2. **One commercial buyer** (commodity trader, insurer, large agri-lender) **signals willingness to pay for a pilot data feed** — even at five-figure scale.
3. **We can articulate, in one sentence, what we'd own that Cropin or SatSure couldn't replicate in 18 months.** If we can't, we don't have a company; we have a feature.

If only one or two land, we have an interesting consulting practice, not a platform. That's also a fine outcome — but it changes everything about how we'd structure this.

---

## What the RFP is actually asking for

Not an ML model. An **operational intelligence platform** that turns imagery into decisions:

- Crop maps at parcel/village/block/district levels
- Health alerts, acreage estimates, yield forecasts
- Procurement planning (MSP, PACS load, paddy supply)
- Advisories — department, extension, farmer
- Disaster response (flood, drought, crop loss)
- Auditable reports, OGC/API services, mobile app, helpdesk

The ML model is ~10% of the work. The other 90% is data plumbing, ground truth, integration, and operations.

---

## Ten "unique asks" buried in Section 12

1. Compliant multi-date imagery (≤3 m, 5–7 day cadence, 4 crop stages, Kharif + Rabi, SAR fallback)
2. Parcel-level classification with confidence scores, including multi-/intercropping
3. Ground-truth driven model improvement — 1–2% sown area, stratified, 30% held out
4. Defensible accuracy — ≥85% parcel-level, ≥70% on major crops, confusion matrices
5. Crop health & stress monitoring with severity tiers and alerts
6. Acreage, change, and production intelligence
7. Yield + procurement planning tied into MSP/PACS workflows
8. Action layer — advisories for departments, extension officers, farmers
9. Disaster monitoring with drone-satellite hybrid workflows
10. DAC + WebGIS + mobile + APIs + O&M + helpdesk — i.e. a *platform*, not a model

---

## Where this lives competitively

**Closest to our thesis**
Cropin, SatSure, RMSI Cropalytics, MapMyCrop, EOSDA — India-relevant, full-stack-ish, each weak in at least one of: parcel-grade accuracy, government workflow, imagery flexibility.

**Adjacent**
EarthDaily/Geosys, Syngenta Cropwise, BASF xarvio, Trimble, Taranis — strong agronomy or enterprise distribution, less government-platform DNA.

**Infrastructure, not competitors**
Planet, Maxar, Airbus/UP42, Pixxel, Esri, GEE, Microsoft Planetary Computer.

**Privately doing it**
Commodity traders (Cargill, ADM, Bunge, Olam), reinsurers (Swiss Re, Munich Re, AXA Climate), large SIs (TCS, Infosys, Wipro, RMSI). They don't sell it as a product — which is exactly the gap.

---

## The cross-state moat

Per RFP §12.2.2, GT data is a state asset — handed over each season. So **labels can't be our moat**. Three things can be:

1. **The engine.** Models, priors, calibration across agro-ecological zones.
2. **Cross-state aggregation.** Once we have three states under contract, we have the only pan-India parcel-level intelligence layer that's *legal* to aggregate (with the right permissions and anonymization). That's the actual moat.
3. **Boring infrastructure.** MeitY empanelment, ISO 27001, state-cloud certifications. The first time is a tax; from then on it's a wall.

The third is unsexy. It may be the most important.

---

## The staged build

**Demo / proposal (now)**
Same-area imagery · aligned parcel overlays · temporal crop states · ML capability panel · GeoJSON + backend APIs · SAR/NISAR fallback positioning · Section 12 traceability

**Pilot (one district, one season)**
Licensed imagery · real AOI boundaries · GT sample plan · model on real data · validation metrics

**Production**
Imagery procurement pipeline · PostGIS / COG / map services · field mobile workflow · MLOps · integrations (AgriStack, land records, Food Dept, MARKFED, PACS, weather) · O&M + security

Each stage is sellable. We don't need to skip to production to monetize.

---

## Why now

- India's AgriStack, ULPIN, and state-level digital ag pushes are creating real integration surfaces for the first time.
- Sentinel-1/2 are free and mature; Pixxel and NISAR add hyperspectral and SAR depth.
- State governments are issuing RFPs like this one — meaning budget is moving from pilots to operational systems.
- ML for crop classification is no longer the bottleneck. GT pipelines and integration are.

The window is the next 24–36 months before one of the incumbents locks in 3–5 state contracts and becomes the default.

---

## Wild ideas — government

The RFP scopes the obvious. The same engine unlocks things state and central govts can't currently do at all:

- **MSP fraud detection.** Cross-check claimed procurement acreage against actually-cultivated parcels.
- **PM-KISAN / DBT verification.** Does the beneficiary's parcel actually grow anything?
- **Parametric crop insurance.** Auto-settle PMFBY claims from imagery — no surveyor, no political queue.
- **Drought / disaster relief audit.** After the cheque is cut, did relief reach the villages that were actually hit?
- **Land-use reclassification leakage.** Agri land quietly converted to non-agri — stamp duty and GST lost.
- **Encroachment on forest / govt / commons land.** Standing automated layer for revenue and forest depts.
- **Groundwater rights enforcement.** Irrigation extent as a proxy for unmetered borewell extraction.
- **Illegal mining + royalty leakage.** Same engine, mining ministry buyer.
- **Sub-national GDP estimates.** District-level economic data is years stale. Cropping intensity is a near-real-time proxy.
- **State-level carbon MRV.** States making net-zero commitments without measurement infrastructure.

Most of these don't need new tech. They need someone to survive procurement.

---

## Wild ideas — beyond government

Same engine, non-state buyers, higher margins:

- **"India harvest" data feed for traders + hedge funds.** Acreage and yield 2–4 weeks ahead of official numbers.
- **Parcel-level credit scoring.** Lend on three seasons of cropping history, not a CIBIL score the farmer doesn't have.
- **Smallholder carbon MRV.** Per-parcel MRV at $0.50 instead of $50 cracks the offset market.
- **Climate adaptation finance scoring.** Village-level vulnerability indices for World Bank, ADB, GCF.
- **Famine / food-security early warning as a service.** WFP, FAO, USAID stuck on coarse FEWS NET data.
- **FMCG and quick-commerce rural demand.** Cropping intensity → demand forecasting for HUL, ITC, Dabur, rural Zepto.
- **Telecom / EV infrastructure siting.** Rural economic gradient instead of 2011 census.
- **Migrant-origin insurance.** Insure a Mumbai construction worker on his home village's crop failure risk.
- **Specialty crop traceability.** Basmati, Darjeeling, Alphonso — parcel-level provenance for EU CBAM-adjacent markets.
- **Reinsurance portfolio analytics.** Swiss Re / Munich Re want to price Indian agri risk; they pay anyone with a defensible signal.

The pattern: every one has a buyer already trying to solve the problem with worse data. We don't create demand. We become the better signal.

---

## Why us, specifically

**Me.** Columbia OR (optimization, stochastic systems). Ten years at Apple Maps doing large-scale geospatial data and ML operations — the exact muscle this platform needs at scale. Founding engineer at Mapsense (acquired). Crop classification, multi-temporal modeling, parcel-level reasoning — this is the closest thing to my actual competence that exists in Indian tech right now.

**You.** [To fill in together — what you bring on GTM, operations, capital, network. This slide is a placeholder until we talk.]

**Together, what we're still missing.** A state-relationship person who's run a govt sales cycle to closure. A field-ops lead who's deployed GT surveys at scale. We'd need both within 12 months if we go productized.

---

## Five shapes this could take

Before we say "let's build a company," let's name the alternatives:

1. **Build the company.** Productized platform, state govts as anchor customers. Highest upside, longest grind, most capital, most life cost.
2. **License the engine.** Sell to RMSI / TCS / Wipro for their RFP responses. Lower upside, lower commitment, faster to revenue, no moat.
3. **Become a layer inside an incumbent.** Feature or data partnership with Cropin / SatSure. Equity-light, optionality on acquisition, gives up the platform thesis.
4. **JV with a state-friendly SI.** Them on procurement, us on tech. Splits margin, accelerates first contract, dilutes brand.
5. **Open-source core + commercial overlay.** Mapbox-style. Slow burn, durable moat, requires a different team and capital shape.

I don't think we should pick today. I think we should agree these are the five, and decide which two are worth a real conversation in the next month.

---

## The honest life question

I'm not currently in startup mode. I'm financially independent, I have a 2-year-old, a second kid arriving June 2026, and I'm building State Overflow as the thing I want to be known for at 48.

There is a version of this project that's compatible with that life — architect / tech lead remote, partner runs operations, we pick one of shapes 2–4 above. There's a version that isn't — me operating a govt-sales company out of Indore.

I want to be honest with you that those are different conversations, and which one we're having should be the *first* decision, not the last.

---

## What I'd propose as a next step

- 2-week sprint to harden the **demo asset** into something we can put in front of a state ag department or a commercial buyer.
- Parallel: **3–5 customer conversations** — at least one state, one trader, one insurer — to test which wedge is real.
- Reconvene in 4 weeks with demo + customer signal + a go/no-go on shape.

Low cost, high signal. If the demo lands and one buyer leans in, we'll know.

---

## Open questions for the room

- Is the "platform, not model" framing right for you?
- Of the five shapes, which two would you actually want to pursue?
- What's the version of this *you* want — and does it match a version *I* can commit to?
- What would make you say no?
