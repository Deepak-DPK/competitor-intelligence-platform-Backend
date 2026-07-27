# KNOWN ISSUES
## Travel Intelligence Platform — Phase 3
**Date:** 2026-07-27  
**Branch:** `phase-3-production`

---

## Active Issues

### KI-001 — Recharts Vendor Chunk Still Large (LOW)
- **Severity:** Low  
- **Area:** Frontend Build  
- **Description:** `vendor-charts.js` is 367KB (108KB gzip) due to Recharts being a large library. This is normal for Recharts but adds to total page weight.  
- **Impact:** Initial page load may be slightly slower on slow connections (~1-2s additional on 3G).  
- **Resolution:** Consider lazy-loading chart components with `React.lazy()` / `Suspense` on dashboard routes. Alternatively, replace Recharts with a lighter library (Chart.js, uPlot) for specific charts.  
- **Workaround:** Browser caches the vendor chunk after first load — negligible for returning users.

---

### KI-002 — asyncpg Not Installed in Local venv (MEDIUM)
- **Severity:** Medium  
- **Area:** Backend / Dev Environment  
- **Description:** `asyncpg` (async PostgreSQL driver) is in `requirements.txt` but could not be installed in the local Python 3.14 venv because no pre-built wheel exists for Python 3.14 on Windows, and MSVC Build Tools are required to compile from source.  
- **Impact:** Local development uses SQLite fallback. The production PostgreSQL driver is NOT available locally.  
- **Resolution:** Install Microsoft C++ Build Tools OR use Python 3.11/3.12 (stable asyncpg wheel available) for local development. Render/production deploys correctly because it runs Linux.  
- **Workaround:** The `session.py` gracefully falls back to SQLite in-memory when asyncpg is missing — app starts and runs for development purposes.

---

### KI-003 — Supabase JWT Auth Requires Live Supabase Project (MEDIUM)
- **Severity:** Medium  
- **Area:** Authentication  
- **Description:** The auth flow depends on a live Supabase project (SUPABASE_URL, SUPABASE_KEY, SUPABASE_JWT_SECRET in `.env`). Without valid credentials, login/register return 401.  
- **Impact:** Developers without Supabase credentials cannot authenticate through the real auth flow.  
- **Resolution:** Set `ENVIRONMENT=development` in `.env` to enable the local dev fallback that bypasses Supabase and creates local user records.  
- **Workaround:** Dev fallback is active when `ENVIRONMENT=development` (default). Set credentials in `.env` for production.

---

### KI-004 — Firecrawl API Key Required for Live Scans (MEDIUM)
- **Severity:** Medium  
- **Area:** Website Monitoring / Competitor Scans  
- **Description:** Real competitor website scans via Firecrawl require a valid `FIRECRAWL_API_KEY` in the backend `.env`. Without it, scan calls will fail silently (fallback to mock data in dev mode).  
- **Impact:** Scan trigger button works (shows toast) but returns synthetic data instead of real scraped content.  
- **Resolution:** Obtain a Firecrawl API key from firecrawl.dev and set `FIRECRAWL_API_KEY=fc-xxx` in `.env`.  
- **Workaround:** Frontend shows synthetic scan results for demonstration when key is absent.

---

### KI-005 — Gemini AI Insights Require Valid API Key (MEDIUM)
- **Severity:** Medium  
- **Area:** AI Insights  
- **Description:** The `GEMINI_API_KEY` must be a valid Google AI Studio key for real AI summaries. Without it, AI insight generation will fail.  
- **Impact:** AI Insights view will show an error toast. Dashboard won't show Gemini summaries.  
- **Resolution:** Set `GEMINI_API_KEY=your-key` in `.env`. Keys are free at aistudio.google.com.  
- **Workaround:** None. API key is mandatory for AI features.

---

### KI-006 — No End-to-End Playwright Browser Tests (LOW)
- **Severity:** Low  
- **Area:** Testing  
- **Description:** Phase 3 testing covers backend API (pytest) and frontend build (Vite). No Playwright browser automation e2e tests were written for the UI flows (login → workspace → monitoring).  
- **Impact:** UI interaction bugs could escape automated testing.  
- **Resolution:** Write Playwright tests for: login flow, workspace creation wizard, competitor add/scan, AI insights, reports export.  
- **Workaround:** Manual UI audit performed during Phase 3 verification. No critical UI bugs found.

---

## Resolved Issues (Phase 3)

| ID | Issue | Resolution |
|---|---|---|
| FIXED-01 | All 18 SQLAlchemy models crashed SQLite tests (`gen_random_uuid`) | Replaced with `default=uuid.uuid4` |
| FIXED-02 | Auth dev fallback returned 200 for invalid credentials in test env | Gated on `settings.is_development` |
| FIXED-03 | Empty refresh token returned 401 instead of 422 | Added `min_length=1` to `RefreshTokenRequest` |
| FIXED-04 | `test_dashboard.py` used wrong fixture names | Rewrote with standard conftest fixtures |
| FIXED-05 | Tests failed on paginated API responses | Fixed response unwrapping to use `items` key |
| FIXED-06 | Frontend 871KB monolithic JS bundle warning | Split to 471KB app + vendor chunks |
