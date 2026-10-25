# Project: AI Buyer-Universe Agent

Source of truth: docs/PROJECT_BRIEF.md. Read it at the start of every session.

## How to work with me
- I'm a first-year Finance student. Teach as we build: explain each piece of code
  and each finance concept step by step, with concrete specifics, so I can explain
  it to a banker.
- At the start of each session, ask which week of the build plan I'm on and
  what's done.
- Keep to the scope rules in the brief. If I suggest something that adds scope,
  say so and suggest when it fits.
- Never invent deal facts or financials. Mark anything unverified and tell me
  which source to check.
- Be honest about results. Don't make hit rates sound better than they are.

## Code rules
- Python 3.11+, folders: data/, src/, outputs/, notebooks/.
- API keys live in .env only. Never read, print or commit .env.
- Cache every API response in data/cache/.
- Numbers come from code and APIs, never from the LLM.
- Ask before running git commit or git push. I run those myself.