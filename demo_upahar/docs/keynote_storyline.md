# UPAHAR Tender Proposal Storyline

Audience: CEO / executive decision review  
Voice: CTO plus product leader  
Purpose: decide whether to invest in a serious UPAHAR bid, and what budget guardrails to approve before vendor quotes are finalized.

Initial slide draft: https://slidesgpt.com/view/bcb1ec26b807  
Presentation ID: `pres_5045dd55621c392d393db4004dbbada6`
Costing appendix: `docs/cost_breakdown.md`

## Executive Thesis

UPAHAR is not just a remote-sensing tender. It is a state-scale agriculture operating system: crop intelligence, field validation, advisories, procurement planning, disaster monitoring, WebGIS, mobile workflows, analytics center, and integration with existing government systems.

Our advantage is not claiming that we already have every production dataset. Our advantage is showing a working, Section 12-traceable product narrative quickly: real same-area imagery, aligned parcel overlays, temporal crop states, AI4Agri ML evidence, SAR fallback thinking, and a reviewer flow that makes the tender requirement visible in the product.

## CEO Decision Needed

Approve a controlled pre-bid investment to turn the current demo into a polished executive proposal and technical proof package.

Recommended decision:

- Proceed with a 2-3 week bid-readiness sprint.
- Cap pre-bid spend until imagery and ground-truth scope are clearer.
- Authorize vendor outreach for Planet/Maxar/Airbus imagery quotes and NISAR/Sentinel fallback validation.
- Use the demo as a CEO/department walkthrough, not as a production accuracy claim.

## Slide Storyline

### 1. Title: From Tender Requirement To Operating System

Message: UPAHAR should be framed as a state agriculture intelligence product, not a collection of GIS screens.

Key points:

- Section 12 asks for imagery, crop classification, health, acreage, yield, advisories, procurement, disaster monitoring, mobile, WebGIS, analytics, integrations, testing, and O&M.
- The winning proposal must make those capabilities feel coherent to non-technical decision makers.
- The demo is designed around the reviewer journey: click the requirement, see the proof, inspect the evidence.

Visual: polished map-first dashboard screenshot with Section 12 badges and parcel overlay.

### 2. Why This Tender Is Strategically Attractive

Message: The tender is a wedge into public-sector agriculture intelligence, not a one-off dashboard build.

Key points:

- State-scale agriculture intelligence creates repeatable assets: crop models, field validation workflows, procurement analytics, disaster monitoring, and government integrations.
- The same product spine can be reused across states and programs with different imagery, crop calendars, and integration endpoints.
- AI4Agri gives us credible technical DNA, while the UPAHAR demo packages it into a buyer-ready product story.

Visual: portfolio map showing "Imagery -> ML -> Field validation -> Advisories -> Procurement -> Analytics center".

### 3. What We Are Proposing

Message: A Section 12-traceable Agriculture Intelligence Command System.

Product pillars:

- Observe: multi-date optical imagery, Sentinel temporal signals, SAR fallback, cadastral/parcel overlays.
- Understand: crop classification, acreage, health, stress, yield, and confidence scoring.
- Act: advisories, field validation, procurement planning, disaster/crop-loss workflows.
- Govern: WebGIS, OGC services, reports, audit trail, integrations, and DAC operations.

Visual: four-pillar product diagram.

### 4. The Product Demo Narrative

Message: The current demo already tells the buyer how the system works.

Demo path:

1. Open reviewer mode.
2. Select Section 12 imagery and crop identification.
3. Show same-area temporal imagery with aligned parcel overlays.
4. Select a parcel and show crop class, confidence, NDVI/EVI, and stress.
5. Show field validation and advisory outputs.
6. Show paddy procurement planning.
7. Close with coverage matrix and source requirement drawer.

Visual: annotated screen sequence with six checkpoints.

### 5. Data And Imagery Strategy

Message: We separate demo display, ML features, and formal compliance evidence.

Positioning:

- Esri Wayback is acceptable for current same-area visual demonstration, but not final procurement-grade evidence.
- PlanetScope is the strongest candidate for 3 m temporal optical monitoring if AOI access and licensing are approved.
- Maxar/Airbus are best for high-resolution boundary and cadastral proof, but likely require quote-based licensing.
- Sentinel-2 supports temporal ML features, but does not satisfy the 3 m optical requirement.
- Sentinel-1/NISAR support SAR fallback, monsoon resilience, waterlogging, drought, and disaster monitoring; they do not replace optical compliance.

Visual: decision table: source, role, compliance value, procurement risk.

### 6. ML Capability Without Overclaiming

Message: We show capability and discipline, not unsupported production accuracy.

ML story:

- Reuse AI4Agri learnings: temporal stacks, vegetation indices, phenology features, nodata/cloud masking, validation discipline.
- Start with a small, defensible model artifact: parcel_id, epoch date, class, confidence, NDVI/EVI/NDWI, stress score, transition label.
- Use SAM/SamGeo for boundary acceleration, followed by human QC.
- Use holdout validation, confusion matrix, per-class recall, and visual mask review before making accuracy claims.

Visual: simple pipeline: imagery chip -> SAM boundary -> temporal features -> model output -> parcel workflow.

### 7. Architecture: Enough To Prove, Not Overbuilt

Message: The architecture is intentionally lean for the bid phase.

Current state:

- Static frontend with reviewer mode and Section 12 traceability.
- Python backend serving demo data, GeoJSON, imagery metadata, NISAR metadata, and local-first tiles.
- File-backed APIs so ML outputs can be dropped in quickly.

Path to production:

- Bid demo: file-backed backend and local tiles.
- Pilot: PostGIS, COG/GeoTIFF storage, model-output registry, field data ingestion.
- Production: scalable GIS services, auth, cloud deployment, monitoring, integrations, and O&M.

Visual: three-stage architecture maturity ladder.

### 8. Budget Framing

Message: Approve a staged investment with gates, because imagery, GT, and integration scope drive the largest uncertainty.

Indicative internal budget ranges, excluding taxes and final vendor pass-throughs:

| Phase | Duration | Budget Range | Outcome |
|---|---:|---:|---|
| Bid-readiness sprint | 2-3 weeks | INR 12-20 lakh | polished demo, CEO deck, technical annex, source strategy, budget model |
| Data/imagery validation | parallel, 2-4 weeks | INR 5-30 lakh placeholder | vendor quotes, sample AOI imagery, SAR/public-data feasibility |
| Pilot proposal package | 8-12 weeks | INR 60 lakh-1.5 crore | one district/block operational pilot, ML artifact, GT workflow, reports |
| Production implementation | 9-12 months | INR 4-9 crore plus pass-throughs | state-scale platform, integrations, cloud, O&M, training, support |

Budget sensitivities:

- Commercial imagery licensing can dominate cost if state-wide high-resolution temporal coverage is required.
- Ground-truth operations scale with crop diversity, district count, sampling density, and validation rigor.
- Cloud/GPU costs are controllable for the demo, but production inference/storage/tiling needs formal sizing.
- Integration complexity depends on access to LRMS/Bhuiyan, AgriStack, Food Department, MARKFED, PACS/CCB, and weather systems.
- Detailed line-item assumptions are maintained in `docs/cost_breakdown.md`.

Visual: stacked budget bar with three uncertainty bands: imagery, field ops, integration.

### 9. Risk Register And Mitigations

Message: The proposal should look mature because it names risks early.

Top risks:

- Imagery availability/licensing: mitigate through vendor quotes and public-source fallback.
- Resolution compliance: keep Sentinel-2 and NISAR positioned correctly, not as 3 m optical replacements.
- Ground-truth sufficiency: define sampling plan, holdout split, QC workflow, and validation metrics.
- Government integrations: stage integration as mock -> sandbox -> production API.
- Overclaiming ML accuracy: show confidence, uncertainty, and GT-needed flags.

Visual: risk matrix with "control now" vs "requires stakeholder/vendor input".

### 10. CEO Ask And Next 10 Days

Message: We can move quickly if the decision is bounded.

CEO ask:

- Approve bid-readiness sprint budget.
- Approve vendor outreach for imagery and data-source quotes.
- Approve a no-overclaiming rule: demo capability is shown; production accuracy waits for real AOI labels.
- Approve one executive-quality storyline: product value first, technical proof second, budget gates explicit.

Next 10 days:

- Polish UI first viewport and reviewer flow.
- Add real/local tile path if source access is resolved.
- Generate first ML artifact from AI4Agri-style features.
- Create budget appendix and delivery workplan.
- Convert this storyline into Keynote/PPT for CEO review.

Visual: 10-day execution roadmap.

## Budget Notes For CEO Conversation

The ranges above are decision ranges, not vendor quotes. They are intended to answer: "Is this opportunity worth a controlled pre-bid investment?" The final commercial proposal should separate:

- internal delivery cost;
- commercial imagery pass-through;
- field data collection cost;
- cloud/GPU infrastructure;
- integration and O&M;
- contingency.

For now, the right CEO decision is not "approve production spend." It is "approve a disciplined bid-readiness sprint with quote gates."

## Tone Guidance

The deck should feel like a CTO/product proposal:

- calm and evidence-led;
- honest about what is demo, what is source-backed, and what needs procurement;
- product-first rather than algorithm-first;
- visually restrained, with map/product screenshots as the primary proof;
- budget-aware, with decision gates rather than open-ended engineering.
