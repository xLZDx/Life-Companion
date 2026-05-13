# Life Companion — Hard Guardrails

**Status:** Mandatory. Every guardrail in this document is non-negotiable.
**Inherits:** Global rules at `D:\test 2\CLAUDE.md`.
**Cross-ref:** Plan at `.\PLAN_2026_05_11_MVP.md`. Project context at `..\CLAUDE.md`.

Violating any rule here = a release blocker. No exceptions, no "we'll fix it in v2", no "the LLM is good enough."

---

## 1. Crisis detection — life-or-death module

**Highest priority module in the product.** Implemented in `src/crisis/`. 100% branch coverage required in `tests/crisis/`.

### 1.1 Triggers (any of these → immediate crisis flow)

- Suicidal ideation: "want to die", "kill myself", "end it all", "no reason to live", "everyone better without me", + RU equivalents ("хочу умереть", "покончить с собой", "не хочу жить")
- Self-harm: "cut myself", "hurt myself", "deserve pain"
- Imminent harm to others: "going to hurt them", "kill him/her"
- Active abuse / domestic violence: "he hits me", "she's hurting the kids", + RU equivalents
- Medical emergencies: chest pain + sweating + arm tingling, stroke signs (FAST), severe allergic reaction, seizure, severe bleeding

### 1.2 Detection pipeline

1. **Regex layer** — fast, exhaustive multilingual list (English, Russian, expandable). Located in `src/crisis/detector.py::REGEX_TRIGGERS`. Updated based on real user data quarterly (no PII stored).
2. **LLM classifier layer** — Claude Sonnet 4.6 (NOT Gemini — Claude has better safety calibration). System prompt: "Classify if this message indicates risk to self/others or a medical emergency. Respond YES_<category> or NO." Cached for cost.
3. **OR logic** — if regex OR LLM classifier flags, treat as positive. Never AND.

### 1.3 Response

On any positive detection:
1. **Stop AI conversation.** No further generative response.
2. **Display crisis card** with geo-appropriate hotline:
   - RU: 8-800-2000-122 (kids), 8-499-791-20-50 (adults), 112 (emergency)
   - US: 988 (Suicide & Crisis Lifeline), 911 (emergency)
   - EU: 116 123 (Samaritans), 112 (emergency)
   - Detected by user profile geography → fallback to all three if unknown
3. **One-tap dial** button.
4. **"I'm safe, continue" button** — requires explicit user tap (not auto-dismiss) to resume.
5. **Logged** to `crisis_events` table (encrypted, admin-audit only) — for product safety review, NEVER for ML training.
6. **No paywall.** Crisis flow works on free tier, expired subscription, anywhere in the app.

### 1.4 Test requirements

- Unit test every trigger phrase (parametrized) — English + Russian.
- Integration test: TestClient POST `/api/reflect` with "I want to die" → response includes `crisis: true` + hotline data + `ai_response: null`.
- Mutation test: if `detector.py` is mutated to return False, all crisis tests must fail.
- Regression test: every false-negative caught in production becomes a new test case.

---

## 2. No diagnoses — medical safety

### 2.1 Prohibited language

The product never says, in any UI text, AI response, push notification, email, or marketing copy:

- "You have [condition]"
- "You're suffering from [X]"
- "This is [diagnosis]"
- "I diagnose..."
- "Your condition is..."
- "You need [specific drug name + dose]"
- Russian equivalents: "у вас [болезнь]", "вы больны", "диагноз — ...", "вам нужно [препарат + доза]"

### 2.2 Allowed language

- "I notice you describe [symptoms]"
- "These signs are worth discussing with a doctor"
- "Here are questions to ask your physician"
- "This range of values is outside the typical reference range — your doctor can interpret what that means for you"
- "Educational only — not medical advice"

### 2.3 Enforcement

- **System prompt** for all health-pillar LLM calls includes the explicit prohibition with examples.
- **Post-generation filter** (`src/health/safety_filter.py`) regex-checks output for diagnostic phrases before delivery. On hit → regenerate once; if still hits → return "I'd rather not say that — please see a doctor for diagnosis."
- **Unit test** every prohibited phrase against the filter.

### 2.4 Drug data

- Only sourced from authoritative public databases: **OpenFDA** (US), **EMA** (EU), **GRLS / РЛС** (Russia).
- AI never invents dosages, brand names, or interactions.
- Drug-drug interactions surfaced from RxNav / public-domain interaction tables only.

---

## 3. Engagement ethics

### 3.1 Banned dark patterns

- ❌ "You broke your streak!" notifications.
- ❌ Push notifications with manufactured urgency ("Don't miss out!", "Last chance!").
- ❌ Counters showing "days since last check-in" framed as guilt.
- ❌ Infinite scroll on reflection history.
- ❌ Variable-reward / gamification on emotional content.
- ❌ A/B testing AI responses to maximize session length or DAU.

### 3.2 Permitted engagement mechanics

- ✅ User-scheduled reminders ("remind me at 9pm" — only if user opted in).
- ✅ Streak shown as a celebration in profile view (no "broken" state).
- ✅ Weekly summary email/push at a user-chosen time, opt-in.
- ✅ A/B testing on UX (button placement, copy clarity, onboarding flow) — NOT on emotional content.

### 3.3 North Star discipline

- The metrics dashboard shows: 30-day retention, monthly "this helped" yes-rate, voluntary referrals.
- The metrics dashboard does NOT show: DAU, session length, streak-break rate, time-in-app.
- The hidden metrics are tracked for billing only and excluded from any optimization PR review.

---

## 4. Disclaimers — required UX

### 4.1 Health pillar

Every health-pillar screen (doc interpreter, triage, meds, chronic log, visit prep, follow-up) shows above the AI response:

> **Educational only — not medical advice. Always consult a licensed physician.**

(RU translation: **Только для справки — это не медицинская консультация. Всегда обращайтесь к лицензированному врачу.**)

### 4.2 Mind pillar

Every reflection / Socratic conversation screen shows on first open per session (dismissable for that session, re-shown next session):

> **This is reflective coaching, not therapy. If you need professional support, [find a therapist].**

(RU: **Это рефлексивный коучинг, а не психотерапия. Если вам нужна профессиональная помощь, [найти психотерапевта].**)

### 4.3 Crisis card (not dismissable until acknowledged)

> **If you are in immediate danger, please call [hotline number] now. This app cannot help in an emergency.**

---

## 5. Data privacy — non-negotiables

### 5.1 Encryption

- **At rest:** PostgreSQL column-level encryption (pgcrypto) for `journal_entries.content`, `reflections.content`, `health_docs.*`, `crisis_events.*`. Per-user encryption keys held in a KMS (AWS KMS, Yandex KMS for RU, or HashiCorp Vault).
- **In transit:** TLS 1.3 only, HSTS preload, no fallback.
- **Backups:** encrypted, key separation, 30-day retention max for journal/reflection/health data.

### 5.2 Access control

- Admin access to mental-health or medical content requires:
  1. Approved support ticket from user.
  2. 2-person review (audit log entry).
  3. Time-boxed access (24h auto-revoke).
- No bulk-export of mental-health or medical data without legal hold + signed acknowledgment.

### 5.3 ML training

- User journal entries, reflections, health docs, and crisis events are **NEVER** used as ML training data — not for our models, not for LLM provider fine-tuning, not for analytics.
- Aggregate, anonymized usage statistics (timestamps, feature counts) are permitted for product analytics.

### 5.4 Third-party analytics

- **Banned on**: any health-pillar screen, any reflection screen, crisis screens.
- **Permitted on**: settings, billing, auth, onboarding — and only with explicit user consent at signup (GDPR + RU equivalents).

### 5.5 GDPR + 152-ФЗ compliance

- User-initiated export: full data dump within 30 days of request.
- User-initiated delete: complete wipe (including backups) within 30 days. Crisis events retained as anonymized records for 7 years per safety review obligations.
- RU users' personal data stored on RU servers (Yandex Cloud or VK Cloud) per 152-ФЗ if RU launch confirmed.
- Cookie + consent banner on web surfaces.

---

## 6. Subscription ethics

- **No paywall on crisis support** — ever.
- **No paywall on basic check-in** — the free tier is genuinely useful, not bait.
- **Downgrade preserves data** — if user cancels Plus/Premium, their history is preserved (read-only access on free tier), not deleted.
- **Cancel as easy as subscribe** — one tap, in-app, no "are you sure" dark pattern beyond a single confirmation.
- **Refund policy:** 14-day no-questions refund on monthly subscriptions; pro-rated refund on annual.
- **Affiliate disclosures:** if the human-coach tier routes to BetterHelp/Yasno/etc., the affiliate relationship is clearly disclosed before user selection.

---

## 7. Audit trail

Every change to this document triggers a code review by `security-reviewer` agent + sign-off in commit message. Reason: these rules protect users and the company from existential risk. They must not erode through normal development.

Changes to crisis detection regex, LLM classifier prompt, hotline numbers, or no-diagnosis filter require an additional human review (operator sign-off in PR description).

---

## 8. Cross-references

- Plan: `.\PLAN_2026_05_11_MVP.md`
- Project context: `..\CLAUDE.md`
- Global rules: `D:\test 2\CLAUDE.md`
- Privacy & legal copy (templates): `.\PRIVACY_LEGAL.md` (to be written in Phase 5)
