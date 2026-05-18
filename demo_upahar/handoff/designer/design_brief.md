# Design Brief

## Product

UPAHAR Section 12 Capability Demonstrator.

This is a map-first agriculture intelligence dashboard showing how satellite imagery, parcel boundaries, crop classification, ground truth, advisories, procurement planning, and disaster monitoring map back to the Chhattisgarh UPAHAR RFP.

## Primary Audience

The immediate audience is not farmers. It is a tender reviewer, senior agriculture official, procurement stakeholder, or partner evaluating whether the team understands the scope and can build the requested system.

## Current UI Structure

- Left/main: satellite imagery and parcel overlay.
- Right/detail: selected parcel state, crop class, confidence, stress, NDVI/EVI, production, advisories, evidence.
- Reviewer mode: guided Section 12 walkthrough.
- Source drawer: RFP requirement summary and matching demo evidence.
- Lower/supporting surfaces: field validation, procurement, reports, integrations, SAM boundary annotation.

## Core User Story

1. Reviewer opens the dashboard.
2. They see same-area imagery with aligned demo parcel boundaries.
3. They click a parcel and inspect crop, confidence, health, area, yield, and evidence.
4. They click an RFP badge and see the source requirement.
5. They move through the reviewer checklist to verify Section 12 coverage.
6. They understand what is shown now, what is demo/mock, and what is planned for production.

## Desired Feel

Operational, credible, restrained, precise.

This should feel closer to an Apple Maps internal operations tool, a government command dashboard, or a serious geospatial SaaS review console than a startup landing page.

## Design Priorities

- Make the first 10 seconds obvious: map, parcel, RFP traceability, current demo status.
- Improve visual hierarchy without adding visual noise.
- Make controls feel deliberate: layer toggles, epoch selector, reviewer flow, parcel tabs.
- Make RFP badges useful but not dominant.
- Make selected parcel content scannable for an executive and credible for a technical reviewer.
- Improve drawer/modal ergonomics.
- Ensure responsive behavior for tablet and small laptop screens.

## Specific Questions For Designer

- Is the first viewport understandable without explanation?
- Does the UI feel credible enough for a state-level buyer or senior partner?
- Are the RFP traceability affordances clear without overwhelming the map?
- Can a reviewer distinguish `Shown`, `Demo`, `Planned`, and `Needs source metadata`?
- Is the parcel detail panel too dense, too sparse, or badly ordered?
- Does the SAM boundary workflow read as a support workflow rather than the main classifier?
- What should be removed from the primary screen and moved behind progressive disclosure?

## Non-Goals

- No brand redesign yet.
- No marketing homepage.
- No full design system.
- No mobile farmer app design in this pass, except checking that the current web demo degrades cleanly.
- No production GIS architecture redesign.

## Assets And Data

The current parcels, imagery metadata, ground truth points, procurement centers, and RFP mappings are demo data. The UI must preserve provenance language and avoid implying live government integration.

