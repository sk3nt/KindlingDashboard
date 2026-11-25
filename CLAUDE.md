# KindlingDashboard

The website and dashboard for Kindling (the engine, `sk3nt/KindlingEngine`, local `D:\AIGameDev\Kindling`) and Kindling Discovery (the game, `sk3nt/KindlingDiscovery`, local `D:\UnityProjects\KindlingDiscovery`). Steven is the creative director.

- The engine's CLAUDE.md and its twelve rules apply here too. This repo reads the engine and game repos; it never writes to them.
- Site navigation: one bar from `shared/sitenav.js` on every page; switch it off there before publishing. Cross-space links use `data-space`, never a plain href.
- Pages: `index.html` (hub), `engine.html`, `dev-dashboard.html` (built by `tools/build_dev_dashboard.py`), `discovery/` (game bible copy). Links stay inside this repo.
- Dashboard v2 (engine queue task 59, spec `docs/dashboard-v2-spec.md` in KindlingEngine) is built in `server/` here. Its engine actions call the engine's own CLIs and modules from `D:\AIGameDev\Kindling`; Steven-only actions need his token (rule 10).
- The chat integrator commits and pushes to `main` here. Agents on Steven's PC never push; their changes stay uncommitted for Steven.
