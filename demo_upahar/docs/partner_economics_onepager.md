# Economics, honestly

*A one-pager for [partner], kept out of the deck on purpose.*

The deck tells the story. This page tells the truth about money. Numbers are back-of-envelope and I've marked confidence; treat them as conversation starters, not commitments.

---

## Five economic truths about this market

**1. The customer has money, but pays like a customer who has money.**
A full state Data Analytics Centre + WebGIS + crop intelligence contract — the Chhattisgarh-shaped thing — runs in the **₹20–80 crore range over 3–5 years** depending on scope (≈ $2.5–10M USD). *Confidence: medium; based on comparable state agri-IT and revenue/GIS contracts I've seen referenced publicly.* Payment terms are quarterly milestone-based and late by 60–180 days. Plan working capital accordingly or this will kill us before competitors do.

**2. Ground truth is the single largest line item nobody talks about.**
Chhattisgarh has ~5.6M ha sown. The RFP says 1–2% GT coverage. At a realistic stratified sampling density that's **~3,000–6,000 GT points per season, three seasons a year**. All-in cost per point (field staff, mobile app, photos, QC, recollection within 5 days) is ₹800–1,500. That's **₹70 lakh to ₹2.7 crore per year, per state, on GT alone** — before software, hosting, integration, or margin. *Confidence: medium-high on the math; medium on the per-point cost.* This is the line item that decides whether we own GT operations or partner it out, and the answer probably has to be "partner."

**3. Software is the cheap part. Reference customers are the expensive part.**
The platform itself — engine, WebGIS, APIs, mobile, MLOps — is **6–10 engineer-years to production**. At Indian senior rates, that's **₹2.5–4 crore in salary**. That's tractable. The expensive part is the **18-month sales cycle to the first state**, during which we're burning ~₹50 lakh/month and producing zero revenue. **First-state-to-first-cheque is where companies die in this market.** Capital strategy has to be designed around surviving that window, not around scaling the engine.

**4. Margins fork sharply based on shape.**
The same intellectual product has wildly different margin profiles depending on how we sell it:

| Shape | Gross margin | Capital required to ₹10cr revenue | Time to revenue |
|---|---|---|---|
| State govt SaaS / DAC contract | 35–50% (GT + ops drag) | ₹6–10 cr | 18–24 months |
| Engine licensing to SIs (RMSI, TCS) | 70–80% | ₹1–2 cr | 6–9 months |
| Commercial data feed (traders, insurers) | 75–85% | ₹2–4 cr | 9–15 months |
| Productized SaaS for private agribusiness | 60–70% | ₹4–7 cr | 12–18 months |

The interesting line is the **second one**. We've been writing the deck as if shape 1 (state contracts) is the business. Shape 2 (licensing the engine to the SIs who win the contracts) is half the revenue and three times the margin and might be the actually-correct play. Worth a conversation.

**5. The comparable is Cropin, and it's a humbling number.**
Cropin has raised `~$140M` over a decade and is, by most accounts, in the **$15–25M ARR range** with mixed unit economics. *Confidence: low on the exact revenue number; the shape is right.* That's the optimistic ceiling for "build the company" with patient capital. SatSure is smaller. RMSI is bigger but mostly services revenue. **No Indian agri-EO company is yet a category winner.** That's either the opportunity or the warning sign, depending on how we read it.

---

## What I'd want capital to look like by stage

| Stage | What it pays for | Indicative size | Source |
|---|---|---|---|
| **Demo (now → +2 months)** | Harden existing demo, 5 buyer conversations, no hires | ~₹10–15 lakh | Our own time + minimal cash |
| **Wedge (months 2–9)** | First reference customer, 2 engineers, first GT partnership | ₹1–1.5 cr | Self-fund or angel; *don't* take VC yet |
| **Pilot in production (months 9–24)** | 4–6 engineers, first state contract delivery, MeitY empanelment | ₹4–6 cr | Strategic angels (geo / govt-tech), small VC round if shape is right |
| **Scale (year 2–4)** | 3 states under contract, cross-state platform | ₹15–30 cr | Series A — but only if shape 1 is locked |

The trap is taking VC at the wedge stage. It forces shape 1 (state contracts) before we've tested whether shape 2 (licensing) or shape 3 (commercial feed) is actually better. **Stay self-funded through wedge.**

---

## The interesting unit economics question

If we sell shape 2 — license the engine to an SI that wins a state RFP — the unit economics look roughly like:

- Engine license to SI: ₹2–4 cr / state / 3 years
- Our cost to serve: ~₹40–60 lakh / state / 3 years (model retraining, support, updates)
- **Contribution margin per state: ~75–85%**

At three states under license, that's **₹6–12 cr revenue, ₹4.5–10 cr contribution**, with a team of ~5 people. **That's a business you could run from Indore with a remote architect, no field ops, no procurement queue, and reasonable life cost.** That math is interesting. That math may be the actual business.

---

## What I want to discuss

1. Is shape 2 (licensing) more interesting than shape 1 (own the state contract)? The deck assumes 1; I increasingly think 2.
2. What's your appetite for the 18-month sales cycle on shape 1? Mine, honestly, is low.
3. If we're patient-capital (no VC), can we be unembarrassed about it? It changes who we hire and what we promise.
4. Are you up for putting ₹X in to get to the wedge, and how much is X for you?
