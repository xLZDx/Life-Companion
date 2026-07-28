# AGENTS.md — Life Companion

Tool-agnostic conventions for any coding agent operating in this checkout — Claude Code, OpenAI
Codex/ChatGPT, Aider, or anything else. `CLAUDE.md` is the Claude Code entry point; this file is for
everyone else, and for the parts that apply regardless of which agent is reading them.

## Build / test / run

```powershell
cd "D:\test 2\Life Companion"
venv\Scripts\python.exe -m pytest tests/ -x -q      # canonical regression suite, 0 failures gates every push
```

```powershell
cd "D:\test 2\Life Companion\mobile"
flutter analyze
flutter test
```

For features touching the FastAPI server: restart via `.\restart.ps1`, then verify health endpoints + a
sample API call — a passing test suite does not prove the running server picked up the change.

## Git safety — MANDATORY for any agent touching this repo

1. **Never push without the operator's explicit push authorization for that specific commit list.** A
   local commit does not imply permission to push.
2. **Never `git commit --no-verify` / `git push --no-verify`** without the operator explicitly asking for
   it in that message.
3. **Read `git log @{u}..HEAD --oneline` before every push attempt** (once a remote is configured — none
   is set as of this writing) and compare it against what was actually authorized.
4. Branch: `main`. No remote configured yet — confirm before assuming any push destination.

## Testing requirement

- `pytest tests/ -x -q` — 0 failures required before claiming a change complete.
- **`tests/crisis/` requires 100% branch coverage** — this module gates a life-or-death path
  (crisis-detection → hotline handoff). Do not relax this for convenience.
- **Functional tests prove behavior** — every test must call the code and assert on observable state.
  String-match-only tests are not acceptable as sole proof.
- Mobile: `flutter analyze` + `flutter test` from `mobile/`.

## Domain guardrails agents must not silently violate

These are product-safety constraints, not style preferences — see `core/GUARDRAILS.md` for the full spec:
- No diagnoses — AI never says "you have X," only "I notice X, here are questions for your doctor."
- Crisis detection suppresses the AI conversation and shows a hotline on any hit; never paywalled.
- No engagement A/B testing on emotional content (UX-only A/B testing is fine).
- No "streak broken" shame notifications.

## Where everything else lives

| Need | Go to |
|---|---|
| Product pillars, north-star metric, hard guardrails, stack table | `CLAUDE.md` |
| MVP plan (7-phase, ~7-8 weeks) | `core/PLAN_2026_05_11_MVP.md` |
| Guardrails spec (crisis detection, disclaimers, privacy) | `core/GUARDRAILS.md` |
| Backend module map | `CLAUDE.md` → Layout section (`src/api`, `src/reflection`, `src/crisis`, etc.) |
