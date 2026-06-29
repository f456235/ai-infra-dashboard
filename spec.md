# AI Infrastructure Research Platform Spec

## Project Goal

Build a local-first AI infrastructure research workspace.

The project is no longer only a financial dashboard. The dashboard remains useful, but the next phase is to organize research knowledge around companies, industry theses, technologies, products, events, evidence, market indicators, and watchlist / portfolio context.

The platform should help answer:

* What changed in the AI infrastructure ecosystem?
* Which industry thesis is affected?
* Which companies are exposed?
* What evidence supports, weakens, or challenges a thesis?
* Why does this company matter under the current industry thesis?
* What should be reviewed next?

The platform should assist research thinking. It should not replace the user's judgement.

## Current Architecture Assumptions

The current implementation is a local Streamlit app backed by manually editable CSV files.

Current stack:

* Python 3.11+
* Streamlit
* Pandas
* Plotly
* CSV files as the data source

Current architecture:

* `app.py` contains the Streamlit pages and page-level UI functions.
* `src/data_loader.py` contains reusable CSV loading and required-column validation.
* `src/charts.py` contains reusable Plotly chart helpers.
* `data/` contains all local research data.

Near-term architecture rule:

* Keep the app simple and reviewable.
* Keep data local and manually editable.
* Keep schemas explicit.
* Keep facts, evidence, relationships, and theses separate.
* Do not introduce databases, agents, APIs, or background automation in v0.7.

## Data Files

The app should use CSV files in `data/`.

### Existing Files

#### companies.csv

Static company profile data.

Columns:

* company_id
* ticker
* company_name
* exchange
* country
* sector
* ai_infra_category
* website
* description

#### financial_metrics.csv

Quarterly company financial metrics.

Columns:

* company_id
* period
* revenue_usd_m
* revenue_yoy_pct
* gross_margin_pct
* operating_margin_pct
* net_income_usd_m
* eps
* eps_yoy_pct
* capex_usd_m
* free_cash_flow_usd_m
* inventory_usd_m

#### valuation_metrics.csv

Valuation metrics by date.

Columns:

* company_id
* date
* price
* market_cap_usd_m
* trailing_pe
* forward_pe
* price_to_sales
* ev_to_ebitda

#### estimates.csv

Market consensus estimates.

Columns:

* company_id
* period
* estimated_revenue_usd_m
* estimated_eps
* estimated_revenue_yoy_pct
* estimated_eps_yoy_pct
* analyst_count
* revision_direction

#### ai_infra_events.csv

Events, news, earnings call notes, product announcements, pricing updates, and supply chain developments.

Columns:

* event_id
* date
* company_id
* category
* event_title
* summary
* source_url
* importance
* thesis_impact

#### industry_theses.csv

Industry thesis records. Refine this file if needed for v0.7.

Minimum columns:

* thesis_id
* industry_layer
* thesis_category
* thesis_title
* thesis_summary
* key_drivers
* risks
* status
* conviction
* last_reviewed

Optional v0.7 columns:

* thesis_type
* review_frequency
* owner
* key_questions

#### company_exposure.csv

Company-to-industry-thesis exposure file.

Preferred v0.7 columns:

* exposure_id
* company_id
* thesis_id
* exposure_level
* exposure_reason
* evidence_id
* last_reviewed

Migration note:

* The existing `theme_exposure.csv` can be migrated or renamed to `company_exposure.csv`.
* Old `theme` values should map to `industry_theses.industry_layer` or `industry_theses.thesis_category`.

#### watchlist.csv

Personal research and portfolio context.

Columns:

* company_id
* priority
* current_position
* thesis
* risk
* next_check

#### entity_relationships.csv

Existing simple relationship file. In v0.7, replace or refine this into the more general `relationships.csv`.

Current columns:

* relationship_id
* source_entity
* source_type
* relationship_type
* target_entity
* target_type
* notes
* importance

### New v0.7 Files

#### technologies.csv

Technology entities such as HBM, CoWoS, NVLink, CPO, liquid cooling, SiC, GaN, or power shelf architecture.

Columns:

* technology_id
* technology_name
* technology_category
* description
* related_thesis_ids
* maturity_stage
* key_companies
* last_reviewed

Relationship note:

* `related_thesis_ids` is acceptable for simple display.
* The primary source of technology-to-thesis links should be `relationships.csv`.

#### products.csv

Product, platform, architecture, or system entities such as GB300, Blackwell, Rubin, MI300, TPU, AI server racks, or liquid-cooled rack systems.

Columns:

* product_id
* product_name
* primary_company_id
* product_category
* description
* launch_status
* related_technology_ids
* related_thesis_ids
* last_reviewed

Ownership note:

* `primary_company_id` may be blank when a product, platform, architecture, or standard is not owned by a single company.
* Additional product-to-company links should be represented in `relationships.csv`.

#### relationships.csv

General entity relationship table. This should support the first version of the knowledge graph without implementing a graph database.

Columns:

* relationship_id
* source_id
* source_type
* relationship_type
* target_id
* target_type
* reason
* confidence
* evidence_id
* last_updated

Supported first-version entity types:

* Company
* Industry Thesis
* Technology
* Product
* Event
* Evidence
* Market Indicator
* Watchlist / Portfolio Item

Supported first-version relationship types:

* uses
* requires
* belongs_to
* impacts
* benefits
* exposes_to
* competes_with
* supplies_to
* tracked_in
* supports
* challenges
* mentions

#### evidence.csv

Evidence records. Evidence should be observable and source-linked when possible. Evidence is not the same as reasoning or thesis conclusion.

Columns:

* evidence_id
* date
* fact_text
* evidence_title
* evidence_summary
* source_type
* source_url
* related_event_id
* related_company_id
* related_thesis_id
* evidence_direction
* confidence
* notes

Field meaning:

* `fact_text` stores the directly observed fact.
* `evidence_summary` explains why that fact is relevant to a thesis.
* `notes` can hold review context or open questions.

Allowed `evidence_direction` values:

* supports
* weakens
* challenges
* neutral
* needs_review

## Pages

### Existing Pages

Keep existing pages unless a future milestone explicitly removes or merges them.

Current pages:

* Overview
* Companies
* Company Detail
* Financial Metrics
* Valuation
* Estimates
* Events
* Company Exposure
* Watchlist
* Industry Thesis

### v0.7 Page Additions

#### Technology

Purpose:

Show technology entities and their links to industry theses and companies.

Requirements:

* Read from `technologies.csv`.
* Filter by technology category.
* Filter by maturity stage.
* Show related thesis ID and key companies.
* Keep display table-based for v0.7.

#### Product

Purpose:

Show product, platform, and architecture entities.

Requirements:

* Read from `products.csv`.
* Filter by company.
* Filter by product category.
* Filter by launch status.
* Show related technology IDs and related thesis IDs.
* Keep display table-based for v0.7.

#### Evidence

Purpose:

Show evidence records that may support, weaken, challenge, or require review of a thesis.

Requirements:

* Read from `evidence.csv`.
* Filter by evidence direction.
* Filter by related company.
* Filter by related thesis.
* Show source URL as a clickable link if possible.
* Keep evidence separate from conclusions.

#### Relationships

Purpose:

Show explicit connections between entities.

Requirements:

* Read from `relationships.csv`.
* Filter by source type.
* Filter by relationship type.
* Filter by target type.
* Filter by confidence.
* Show reason and linked evidence ID.
* Use a table. Do not build graph visualization in v0.7.

#### Industry Thesis

Purpose:

Continue to show industry theses, but make the page align with the knowledge model.

v0.7 refinements:

* Filter by industry layer.
* Filter by thesis category.
* Show related evidence when available.
* Show related technologies and products when available.
* Keep theses user-reviewable and manually editable.
* Do not automatically update thesis text from evidence.

#### Company Detail

Purpose:

Shift the page from "company facts" toward "Why this company?"

v0.7 refinements:

* Make the first section: "Why this company?"
* In that first section, show thesis exposure.
* In that first section, show exposure reason.
* In that first section, show supporting or challenging evidence.
* In that first section, show recent events.
* In that first section, show watchlist priority and next check.
* Show company profile.
* Show watchlist / portfolio context.
* Show industry thesis exposure.
* Show related evidence.
* Show related technologies and products.
* Show recent events.
* Keep financial and valuation context visible.
* Emphasize why the company matters under current industry theses.

## v0.7 Implementation Scope

Milestone name:

**v0.7 Knowledge Model Foundation**

Implement only the first simple version of the knowledge model.

Required implementation:

* Add `data/technologies.csv` with sample data.
* Add `data/products.csv` with sample data.
* Add `data/relationships.csv` with sample data.
* Add `data/evidence.csv` with sample data.
* Refine `data/industry_theses.csv` if needed.
* Refine or add `data/company_exposure.csv` if needed.
* Add reusable data loading functions and required-column validation for the new CSV files.
* Add Technology page.
* Add Product page.
* Add Evidence page.
* Add Relationships page.
* Refine Industry Thesis page to show knowledge-model context.
* Refine Company Detail page to emphasize "Why this company?" using industry thesis exposure, exposure reason, evidence, recent events, and watchlist context.
* Keep all new data manually editable.

Implementation constraints:

* Prefer tables and simple filters.
* Prefer clear CSV schemas over clever abstractions.
* Use functions, not classes, unless there is a clear need.
* Keep code understandable for a beginner Python/Streamlit reader.
* Keep the current local Streamlit app structure.

## Out Of Scope

Do not implement in v0.7:

* External APIs
* Web crawlers
* Autonomous agents
* LLM agent workflows
* Automatic news analysis
* Automatic thesis updates
* Buy / sell recommendations
* Recommendation engine
* Graph database
* Complex graph visualization
* Login system
* Cloud deployment
* Background jobs
* Automated data updates

## Code Requirements

* Keep code simple and beginner-friendly.
* Avoid unnecessary classes.
* Use functions where possible.
* Create reusable data loading functions.
* Validate that required CSV columns exist.
* Display a clear Streamlit error message if a CSV file is missing or columns are missing.
* Keep CSV schemas explicit in `src/data_loader.py`.
* Keep chart helpers in `src/charts.py`.
* Keep page logic readable in `app.py`.
* App should run with:

```bash
streamlit run app.py
```

Testing expectations:

* Run `python -m py_compile app.py src/data_loader.py src/charts.py`.
* Use Streamlit app testing or manual startup to verify new pages render.
* Report exactly what checks were run.

## Design Principles

### Local First

All v0.7 data should live in local CSV files.

### Manual And Reviewable

The user should be able to open every data file, understand it, and edit it manually.

### Facts Before Reasoning

Evidence should store observable facts and source context. Reasoning and thesis conclusions should remain separate.

### Explainable Relationships

Relationships should include a reason, confidence, and optional evidence link.

### Research Before Investment

The platform should support research quality. It should not generate buy or sell recommendations.

### Simple Before Powerful

Prefer a useful table and filter over a complex visualization or abstraction.

### Preserve Existing Workflows

Existing financial, valuation, event, watchlist, company-exposure, and company-detail workflows should remain usable while the knowledge model is added.
