# AI Buyer-Universe Agent — Project Brief

Oct 23, 2026 · @Jegajeeth

## Overview

The project is an AI agent that, given a target company, produces a ranked list of likely acquirers. Its quality is tested against real UK deals, and that test is the headline result.

**One-line pitch:** an agent that does a task M&A analysts spend days on, tested on around 30 completed UK deals, with a documented analysis of where it fails and why.

**Why this project:**

- Buyer lists ("buyer universes") are core work for advisory analysts, at firms like Rothschild, Lazard, Jefferies and Kroll.
- Measuring the agent against real outcomes shows practical AI skill: designing an evaluation, controlling for data leakage, and analysing errors.
- It came out of a networking conversation in which a banker said teams want new hires who are fluent with AI and can use it well.
- Target timeline: about 6 weeks part-time, with a working version before spring week and internship interviews in early 2027.

## Context about me

I'm a first-year BSc (Hons) Finance student at the University of Bristol, and I started in September 2026.

- **Coding:** Python, A-level Computer Science. Previous projects: an LSTM stock forecaster, and a news-sentiment portfolio risk app built in Python and Flask using the Alpaca News API.
- **Finance:** an accounting internship, Financial Times student advocate, Morgan Stanley Summer Academy, and Equities Analyst (emerging markets) at the Bristol Trading Society.
- **Target roles:** spring weeks and internships in advisory and investment banking (Rothschild, Lazard, Jefferies, Kroll), plus markets roles.

**Goals for the project:**

1. A working tool on GitHub with a clear README.
2. One headline accuracy result I can quote in interviews.
3. A 2-page write-up and a 60-second verbal explanation.
4. I want to understand every part well enough to explain it to a banker. The project should not be too quant-heavy.

## What the agent does

The agent takes one target company and returns four outputs that together look like an analyst's first-pass buyer analysis.

**Input:** a target company profile: name (or an anonymised description), sector, geography, revenue, EBITDA, business description, and approximate deal size.

| Output | What it contains | Analyst equivalent |
| --- | --- | --- |
| 1. Ranked buyer list | Top 10–20 strategic buyers and PE firms, each with a score and a 2–3 line rationale (strategic fit, product or customer overlap, geographic logic) | Buyer universe |
| 2. Ability-to-pay check | Each buyer's market cap, net debt/EBITDA, estimated debt headroom and recent acquisitions, plus a flag if it can't afford the deal | Buyer financial screening |
| 3. Precedent deals | 5–10 comparable sector transactions with EV/EBITDA or EV/Revenue multiples where available | Precedent transactions table |
| 4. Pitch slide | A one-page summary of the top 5 buyers and an implied valuation range | Pitch book page |

**Buyer types to cover:**

- **Strategic:** competitors, companies in adjacent sectors, and overseas players wanting to enter the UK.
- **Financial:** PE funds with existing sector platforms, which buy add-on acquisitions, plus generalist mid-market funds.

**Scoring idea (version 1):** a weighted score of strategic fit (LLM-judged, 1–5), ability to pay (rule-based from financials), and acquisition track record (count of recent deals in the sector). The weights are documented and adjustable.

## Evaluation: the backtest

The headline metric is **top-10 hit rate**: the share of completed deals where the real acquirer appears in the agent's top 10.

**Method:**

1. Build a dataset of 25–30 completed UK acquisitions with known buyers (see Data).
2. For each deal, give the agent only the target's pre-deal profile, with the outcome hidden.
3. Record where the real acquirer ranks (1–20, or "not listed").
4. Report top-1, top-5 and top-10 hit rates, plus the hit rate split by buyer type (strategic vs PE).
5. Compare against a simple baseline, such as "the 10 largest companies in the same sector", to show the agent adds value beyond the obvious.

**Data leakage (the most important risk):** the LLM may already know who bought a company from its training data, which would make the test meaningless. Controls:

- **Anonymise targets:** describe the company by sector, size and business model, with no name, brands or distinctive details.
- **Post-cutoff deals:** where possible, include deals announced after the model's training cutoff, and report results for them separately.
- **Closed-book check:** ask the model directly "who acquired X?" for each deal. If it knows, flag that deal as contaminated and report results with and without it.
- **Restricted reasoning:** tell the agent to rank only from the data it's given, and log its rationale so leaks can be spotted.

**Error analysis:** for each miss, record the reason: a PE buyer was missed, a cross-border buyer was missed, the buyer was too small or private, or the deal was opportunistic or unpredictable. The patterns in the misses become the "what I learned" story.

## Data

All data sources are free. Each needs confirming at build time, because access terms change.

| Source | Used for | Notes |
| --- | --- | --- |
| Companies House API | UK private and public company profiles, filed accounts, SIC codes | Free API key; many accounts are in iXBRL format |
| FCA National Storage Mechanism / RNS announcements | Listed-company annual reports and deal announcements | Good for confirming deal dates and terms |
| Takeover Panel disclosure table | List of UK public-company offer periods | Useful for finding public deals |
| Market data library (e.g. yfinance) | Buyer market caps and share prices | Unofficial; cross-check key figures |
| Bloomberg Terminal (university) | Deal multiples and buyer financials | If Bristol has access; use for verification |
| Financial news (FT, Reuters) | Deal rationale and buyer identity | For the dataset only, never fed to the agent during testing |

**Deal dataset (a hand-built spreadsheet, one row per deal):**

| Column | Example of what goes in it |
| --- | --- |
| deal\_id | D001 |
| target\_name | Real name (hidden from the agent) |
| target\_anon\_description | Sector, size and business model in 3–4 sentences, no names |
| sector / sub-sector | e.g. B2B software / payroll |
| target\_revenue\_gbp\_m, target\_ebitda\_gbp\_m | Pre-deal figures |
| announce\_date | ISO date |
| acquirer\_name | The real buyer (the answer) |
| acquirer\_type | Strategic / PE / Other |
| acquirer\_country | UK / US / EU / Other |
| ev\_gbp\_m, ev\_ebitda | Deal value and multiple, if disclosed |
| source\_url | Where the deal facts came from |
| post\_cutoff | Yes / No |
| model\_knows\_answer | Yes / No (from the closed-book check) |

**Selection rules:** a mix of sectors (no more than 5 deals from any one), a mix of strategic and PE buyers (aim for about 50/50), and deal sizes roughly £20m–£2bn, so that buyers are realistically identifiable.

## Architecture and tech stack

The LLM does the judgment work (who might buy, and why). Code does anything numerical, so figures are never invented.

&#91;embedded content: agent pipeline and backtest · 7 components\]

The top row runs for every target. The bottom row scores the agent's predictions against the real acquirers.

| Layer | Tool | Purpose |
| --- | --- | --- |
| Language | Python 3.11+ | Everything |
| Data handling | pandas, requests | Deal dataset, API calls |
| LLM | An LLM API with structured JSON output | Buyer proposals and rationales |
| Market data | Companies House API, yfinance | Target and buyer financials |
| Caching | JSON files or SQLite | Avoid repeat API costs; reproducible runs |
| Outputs | python-pptx or HTML to PDF | Pitch slide |
| Analysis | Jupyter notebook | Backtest results and charts |
| Version control | GitHub | Public portfolio piece |

**Folder structure:** data/ (deals.csv, cache/), src/ (profile.py, agent.py, financials.py, rank.py, outputs.py, backtest.py), outputs/, notebooks/, README.md.

## Six-week build plan

The plan assumes 5–8 hours a week alongside my degree. Each week ends with something that works, even if it's rough.

1. **Week 1: Set-up and deal dataset (part 1)**
   - Create the GitHub repo, a Python virtual environment, a .env file for API keys, and a README skeleton.
   - Get a Companies House API key and pull one company profile as a test.
   - Fill in the first 15 deals in the spreadsheet.
2. **Week 2: Dataset (part 2) and target profiles**
   - Complete 25–30 deals.
   - Write the anonymised descriptions and run the closed-book contamination check.
   - Write a script that builds a target profile from Companies House data.
3. **Week 3: Agent version 1**
   - LLM prompt: target profile in, 20 candidate buyers out as structured JSON (name, type, rationale, fit score).
   - Code step: fetch each buyer's market cap and net debt, apply the ability-to-pay filter, and re-rank.
   - Run it on 3 deals by hand and read the outputs closely.
4. **Week 4: Outputs**
   - Precedent deals table and implied valuation range.
   - Generate the one-page pitch slide (python-pptx or an HTML page exported to PDF).
5. **Week 5: Backtest and error analysis**
   - Run all deals, record rankings, and calculate top-1, top-5 and top-10 hit rates against the baseline.
   - Categorise every miss, then make one improvement and re-run (e.g. a dedicated PE-buyer prompt).
6. **Week 6: Write-up and polish**
   - README with results table, method and limitations.
   - 2-page PDF summary, and the CV bullet.
   - Practise the 60-second explanation out loud.

## Risks, limitations and scope rules

The biggest threats to the project are data leakage and scope creep, so both get explicit rules.

| Risk | What could go wrong | Mitigation |
| --- | --- | --- |
| Data leakage | Model recalls the real buyer from training data | Anonymisation, post-cutoff deals, closed-book check (see Evaluation) |
| Hallucinated buyers or figures | LLM invents a company or financial numbers | Financials come from code and APIs, never from the LLM; check every named buyer exists |
| Small sample | 30 deals gives noisy hit rates | Present results as indicative, show per-deal results, avoid over-claiming |
| Private-company data gaps | Little public data for private targets and buyers | Use filed accounts; mark missing fields clearly |
| API costs | LLM calls add up | Cache every response, test on 3 deals before full runs, use a cheaper model for iteration |
| Scope creep | Project never finishes | Follow the scope rules below |

**Scope rules:**

- UK targets only in version 1.
- No web front-end until the backtest is done. A command-line tool plus generated files is enough.
- No fine-tuning or training models. The work is prompting, retrieval and evaluation.
- Every number in an output must be traceable to a source or a calculation.
- Never use confidential or non-public information. Public data only.

## Deliverables and interview pitch

The finished project is four things: the repo, the results, a short write-up, and a story I can tell in 60 seconds.

**Deliverables:**

- [ ] GitHub repo with code, README, results table, and sample output for 2–3 deals
- [ ] Deal dataset (CSV) with sources
- [ ] Sample pitch slide (PDF)
- [ ] 2-page summary: problem, method, results, failure analysis, next steps
- [ ] CV bullet
- [ ] Rehearsed 60-second explanation

**CV bullet (template, filled in once results exist):**

> Built an AI agent that generates M&A buyer universes for UK targets (Python, LLM API, Companies House data); backtested on \[N\] completed deals, where the real acquirer ranked in the top 10 in \[X\]% of cases vs \[Y\]% for a sector-size baseline.

**60-second explanation:**

1. **Problem:** finding likely buyers is one of the first things an M&A team does for a sell-side mandate, and it takes analysts days.
2. **What I built:** an agent that proposes and ranks buyers, checks whether they can afford the deal, and produces a pitch page.
3. **How I tested it:** \[N\] real UK deals with the outcome hidden. The real buyer was in the top 10 \[X\]% of the time.
4. **What went wrong and what I learned:** e.g. it missed PE add-on buyers, and the model sometimes already knew the answer, so I built a contamination check.
5. **Responsible use:** every number comes from source data, and in a real bank I'd only use approved tools for client information.

**Likely interview questions to prepare for:**

- "How do you know it isn't just remembering the answer?"
- "Why did it miss the deals it missed?"
- "How would a bank actually use this?"
- "What would you do differently with more data?"

## Instructions for Claude in this project

Treat this brief as the source of truth for the project, and help me build it week by week.

- **Teach as we build:** explain each piece of code and each finance concept (EV/EBITDA, debt headroom, buyer types) step by step, with concrete specifics, so I can explain it in an interview myself.
- **Keep to the scope rules.** If I suggest something that adds scope, point it out and suggest when it fits.
- **Be honest about results.** If the hit rate is low, help me analyse why. Don't make the results sound better than they are.
- **Never invent deal facts or financials.** Mark anything unverified and tell me to check it against a source.
- **Code style:** Python, clear file structure (data/, src/, outputs/, notebooks/), cached API responses, and API keys in .env files, never in code.
- **Track progress:** at the start of each session, ask which week I'm on and what's done, then pick up from the build plan.
- **Writing:** when helping with CV lines or write-ups, let the results speak for themselves. No comparative phrases like "unlike most students".
