# ARCHITECTURE.md

# AI Infrastructure Research Platform Architecture

This document describes the architecture of the AI Infrastructure Research Platform.

It focuses on:

* Knowledge model
* Entity design
* Relationship design
* Evidence and reasoning workflow
* Ownership and update frequency
* Agent boundaries

This document explains **how the platform thinks**.

Implementation details such as Streamlit pages, CSV file names, APIs, or databases belong in `SPEC.md`.

---

# 1. Architecture Overview

The platform is built around one core idea:

> New information should be transformed into structured evidence, connected to existing knowledge, and used to review investment hypotheses.

The architecture has three main layers:

```text
Knowledge Layer
      ↓
Reasoning Layer
      ↓
Presentation Layer
```

## Knowledge Layer

Stores structured knowledge about:

* Companies
* Industries
* Technologies
* Products
* Events
* Evidence
* Relationships
* Watchlist and portfolio context

This layer should be persistent and reviewable.

## Reasoning Layer

Uses the Knowledge Layer to analyze new information.

It should:

* summarize information
* extract facts
* connect facts to existing entities
* reason about industry impact
* reason about company impact
* suggest research actions
* suggest thesis review status

It should not directly make investment decisions.

## Presentation Layer

Displays information in a way that supports research.

It should help the user answer:

* What happened?
* Why does it matter?
* Which industry thesis is affected?
* Which companies are affected?
* What should I research next?
* Does my thesis need review?

---

# 2. Core Workflow

The platform supports two main research workflows.

---

## 2.1 News-driven Workflow

This workflow starts from a new event.

Examples:

* NVIDIA announces a new server architecture
* Oracle raises AI CapEx guidance
* Micron reports stronger HBM demand
* A conference presentation introduces a new cooling requirement

Pipeline:

```text
Event / News
      ↓
Summary
      ↓
Fact Extraction
      ↓
Evidence
      ↓
Reasoning
      ↓
Industry Impact
      ↓
Company Impact
      ↓
Research Actions
      ↓
Watchlist / Portfolio Context
      ↓
Thesis Review
```

The key rule is:

> Facts must be extracted before reasoning begins.

The agent should not jump directly from summary to conclusion.

---

## 2.2 Company-driven Workflow

This workflow starts from a company.

Example:

The user wants to research ON Semiconductor.

Pipeline:

```text
Company
      ↓
Related Industry Thesis
      ↓
Company Exposure
      ↓
Current Evidence
      ↓
Financial / Valuation Context
      ↓
Recent Events
      ↓
Why This Company?
      ↓
Research Actions
```

The first question is not:

> What does this company do?

The first question is:

> Why does this company matter under the current industry thesis?

Example:

```text
ON Semiconductor
      ↓
Power Semiconductor Thesis
      ↓
AI server power demand may increase power semiconductor demand
      ↓
ON has exposure to power semiconductors
      ↓
Research whether lead time, pricing, and margin evidence support this thesis
```

---

# 3. Knowledge Model

The Knowledge Layer is organized around entities and relationships.

## 3.1 Entity

An entity is a meaningful object in the AI infrastructure research world.

First-version entity types:

```text
Company
Industry Thesis
Technology
Product
Event
Evidence
Market Indicator
Watchlist / Portfolio Item
```

---

## 3.2 Relationship

A relationship connects two entities.

Examples:

```text
Product uses Technology
Technology belongs_to Industry Thesis
Industry Thesis impacts Company
Company exposes_to Industry Thesis
Event provides Evidence
Evidence supports Industry Thesis
Company tracked_in Watchlist
```

A relationship should be explicit, explainable, and reviewable.

---

## 3.3 Layer

A layer describes where an entity sits in the research flow.

Example layers:

```text
Macro Layer
Event Layer
Product Layer
Technology Layer
Industry Layer
Company Layer
Portfolio Layer
Research Layer
```

Important distinction:

```text
Entity = node
Relationship = edge
Layer = position in the research flow
```

Example:

```text
[Event] NVIDIA server architecture announcement
      ↓ mentions
[Product] GB300
      ↓ uses
[Technology] HBM4e
      ↓ belongs_to
[Industry Thesis] Memory
      ↓ exposes_to
[Company] Micron
      ↓ tracked_in
[Watchlist]
```

---

# 4. Entity Definitions

## 4.1 Company

A company is a business entity.

Examples:

* NVIDIA
* Micron
* ON Semiconductor
* Delta Electronics
* Vertiv
* Broadcom

Company data may include:

* static profile
* financial data
* valuation data
* company thesis
* theme / industry exposure
* watchlist status
* portfolio context
* recent events

A company should not directly own an industry thesis.

Instead, a company has **exposure** to one or more industry theses.

Example:

```text
ON Semiconductor
      exposes_to → Power Semiconductor
      exposure_level → High
```

---

## 4.2 Industry Thesis

An Industry Thesis represents the current research view of an industry layer.

Examples:

* Memory
* Power Semiconductor
* Power Infrastructure
* Cooling
* Networking
* Advanced Packaging
* Server ODM
* Industrial AI

An Industry Thesis may include:

* summary
* current status
* confidence
* key drivers
* key risks
* representative companies
* key evidence to monitor
* recent changes

An Industry Thesis should be updated less frequently than evidence.

The agent may suggest updates, but the user should approve thesis changes.

---

## 4.3 Technology

A Technology is a technical concept, capability, or architecture.

Examples:

* HBM4e
* CoWoS
* CPO
* NVLink
* Liquid Cooling
* SiC
* GaN
* Power Shelf

Technology should be independent from individual news events.

A technology may be mentioned by events, used by products, or connected to industry theses.

Example:

```text
HBM4e
      belongs_to → Memory
      requires → Advanced Packaging
```

---

## 4.4 Product

A Product is a specific product, platform, architecture, or system.

Examples:

* GB300
* Blackwell
* Rubin
* MI400
* TPU
* AI server rack architecture

Product is different from Technology.

Example:

```text
GB300 = Product
HBM4e = Technology
NVLink = Technology
Liquid Cooling = Technology
```

Product relationships may include:

```text
Product uses Technology
Product requires Technology
Product increases demand_for Industry Thesis
```

---

## 4.5 Event

An Event is a new piece of information.

Examples:

* earnings call
* conference announcement
* product launch
* pricing update
* supply chain news
* macroeconomic release

Events are the main input to the news-driven workflow.

An event should be processed into:

* summary
* extracted facts
* related entities
* evidence
* possible industry impact
* possible company impact

---

## 4.6 Evidence

Evidence is an observable fact that may support, weaken, or challenge a thesis.

Examples:

* lead time increased
* HBM ASP increased
* Oracle raised AI CapEx guidance
* inventory declined
* rack power increased
* liquid cooling adoption increased
* gross margin improved

Evidence should always be linked to a source when possible.

Evidence is not the same as reasoning.

Example:

```text
Evidence:
Oracle raised AI CapEx guidance.

Reasoning:
Higher CapEx may support the AI infrastructure demand thesis.
```

---

## 4.7 Market Indicator

A Market Indicator is a market-level or macro-level data point.

Examples:

* VIX
* SOX index
* Nasdaq
* US 10Y yield
* USD/TWD
* electricity price
* DRAM spot price

Market indicators provide context.

They should not automatically change a thesis without reasoning.

---

## 4.8 Watchlist / Portfolio Item

Watchlist and portfolio items represent the user's research context.

They may include:

* current position
* priority
* thesis
* risks
* next check
* ownership status

The agent may recommend adding a company to the watchlist.

The user should decide whether to accept.

---

# 5. Relationship Types

First-version relationship types:

```text
uses
requires
belongs_to
impacts
benefits
exposes_to
competes_with
supplies_to
tracked_in
supports
challenges
mentions
```

## Examples

```text
GB300 uses HBM4e
HBM4e belongs_to Memory
Liquid Cooling impacts Cooling
Power Semiconductor benefits ON Semiconductor
ON Semiconductor exposes_to Power Semiconductor
Micron competes_with SK hynix
Oracle CapEx Event supports Power Infrastructure Thesis
Weak guidance challenges AI Server Demand Thesis
```

Relationships should have:

* source entity
* relationship type
* target entity
* reason
* confidence
* last updated

---

# 6. Evidence, Reasoning, and Hypothesis

The platform should clearly separate:

```text
Fact
Evidence
Reasoning
Hypothesis
```

## Fact

A fact is something directly stated or observed.

Example:

```text
Oracle increased AI CapEx guidance.
```

## Evidence

Evidence is a fact interpreted as relevant to a thesis.

Example:

```text
Oracle CapEx guidance is evidence for AI infrastructure demand.
```

## Reasoning

Reasoning explains why evidence affects a thesis.

Example:

```text
Higher AI CapEx may lead to more AI server deployment.
More AI server deployment may increase demand for power, cooling, networking, and memory.
```

## Hypothesis

A hypothesis is the current research view.

Example:

```text
Power infrastructure demand may continue to improve as AI rack power increases.
```

Important rule:

> Evidence may trigger thesis review, but it should not automatically overwrite the thesis.

---

# 7. Knowledge Update Frequency

No knowledge is truly permanent.

Instead of using static vs dynamic, the platform uses update frequency.

Suggested categories:

```text
yearly
half_yearly
quarterly
monthly
weekly
daily
event_driven
```

Examples:

| Knowledge Type          | Update Frequency          |
| ----------------------- | ------------------------- |
| Company profile         | yearly                    |
| Product description     | half_yearly               |
| Technology description  | half_yearly               |
| Industry thesis summary | quarterly                 |
| Company thesis          | quarterly                 |
| Relationships           | quarterly or event_driven |
| Financial data          | quarterly                 |
| Market indicators       | daily                     |
| News / events           | daily                     |
| Evidence                | daily or event_driven     |

---

# 8. Knowledge Ownership

Every knowledge type should have an owner.

Suggested owners:

```text
user
agent
external_data
shared
```

## Ownership Rules

### User-owned

The user has final authority.

Examples:

* Industry Thesis
* Company Thesis
* Portfolio decision
* Watchlist priority

The agent may suggest changes, but should not overwrite.

### Agent-owned

The agent may generate or update.

Examples:

* summaries
* extracted facts
* suggested evidence
* suggested research actions

Agent-owned outputs should remain reviewable.

### External-data-owned

Data comes from external sources.

Examples:

* financial statements
* market data
* macro data
* price data

The agent should not modify these values.

### Shared

Both user and agent may contribute, but user approval may be required for major changes.

Examples:

* entity relationships
* company exposure
* thesis status

---

# 9. Agent Boundaries

The agent may:

* summarize events
* extract facts
* identify related entities
* propose evidence
* explain reasoning
* suggest affected industries
* suggest affected companies
* suggest research actions
* suggest thesis review status

The agent should not:

* directly recommend buying or selling
* overwrite user theses without approval
* fabricate evidence
* treat reasoning as fact
* update portfolio decisions automatically

The agent should always separate:

```text
What happened?
What is the evidence?
Why might it matter?
What should be reviewed?
```

---

# 10. Design Principle

The platform should help the user think better.

It should not replace thinking.

Every feature should improve at least one of the following:

* evidence quality
* reasoning clarity
* thesis management
* research workflow
* knowledge accumulation

If a feature does not improve research quality, it should be reconsidered.
