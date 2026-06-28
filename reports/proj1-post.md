# Proj1-v* — Social Media Posts

Attach output images: `outputs/proj1-v2.png`, `outputs/proj1-v3.png`, and `outputs/proj1-v4.gif`

---

## LinkedIn

⚡ **Power Systems + Python = Beautiful Insights**

I've been building up my pandapower scripting skills, and wanted to share a progression I'm really proud of — four iterations of the same two-bus network, each one adding more analytical depth.

**The scenario:** A simple 20 kV distribution feeder — a 1 km cable (NAYY 4x50 SE) connecting a grid supply point to a load bus drawing 3 MW / 0.2 MVAr. Run a load flow to compute voltages, line loading, and losses.

**proj1-v1** — The foundation: create a 20 kV network, add a slack bus, a load bus, a cable (NAYY 4x50 SE), and a 1 MW load. Run a Newton-Raphson load flow. Results rendered as clean matplotlib tables (bus voltages, line flows, losses, loading) and saved to PNG. Simple, clean, works.

**proj1-v2** — Added visualization: same network, but now with geodata-driven topology plots, bus voltage annotations, line loading labels, and a custom legend — all via pandapower's plotting module + matplotlib.

**proj1-v3** — Full analytical dashboard: a 3-panel figure with network topology (color-coded by loading), voltage profile with ±5% operating band, and a line-loading bar chart with thermal limit indicator. Loading-aware color logic: green within limits, red if overloaded.

**proj1-v4** — Animated parameter sweep: the same 3-panel dashboard driven by `matplotlib.animation.FuncAnimation`. Sweeps load from 1–9 MW and line length from 0.5–5 km across 50 frames, rebuilt and re-solved per frame. Watch the voltage drop and line loading climb in real time. Output as a GIF.

Each version builds on the last — from bare results to actionable engineering visuals. This is what I love about Python in power systems: you start with `pp.runpp(net)` and end with publication-ready figures.

What's your go‑to Python stack for power system analysis?

Comment **"⚡ power flow"** and I'll DM you the full Python script — all four versions.

#Pandapower #Python #PowerSystems #DataVisualization #Engineering #LoadFlow

---

## Twitter / X

⚡ Three versions of the same power system model, each leveling up the analysis:

v1 → load flow + results as formatted tables
v2 → topology plot with annotations
v3 → 3-panel dashboard: topology + voltage profile + line loading
v4 → animated parameter sweep (load × line length) → GIF

Green line = good. Red line = overloaded. All in @pandapower + matplotlib.

Love how fast you can go from `pp.runpp()` to a publication-ready figure. 🐍🔌

Drop **"⚡ power flow"** in the replies and I'll send you the scripts.

Attach: `outputs/proj1-v4.gif`

#Pandapower #Python #PowerSystems
