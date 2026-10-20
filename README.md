# Life Companion

Life Companion is a planned mobile and backend application organized around everyday reflection, life patterns, guided conversation, and user-controlled health-document assistance.

**Status:** Engineering/MVP workspace. The feature roadmap is a plan and does not demonstrate that every feature is implemented, clinically validated, or ready for general release.

## Product areas

- **Life:** journaling, weekly reviews, and patterns based on a user's own history.
- **Mind:** guided reflection and educational cognitive-reframing interactions; not a substitute for licensed therapy.
- **Health:** explanations and translations of health documents and visit preparation; not diagnosis or treatment advice.

## Repository layout

- `mobile/` — mobile application sources.
- `src/` — backend application code.
- `tests/` — available automated tests.
- `core/` — plans, guardrails, reviews, and engineering decisions.
- `docker-compose.dev.yml`, `alembic.ini` — development infrastructure and database migration configuration.
- `requirements.txt`, `pyproject.toml` — Python dependencies and tooling.

## Planning and local setup

Start with [the MVP plan](core/PLAN_2026_05_11_MVP.md), [project guardrails](core/GUARDRAILS.md), [AGENTS.md](AGENTS.md), and [CLAUDE.md](CLAUDE.md). Use a local development environment and synthetic data for initial verification. Check the source and configuration for actual supported start commands instead of assuming that the full MVP is deployed.

## Safety, privacy, and release

Health information and personal journal content require strict authorization, confidentiality, and retention controls. Features concerning crisis support and medical content require real safety evaluation and appropriate user-facing limitations. Payment and subscription capabilities require separate end-to-end testing before launch.

## Language policy

Write all new GitHub-facing documentation, comments, commit messages, issues, and PRs in English. Preserve user-generated records and structured identifiers without automatic translation.
