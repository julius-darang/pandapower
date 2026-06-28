# pandapower for Beginners: Practice Project Ideas

A hands-on guide for electrical engineers learning pandapower from scratch.
Each project is self-contained, progressively builds on the last, and takes
roughly 30–60 minutes to complete. By the end, you will have covered the core
80% of day-to-day pandapower workflow.

---

## How to Use This Guide

Work through the projects **in order**. The first five can be done in a single
sitting. Later ones introduce new concepts one at a time so nothing feels like
a jump. Every project includes:

- **What you will learn** — the core concept
- **Why it matters** — the engineering context
- **Key pandapower functions** — the exact API calls involved
- **What to try next** — a small extension to deepen understanding

Install pandapower before starting:

```bash
pip install pandapower matplotlib pandas
```

---

## Project 1 — Single-Line Network (2-Bus)

### What you will learn
How to create the simplest possible pandapower network and run a load flow.

### Why it matters
Every pandapower network, no matter how large, is built from the same three
primitives: buses, branches (lines or transformers), and elements (loads,
generators). Mastering the 2-bus case means you understand the data model
before complexity gets in the way.

### The concept
A **slack bus** (also called the reference bus or swing bus) is the bus where
the power system's voltage magnitude and angle are fixed. It acts as the
balance point — any mismatch between generation and load is absorbed here.
All other buses in the network have their voltages solved by the load flow
algorithm relative to this reference.

### Code walkthrough

```python
import pandapower as pp

# Create an empty network
net = pp.create_empty_network()

# Create two buses at 20 kV
bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus")

# Create an external grid (slack source) at bus1
pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")

# Create a standard line between the two buses (1 km long)
pp.create_line(net, from_bus=bus1, to_bus=bus2,
               length_km=1.0, std_type="NAYY 4x50 SE", name="Line 1-2")

# Create a 1 MW, 0.2 MVAr load at bus2
pp.create_load(net, bus=bus2, p_mw=1.0, q_mvar=0.2, name="Load")

# Run load flow
pp.runpp(net)

# Print results
print(net.res_bus)    # Bus voltages and angles
print(net.res_line)   # Line loading, losses, currents
```

### Reading the results
After `pp.runpp(net)`, pandapower populates result tables:

- `net.res_bus.vm_pu` — voltage magnitude in per unit (1.0 = nominal)
- `net.res_bus.va_degree` — voltage angle in degrees
- `net.res_line.loading_percent` — how loaded the line is (>100% = overload)
- `net.res_line.pl_mw` — active power loss on the line

### What to try next
Change the load to `p_mw=5.0` and re-run. Watch the load bus voltage drop.
Increase the line length to `10.0 km` and see how losses grow. This builds
intuition before you add any automation.

---

## Project 2 — Add and Remove a Load

### What you will learn
That a pandapower network is a live Python object — you can modify it between
runs and compare results.

### Why it matters
In real studies you often run "before and after" scenarios: before a new
industrial load connects, after a feeder is upgraded. This project teaches
the workflow for scenario comparison.

### The concept
In pandapower, `net` is a dictionary of pandas DataFrames. Every element you
add (bus, load, line, etc.) becomes a row in one of those DataFrames.
Modifying `net` between runs lets you simulate different operating conditions
without rebuilding the network from scratch each time.

### Code walkthrough

```python
import pandapower as pp

net = pp.create_empty_network()

bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus")
bus3 = pp.create_bus(net, vn_kv=20, name="Secondary Load Bus")

pp.create_ext_grid(net, bus=bus1, vm_pu=1.0)
pp.create_line(net, from_bus=bus1, to_bus=bus2, length_km=2.0,
               std_type="NAYY 4x50 SE")
pp.create_line(net, from_bus=bus2, to_bus=bus3, length_km=1.0,
               std_type="NAYY 4x50 SE")
pp.create_load(net, bus=bus2, p_mw=1.0, q_mvar=0.2, name="Load A")

# --- Scenario 1: Base case (Load A only) ---
pp.runpp(net)
print("=== Base Case ===")
print(net.res_bus[["vm_pu", "va_degree"]])

# --- Add a second load and re-run ---
load_b = pp.create_load(net, bus=bus3, p_mw=2.0, q_mvar=0.5, name="Load B")
pp.runpp(net)
print("\n=== With Load B Added ===")
print(net.res_bus[["vm_pu", "va_degree"]])

# --- Remove Load B and confirm we're back to base ---
net.load.drop(load_b, inplace=True)
pp.runpp(net)
print("\n=== After Removing Load B ===")
print(net.res_bus[["vm_pu", "va_degree"]])
```

### What to observe
The voltage at bus3 will drop noticeably when Load B is added. When Load B is
removed, voltages should return to the base-case values. This confirms that
the network object is stateful and your modifications are correctly tracked.

### What to try next
Instead of removing the load, try setting it to out-of-service:
`net.load.at[load_b, 'in_service'] = False`. This is a cleaner approach
in professional workflows because it preserves the element's parameters for
future reference.

---

## Project 3 — Change Line Impedance

### What you will learn
How line parameters directly affect system losses and bus voltages, and how
to modify element parameters between runs.

### Why it matters
In planning studies you often evaluate the impact of upgrading a line to a
larger conductor or replacing an aging cable. This project shows you how to
simulate that without rebuilding the entire network.

### The concept
A line's resistance (`r_ohm_per_km`) causes active power losses (`I² × R`).
Its reactance (`x_ohm_per_km`) drives reactive power consumption and voltage
drops. Longer lines and smaller conductors mean higher impedance — which
means more losses and lower voltages at the receiving end.

### Code walkthrough

```python
import pandapower as pp

net = pp.create_empty_network()

bus1 = pp.create_bus(net, vn_kv=20, name="Source")
bus2 = pp.create_bus(net, vn_kv=20, name="Load End")

pp.create_ext_grid(net, bus=bus1, vm_pu=1.0)
line_idx = pp.create_line(net, from_bus=bus1, to_bus=bus2,
                          length_km=5.0, std_type="NAYY 4x50 SE")
pp.create_load(net, bus=bus2, p_mw=2.0, q_mvar=0.5)

# --- Run with original line length ---
pp.runpp(net)
print(f"Original (5 km) — Load bus voltage: {net.res_bus.vm_pu[bus2]:.4f} pu")
print(f"Line losses: {net.res_line.pl_mw[line_idx]:.4f} MW")

# --- Simulate a shorter line (infrastructure upgrade) ---
net.line.at[line_idx, 'length_km'] = 2.0
pp.runpp(net)
print(f"\nUpgraded (2 km) — Load bus voltage: {net.res_bus.vm_pu[bus2]:.4f} pu")
print(f"Line losses: {net.res_line.pl_mw[line_idx]:.4f} MW")

# --- Simulate a longer, degraded line ---
net.line.at[line_idx, 'length_km'] = 10.0
pp.runpp(net)
print(f"\nDegraded (10 km) — Load bus voltage: {net.res_bus.vm_pu[bus2]:.4f} pu")
print(f"Line losses: {net.res_line.pl_mw[line_idx]:.4f} MW")
```

### What to observe
As line length increases: voltage at the load bus drops, and losses increase.
You are essentially simulating three different infrastructure scenarios using
the same model — this is exactly how planning engineers use scripted tools.

### What to try next
Instead of changing the line length, change the standard type to a larger
conductor: `net.line.at[line_idx, 'std_type'] = "NAYY 4x150 SE"` and call
`pp.change_std_type(net, line_idx, element='line', std_type="NAYY 4x150 SE")`
to update the impedance values. Compare losses with the original conductor.

---

## Project 4 — Print a Results Summary Function

### What you will learn
How to extract key results from pandapower and format them into a readable
engineering report — a skill you will reuse in every project from here on.

### Why it matters
Raw pandas DataFrames are fine for debugging, but stakeholders and future-you
need a clean summary. Building a reusable `print_summary()` function now means
all your future projects immediately have professional-looking output.

### The concept
After `pp.runpp()`, the main result tables are:

| Table | Contents |
|---|---|
| `net.res_bus` | Voltage magnitude (pu), angle (deg), P and Q injection |
| `net.res_line` | Loading (%), losses (MW, MVAr), current (kA) |
| `net.res_load` | Actual active and reactive power consumed |
| `net.res_ext_grid` | Power supplied by the slack source |

### Code walkthrough

```python
import pandapower as pp

def build_sample_network():
    net = pp.create_empty_network()
    b1 = pp.create_bus(net, vn_kv=20, name="Slack")
    b2 = pp.create_bus(net, vn_kv=20, name="Bus A")
    b3 = pp.create_bus(net, vn_kv=20, name="Bus B")
    pp.create_ext_grid(net, bus=b1, vm_pu=1.0)
    pp.create_line(net, from_bus=b1, to_bus=b2, length_km=3.0,
                   std_type="NAYY 4x50 SE")
    pp.create_line(net, from_bus=b2, to_bus=b3, length_km=2.0,
                   std_type="NAYY 4x50 SE")
    pp.create_load(net, bus=b2, p_mw=1.5, q_mvar=0.3)
    pp.create_load(net, bus=b3, p_mw=2.0, q_mvar=0.5)
    return net

def print_summary(net):
    total_load_mw = net.res_load.p_mw.sum()
    total_loss_mw = net.res_line.pl_mw.sum()
    min_voltage = net.res_bus.vm_pu.min()
    min_voltage_bus = net.res_bus.vm_pu.idxmin()
    max_loading = net.res_line.loading_percent.max()
    max_loading_line = net.res_line.loading_percent.idxmax()

    print("=" * 40)
    print("     LOAD FLOW SUMMARY REPORT")
    print("=" * 40)
    print(f"  Total Load:          {total_load_mw:.3f} MW")
    print(f"  Total Line Losses:   {total_loss_mw:.4f} MW")
    print(f"  Min Voltage:         {min_voltage:.4f} pu  (Bus {min_voltage_bus})")
    print(f"  Max Line Loading:    {max_loading:.2f}%  (Line {max_loading_line})")

    if min_voltage < 0.95:
        print(f"\n  ⚠ VOLTAGE VIOLATION at Bus {min_voltage_bus}!")
    if max_loading > 100:
        print(f"\n  ⚠ OVERLOAD on Line {max_loading_line}!")
    print("=" * 40)

net = build_sample_network()
pp.runpp(net)
print_summary(net)
```

### What to try next
Extend `print_summary()` to also print a per-bus voltage table and a per-line
loading table. Format it so it looks like something you could paste into an
engineering report. This function will become your standard starting point
for all future projects.

---

## Project 5 — Loop Over Load Scenarios

### What you will learn
How to automate parametric studies — the core skill that makes Python-based
power system analysis far more powerful than point-and-click GUI tools.

### Why it matters
In real planning work, you never study just one operating condition. You study
a range: light load, peak load, future load growth. Writing a loop that does
this automatically saves hours compared to manually updating a GUI tool and
re-running each case.

### The concept
This is your first parametric study. You define a list of scenarios, loop
through them, update the network, run the load flow, and collect results.
The output is a table or plot showing how a key metric (voltage, losses,
loading) changes across the scenario range.

### Code walkthrough

```python
import pandapower as pp
import matplotlib.pyplot as plt

net = pp.create_empty_network()
b1 = pp.create_bus(net, vn_kv=20, name="Source")
b2 = pp.create_bus(net, vn_kv=20, name="Load Bus")
pp.create_ext_grid(net, bus=b1, vm_pu=1.0)
pp.create_line(net, from_bus=b1, to_bus=b2, length_km=5.0,
               std_type="NAYY 4x50 SE")
load_idx = pp.create_load(net, bus=b2, p_mw=1.0, q_mvar=0.2)

# Define load scenarios (50% to 150% in steps)
load_levels_mw = [0.5, 1.0, 1.5, 2.0, 2.5, 3.0]
voltages = []
losses = []

for load_mw in load_levels_mw:
    net.load.at[load_idx, 'p_mw'] = load_mw
    pp.runpp(net)
    voltages.append(net.res_bus.vm_pu[b2])
    losses.append(net.res_line.pl_mw.sum())

# Print results table
print(f"{'Load (MW)':<12} {'Voltage (pu)':<15} {'Losses (MW)':<12}")
print("-" * 40)
for load, v, l in zip(load_levels_mw, voltages, losses):
    flag = " ⚠" if v < 0.95 else ""
    print(f"{load:<12.1f} {v:<15.4f} {l:<12.4f}{flag}")

# Plot voltage vs load
plt.figure(figsize=(8, 4))
plt.plot(load_levels_mw, voltages, 'b-o', linewidth=2)
plt.axhline(y=0.95, color='red', linestyle='--', label='0.95 pu limit')
plt.xlabel("Load (MW)")
plt.ylabel("Bus Voltage (pu)")
plt.title("Load Bus Voltage vs. Load Level")
plt.legend()
plt.grid(True)
plt.tight_layout()
plt.savefig("voltage_vs_load.png", dpi=150)
plt.show()
```

### What to observe
The voltage drops as load increases, eventually crossing the 0.95 pu limit.
The flag in the print table tells you exactly which scenarios are violations.
The plot makes this trend immediately readable to any engineer or manager.

### What to try next
Add a second loop that also varies the line length, and store results in a
2D dictionary. Then use a heatmap to show voltage as a function of both
load level and line length simultaneously.

---

## Project 6 — Two Parallel Lines (In-Service Toggle)

### What you will learn
How to take a line out of service and observe how current redistributes —
your first taste of contingency analysis.

### Why it matters
The `in_service` flag is one of the most used parameters in power system
analysis. Every N-1 contingency study is built on this toggle. Understanding
how load redistributes when a line trips is fundamental to transmission and
distribution planning work.

### The concept
When two lines connect the same two buses (parallel lines), current splits
between them proportional to their admittances (the inverse of impedance).
If one line trips, all the current must flow through the remaining line —
which may or may not cause an overload. This is the N-1 security question
at its most basic.

### Code walkthrough

```python
import pandapower as pp

net = pp.create_empty_network()
b1 = pp.create_bus(net, vn_kv=20, name="Source")
b2 = pp.create_bus(net, vn_kv=20, name="Load Bus")

pp.create_ext_grid(net, bus=b1, vm_pu=1.0)

# Two parallel lines — same type and length
line1 = pp.create_line(net, from_bus=b1, to_bus=b2, length_km=3.0,
                       std_type="NAYY 4x50 SE", name="Line 1 (Main)")
line2 = pp.create_line(net, from_bus=b1, to_bus=b2, length_km=3.0,
                       std_type="NAYY 4x50 SE", name="Line 2 (Backup)")

pp.create_load(net, bus=b2, p_mw=3.0, q_mvar=0.6)

# --- Normal operation: both lines in service ---
pp.runpp(net)
print("=== N-0: Both Lines In Service ===")
print(net.res_line[["name", "loading_percent", "i_ka"]].to_string())

# --- Contingency: Line 1 trips ---
net.line.at[line1, 'in_service'] = False
pp.runpp(net)
print("\n=== N-1: Line 1 Out of Service ===")
print(net.res_line[["name", "loading_percent", "i_ka"]].to_string())

# Restore
net.line.at[line1, 'in_service'] = True
```

### What to observe
In the N-0 case, loading splits roughly 50/50 between the two lines. In the
N-1 case, Line 2 carries the full load — its loading percentage approximately
doubles. If you set the load high enough, the N-1 case will show an overload
even though N-0 is fine. That is exactly the kind of finding a planning
engineer documents in a security study.

### What to try next
Make the two lines different lengths (e.g., 3 km and 5 km). The shorter line
will carry more current in the N-0 case because it has lower impedance.
Verify this with the results.

---

## Project 7 — Transformer Basic Model

### What you will learn
How to model a two-winding transformer and verify that pandapower correctly
handles the voltage transformation between HV and LV buses.

### Why it matters
Transformers are at the heart of every substation. You cannot model any
realistic power system without them. This project gets you comfortable with
creating transformer elements and reading per-unit results across different
voltage levels.

### The concept
In per-unit analysis, a transformer's turns ratio is implicit — all buses are
normalized to 1.0 pu regardless of their nominal kV. So a 20 kV bus and a
0.4 kV bus can both show `vm_pu ≈ 1.0` in the results. The transformer
introduces a small voltage drop due to its series impedance (leakage
reactance), which is what you will observe in this project.

### Code walkthrough

```python
import pandapower as pp

net = pp.create_empty_network()

# HV bus at 20 kV, LV bus at 0.4 kV
hv_bus = pp.create_bus(net, vn_kv=20, name="HV Bus (20 kV)")
lv_bus = pp.create_bus(net, vn_kv=0.4, name="LV Bus (400 V)")

# Slack source on HV side
pp.create_ext_grid(net, bus=hv_bus, vm_pu=1.0)

# Standard distribution transformer: 20 kV / 0.4 kV, 250 kVA
pp.create_transformer(net, hv_bus=hv_bus, lv_bus=lv_bus,
                      std_type="0.25 MVA 20/0.4 kV")

# Load on LV side: 150 kW, 50 kVAr
pp.create_load(net, bus=lv_bus, p_mw=0.15, q_mvar=0.05)

pp.runpp(net)

print(f"HV Bus Voltage: {net.res_bus.vm_pu[hv_bus]:.4f} pu  "
      f"({net.res_bus.vm_pu[hv_bus] * 20:.2f} kV)")
print(f"LV Bus Voltage: {net.res_bus.vm_pu[lv_bus]:.4f} pu  "
      f"({net.res_bus.vm_pu[lv_bus] * 0.4 * 1000:.1f} V)")
print(f"\nTransformer Loading: {net.res_trafo.loading_percent[0]:.1f}%")
print(f"Active Power Loss:   {net.res_trafo.pl_mw[0]*1000:.2f} kW")
```

### What to observe
The HV bus stays at 1.0 pu because it is the slack bus. The LV bus will be
slightly below 1.0 pu due to the transformer's leakage impedance under load.
Increase the load toward the transformer's rating (0.25 MVA) and watch the
LV voltage drop and loading approach 100%.

### What to try next
Add a tap changer to the transformer:
`net.trafo.at[0, 'tap_pos'] = 2` and re-run. Observe how adjusting the tap
position changes the LV voltage. This is the basic model for on-load tap
changer (OLTC) studies.

---

## Project 8 — Plot a Voltage Bar Chart

### What you will learn
How to extract results from pandapower and create a clean, publication-ready
voltage profile plot.

### Why it matters
In engineering practice, plots communicate results faster than tables.
A voltage bar chart showing all buses with a red line at the 0.95 pu limit
is immediately readable by any engineer or project manager — even one who
has never seen pandapower code.

### Code walkthrough

```python
import pandapower as pp
import pandapower.networks as pn
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches

# Use a built-in test network for practice
net = pn.case14()  # IEEE 14-bus test system
pp.runpp(net)

voltages = net.res_bus.vm_pu
bus_names = [f"Bus {i}" for i in net.res_bus.index]

# Color code: green = normal, yellow = warning, red = violation
colors = []
for v in voltages:
    if v < 0.95:
        colors.append('#e74c3c')   # red — violation
    elif v < 0.97:
        colors.append('#f39c12')   # yellow — warning
    else:
        colors.append('#2ecc71')   # green — normal

plt.figure(figsize=(12, 5))
bars = plt.bar(bus_names, voltages, color=colors, edgecolor='white', linewidth=0.5)

# Reference lines
plt.axhline(y=0.95, color='red', linestyle='--', linewidth=1.5, label='0.95 pu (lower limit)')
plt.axhline(y=1.05, color='orange', linestyle='--', linewidth=1.5, label='1.05 pu (upper limit)')
plt.axhline(y=1.00, color='gray', linestyle=':', linewidth=1.0, label='1.00 pu (nominal)')

plt.xlabel("Bus")
plt.ylabel("Voltage (pu)")
plt.title("Bus Voltage Profile — IEEE 14-Bus System")
plt.xticks(rotation=45, ha='right')
plt.ylim(0.90, 1.10)

green_patch = mpatches.Patch(color='#2ecc71', label='Normal (≥0.97 pu)')
yellow_patch = mpatches.Patch(color='#f39c12', label='Warning (0.95–0.97 pu)')
red_patch = mpatches.Patch(color='#e74c3c', label='Violation (<0.95 pu)')
plt.legend(handles=[green_patch, yellow_patch, red_patch], loc='lower left')

plt.tight_layout()
plt.savefig("voltage_profile.png", dpi=150)
plt.show()
```

### What to observe
The color coding immediately highlights which buses are in violation or
approaching the limit. This is the style used in real engineering reports.
The IEEE 14-bus system is a standard test case used in academic and
professional power system studies worldwide.

### What to try next
Replace the bar chart with a line plot connecting the buses in feeder order
(for a radial network). This is the classic "voltage profile along a feeder"
plot that distribution engineers use daily.

---

## Project 9 — Compare AC vs DC Load Flow

### What you will learn
The difference between the full AC load flow (`runpp`) and the linearized DC
approximation (`rundcpp`), and when each is appropriate.

### Why it matters
DC load flow is used extensively in transmission planning and market studies
because it runs much faster and always converges. Understanding when DC is
"good enough" and when you need AC is a practical engineering judgment that
separates beginners from experienced analysts.

### The concept

| Feature | AC Load Flow | DC Load Flow |
|---|---|---|
| Voltage magnitudes | Solved | Assumed = 1.0 pu |
| Reactive power | Solved | Ignored |
| Line resistance | Included | Ignored |
| Accuracy | High | Approximate |
| Speed | Slower | Faster |
| Convergence | May fail | Always converges |

DC load flow is a linearized approximation that only solves for active power
flows and voltage angles. It is reasonable for meshed transmission networks
under normal operating conditions but should never be used for voltage studies
or reactive power planning.

### Code walkthrough

```python
import pandapower as pp
import pandapower.networks as pn

net_ac = pn.case14()
net_dc = pn.case14()

# Run both
pp.runpp(net_ac)
pp.rundcpp(net_dc)

# Compare bus voltages (DC assumes vm_pu = 1.0 everywhere)
print("Bus Voltage Comparison (AC vs DC)")
print(f"{'Bus':<6} {'AC vm_pu':<12} {'DC vm_pu':<12} {'Diff':<10}")
print("-" * 42)
for idx in net_ac.res_bus.index:
    ac_v = net_ac.res_bus.vm_pu[idx]
    dc_v = net_dc.res_bus.vm_pu[idx]
    diff = ac_v - dc_v
    print(f"{idx:<6} {ac_v:<12.4f} {dc_v:<12.4f} {diff:<10.4f}")

# Compare active power flows on lines
print("\nLine Active Power Flow Comparison (MW)")
print(f"{'Line':<6} {'AC p_from_mw':<16} {'DC p_from_mw':<16} {'Error %':<10}")
print("-" * 50)
for idx in net_ac.res_line.index:
    ac_p = net_ac.res_line.p_from_mw[idx]
    dc_p = net_dc.res_line.p_from_mw[idx]
    error = abs(ac_p - dc_p) / (abs(ac_p) + 1e-6) * 100
    print(f"{idx:<6} {ac_p:<16.3f} {dc_p:<16.3f} {error:<10.2f}")
```

### What to observe
DC gives `vm_pu = 1.0` for all buses because it does not solve for voltages.
Active power flows are close but not identical to AC — the error is typically
small (1–5%) for well-loaded transmission networks but can be larger for
heavily loaded or reactive-power-dominated systems.

### What to try next
Run both methods 1000 times in a loop and time them using Python's `time`
module. The speed difference will be obvious for larger networks.

---

## Project 10 — Save and Load a Network

### What you will learn
How to persist a pandapower network to disk and reload it — a fundamental
workflow habit for any serious project.

### Why it matters
In real work, you build a network model once and reuse it across many
studies. Saving to JSON means your model is version-controllable (Git),
shareable with colleagues, and reproducible. This is the beginning of a
professional modeling workflow.

### Supported formats

| Format | Function | Best for |
|---|---|---|
| JSON | `pp.to_json` / `pp.from_json` | General use, Git-friendly |
| Excel | `pp.to_excel` / `pp.from_excel` | Sharing with non-Python users |
| Pickle | `pp.to_pickle` / `pp.from_pickle` | Fast local storage |
| SQLite | `pp.to_sqlite` / `pp.from_sqlite` | Database-backed workflows |

### Code walkthrough

```python
import pandapower as pp
import os

# --- Build a network ---
net = pp.create_empty_network(name="My Practice Network")

b1 = pp.create_bus(net, vn_kv=110, name="HV Source")
b2 = pp.create_bus(net, vn_kv=110, name="Bus A")
b3 = pp.create_bus(net, vn_kv=20,  name="LV Distribution")

pp.create_ext_grid(net, bus=b1, vm_pu=1.0)
pp.create_line_from_parameters(
    net, from_bus=b1, to_bus=b2,
    length_km=10, r_ohm_per_km=0.1, x_ohm_per_km=0.35,
    c_nf_per_km=10, max_i_ka=0.5, name="110kV Feeder"
)
pp.create_transformer(net, hv_bus=b2, lv_bus=b3, std_type="25 MVA 110/20 kV")
pp.create_load(net, bus=b3, p_mw=10.0, q_mvar=3.0, name="Distribution Load")

# --- Run load flow ---
pp.runpp(net)
print("Original network results:")
print(net.res_bus[["vm_pu", "va_degree"]])

# --- Save to JSON ---
filepath = "practice_network.json"
pp.to_json(net, filepath)
print(f"\nNetwork saved to: {os.path.abspath(filepath)}")

# --- Load it back ---
net_loaded = pp.from_json(filepath)
pp.runpp(net_loaded)
print("\nLoaded network results (should be identical):")
print(net_loaded.res_bus[["vm_pu", "va_degree"]])

# --- Verify they match ---
match = net.res_bus.vm_pu.round(6).equals(net_loaded.res_bus.vm_pu.round(6))
print(f"\nResults match: {match}")
```

### What to try next
Save the network, open `practice_network.json` in a text editor, and read
through the structure. You will see how pandapower serializes each element
table. Then try loading the file in a completely separate Python script to
confirm it is fully self-contained.

---

## Suggested Study Path

```
Week 1: Projects 1–5    (network creation, result reading, basic automation)
Week 2: Projects 6–7    (contingency toggle, transformer modeling)
Week 3: Projects 8–10   (visualization, AC vs DC, file I/O)
Week 4: Combine all 10  (build a small radial feeder, run scenarios, save results, generate plots)
```

After completing all 10 projects, move on to the intermediate projects:
load scaling sensitivity, line loading heatmaps, the IEEE 14-bus load flow
from scratch, and the CSV-driven network builder.

---

## Quick Reference — Most Used pandapower Commands

```python
# Network creation
net = pp.create_empty_network()
pp.create_bus(net, vn_kv=..., name=...)
pp.create_line(net, from_bus=..., to_bus=..., length_km=..., std_type=...)
pp.create_transformer(net, hv_bus=..., lv_bus=..., std_type=...)
pp.create_load(net, bus=..., p_mw=..., q_mvar=...)
pp.create_ext_grid(net, bus=..., vm_pu=1.0)
pp.create_sgen(net, bus=..., p_mw=..., q_mvar=...)  # for generators/PV

# Load flow
pp.runpp(net)       # Full AC Newton-Raphson
pp.rundcpp(net)     # Linearized DC approximation

# Key result tables
net.res_bus         # Bus voltages and angles
net.res_line        # Line loading and losses
net.res_trafo       # Transformer loading and losses
net.res_load        # Load results
net.res_ext_grid    # External grid power injection

# Element control
net.line.at[idx, 'in_service'] = False   # Take element out of service
net.load.at[idx, 'p_mw'] = value         # Update load
net.trafo.at[idx, 'tap_pos'] = value     # Adjust tap changer

# File I/O
pp.to_json(net, 'filename.json')
net = pp.from_json('filename.json')

# Built-in test networks
import pandapower.networks as pn
net = pn.case14()   # IEEE 14-bus
net = pn.case33bw() # 33-bus radial distribution
```

---

*pandapower documentation: https://pandapower.readthedocs.io*
*pandapower GitHub: https://github.com/e2nIEE/pandapower*