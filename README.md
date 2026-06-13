# Pandapower Simple Network Simulation

A Python script that creates a small distribution network, runs power flow analysis, and visualizes the results using a **MultiGraph** (NetworkX).

## Network Topology

```
Grid ──Bus 1──┬──Line A──Bus 2──┬──Line C──Bus 3──Trafo──Bus 4
              │                │                        │
              └──Line B────────┘                   Load B + Solar PV
                                              Load A
```

- **4 buses** (3 × 20 kV, 1 × 0.4 kV)
- **3 lines** (Line A & B are parallel — true multigraph)
- **1 transformer** (20/0.4 kV)
- **2 loads** + **1 solar PV**

## Setup

```bash
# Create virtual environment
python3 -m venv .venv

# Activate
source .venv/bin/activate

# Install dependencies
pip install pandapower matplotlib networkx

# (Optional) For faster execution
pip install numba
```

## Run

```bash
source .venv/bin/activate
python simple_network.py
```

Outputs:
- Console: power flow results (bus voltages, line loadings, power balance)
- `multigraph_results.png`: 4-panel visualization

## Output Panels

| Panel | Description |
|-------|-------------|
| **MultiGraph** | Network topology with parallel edges, color-coded voltages & loadings |
| **Voltage Profile** | Bar chart of bus voltage magnitudes with angle annotations |
| **Line Loading** | Horizontal bar chart of line/transformer loading percentages |

## MultiGraph Attributes

**Nodes** (buses):
- `label`: bus name
- `vn_kv`: voltage level
- `vm_pu`: voltage magnitude (result)

**Edges** (lines):
- `etype`: "line" or "transformer"
- `label`: element name
- `loading`: loading percentage
- `p_from`, `p_to`, `pl`: power flow (MW)
- `length_km`: line length

**Edges** (transformers):
- `sn_mva`: rated power
- `p_hv`, `p_lv`: HV/LV side power
