> **Inherits global rules from `D:\test 2\CLAUDE.md`** — approval gate, no-guessing, regression tests, git lifecycle (including todo-in-commits), shell pre-approval, D:-drive-only disk policy, agents-first routing, cite-source rule, validate-logs-before-success rule. Read that file too.

# Life Companion — Project Context

## What this is

A daily-use mobile + backend product that helps everyday people work on three pillars of their life with affordable subscriptions:

1. **Life pillar — reflection & patterns.** Daily 60-second Socratic check-in, weekly life-balance review across 6 areas (profession, family, hobby, sport, entertainment, outdoors), pattern surfacing across history.
2. **Mind pillar — emotional support (NOT therapy).** Socratic reflection, CBT-style cognitive reframes, crisis detection → hotline handoff, optional human coach affiliate.
3. **Health pillar — navigation, NOT diagnosis.** Medical document interpreter, doctor-visit prep + follow-up, symptom triage, medication helper, chronic condition log.

**Target user:** "simple people" with small budgets (free / $3 / $8 tiers + $1.99–$4.99 à la carte problem packs). Primary launch market: Russia/CIS; architecture EU-compliant for later expansion.

**Tagline:** "The friend who knows your feelings, your life patterns, and your health — and never forgets."

## What this is NOT

- **NOT therapy / psychoanalysis** — illegal without licensed clinicians; positioned as "reflective coaching."
- **NOT an AI doctor** — illegal as a medical device without FDA/EMA/Roszdravnadzor clearance; positioned as "health navigation + medical translation."
- **NOT engagement-maximizing** — DAU / session-length explicitly NOT optimized. North Star = 30-day retention + monthly "this helped" yes-rate.

## North Star metric

1. **Primary:** 30-day retention (weekly cohort tracking on internal dashboard).
2. **Secondary:** Monthly "this helped me" survey yes-rate (≥60% target).
3. **Tertiary:** Voluntary referrals per user.
4. **NEVER on dashboard:** DAU, session length, streak-break rate. These are tracked for billing only and never optimized.

## Hard guardrails (NON-NEGOTIABLE — see core/GUARDRAILS.md)

- **Crisis detection ships before first user.** Pattern matching + LLM classifier on every message; on hit → immediate hotline display (988 US, 116 123 EU, 8-800-2000-122 RU) + suppress AI conversation until acknowledged.
- **No diagnoses.** AI never says "you have X" — only "I notice X, here are questions for your doctor."
- **No streaks-as-shame.** No "you broke your streak" notifications. Streaks shown as celebrations only.
- **No engagement A/B testing on emotional content.** Only on UX (button placement, copy).
- **No paywall on crisis support.** Free tier or not, crisis flow always works.
- **Disclaimers** on every health screen + every emotionally heavy reflection.
- **Mental + medical data encrypted at rest with per-user keys.** No third-party analytics on these screens.
- **152-ФЗ compliant** for RU users (data localized via Yandex Cloud mirror if launched in RU).
- **GDPR-compliant** export + delete from day 1.

## Layout

- Working directory: `D:\test 2\Life Companion`
- Python venv: `venv\` (create with `python -m venv venv` then `venv\Scripts\pip install -r requirements.txt`)
- Backend source: `src/`
  - `src/api/` — FastAPI routes
  - `src/reflection/` — Socratic engine, prompt templates
  - `src/patterns/` — history analyzer, weekly review
  - `src/health/` — doc interpreter, triage, meds, chronic log
  - `src/crisis/` — crisis detection (highest-tested module)
  - `src/billing/` — Stripe + YooKassa adapters
  - `src/db/` — SQLAlchemy models, Alembic migrations
  - `src/llm/` — multi-provider adapter (Gemini / Claude / OpenAI)
  - `src/auth/` — Firebase Auth verification middleware
- Backend tests: `tests/`
- Mobile app: `mobile/` (Flutter; `flutter create mobile --project-name life_companion` once Flutter SDK ready)
- Plans + docs: `core/`
- Memory pointer: index in `MEMORY.md` cross-project location

## Stack

| Layer | Choice | Why |
|---|---|---|
| Backend framework | FastAPI (Python 3.12) | Async, type-checked, matches trading-bot skillset |
| DB | PostgreSQL 16 | Relational user data; mature, GDPR-friendly |
| Cache / rate limit | Redis 7 | Sessions, idempotency, rate limits |
| Mobile | Flutter 3.x | Cross-platform Android+iOS from day 1 |
| Auth | Firebase Auth | Multi-platform, OAuth providers, cheap |
| LLM primary | Gemini 3.1 Pro (`gemini-3.1-pro-preview`) | Matches operator's existing setup |
| LLM safety | Claude Sonnet 4.6 | Used for crisis detection + sensitive content |
| LLM cheap classify | OpenAI o-mini | Fast intent classification |
| Payments (global) | Stripe | Standard |
| Payments (RU) | YooKassa | RU compliance |
| Push | FCM | Standard |
| Hosting (backend) | Hetzner Cloud (EU-Germany) | Cheap, reliable |
| Hosting (RU mirror) | Yandex Cloud | 152-ФЗ data localization (only if RU launch) |
| Observability | OpenTelemetry + Grafana Cloud (free tier) | Cross-stack tracing |

## Tests (canonical regression suite)

- `venv\Scripts\python.exe -m pytest tests/ -x -q` — 0 failures gate every push.
- After every code change, add/update assertions and verify 0 failures (per global rule).
- **Functional tests prove behavior** — every test must call the code and assert on observable state. String-match-only tests are NOT acceptable as sole proof.
- **Crisis detection module has its own test suite** at `tests/crisis/` with 100% branch coverage required (this module gates life-or-death paths).
- Mobile: `flutter analyze` + `flutter test` from `mobile/`.

## Per-task workflow

- Run `pytest tests/ -x -q` after every backend change.
- For mobile changes: `cd mobile && flutter analyze && flutter test`, plus build APK and visually verify on emulator for UI changes.
- For features that touch the FastAPI server: restart via `.\restart.ps1` (to be written in Phase 1) and verify health endpoints + sample API call.

## Project plan & state

- Outstanding-work plan: `core/PLAN_2026_05_11_MVP.md` (consolidated 7-phase MVP, ~7-8 weeks).
- Guardrails spec: `core/GUARDRAILS.md` (crisis detection, no-diagnosis rules, disclaimer copy, privacy controls).
- Privacy + legal copy: `core/PRIVACY_LEGAL.md` (GDPR / 152-ФЗ / disclaimer templates) — to be written before launch.

## Defaults (per operator approval 2026-05-13)

- Launch geography: Russia/CIS first, EU-compliant architecture from day 1.
- User segment: all three (overwhelmed / stuck / self-improving) — onboarding picks primary mode and tailors prompts.
- Medical advisor: hire part-time GP starting month 2 ($500-800/mo) to review prompts + crisis rules.
- Diagnosis policy: NEVER says "you have X" — always "I notice X, here are questions for your doctor."
