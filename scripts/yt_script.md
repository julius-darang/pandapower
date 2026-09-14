# pandapower "Learn in Public" — YouTube Script Framework

**Premise:** You're not presenting as an expert. You're an REE learning pandapower
on camera, and the audience learns alongside you. That's a real edge — lean into
it instead of hiding it. "I'm figuring this out too" is more watchable than
"let me show you what I already know."

---

## Why the original doc doesn't work as a script (as-is)

| Doc structure | Problem on video | Fix |
|---|---|---|
| What you'll learn → Why it matters → Code → Results | Buries the payoff at the end | Show the result/visual FIRST, then explain how you got there |
| Concept explained in prose before any code | Dead air on screen, nothing to look at | Talk over the network diagram or terminal, not a blank slide |
| "What to try next" as a closing suggestion | Passive, easy to skip | Turn it into a direct on-camera challenge + pinned comment |
| No tension/stakes | Nothing pulls the viewer through | Open with a question or a broken/wrong result, then fix it live |
| Uniform pacing across all 10 | Viewer fatigue by project 4 | Vary episode length/format (some are 6 min, some are 90 sec shorts) |

---

## Universal Episode Template (apply to every project)

**Length target:** 6–9 min for main projects, 60–90 sec for the "what to try next" as a Short

```
[0:00–0:15] COLD OPEN — Hook
  Show the END STATE first: the plot, the voltage drop, the overload warning.
  One sentence: "This bus is about to violate voltage limits. Let's see why — and how 3 lines of code show us exactly that."
  NO intro, no "hey guys welcome back" yet.

[0:15–0:35] WHO/WHAT (fast)
  "I'm Juls, I'm an REE learning pandapower in public. Today: [concept]."
  On-screen text: Episode title + project number (e.g. "EP 01 — The 2-Bus Network")

[0:35–1:30] WHY THIS MATTERS (the engineering hook, not the textbook version)
  Reframe "why it matters" as a real scenario: "Every transmission/distribution
  study you'll ever run — no matter how big the network — reduces to this."
  Show a real or simplified one-line diagram, hand-drawn or simple SVG, NOT code yet.

[1:30–5:30] BUILD IT LIVE (screen capture, narrated)
  Type the code in real time (or sped up 1.5x with voiceover), pausing at:
    - the moment a bus/line is created → cut to diagram updating
    - pp.runpp() → "this is the line that actually solves the physics"
    - the result table → DON'T just read numbers, point at the ONE number that matters
  Mistake-friendly: if you actually hit an error while learning, KEEP IT IN.
  That's the most replayed kind of moment in tutorial content.

[5:30–7:00] WHAT JUST HAPPENED (the "aha")
  Translate the numbers into plain language: "Bus 2 is at 0.94 pu. That's not just
  a number — that's a brownout. Anything under 0.95 and a real load would be unhappy."

[7:00–8:00] YOUR TURN (engagement, not just "try this at home")
  State the specific challenge from "what to try next" as a DIRECT CHALLENGE:
  "Change the load to 5 MW and tell me in the comments what voltage you get before
  you even run it — guess first."
  This is the single highest-leverage retention/comments device for tutorial channels.

[8:00–8:20] BRIDGE TO NEXT EPISODE
  One sentence teaser tied to a real question: "Next time: what happens when we
  add a SECOND load — does removing one bring us back to normal? Not always. Here's why."
```

---

## Visual/On-Screen Cues (use consistently across the series — builds brand recognition)

- **Diagram-first, code-second.** Before any code block appears, show a simple
  bus/line diagram (even hand-drawn or a 2-node SVG). Update it as elements are added.
- **One color = one meaning, every episode:**
  - 🟢 green = normal / within limits
  - 🟡 amber = warning zone
  - 🔴 red = violation / overload
  (You already use this amber/green palette in your tutorial decks — reuse it here for consistency across your channel.)
- **Freeze-frame the result line that matters.** Don't show the whole DataFrame
  and talk over it — crop/zoom to the 1–2 numbers that answer the episode's question.
- **Running progress bar** ("Project 3 of 10") in a corner — signals series structure
  and encourages binge-watching.

---

## Title / Thumbnail Formula

Pattern: **[Concrete result] + [the tool/concept] + [implied stakes]**

| Project | Weak title (doc style) | Strong title (hook style) |
|---|---|---|
| 1 | "Single-Line Network (2-Bus)" | "I Simulated a Power Grid in 12 Lines of Python" |
| 3 | "Change Line Impedance" | "Why Longer Power Lines Lose More Energy (and How to Prove It in Code)" |
| 6 | "Two Parallel Lines (In-Service Toggle)" | "What Happens When a Power Line Trips? (N-1 Contingency, Explained Live)" |
| 9 | "Compare AC vs DC Load Flow" | "AC vs DC Load Flow: Which One Lies to You?" |

Thumbnail: result number/plot in big text (e.g. "0.94 pu ⚠") + your face reacting,
not a screenshot of code.

---

# WORKED EXAMPLE — Full Script: Episode 1

## "I Simulated a Power Grid in 12 Lines of Python"
**(Project 1 — Single-Line Network, 2-Bus)**

---

**[0:00] COLD OPEN**
*(Screen: terminal already running, final plot/output visible — voltage table on screen)*

> "This number — 0.96 — tells you whether a power grid is healthy or about to
> brown out. I just got it from twelve lines of Python. Let's build it together,
> live, because I'm learning this tool the same way you are."

**[0:15] INTRO CARD**
*On-screen text: "EP 01 / 10 — pandapower for Beginners"*

> "I'm Juls — electrical engineer, currently a shift operator on a solar plant —
> and I'm teaching myself pandapower on camera. No script where I already know
> the answer. If I mess up, you'll see it."

**[0:35] WHY THIS MATTERS**
*(Simple diagram: two circles, one labeled "Slack/Grid", one "Load", a line between them)*

> "Every power system model — whether it's two buses or two thousand — is built
> from the same three Lego pieces: buses, branches, and elements. If you understand
> this 2-bus system, you understand the building block of literally every grid study
> that exists. That's the whole game today."

> "And there's one concept you need before any of this makes sense: the **slack bus**.
> It's the reference point — the one bus whose voltage is fixed by definition.
> Every other bus gets solved *relative to it*. Think of it as the grid's anchor."

**[1:30] BUILD IT LIVE**
*(Screen capture, typing in real time)*

```python
import pandapower as pp

net = pp.create_empty_network()

bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus")
```
> "Two buses. Nothing's connected yet — this is just two dots in space."

```python
pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")
```
> "This line is what MAKES bus1 the slack bus. Without an external grid source,
> pandapower has nothing to anchor the math to — it won't even run."

```python
pp.create_line(net, from_bus=bus1, to_bus=bus2,
               length_km=1.0, std_type="NAYY 4x50 SE", name="Line 1-2")

pp.create_load(net, bus=bus2, p_mw=1.0, q_mvar=0.2, name="Load")
```
> "Now they're connected, and bus2 has something demanding power — 1 megawatt."

```python
pp.runpp(net)
print(net.res_bus)
print(net.res_line)
```
> "And THIS is the line doing the actual physics — Newton-Raphson load flow,
> solving for every voltage and current in the network. Let's see what it says."

*(cut to terminal output, zoom into res_bus table)*

**[5:30] THE AHA MOMENT**
*(Crop/zoom on `vm_pu` column only)*

> "Bus 2 sits at roughly 0.96 per-unit. That 'per-unit' thing just means: 1.0 = perfectly
> normal voltage. 0.96 means we're 4% low — still fine, but if I crank that load up,
> watch what happens."

*(quick live re-run with p_mw=5.0 — show the number drop further, ideally below 0.95)*

> "There it is — that's a voltage violation. Same network, same code, just a bigger
> load. That's the entire foundation of voltage studies, and we just reproduced it
> in under 2 minutes."

**[7:00] YOUR TURN**
> "Before you run anything — guess: if I make the line 10x longer instead of
> increasing the load, does the voltage drop by more, less, or about the same?
> Comment your guess, then go test it. I'll pin the best answer."

**[8:00] BRIDGE**
> "Next episode: what happens when I add a SECOND load to this network, then
> remove it? Does the grid actually 'forget' it was ever there? The answer
> surprised me a little — see you in the next one."

---

## Production notes for this episode
- **B-roll opportunity:** if you have any access to your actual 20 MWp plant SCADA
  screen (sanitized), a 2-second cutaway of a real voltage readout while you say
  "this isn't just theoretical" adds huge credibility for an REE-led channel.
- **Reused asset:** the slack-bus diagram and the 🟢🟡🔴 voltage legend should be
  built once as a template (Keynote/Figma/Marp, matching your existing deck style)
  and reused across all 10 episodes — saves production time and builds visual consistency.
- **Shorts spinoff:** the "Your Turn" segment (0:35 sec) can be cut as a standalone
  Short: "Guess this before I tell you the answer" — strong format for pandapower-curious
  beginners who find you via Shorts.

---

# WORKED EXAMPLE — Full Script: Episode 2

## "Can You Undo a Decision in a Power Grid? (Add/Remove Load Test)"
**(Project 2 — Add and Remove a Load)**

**[0:00] COLD OPEN**
*(Screen: two side-by-side voltage tables — "before Load B" and "after removing Load B" — identical)*

> "If I add a load to this grid, run the numbers, then delete that load completely —
> does the system actually forget it was ever there? Let's test it, live."

**[0:15] INTRO CARD** — *"EP 02/10"*

**[0:35] WHY THIS MATTERS**
> "In real planning work you almost never study one scenario — you study 'before
> a new factory connects' and 'after.' Today's whole lesson is: `net` isn't a
> static file, it's a live Python object. Every bus, line, and load is just a
> row in a pandas DataFrame, sitting in memory, that you can change between runs."

**[1:30] BUILD IT LIVE**

```python
import pandapower as pp

net = pp.create_empty_network()
bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus")
bus3 = pp.create_bus(net, vn_kv=20, name="Secondary Load Bus")

pp.create_ext_grid(net, bus=bus1, vm_pu=1.0)
pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=2.0, std_type="NAYY 4x50 SE")
pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=1.0, std_type="NAYY 4x50 SE")
pp.create_load(net, bus=bus2, p_mw=1.0, q_mvar=0.2, name="Load A")
```
> "Three buses, one load so far. Let's lock in the baseline."

```python
pp.runpp(net)
print("=== Base Case ===")
print(net.res_bus[["vm_pu", "va_degree"]])
```
*(pause on the printed table — this is the number we'll come back to)*

> "Now I'm adding a second load — like a new customer connecting to bus 3."

```python
load_b = pp.create_load(net, bus=bus3, p_mw=2.0, q_mvar=0.5, name="Load B")
pp.runpp(net)
print("\n=== With Load B Added ===")
print(net.res_bus[["vm_pu", "va_degree"]])
```
*(point at bus3's voltage — visibly lower)*

> "And now — delete it completely."

```python
net.load.drop(load_b, inplace=True)
pp.runpp(net)
print("\n=== After Removing Load B ===")
print(net.res_bus[["vm_pu", "va_degree"]])
```

**[5:30] THE AHA MOMENT**
*(side-by-side: base case table vs. "after removing" table)*

> "Identical. Down to the same decimals. The network has zero memory of Load B
> ever existing — which sounds obvious, but it's actually an important guarantee:
> your simulation is a pure function of whatever's currently in `net`, nothing more."

**[7:00] YOUR TURN**
> "Instead of `drop()`, try `net.load.at[load_b, 'in_service'] = False` instead.
> Does it give you the exact same result? It should — and in real workflows, this
> is the cleaner move, because the load's parameters are still sitting there for
> later, just switched off. Try it and compare in the comments."

**[8:00] BRIDGE**
> "Adding and removing a whole load is one kind of change. Next time: what if we
> don't touch what's connected at all, and just make ONE line weaker or stronger?
> Same network, same loads — watch what happens to losses."

---

# WORKED EXAMPLE — Full Script: Episode 3

## "Why Longer Power Lines Lose More Energy (Proving It in Code)"
**(Project 3 — Change Line Impedance)**

**[0:00] COLD OPEN**
*(Screen: three numbers stacked — losses at 2km / 5km / 10km, same load)*

> "Same network. Same load. The only thing I'm changing is ONE number — how long
> a single line is. Watch what that does to energy losses."

**[0:15] INTRO CARD** — *"EP 03/10"*

**[0:35] WHY THIS MATTERS**
> "This is the exact question behind every line-upgrade decision a utility makes:
> 'if we replace this aging cable, how much do we actually save?' A line's
> resistance burns energy as heat — that's `I²R` — and its reactance causes the
> voltage to sag toward the far end. Longer line, more of both."

**[1:30] BUILD IT LIVE**

```python
import pandapower as pp

net = pp.create_empty_network()
bus1 = pp.create_bus(net, vn_kv=20, name="Source")
bus2 = pp.create_bus(net, vn_kv=20, name="Load End")

pp.create_ext_grid(net, bus=bus1, vm_pu=1.0)
line_idx = pp.create_line(net, from_bus=bus1, to_bus=bus2,
                          length_km=5.0, std_type="NAYY 4x50 SE")
pp.create_load(net, bus=bus2, p_mw=2.0, q_mvar=0.5)

pp.runpp(net)
print(f"Original (5 km) — Voltage: {net.res_bus.vm_pu[bus2]:.4f} pu, "
      f"Losses: {net.res_line.pl_mw[line_idx]:.4f} MW")
```
> "That's our baseline — 5 km of cable. Now let's simulate an upgrade."

```python
net.line.at[line_idx, 'length_km'] = 2.0
pp.runpp(net)
print(f"Upgraded (2 km) — Voltage: {net.res_bus.vm_pu[bus2]:.4f} pu, "
      f"Losses: {net.res_line.pl_mw[line_idx]:.4f} MW")
```
> "And now a degraded, longer scenario — imagine the utility never invests."

```python
net.line.at[line_idx, 'length_km'] = 10.0
pp.runpp(net)
print(f"Degraded (10 km) — Voltage: {net.res_bus.vm_pu[bus2]:.4f} pu, "
      f"Losses: {net.res_line.pl_mw[line_idx]:.4f} MW")
```

**[5:30] THE AHA MOMENT**
*(three numbers side by side, highlight the loss column)*

> "Going from 2 km to 10 km doesn't just multiply losses by 5 — it's worse, because
> the voltage sag at the far end means current has to creep up to deliver the same
> power. Length doesn't just add resistance, it compounds with voltage drop. That's
> the kind of nonlinearity a spreadsheet hides and a load flow tool reveals."

**[7:00] YOUR TURN**
> "Instead of changing the length, change the conductor:
> `pp.change_std_type(net, line_idx, element='line', std_type='NAYY 4x150 SE')`.
> Keep the length at 5 km. Does a bigger conductor save more than the 2 km
> upgrade did? Test it and tell me which lever — length or conductor size —
> matters more here."

**[8:00] BRIDGE**
> "We've been changing ONE line this whole series. Next time: what if there are
> TWO lines doing the same job, and one of them just... trips offline?"

---

# WORKED EXAMPLE — Full Script: Episode 4

## "I Built My Own Power System Report Generator in Python"
**(Project 4 — Print a Results Summary Function)**

**[0:00] COLD OPEN**
*(Screen: the printed `LOAD FLOW SUMMARY REPORT` box, with a ⚠ flag visible)*

> "This report took me about fifteen lines of Python, and it's basically the
> exact summary a grid engineer hands their boss after a study. Let's build it
> from scratch."

**[0:15] INTRO CARD** — *"EP 04/10"*

**[0:35] WHY THIS MATTERS**
> "Raw DataFrames are great for debugging but terrible for communicating. The
> function we write today, we'll literally reuse in every project for the rest
> of this series — this is the last time we build it from zero."

**[1:30] BUILD IT LIVE**

```python
def build_sample_network():
    net = pp.create_empty_network()
    b1 = pp.create_bus(net, vn_kv=20, name="Slack")
    b2 = pp.create_bus(net, vn_kv=20, name="Bus A")
    b3 = pp.create_bus(net, vn_kv=20, name="Bus B")
    pp.create_ext_grid(net, bus=b1, vm_pu=1.0)
    pp.create_line(net, from_bus=b1, to_bus=b2, length_km=3.0, std_type="NAYY 4x50 SE")
    pp.create_line(net, from_bus=b2, to_bus=b3, length_km=2.0, std_type="NAYY 4x50 SE")
    pp.create_load(net, bus=b2, p_mw=1.5, q_mvar=0.3)
    pp.create_load(net, bus=b3, p_mw=2.0, q_mvar=0.5)
    return net
```
> "A small helper just so we have something to report on."

```python
def print_summary(net):
    total_load_mw = net.res_load.p_mw.sum()
    total_loss_mw = net.res_line.pl_mw.sum()
    min_voltage = net.res_bus.vm_pu.min()
    min_voltage_bus = net.res_bus.vm_pu.idxmin()
    max_loading = net.res_line.loading_percent.max()
    max_loading_line = net.res_line.loading_percent.idxmax()
```
> "Five numbers. That's genuinely all a first-pass engineering summary needs —
> total demand, total losses, the worst voltage and where it is, the worst
> loading and where it is."

```python
    print(f"  Min Voltage:  {min_voltage:.4f} pu  (Bus {min_voltage_bus})")
    print(f"  Max Loading:  {max_loading:.2f}%  (Line {max_loading_line})")
    if min_voltage < 0.95:
        print(f"  ⚠ VOLTAGE VIOLATION at Bus {min_voltage_bus}!")
    if max_loading > 100:
        print(f"  ⚠ OVERLOAD on Line {max_loading_line}!")
```
> "And these two `if` statements are the actual value of the whole function —
> they turn a wall of numbers into a single thing your eyes catch instantly: a flag."

**[5:30] THE AHA MOMENT**
> "Notice what I did NOT do — I didn't hardcode which bus or line to check. `idxmin()`
> and `idxmax()` find the worst one automatically. Run this same function on a
> totally different network, and it still finds the right thing to flag. That's
> the difference between a script and a tool."

**[7:00] YOUR TURN**
> "Extend `print_summary()` to also print a full per-bus voltage table, formatted
> so it looks like something you'd paste straight into a report. Show me your
> version in the comments — I'll feature the cleanest one."

**[8:00] BRIDGE**
> "We've got a report for ONE scenario. Next time: what if we want this exact
> report for six different load levels, automatically, without re-running anything
> by hand?"

---

# WORKED EXAMPLE — Full Script: Episode 5

## "I Automated 6 Power Grid Scenarios in One Loop"
**(Project 5 — Loop Over Load Scenarios)**

**[0:00] COLD OPEN**
*(Screen: the voltage-vs-load plot, red dashed 0.95 pu line, one point clearly below it)*

> "This chart represents six full simulations. I didn't run them one at a time —
> a single loop did all six. This is the moment pandapower stops being a toy
> and starts being an actual engineering tool."

**[0:15] INTRO CARD** — *"EP 05/10"*

**[0:35] WHY THIS MATTERS**
> "Nobody studies a power system at just one operating point. You study light
> load, peak load, future growth — a whole range. Doing that by hand in a GUI
> tool is hours of clicking. Today it's one `for` loop."

**[1:30] BUILD IT LIVE**

```python
load_levels_mw = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
voltages = []
losses = []

for load_mw in load_levels_mw:
    net.load.at[load_idx, 'p_mw'] = load_mw
    pp.runpp(net)
    voltages.append(net.res_bus.vm_pu[b2])
    losses.append(net.res_line.pl_mw.sum())
```
> "Six numbers in, six load flow solutions out. Every iteration overwrites the
> load, reruns the solver, and we just record the result before moving on."

```python
for load, v, l in zip(load_levels_mw, voltages, losses):
    flag = " ⚠" if v < 0.95 else ""
    print(f"{load:<12.1f} {v:<15.4f} {l:<12.4f}{flag}")
```
*(scroll down the printed table live, point at the row where the flag first appears)*

```python
plt.plot(load_levels_mw, voltages, 'b-o')
plt.axhline(y=0.95, color='red', linestyle='--', label='0.95 pu limit')
plt.savefig("voltage_vs_load.png", dpi=150)
```

**[5:30] THE AHA MOMENT**
*(zoom into the exact load level where the line crosses the red dashed limit)*

> "Somewhere between 2.0 and 2.5 megawatts, this bus crosses into violation
> territory. I didn't guess that — the loop found it. I now know exactly where
> my safety margin runs out, in a network I built ten minutes ago."

**[7:00] YOUR TURN**
> "Add a SECOND loop that also varies line length, store results in a 2D structure,
> and turn it into a heatmap — voltage as a function of both load AND line length
> at once. That's a genuinely portfolio-worthy chart if you pull it off — tag me
> if you do."

**[8:00] BRIDGE**
> "Every scenario so far has had exactly one path for power to flow. Next time:
> what happens when there are TWO paths, and one of them disappears?"

---

# WORKED EXAMPLE — Full Script: Episode 6

## "What Happens When a Power Line Trips? (N-1 Contingency, Live)"
**(Project 6 — Two Parallel Lines, In-Service Toggle)**

**[0:00] COLD OPEN**
*(Screen: res_line loading_percent table, N-0 roughly 50/50, then N-1 with one line spiking)*

> "Right now, two power lines are quietly splitting one job, about 50/50.
> Watch what happens to the survivor the instant I take ONE of them offline."

**[0:15] INTRO CARD** — *"EP 06/10"*

**[0:35] WHY THIS MATTERS**
> "This `in_service` flag is the single most-used parameter in real grid studies.
> Every 'N-1 contingency' analysis you'll ever hear about — required by grid codes
> worldwide — is built on exactly this toggle."

**[1:30] BUILD IT LIVE**

```python
line1 = pp.create_line(net, from_bus=b1, to_bus=b2, length_km=3.0,
                       std_type="NAYY 4x50 SE", name="Line 1 (Main)")
line2 = pp.create_line(net, from_bus=b1, to_bus=b2, length_km=3.0,
                       std_type="NAYY 4x50 SE", name="Line 2 (Backup)")
pp.create_load(net, bus=b2, p_mw=3.0, q_mvar=0.6)

pp.runpp(net)
print("=== N-0: Both Lines In Service ===")
print(net.res_line[["name", "loading_percent", "i_ka"]])
```
> "Two identical lines, one load. Let's see the split."

```python
net.line.at[line1, 'in_service'] = False
pp.runpp(net)
print("\n=== N-1: Line 1 Out of Service ===")
print(net.res_line[["name", "loading_percent", "i_ka"]])
```
*(point directly at Line 2's loading_percent — it should roughly double)*

**[5:30] THE AHA MOMENT**
> "Line 2's loading just roughly doubled the moment Line 1 went down. If I'd
> sized that backup line for exactly 50% load thinking 'it'll never need more,'
> it would be overloaded right now — and in real life, you wouldn't know until
> something actually tripped."

**[7:00] YOUR TURN**
> "Make the two lines different lengths — say 3 km and 5 km. Before you run it,
> guess: which one carries MORE current in the N-0 case? (Hint: think about
> impedance, not just 'they're parallel so it's 50/50.') Comment your guess,
> then verify."

**[8:00] BRIDGE**
> "We've handled lines tripping. Next: what happens the moment voltage has to
> cross from one voltage *level* to another entirely — through a transformer?"

---

# WORKED EXAMPLE — Full Script: Episode 7

## "Why Does a Transformer Make Voltage Disappear? (20kV → 400V, Live)"
**(Project 7 — Transformer Basic Model)**

**[0:00] COLD OPEN**
*(Screen: HV vm_pu ≈ 1.0 next to LV vm_pu ≈ 0.98, plus actual kV/V conversion printed beneath)*

> "20,000 volts go into this transformer. 400 volts come out. And yet both buses
> show almost the exact same number in this table. That's not a bug — that's
> the whole trick behind per-unit analysis, and today we prove it live."

**[0:15] INTRO CARD** — *"EP 07/10"*

**[0:35] WHY THIS MATTERS**
> "There's a transformer in basically every substation you've ever seen. You
> cannot model a real grid without them. And per-unit is WHY engineers can
> compare a 500kV transmission bus and a 230V household bus on the same 0-to-1.1
> scale without it being confusing."

**[1:30] BUILD IT LIVE**

```python
hv_bus = pp.create_bus(net, vn_kv=20, name="HV Bus (20 kV)")
lv_bus = pp.create_bus(net, vn_kv=0.4, name="LV Bus (400 V)")
pp.create_ext_grid(net, bus=hv_bus, vm_pu=1.0)
pp.create_transformer(net, hv_bus=hv_bus, lv_bus=lv_bus,
                      std_type="0.25 MVA 20/0.4 kV")
pp.create_load(net, bus=lv_bus, p_mw=0.15, q_mvar=0.05)

pp.runpp(net)
print(f"HV: {net.res_bus.vm_pu[hv_bus]:.4f} pu ({net.res_bus.vm_pu[hv_bus]*20:.2f} kV)")
print(f"LV: {net.res_bus.vm_pu[lv_bus]:.4f} pu ({net.res_bus.vm_pu[lv_bus]*0.4*1000:.1f} V)")
print(f"Transformer Loading: {net.res_trafo.loading_percent[0]:.1f}%")
```

**[5:30] THE AHA MOMENT**
> "The HV bus sits at exactly 1.0 — it's the slack bus, fixed by definition.
> The LV bus is just slightly under 1.0. That tiny gap isn't the transformer's
> turns ratio — that part's already baked into the per-unit math. It's the
> transformer's own internal impedance pulling voltage down under load. Small
> number, but at scale, that's a real design constraint."

**[7:00] YOUR TURN**
> "Push the load up toward the transformer's 0.25 MVA rating in steps. At what
> load percentage does the LV voltage cross 0.95 pu? Report the number — that's
> effectively the transformer's real-world safety margin for this load profile."

**[8:00] BRIDGE**
> "We've been reading every result as tables so far. Next time: I'm turning all
> of this into a single chart you can read in three seconds — no table required."

---

# WORKED EXAMPLE — Full Script: Episode 8

## "I Color-Coded an Entire Power Grid by Voltage Health"
**(Project 8 — Plot a Voltage Bar Chart)**

**[0:00] COLD OPEN**
*(Screen: full IEEE 14-bus voltage profile bar chart, green/amber/red bars)*

> "Every bar here is a real bus from a test system used by power engineers
> worldwide. Green means healthy. Red means trouble. You can read this entire
> grid's health in about three seconds — no table required."

**[0:15] INTRO CARD** — *"EP 08/10"*

**[0:35] WHY THIS MATTERS**
> "In real work, plots communicate faster than tables, full stop. A chart like
> this is something a non-technical manager can understand instantly — that's
> the actual job half the time, not just solving the math."

**[1:30] BUILD IT LIVE**

```python
import pandapower.networks as pn

net = pn.case14()
pp.runpp(net)
voltages = net.res_bus.vm_pu

colors = []
for v in voltages:
    if v < 0.95:
        colors.append('#e74c3c')   # red
    elif v < 0.97:
        colors.append('#f39c12')   # amber
    else:
        colors.append('#2ecc71')   # green
```
> "Three thresholds, three colors — that's the entire 'intelligence' of this chart."

```python
plt.bar(bus_names, voltages, color=colors)
plt.axhline(y=0.95, color='red', linestyle='--', label='0.95 pu limit')
plt.axhline(y=1.05, color='orange', linestyle='--', label='1.05 pu limit')
plt.legend()
plt.savefig("voltage_profile.png", dpi=150)
```

**[5:30] THE AHA MOMENT**
> "I never told the code which bus to color red — it decided that from the
> actual number, every time. Swap in a completely different network and this
> same script correctly flags whoever's struggling. That's the difference
> between a one-off chart and a reusable tool."

**[7:00] YOUR TURN**
> "Swap `pn.case14()` for `pn.case33bw()` — a 33-bus radial distribution system
> instead of a transmission system. Does anything turn red? Post your chart."

**[8:00] BRIDGE**
> "We've used the full AC solver every single episode. Next time: there's a
> faster method that a huge amount of the industry uses — and it's quietly
> lying to you about half the physics. Let's catch it."

---

# WORKED EXAMPLE — Full Script: Episode 9

## "AC vs DC Load Flow: Which One Lies to You?"
**(Project 9 — Compare AC vs DC Load Flow)**

**[0:00] COLD OPEN**
*(Screen: side-by-side bus voltage comparison table — DC column is a flat column of 1.0000)*

> "One of these two methods is secretly ignoring half the physics. It's not
> even hiding it — look at this column. Let's catch it red-handed."

**[0:15] INTRO CARD** — *"EP 09/10"*

**[0:35] WHY THIS MATTERS**
> "DC load flow gets used constantly in transmission planning and market
> studies, because it's fast and it always converges. Knowing exactly when
> 'good enough' really is good enough is what separates a beginner from
> someone who gets trusted with real planning decisions."

**[1:30] BUILD IT LIVE**

```python
net_ac = pn.case14()
net_dc = pn.case14()

pp.runpp(net_ac)
pp.rundcpp(net_dc)

for idx in net_ac.res_bus.index:
    ac_v = net_ac.res_bus.vm_pu[idx]
    dc_v = net_dc.res_bus.vm_pu[idx]
    print(f"{idx}: AC={ac_v:.4f}  DC={dc_v:.4f}  diff={ac_v-dc_v:.4f}")
```
*(scroll down — DC column is a flat wall of 1.0000)*

> "DC never even tries to solve for voltage magnitude. It just assumes 1.0
> everywhere. Now let's check what it gets right."

```python
for idx in net_ac.res_line.index:
    ac_p = net_ac.res_line.p_from_mw[idx]
    dc_p = net_dc.res_line.p_from_mw[idx]
    error = abs(ac_p - dc_p) / (abs(ac_p) + 1e-6) * 100
    print(f"Line {idx}: AC={ac_p:.3f} MW  DC={dc_p:.3f} MW  error={error:.2f}%")
```

**[5:30] THE AHA MOMENT**
> "Voltage: completely wrong. Active power flow: within a few percent on most
> lines. That's exactly why DC survives in the industry — it's wrong about one
> thing and close enough about the thing market studies actually care about,
> at a fraction of the computation cost."

**[7:00] YOUR TURN**
> "Time both methods over 1000 runs using Python's `time` module. Report the
> speedup ratio you measure in the comments — I want to see how it scales on
> your machine vs mine."

**[8:00] BRIDGE**
> "Last project of the core ten: how do you actually save your work so you — or
> someone else — can pick up exactly where you left off?"

---

# WORKED EXAMPLE — Full Script: Episode 10

## "Can You Save a Power Grid Simulation and Reload It Perfectly?"
**(Project 10 — Save and Load a Network)**

**[0:00] COLD OPEN**
*(Screen: terminal printing "Results match: True")*

> "I just built a power grid, saved it to a plain text file, completely closed
> everything, reloaded it in a fresh script — and got the exact same numbers
> back, down to six decimal places. That's the line between a hobby script
> and a real engineering workflow."

**[0:15] INTRO CARD** — *"EP 10/10 — Finale"*

**[0:35] WHY THIS MATTERS**
> "Real models get reused across dozens of studies over months. Saving to JSON
> means your model is Git-friendly, shareable with a colleague, and fully
> reproducible. This one habit is what actually makes a project a *project*,
> not just a script you'll lose track of."

**[1:30] BUILD IT LIVE**

```python
net = pp.create_empty_network(name="My Practice Network")
# ...bus/line/transformer/load setup...
pp.runpp(net)
print(net.res_bus[["vm_pu", "va_degree"]])

pp.to_json(net, "practice_network.json")
```
> "One line — `to_json` — and the entire model, every bus, line, and transformer,
> is now sitting in a plain text file."

```python
net_loaded = pp.from_json("practice_network.json")
pp.runpp(net_loaded)
print(net_loaded.res_bus[["vm_pu", "va_degree"]])

match = net.res_bus.vm_pu.round(6).equals(net_loaded.res_bus.vm_pu.round(6))
print(f"Results match: {match}")
```

**[5:30] THE AHA MOMENT**
> "I didn't rebuild a single bus. The model round-tripped through a text file
> and came back identical. That file is now something I could commit to GitHub,
> email to a colleague, or load into a totally different script months from now."

**[7:00] YOUR TURN**
> "Open `practice_network.json` in a plain text editor and find the bus table
> inside it. Tell me in the comments what you notice about how pandapower
> actually stores a network on disk."

**[8:00] SERIES WRAP**
> "That's the core ten — buses, lines, loads, transformers, contingencies,
> AC vs DC, and saving your work. If you followed along, you've covered roughly
> 80% of what you'll actually use pandapower for, day to day. Next, I'm moving
> into intermediate territory — load scaling sensitivity, line loading heatmaps,
> and building the IEEE 14-bus system completely from scratch. Subscribe if you
> want to keep learning this with me."

---

## Publishing notes for the full series

- **Cadence:** 2x/week is sustainable for 6–9 min scripted episodes; pair each
  main episode with a 60–90 sec "Your Turn" Short cut from the same footage —
  doubles your upload surface area with almost no extra filming.
- **Consistent recurring intro card** ("EP 0X/10") trains viewers to binge —
  put it as a pinned playlist with episode numbers in titles, not just topics.
- **Recycle the same diagram/legend assets** (🟢🟡🔴 thresholds, bus/line icons)
  across all 10 — built once in Episode 1, reused for the rest. Saves real
  production time and gives the series a consistent visual identity.
- **Episode 10 doubles as a natural "part 2" cliffhanger** — intermediate
  projects (hosting capacity, N-1 sweep, IEC 60909 short-circuit, OPF, GNN
  surrogate models) are a strong follow-up season once the core 10 has an
  audience.