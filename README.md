# affiliate-content-agent

A beginner-friendly Python project for building a compliance-aware affiliate content workflow.

It loads product data, scores products, generates affiliate-ready drafts, runs compliance checks, stores drafts in a human review queue, and supports safe dry-run publishing previews.

The project is designed for a human-in-the-loop workflow:
- the app can prepare drafts
- the review queue helps organize decisions
- publishing is intentionally guarded
- compliance checks support safer content handling

This project does not replace legal review, platform policy review, or final editorial judgment.

## Why This Project Matters

Affiliate content workflows often break down in one of two ways:
- they are too manual, slow, and inconsistent
- they automate too aggressively and skip compliance review

This project focuses on the middle ground:
- modular automation
- readable Python code
- explicit approval steps
- safer defaults

That makes it a useful portfolio project for showing:
- Python application structure
- config and logging practices
- SQLite workflow design
- test coverage with pytest
- compliance-aware product thinking

## What The Project Does

The current workflow supports:
- loading products from a mock provider
- scoring products for simple internal ranking
- building affiliate-tagged links
- generating plain-language draft content
- attaching disclosure text
- checking drafts for common compliance issues
- saving drafts and compliance results to SQLite
- reviewing drafts manually through a terminal queue
- previewing publishing behavior in `DRY_RUN` mode

## Human-In-The-Loop Workflow

The intended workflow is:

1. Load products
2. Score products
3. Generate drafts
4. Run compliance checks
5. Save drafts to the approval queue
6. Review drafts manually
7. Use dry-run publish preview before any live publishing step

Drafts are not auto-approved, and publishing should not happen without human review.

## Architecture Overview

```text
Product Source
    |
    v
Deal Scoring
    |
    v
Link Builder
    |
    v
Draft Generator + Disclosure
    |
    v
Compliance Checks
    |
    v
SQLite Approval Queue
    |
    v
Manual Review Queue
    |
    v
DRY_RUN Publish Preview
```

## Project Structure

```text
affiliate-content-agent/
├─ app/
│  ├─ approval_queue.py
│  ├─ compliance.py
│  ├─ config.py
│  ├─ db.py
│  ├─ deal_scoring.py
│  ├─ disclosure.py
│  ├─ drafts.py
│  ├─ link_builder.py
│  ├─ logger.py
│  ├─ main.py
│  ├─ models.py
│  ├─ product_source.py
│  └─ publishers/
│     └─ facebook_page.py
├─ scripts/
│  └─ review_queue.py
├─ tests/
├─ data/
├─ requirements.txt
└─ README.md
```

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/trenpatterson-dot/affiliate-content-agent.git
cd affiliate-content-agent
```

### 2. Create and activate a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

macOS / Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

## Environment Configuration

Create a local `.env` file in the project root.

Example:

```env
AMAZON_ASSOCIATE_TAG=yourtag-20
APP_ENV=development
LOG_LEVEL=INFO
DEBUG=false
DRY_RUN=true
FACEBOOK_PAGE_ID=
FACEBOOK_PAGE_ACCESS_TOKEN=
```

### Required settings

- `AMAZON_ASSOCIATE_TAG`

### Common optional settings

- `APP_ENV`
- `LOG_LEVEL`
- `DEBUG`
- `DRY_RUN`
- `DATABASE_PATH`
- `FACEBOOK_PAGE_ID`
- `FACEBOOK_PAGE_ACCESS_TOKEN`

Notes:
- `.env` is for local development convenience
- real environment variables override `.env`
- `.env` should not be committed to Git

## How To Run

### Run the app

```bash
python -m app.main
```

Current workflow example:

```text
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Starting amazon-affiliate-content-agent in development mode
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Configuration loaded: {...}
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Database ready at ...\data\agent.db
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Loading products from the default product source
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Loaded 4 products from the default provider
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Scoring loaded products
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Scored 4 products
2026-04-09 19:42:45 | INFO | amazon_affiliate_agent | Workflow complete
Workflow Summary
- total products loaded: 4
- total drafts generated: 12
- drafts ready for review: 12
- drafts blocked: 0
```

### Run the review queue

```bash
python -m scripts.review_queue
```

Example menu:

```text
Approval Queue
1. List all drafts
2. List drafts by status
3. Inspect one draft
4. Approve a draft
5. Reject a draft
6. Exit
```

### Run the tests

```bash
python -m pytest
```

Example test output:

```text
============================= test session starts =============================
collected 30 items
...
============================= 30 passed in 0.27s ==============================
```

## End-To-End Workflow

The project is organized around a safe draft pipeline:

1. The product source layer loads products from the mock provider
2. The scoring layer ranks products for internal review
3. The link builder creates affiliate-tagged URLs
4. The draft generator creates multiple draft styles per product
5. The compliance layer checks disclosure, link presence, and wording risks
6. The approval queue stores drafts and compliance results in SQLite
7. A reviewer inspects drafts in the terminal review queue
8. Publishing remains guarded and supports dry-run preview mode

## Testing

The project uses `pytest` and includes tests for:
- config validation
- mock product loading
- deal scoring
- affiliate link building
- disclosure handling
- draft generation
- compliance checks
- approval queue save/load/status flow
- app startup smoke tests

The tests are designed to be:
- local
- readable
- free from live API requirements
- safe to run repeatedly

SQLite tests use temporary database files where practical.

## Safety And Compliance

This project is intentionally conservative.

It aims to support a compliance-aware workflow by:
- requiring disclosure text in drafts
- checking for blocked hype language
- checking for risky price and availability wording
- keeping approval as a separate human step
- preventing publishing unless a draft is already approved
- supporting `DRY_RUN` publishing previews

Important limits:
- this project does not replace legal review
- this project does not guarantee policy compliance
- this project does not verify live product truth automatically
- this project does not scrape Amazon product pages

Any content produced by the system should still be reviewed by a human before publication.

## Current Status

The project currently supports:
- mock product sourcing
- local draft generation
- SQLite approval queue storage
- terminal review flow
- Facebook Page publisher dry-run preview
- pytest coverage for core modules

Live publishing APIs are intentionally kept incomplete so the default behavior stays safe.

## Future Improvements

Possible next steps include:
- real provider integrations behind the existing provider interface
- richer approval queue filtering and search
- storing scoring results in SQLite
- adding structured reviewer notes
- adding CSV or JSON export for draft batches
- implementing safe live publisher integrations
- adding CI for automated test runs
- expanding compliance checks with configurable rule sets
- adding richer draft templates for different platforms

## Portfolio Notes

This project is a strong portfolio example because it combines:
- Python application structure
- modular architecture
- practical data flow
- local persistence
- test-driven reliability
- compliance-aware product design

It is especially relevant for roles involving:
- backend Python development
- workflow automation
- content systems
- creator tools
- safety-conscious product engineering
