# Phase 1 Review Backlog (MEDIUM / LOW)

**Date:** 2026-05-13 (review run after the Phase 1 commit).
**Source:** parallel review by `python-reviewer`, `security-reviewer`, `database-reviewer`, `flutter-reviewer`.
**CRITICAL + HIGH findings** were applied in the Phase 1 review-fixes commit. This file tracks **MEDIUM + LOW** items to address before Phase 2 ships features on top.

---

## MEDIUM - fix before alpha users

### Backend Python

| ID | Source | Item | Where |
|---|---|---|---|
| PY-M1 | python-reviewer | `_firebase_initialized` global needs a `threading.Lock` for ASGI multi-worker | `src/auth/firebase.py:30` |
| PY-M2 | python-reviewer | `crisis_api.fallback` flag uses `len > 3` heuristic — replace with explicit `cc not in _HOTLINES` check | `src/api/crisis.py:28` |
| PY-M3 | python-reviewer | `test_estimate_cost_returns_nonnegative` should call `reset_registry_for_tests()` first to avoid stale-state coupling | `tests/llm/test_adapter.py:71` |
| PY-M4 | python-reviewer | `src/db/migrations/env.py::asyncio.run()` will fail if called from inside a running loop (integration tests in Phase 2) | `src/db/migrations/env.py:62` |
| PY-M5 | python-reviewer | Remove `tests/` from mypy exclude — type-check fixtures and conftest too | `pyproject.toml:48` |
| PY-M6 | python-reviewer | Replace `_ = Any  # keep import live` with proper removal of unused `Any` import | (resolved in this commit — removed) |
| SEC-M1 | security-reviewer | `User.email` stored as plain `String(320)` — encrypt or document the conscious tradeoff (GDPR Article 9) | `src/db/models.py:82` |
| SEC-M2 | security-reviewer | `CrisisEvent.user_id` is a joinable FK — long-term, add Postgres row-level security or move to a separate schema with restricted DB role | `src/db/models.py:241` |
| SEC-M3 | security-reviewer | Test fixtures use `"test-key"` for LLM API keys — switch to sentinel `"NOT_A_REAL_KEY_TEST_ONLY"` and assert refuses real use under `APP_ENV=test` | `tests/conftest.py:24` |
| SEC-M4 | security-reviewer | Add rate limiting (`slowapi` or `fastapi-limiter`) before Phase 2 wiring | `src/main.py` |

### Database

| ID | Source | Item | Where |
|---|---|---|---|
| DB-M1 | database-reviewer | `get_read_session()` variant skipping commit overhead for read-only endpoints | `src/db/session.py` |
| DB-M2 | database-reviewer | Document `expire_on_commit=False` implications inline | `src/db/session.py:42` |
| DB-M3 | database-reviewer | `alembic.ini::sqlalchemy.url=` empty; CI pre-check that `.env.test` exists before running migrations | `alembic.ini:8` |

### Mobile

| ID | Source | Item | Where |
|---|---|---|---|
| FL-M1 | flutter-reviewer | `currentUserProvider` collapses loading + error into `null` — surface distinct loading state to prevent sign-in screen flash | `mobile/lib/features/auth/auth_providers.dart:12` |
| FL-M2 | flutter-reviewer | `DisclaimerBanner` mind-pillar calm-blue text in light theme — contrast 3.44:1, below WCAG AA 4.5:1; darken to `#3D6B91` | `mobile/lib/core/theme/app_colors.dart` |
| FL-M3 | flutter-reviewer | Replace hardcoded `TextStyle(fontSize: 28/20)` with `Theme.of(context).textTheme.*` | `mobile/lib/features/auth/auth_screen.dart:21`, `home_screen.dart:29` |
| FL-M4 | flutter-reviewer | `Colors.grey` is not dark-mode aware in `auth_screen.dart:39`; use `Theme.of(context).colorScheme.onSurfaceVariant` | `mobile/lib/features/auth/auth_screen.dart:39` |
| FL-M5 | flutter-reviewer | `main.dart` swallows ALL Firebase init exceptions silently — gate on `AppConfig.appEnv != 'development'` | `mobile/lib/main.dart:13` |
| FL-M6 | flutter-reviewer | `apiClientProvider` does not dispose Dio — add `ApiClient.dispose()` + `ref.onDispose` | `mobile/lib/core/services/api_client.dart:7` |
| FL-M7 | flutter-reviewer | Add `riverpod_lint` to dev_deps + `custom_lint` plugin | `mobile/pubspec.yaml`, `analysis_options.yaml` |
| FL-M8 | flutter-reviewer | `flutter_secure_storage` iOS options - explicit `KeychainAccessibility.when_unlocked_this_device` | `mobile/lib/core/services/secure_storage.dart` |

---

## LOW / nits

### Backend

| ID | Source | Item |
|---|---|---|
| PY-L1 | python-reviewer | `GeminiAdapter.__init__` should precede `provider_name` (style) |
| PY-L2 | python-reviewer | Add `CheckConstraint` or Postgres enum types to `tier`, `pillar`, `trigger_source`, `status` columns (applied to `tier` and `status` in this commit; `pillar` applied to journal_entries; remaining: `trigger_source`, `provider`) |
| PY-L3 | python-reviewer | `PUBLIC_PATHS` exact-match — `/docs/oauth2-redirect` slips through as protected (route is public anyway, just a confusing log entry) |
| PY-L4 | python-reviewer | `test_hotline_entry_is_frozen_dataclass` should use `pytest.raises(dataclasses.FrozenInstanceError)` not bare `Exception` |
| SEC-L1 | security-reviewer | Document what `SECRET_KEY` will eventually sign in `.env.example` |
| SEC-L2 | security-reviewer | Hotline number accuracy — France `3114`, Italy `Telefono Azzurro 19696`, Belarus mobile-call status — medical advisor review |
| SEC-L4 | security-reviewer | Confirm `.env` is in `.gitignore` (it is, but verify in CI) |

### Database

| ID | Source | Item |
|---|---|---|
| DB-L1 | database-reviewer | Phase 3: switch dev image to `pgvector/pgvector:pg16` for embeddings |
| DB-L2 | database-reviewer | Document Docker WSL2 backend requirement in `docker-compose.dev.yml` (space in path) |

### Mobile

| ID | Source | Item |
|---|---|---|
| FL-L1 | flutter-reviewer | Add `riverpod_annotation` dep for `@riverpod` codegen in Phase 2 |
| FL-L2 | flutter-reviewer | `Routes` constants for `checkin`, `reflect`, `patterns`, `weekly`, `health`, `settings` have no GoRoute yet — keep with TODO comment or remove |
| FL-L3 | flutter-reviewer | `widget_test.dart` should add `pumpAndSettle` for Phase 2 async loading |
| FL-L4 | flutter-reviewer | `AppConfig.assertProductionSafety()` for HTTPS-only backend in prod |

---

## Pre-Phase-2 setup notes (operator action)

1. **`flutterfire configure`** before `flutter run`. Without it, Firebase init swallows the failure silently in dev.
2. **`mobile/env/dev.json`** (gitignored) with `BACKEND_BASE_URL`, `APP_ENV`, `ENABLE_CRASH_REPORTING` keys. Run: `flutter run --dart-define-from-file=env/dev.json`.
3. **`flutter pub run build_runner build --delete-conflicting-outputs`** for Phase 2 `@riverpod` codegen.
4. **Postgres install on D:** for `pytest-postgresql` local runs — set `POSTGRESQL_BIN=D:/PostgreSQL/16/bin`.
5. **`alembic revision --autogenerate -m "initial"`** to generate the first schema migration from the current `models.py`.

---

## Resolved in the Phase 1 review-fixes commit

### CRITICAL
- AuthMiddleware now reads `request.app.state.redis` lazily; `__init__` constructor removed (PY-C1 / SEC-C1).
- `verify_id_token` wrapped in `loop.run_in_executor(None, ...)` to free the event loop (PY-C2).
- `get_session()` return type changed to `AsyncGenerator[AsyncSession, None]` (PY-C3).
- Foreign-key index added on `reflections.journal_entry_id` (DB-C1).
- `ON DELETE CASCADE` on all child FKs to `users.id` except `crisis_events` which uses `SET NULL` + `anonymized_at` for 7-year retention (DB-C2).
- `crisis_events.hotlines_shown` widened to `String(256)` (DB-L3 promoted).
- Partial active-rows indexes on `journal_entries` and `health_docs` (DB-C2).
- Alembic `compare_type=True` + `compare_server_default=True` (DB-C3).

### HIGH
- `datetime.utcnow()` -> `datetime.now(timezone.utc)` in `LLMCallLog` (PY-H1 / SEC-L2).
- `AsyncGenerator[str, None]` -> `AsyncIterator[str]` on `LLMAdapter.stream` + concrete stubs; removed unreachable `yield ""` (PY-H4).
- `structlog.configure` gains `logger_factory=structlog.stdlib.LoggerFactory()`; ConsoleRenderer in dev + test, JSON in prod (PY-H5 / PY-H6 / M-1).
- `_clear_settings_cache` autouse session fixture in `conftest.py` (PY-H7).
- `verify_token` Redis cache-hit test added (PY-H8).
- Firebase outage path now sets `request.state.auth_error = "service_unavailable"`; `get_current_user` raises 503 (SEC-H1). Regression test added.
- `Settings.reject_stub_key_in_production` validator (SEC-H2).
- `Settings.reject_localhost_cors_in_production` validator (SEC-M2 promoted to HIGH).
- `/docs`, `/redoc`, `/openapi.json` disabled when `APP_ENV=production` (SEC-H3).
- CORS `allow_methods` narrowed to `GET, POST, OPTIONS` for Phase 1 surface (SEC-M1 promoted).
- Redis cache log no longer emits exception info (could include credentials in URL) (SEC-M6).
- `EncryptedString.cache_ok = False` with comment for Phase 4 (DB-H1).
- `EncryptedString` design comment documents Option A vs B for Phase 4 (DB-H2).
- `cost_usd` changed from `Float` to `Numeric(10, 6)` (DB-H3).
- `subscriptions.provider_subscription_id` is now `unique=True` (DB-H4).
- `users.email` got a partial unique index (DB-M1 promoted).
- `CheckConstraint` added to `users.tier`, `subscriptions.status`, `journal_entries.pillar` (PY-L2 partial).
- Router `refreshListenable` pattern via `_AuthRefreshNotifier` - router instance stable (FL-H1).
- Crisis modal uses `context.pop()` / `context.go(Routes.home)` (FL-H2). Regression test added.
- `_RetryInterceptor` only retries idempotent methods (GET/HEAD/OPTIONS) unless `extra['retry_safe']=true` (FL-H3).
- Crisis modal `withOpacity` -> `withValues(alpha:)` (FL-M9 deprecation).

Total CRITICAL+HIGH fixes applied: 27.
Total MEDIUM/LOW deferred to this backlog: ~30.
