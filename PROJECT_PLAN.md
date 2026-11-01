---
project: Life_Companion
as_of: 2026-11-01
active_sprint: P2
scope: single_sprint
approved_sprints: P2
operator_approved: true
---
# Life_Companion - project plan

Sources: core/PLAN_2026_05_11_MVP.md (7-phase MVP plan, approved 2026-05-13), core/PHASE_1_REVIEW_BACKLOG.md, core/GUARDRAILS.md, CLAUDE.md, README.md, git history (HEAD 0f11da3, branch main). The project has been dormant since 2026-07-28; no Phase 2 work exists.

## Roadmap
| Sprint | Title | Status | Goal |
|---|---|---|---|
| P0 | Bootstrap | ACCEPTED | Project scaffold, plan and guardrails committed (7a5dab5) |
| P1 | Foundation | PARTIAL | FastAPI, DB schema, auth, LLM adapter, crisis scaffold, Flutter skeleton; CRITICAL/HIGH review fixes applied (28a4482), MEDIUM/LOW backlog open |
| P2 | Daily check-in and crisis (with Phase 1 backlog) | ACTIVE | Close the Phase 1 MEDIUM backlog the project says must precede Phase 2, then deliver Socratic reflection, crisis detection v1 and journal CRUD |
| P3 | Pattern and weekly review | NOT_STARTED | Embedding-based pattern surfacing and weekly 6-axis review |
| P4 | Health pillar v1 | NOT_STARTED | Document upload, plain-language translation, visit prep, no-diagnosis enforcement |
| P5 | Subscription and payments | NOT_STARTED | Stripe and YooKassa, tier gating, paywall flows |
| P6 | North Star instrumentation | NOT_STARTED | Retention cohorts, "this helped" survey, referral tracking |
| P7 | Polish and alpha | NOT_STARTED | Onboarding polish, store assets, soft launch with 10 friends |

## Sprint P2 - Daily check-in and crisis (with Phase 1 backlog)
Goal: Phase 2 of core/PLAN_2026_05_11_MVP.md (exit: crisis detection 100% branch coverage; e2e "I want to die" shows the hotline screen), preceded by the pre-Phase-2 backlog items from core/PHASE_1_REVIEW_BACKLOG.md. Dormant project: tasks are the plan's own scope, none started.

| Task | Title | Acceptance | Status | Evidence | Owner | Depends | Commit |
|---|---|---|---|---|---|---|---|
| P2-T01 | Close Phase 1 MEDIUM review backlog | PY-M*, SEC-M*, DB-M*, FL-M* items fixed or consciously deferred in core/PHASE_1_REVIEW_BACKLOG.md | NOT_STARTED | Backlog lists about 30 MEDIUM/LOW items open; CRITICAL+HIGH (27) already applied in 28a4482 | assistant | | |
| P2-T02 | Rate limiting on the FastAPI app | Rate limiter wired before Phase 2 endpoints (SEC-M4) | NOT_STARTED | CLAUDE.md states no rate limiting exists | assistant | | |
| P2-T03 | Initial Alembic migration | First schema migration generated from models.py | NOT_STARTED | Backlog pre-Phase-2 note 5; backend/ is empty per CLAUDE.md | assistant | | |
| P2-T04 | Crisis detection v1 | Regex plus LLM classifier plus hotline routing; 100% branch coverage on crisis module | NOT_STARTED | Phase 2 exit criteria; only a crisis scaffold and hotline map exist from Phase 1 | assistant | P2-T01 | |
| P2-T05 | Socratic reflection (Gemini) and journal CRUD | Reflection engine and journal endpoints working | NOT_STARTED | Phase 2 scope; no Phase 2 commits | assistant | P2-T01 | |
| P2-T06 | Flutter chat UI and daily push reminder | Basic chat UI; e2e: user submits "I want to die", hotline screen shown | NOT_STARTED | Phase 2 exit criteria; operator setup (flutterfire configure, env json) listed in backlog | assistant | P2-T04, P2-T05 | |
