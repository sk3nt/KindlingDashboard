# Kindling dashboard

The local website for Kindling. Open `index.html` in a browser: three tiles lead to the engine overview (`engine.html`), engine development (`dev-dashboard.html`) and the Kindling Discovery game bible (`discovery/`). Every link stays inside this folder.

Local path: `D:\AIGameDev\KindlingDashboard`, next to `D:\AIGameDev\Kindling` (KindlingEngine) and `D:\UnityProjects\KindlingDiscovery`.

- `tools/build_dev_dashboard.py` rebuilds `dev-dashboard.html` from the engine's task queue (`../Kindling/handover/queue/kindling-task-queue.md` by default).
- `discovery/` is a presentation copy of the game bible. The game repo stays the source of truth; agents never read lore from here.
- Dashboard v2 (queue task 59 in KindlingEngine, spec `docs/dashboard-v2-spec.md`) is built here: a small local server for track development, morning review, and track and run the engine.

## Navigation and publishing

- One bar across every space (Kindling home, Engine, Development, Discovery) comes from `shared/sitenav.js`. Each page keeps its own in-page navigation below it: the engine's sidebar, the development page's section bar, the game bible's section bar.
- Links from one space to another inside page content are written as `<a data-space="engine">` and only become links while the bar is on.
- **Before publishing:** set `ENABLED = false` at the top of `shared/sitenav.js` (or delete the file). The bar, its offsets and every cross-space link go away; each space then stands alone.
