# The Data Science Pyramid

I've been doing data work for roughly fifteen years — operations research at Columbia, large-scale data and ML at Apple Maps, founding engineering at a geospatial startup before that. Across all of it, the same shape has held: data science as a field is a pyramid with three layers — data engineering at the base, statistics in the middle, domain knowledge at the top — and most teams build it inverted, then wonder why nothing compounds.

This is my framing of the field. It's not the only one, but it's the one that's held up across the longest stretches of my own work.

## The pyramid

```
              [ Domain knowledge ]
          [        Statistics        ]
    [         Data engineering          ]
```

Three layers. Each rests on the one below. The width of each layer corresponds roughly to how much of it you need underneath to do the work above well — the base is the widest because the work at the top quietly assumes the work at the bottom is already solid.

## Data engineering is the core

This is the unglamorous layer most discussions of data science skip past. It's also the layer that decides whether the rest works.

Data engineering is the work of making data reliable, fresh, observable, addressable, and reproducible. Schemas that mean what they say. Pipelines that fail loudly rather than silently. Lineage that lets you trace any number back to the source rows it came from. Idempotent jobs you can re-run without fear. Storage that's queryable in the dimensions people actually want to query.

When this layer is weak, everything above it bends to compensate. The statistician spends most of her time cleaning data. The domain expert loses trust in the dashboards. The model that worked in the notebook breaks in production because the feature distribution shifted and no one noticed. Most "model failures" I've debugged were data failures wearing a model's clothing.

When this layer is strong, the work above it compounds. A new analysis takes hours instead of weeks. A new model gets to "is this idea even worth pursuing" the same day it's proposed. Provenance is automatic rather than retrofitted.

This is the layer where investment compounds longest. A good feature store, a clean lineage graph, a well-named set of tables — these pay rent for years. A clever model usually doesn't.

## Statistics sits above it

Statistics is what distinguishes signal from noise, and quantified uncertainty from confident guessing.

The work at this layer is about asking what the data is actually telling you, given how it was collected and what variability lives inside it. Without it, you have descriptive analytics — counts, averages, charts — which are useful but limited. With it, you can say things like "this difference is unlikely to be chance," "this estimate has a 95% interval of X to Y," "this effect attenuates after controlling for Z," "this model is overfit and won't generalize."

Statistics requires the layer below. Correlations on dirty data lie confidently. P-values on garbage are still numbers, just meaningless ones. The hardest bugs in stats work are upstream — a join that silently duplicated rows, a backfill that overwrote the source of truth, a timezone that shifted by six hours and made the time series look seasonal. You don't catch these with a better model; you catch them with a better data layer.

The current discourse conflates statistics with machine learning. They overlap, but the framing matters. Statistics asks "what can I say given this data and these assumptions?" Machine learning asks "what's the best function I can fit?" The first is closer to the actual decision the data is supposed to inform. Bayesian thinking — which I've been working through via McElreath — sits cleanly in this layer; it's the framework I'd most want a team to internalize before any modeling sophistication.

## Domain knowledge is the apex — and the decision is what it's for

Domain knowledge is what tells you which question to ask and which answer would actually change a decision. That last word is the point: the apex exists to serve a decision. The reason domain knowledge can't be commoditized is the same reason the decision can't be — both carry judgment and accountability that no model inherits. When I think about where the irreducible human work lives, "domain knowledge" and "the decision it informs" are two names for the same layer.

It's the rarest combination, which is why it sits at the top and is the narrowest layer. Most data scientists are generalists who pattern-match across domains. Most domain experts have never written a join. The intersection — someone who has both the depth to know what matters in a field and the layers below them to investigate it — is uncommon enough that one such person is often worth a team of generalists.

Without this layer, you optimize the wrong loss function. You build a model that's technically excellent and operationally irrelevant. You report a result that's statistically valid but misframes the question. I've watched many a sophisticated analysis die because no one had the domain instinct to notice that the metric being optimized wasn't the metric the business actually cared about.

Domain knowledge also has the longest learning curve. You don't get it from reading; you get it from years of friction with the actual problem. There's no shortcut, which is part of why it sits at the top.

## Why the order matters

The pyramid has a direction. You build it from the base up. Most teams build it inverted: they hire a famous domain expert first, then realize they need a statistician, then realize they need a data engineer, and watch the foundation get rebuilt reactively while the upper layers wait.

The healthier pattern, in my experience, is:

1. Invest in the data engineering layer first. Without it, everything you do above is fragile and slow.
2. Build the statistics layer on top of solid data. Use it to quantify what you actually know versus what you're guessing.
3. Pair the upper layers with deep domain immersion — either by hiring domain people who can learn the lower layers, or by embedding data people in the domain long enough that they become it.

The pyramid also explains why some data science teams compound and others don't. Teams that compound have invested in the base. Their work gets faster over time because each piece of infrastructure makes the next analysis cheaper. Teams that don't keep rebuilding the foundation for every project, and their senior people spend their time fighting the same fires they fought last year.

## How this shapes how I work

When I'm thinking about a new data product or a new project, I check the layers in order:

- Is the data layer reliable enough that the analysis I want to do can actually be trusted? If not, that's the first investment, no matter how exciting the modeling idea is.
- Am I being honest about uncertainty? Have I checked whether the effect I'm seeing could be explained by noise, by sampling, or by an unmodeled confounder?
- Do I understand the domain well enough to know whether the question I'm answering is the question that matters? If not, the right move is to spend time with the people who live the problem before writing any code.

This is the pyramid I keep returning to. The order is not novel, but it matters more than I think most people in the field appreciate. The base is what compounds. The middle is what protects you from fooling yourself. The top is what makes the work matter.
