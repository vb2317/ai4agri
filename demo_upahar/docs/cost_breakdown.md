# UPAHAR Costing Breakdown

Purpose: support the CEO discussion with line-item budget logic behind the headline ranges in `docs/keynote_storyline.md`.

Status: planning estimate, not a vendor quote. Commercial imagery, field operations, and integration effort should be quote-gated before any binding bid number is committed.

Planning currency: INR. Where cloud/GPU costs are discussed in USD, use a planning conversion rate approved by finance before finalizing the proposal.

## Budget Summary

| Phase | Duration | Internal / Controlled Spend | Quote-Gated Pass-Throughs | Decision Purpose |
|---|---:|---:|---:|---|
| 0. Bid-readiness sprint | 2-3 weeks | INR 12-20 lakh | minimal | Decide whether we can bid credibly |
| 1. Data and imagery validation | 2-4 weeks parallel | INR 5-10 lakh | INR 0-20 lakh+ | Confirm source availability, licensing, and AOI feasibility |
| 2. Pilot proposal package | 8-12 weeks | INR 45-90 lakh | INR 15-60 lakh | Build one district/block pilot story with real artifacts |
| 3. Production implementation | 9-12 months | INR 3-6 crore | INR 1-3 crore+ | State-scale platform, integrations, support, and O&M |

CEO approval should start with Phase 0 only. Phase 1 spend should be released only for specific vendor/data validation tasks.

## Phase 0: Bid-Readiness Sprint

Target range: INR 12-20 lakh  
Duration: 2-3 weeks  
Objective: create an executive-ready tender proposal package without pretending production data is ready.

| Line Item | Estimate | Notes |
|---|---:|---|
| Product / proposal leadership | INR 2.0-3.5 lakh | CEO narrative, tender positioning, bid story, stakeholder walkthrough script |
| CTO / solution architecture | INR 1.5-3.0 lakh | Section 12 mapping, delivery architecture, risk controls, technical annex |
| UI and demo polish | INR 2.5-4.0 lakh | First-viewport polish, reviewer flow, executive-grade copy, responsive cleanup |
| Backend / data API refinement | INR 1.0-2.0 lakh | File-backed APIs, GeoJSON, tile metadata, ML artifact loading path |
| ML proof planning | INR 1.5-3.0 lakh | AI4Agri artifact definition, SAM/SamGeo boundary workflow, validation framing |
| Imagery and SAR source validation | INR 0.8-1.5 lakh | Planet/Maxar/Airbus outreach, Sentinel/NISAR positioning, source matrix |
| Keynote / technical annex / budget pack | INR 1.5-2.5 lakh | CEO deck, costing appendix, demo script, decision gates |
| Contingency | INR 1.2-2.5 lakh | 10-15% for rework after executive review |

Recommended Phase 0 cap: INR 15 lakh unless vendor quote work expands the scope.

## Phase 1: Data And Imagery Validation

Target range: INR 5-30 lakh  
Duration: 2-4 weeks, partly parallel with Phase 0  
Objective: replace assumptions with source-specific feasibility and quote data.

| Line Item | Estimate | Notes |
|---|---:|---|
| Commercial imagery sample / evaluation access | INR 0-20 lakh+ | Quote-gated. Planet/Maxar/Airbus pricing depends on AOI, archive/tasking, dates, license, display rights, and area. |
| Public imagery and SAR processing | INR 1.0-3.0 lakh | Sentinel-2/Sentinel-1/NISAR feasibility, AOI search, product metadata, derived layer tests |
| Local tile / COG rendering pipeline | INR 1.5-4.0 lakh | Convert source imagery into backend-served tiles and future GIS-ready artifacts |
| Ground-truth sampling design | INR 1.0-3.0 lakh | Sampling frame, holdout split, field schema, QC protocol, validation dashboard spec |
| Licensing and procurement review | INR 0.5-1.5 lakh | Check display, redistribution, government submission, and derivative-output constraints |
| Contingency | INR 1.0-3.0 lakh | Cloud storage, conversion issues, additional AOI checks |

Phase 1 should not proceed as a blank check. Each vendor/source task should have a named output: quote, AOI availability, sample scene metadata, or rejection reason.

## Phase 2: Pilot Proposal Package

Target range: INR 60 lakh-1.5 crore  
Duration: 8-12 weeks  
Objective: build a defensible one district/block pilot package that can anchor a full tender response.

| Line Item | Estimate | Notes |
|---|---:|---|
| Product management and delivery PMO | INR 8-15 lakh | Sprint management, stakeholder review, demo governance, acceptance criteria |
| GIS/backend/data engineering | INR 10-22 lakh | Post-file loaders, GeoJSON/COG path, model artifact registry, report exports |
| ML / remote-sensing engineering | INR 12-28 lakh | Temporal features, classifier, stress/yield proxy, SAR fallback features, validation summaries |
| Frontend / WebGIS / executive UX | INR 6-14 lakh | Map-first workflows, reviewer mode, mobile/tablet polish, dashboard refinements |
| SAM/SamGeo boundary workflow | INR 4-10 lakh | Prompting, mask cleanup, topology simplification, manual QC loop |
| Field validation pilot | INR 8-30 lakh | Depends heavily on sample count, travel, supervisor/QC structure, crop diversity |
| Imagery acquisition / rights | INR 5-35 lakh+ | Quote-gated; may be lower for sample/archive access and much higher for wider coverage |
| Cloud/GPU/storage | INR 3-8 lakh | Development compute, tile storage, model experiments, backups |
| QA, reports, training material | INR 3-8 lakh | Demo scripts, test evidence, user guide, technical annex |
| Contingency | INR 8-20 lakh | 12-15% for data/vendor/field uncertainty |

Pilot scope must be fixed by AOI, season, crop classes, number of villages/blocks, and GT sample count. Without those, the range will remain wide.

## Phase 3: Production Implementation

Target range: INR 4-9 crore plus pass-throughs  
Duration: 9-12 months  
Objective: state-scale platform with O&M, integrations, training, and operational support.

| Line Item | Estimate | Notes |
|---|---:|---|
| Core platform engineering | INR 90 lakh-1.8 crore | Backend services, workflow engine, reporting, role-based interfaces |
| GIS/data infrastructure | INR 50 lakh-1.2 crore | PostGIS, COG/GeoTIFF storage, map services, tiling, data catalog |
| ML/remote-sensing productionization | INR 70 lakh-1.6 crore | Model training/inference, feature pipelines, validation, monitoring, retraining path |
| Field/mobile workflows | INR 40-90 lakh | Mobile collection, QC, offline sync, supervisor review, audit trail |
| Government integrations | INR 60 lakh-1.4 crore | LRMS/Bhuiyan, AgriStack, Food Dept, MARKFED, PACS/CCB, mandi/weather systems |
| DAC dashboards and reporting | INR 30-70 lakh | Command-center views, exports, recurring reports, executive dashboards |
| QA, security, UAT, documentation | INR 35-80 lakh | Test cycles, hardening, release governance, tender evidence |
| Training and change management | INR 30-70 lakh | Department training, district rollout material, operating manuals |
| Cloud/GPU/storage/O&M setup | INR 25-80 lakh | Infrastructure baseline before recurring run cost; depends on hosting policy |
| Program governance and contingency | INR 60 lakh-1.5 crore | 15-20% risk buffer across data, integration, and stakeholder delays |

Production excludes major commercial imagery and large-scale field data collection unless the bid explicitly treats those as pass-throughs or reimbursables.

## Recurring Annual Cost Drivers

These should be priced separately from implementation:

| Driver | Cost Behavior | Notes |
|---|---|---|
| Imagery refresh | Highly variable | Driven by area, GSD, cadence, archive vs tasking, redistribution rights |
| Field validation | Variable | Driven by sample density, crop seasons, travel, supervisor ratio, QC standard |
| Cloud hosting | Moderate to high | Depends on tile volume, user concurrency, GPU inference strategy, retention |
| O&M team | Predictable | Helpdesk, model monitoring, data ops, map ops, reporting, release support |
| Integrations | Variable | More stable after production APIs are accepted and tested |

## Cost Controls

- Keep Phase 0 capped and outcome-based.
- Separate vendor pass-throughs from internal delivery cost.
- Use public sources for feasibility, but do not claim they satisfy 3 m optical compliance.
- Use GPU only for targeted experiments; start with small AOI and fast models.
- Require source metadata for every imagery layer used in the proposal.
- Tie field validation cost to a defined sample plan.
- Gate production architecture decisions until pilot data proves the workflow.

## Costing Sources To Verify Before Final Bid

- RunPod pricing: GPU compute is billed by the second/minute depending on product, and storage has separate per-GB monthly charges. Latest GPU prices should be verified in the RunPod console before use.
- AWS EC2 pricing: On-Demand is pay-as-you-go by hour/second with no long-term commitment; final cloud numbers should be calculated in the AWS Pricing Calculator for the target region and architecture.
- Planet, Maxar, Airbus: commercial imagery is quote-gated. Public web pages describe products and access paths, but proposal pricing should use vendor responses for AOI, dates, rights, and volume.
- Public data: Sentinel and NISAR data access may reduce imagery cost for ML/fallback features, but processing, storage, QA, and validation still cost money.
