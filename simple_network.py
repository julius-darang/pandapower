"""
Pandapower Simulation: Simple Network with Multigraph Visualization
====================================================================
Creates a distribution network with parallel lines and a transformer,
runs power flow, converts to a NetworkX MultiGraph, and visualizes
the results in a multi-panel figure.  Also produces a pandapower
native plot for comparison.
"""

import pandapower as pp
import pandapower.plotting as ppplot
import matplotlib
matplotlib.use("Agg")  # non-interactive backend; remove if running interactively
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
import numpy as np
import networkx as nx


def create_network() -> pp.Network:
    """
    Build a small distribution network:

        Grid ──Bus 1──┬──Line A──Bus 2──┬──Line C──Bus 3──Load A
                       │                │
                       └──Line B────────┘   └──Trafo──Bus 4──Load B
                                                            └──Solar PV
    """
    net = pp.create_empty_network(name="Simple Distribution Network")

    b1 = pp.create_bus(net, vn_kv=20, name="Bus 1")
    b2 = pp.create_bus(net, vn_kv=20, name="Bus 2")
    b3 = pp.create_bus(net, vn_kv=20, name="Bus 3")
    b4 = pp.create_bus(net, vn_kv=0.4, name="Bus 4")

    pp.create_ext_grid(net, bus=b1, vm_pu=1.02, name="Grid")

    pp.create_line_from_parameters(
        net, from_bus=b1, to_bus=b2,
        length_km=1.5, r_ohm_per_km=0.642, x_ohm_per_km=0.083,
        c_nf_per_km=0.38, max_i_ka=0.142, name="Line A"
    )
    pp.create_line_from_parameters(
        net, from_bus=b1, to_bus=b2,
        length_km=2.0, r_ohm_per_km=0.642, x_ohm_per_km=0.083,
        c_nf_per_km=0.38, max_i_ka=0.142, name="Line B"
    )
    pp.create_line_from_parameters(
        net, from_bus=b2, to_bus=b3,
        length_km=3.0, r_ohm_per_km=0.642, x_ohm_per_km=0.083,
        c_nf_per_km=0.38, max_i_ka=0.142, name="Line C"
    )

    pp.create_transformer_from_parameters(
        net, hv_bus=b3, lv_bus=b4,
        sn_mva=0.63, vn_hv_kv=20, vn_lv_kv=0.4,
        vkr_percent=1.5, vk_percent=6.0,
        pfe_kw=0.3, i0_percent=0.1,
        name="Trafo 1"
    )

    pp.create_load(net, bus=b3, p_mw=1.2, q_mvar=0.3, name="Load A")
    pp.create_load(net, bus=b4, p_mw=0.4, q_mvar=0.1, name="Load B")
    pp.create_sgen(net, bus=b4, p_mw=0.25, q_mvar=0.05, name="Solar PV")

    return net


def build_multigraph(net: pp.Network) -> nx.MultiGraph:
    """
    Convert the pandapower network to a NetworkX MultiGraph.

    Nodes are keyed by integer bus index (net.bus.index).
    Edges carry attributes: type, name, loading, impedance, power flow.
    """
    mg = nx.MultiGraph()

    for bus_idx in net.bus.index:
        bus = net.bus.loc[bus_idx]
        vm = net.res_bus.at[bus_idx, "vm_pu"] if "vm_pu" in net.res_bus.columns else None
        mg.add_node(
            bus_idx,
            label=bus["name"],
            vn_kv=bus["vn_kv"],
            vm_pu=vm,
        )

    for line_idx in net.line.index:
        line = net.line.loc[line_idx]
        res = net.res_line.loc[line_idx]
        mg.add_edge(
            line["from_bus"], line["to_bus"],
            etype="line",
            label=line["name"],
            loading=res["loading_percent"],
            p_from=res["p_from_mw"],
            p_to=res["p_to_mw"],
            pl=res["pl_mw"],
            length_km=line["length_km"],
        )

    for trafo_idx in net.trafo.index:
        trafo = net.trafo.loc[trafo_idx]
        res = net.res_trafo.loc[trafo_idx]
        mg.add_edge(
            trafo["hv_bus"], trafo["lv_bus"],
            etype="transformer",
            label=trafo["name"],
            loading=res["loading_percent"],
            sn_mva=trafo["sn_mva"],
            p_hv=res["p_hv_mw"],
            p_lv=res["p_lv_mw"],
        )

    return mg


def print_results(net: pp.Network):
    """Print a summary of the power flow results."""
    sep = "=" * 62
    print(f"\n{sep}\nPOWER FLOW RESULTS  ({net.name})\n{sep}")

    print("\n--- Bus ---")
    print(net.res_bus.to_string())

    print("\n--- Line ---")
    cols = ["loading_percent", "p_from_mw", "q_from_mvar",
            "p_to_mw", "q_to_mvar", "pl_mw"]
    print(net.res_line[cols].to_string())

    print("\n--- Transformer ---")
    if not net.res_trafo.empty:
        cols_t = ["loading_percent", "p_hv_mw", "q_hv_mvar",
                   "p_lv_mw", "q_lv_mvar"]
        print(net.res_trafo[cols_t].to_string())

    print("\n--- Load ---")
    print(net.res_load.to_string())

    print("\n--- SGen ---")
    print(net.res_sgen.to_string())

    print("\n--- Ext Grid ---")
    print(net.res_ext_grid.to_string())

    print(f"\n--- Element Loadings ---")
    for idx, line in net.line.iterrows():
        ld = net.res_line.at[idx, "loading_percent"]
        tag = "OK" if ld < 80 else "HIGH" if ld < 100 else "OVERLOADED"
        print(f"  {line['name']:12s} {ld:6.1f}%  [{tag}]")
    for idx, trafo in net.trafo.iterrows():
        ld = net.res_trafo.at[idx, "loading_percent"]
        tag = "OK" if ld < 80 else "HIGH" if ld < 100 else "OVERLOADED"
        print(f"  {trafo['name']:12s} {ld:6.1f}%  [{tag}]")

    print(sep)


# ── Colour helpers ──────────────────────────────────────────────
_BUS_COLORS = {"high": "#2ecc71", "mid": "#f39c12", "low": "#e74c3c"}
_LINE_COLORS = {"low": "#3498db", "mid": "#f39c12", "high": "#e74c3c"}


def _bus_color(vm_pu: float) -> str:
    if vm_pu >= 0.95:
        return _BUS_COLORS["high"]
    if vm_pu >= 0.90:
        return _BUS_COLORS["mid"]
    return _BUS_COLORS["low"]


def _line_color(loading: float) -> str:
    if loading > 80:
        return _LINE_COLORS["high"]
    if loading > 50:
        return _LINE_COLORS["mid"]
    return _LINE_COLORS["low"]


# ── Plotting ────────────────────────────────────────────────────
def plot_results(net: pp.Network, mg: nx.MultiGraph):
    fig = plt.figure(figsize=(18, 10))
    gs = fig.add_gridspec(2, 2, hspace=0.35, wspace=0.3)

    # ── 1. MultiGraph topology ──────────────────────────────────
    ax1 = fig.add_subplot(gs[0, :])
    ax1.set_title("Network Topology (MultiGraph)", fontsize=13, fontweight="bold")

    pos = {
        0: np.array([0.0, 0.5]),    # Bus 1
        1: np.array([2.5, 0.5]),    # Bus 2
        2: np.array([5.0, 0.5]),    # Bus 3
        3: np.array([7.5, 0.5]),    # Bus 4
    }

    vm = {n: mg.nodes[n]["vm_pu"] or 1.0 for n in mg.nodes()}
    nx.draw_networkx_nodes(
        mg, pos, ax=ax1,
        node_color=[_bus_color(vm[n]) for n in mg.nodes()],
        node_size=[900 + 1400 * vm[n] for n in mg.nodes()],
        edgecolors="black", linewidths=1.5,
    )
    nx.draw_networkx_labels(
        mg, pos,
        labels={n: f"{mg.nodes[n]['label']}\n{vm[n]:.4f} pu" for n in mg.nodes()},
        ax=ax1, font_size=8, font_weight="bold",
    )

    line_edges = [(u, v, d) for u, v, k, d in mg.edges(keys=True, data=True)
                  if d["etype"] == "line"]
    trafo_edges = [(u, v, d) for u, v, k, d in mg.edges(keys=True, data=True)
                   if d["etype"] == "transformer"]

    if line_edges:
        for u, v, d in line_edges:
            c = _line_color(d["loading"])
            w = 1 + d["loading"] / 25
            nx.draw_networkx_edges(
                mg, pos, ax=ax1,
                edgelist=[(u, v)], edge_color=[c],
                width=w, style="solid",
            )
    if trafo_edges:
        for u, v, d in trafo_edges:
            nx.draw_networkx_edges(
                mg, pos, ax=ax1,
                edgelist=[(u, v)], edge_color=["#9b59b6"],
                width=2.5, style="dashed",
            )

    edge_labels = {}
    for u, v, k, d in mg.edges(keys=True, data=True):
        if d["etype"] == "line":
            edge_labels[(u, v)] = f"{d['label']}\n{d['loading']:.1f}%"
        else:
            edge_labels[(u, v)] = f"{d['label']}\n{d['loading']:.1f}%"
    nx.draw_networkx_edge_labels(mg, pos, edge_labels, ax=ax1, font_size=7)

    legend_items = [
        mpatches.Patch(color=_BUS_COLORS["high"], label="V ≥ 0.95 pu"),
        mpatches.Patch(color=_BUS_COLORS["mid"], label="0.90 ≤ V < 0.95"),
        mpatches.Patch(color=_BUS_COLORS["low"], label="V < 0.90 pu"),
        plt.Line2D([0], [0], color=_LINE_COLORS["low"], lw=2, label="Line (low load)"),
        plt.Line2D([0], [0], color=_LINE_COLORS["mid"], lw=2, label="Line (med load)"),
        plt.Line2D([0], [0], color=_LINE_COLORS["high"], lw=2, label="Line (high load)"),
        plt.Line2D([0], [0], color="#9b59b6", lw=2, ls="--", label="Transformer"),
    ]
    ax1.legend(handles=legend_items, loc="upper left", fontsize=7, framealpha=0.9)
    ax1.set_xlim(-0.8, 8.5)
    ax1.set_ylim(-0.5, 1.5)
    ax1.axis("off")

    # ── 2. Voltage profile ──────────────────────────────────────
    ax2 = fig.add_subplot(gs[1, 0])
    ax2.set_title("Voltage Profile", fontsize=12, fontweight="bold")

    bus_labels = [net.bus.at[i, "name"] for i in net.bus.index]
    vms = net.res_bus.vm_pu.values
    vas = net.res_bus.va_degree.values
    x = np.arange(len(bus_labels))

    bars = ax2.bar(x, vms, color=[_bus_color(v) for v in vms],
                   edgecolor="black", linewidth=0.8)
    ax2.set_xticks(x)
    ax2.set_xticklabels([f"B{i+1}" for i in x], fontsize=10)
    ax2.set_ylabel("Voltage (pu)")
    ax2.set_ylim(0.92, 1.06)
    ax2.axhline(1.0, color="gray", ls="--", alpha=0.5, label="Nominal")
    ax2.axhline(0.95, color="orange", ls=":", alpha=0.5, label="Lower limit (0.95)")
    ax2.legend(fontsize=8)

    for bar, v, va in zip(bars, vms, vas):
        ax2.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.003,
                 f"{v:.4f}\n{va:.1f}°", ha="center", va="bottom", fontsize=8,
                 fontweight="bold")

    # ── 3. Line loading ─────────────────────────────────────────
    ax3 = fig.add_subplot(gs[1, 1])
    ax3.set_title("Line / Transformer Loading", fontsize=12, fontweight="bold")

    load_names = []
    load_vals = []
    load_colors = []
    for idx, line in net.line.iterrows():
        ld = net.res_line.at[idx, "loading_percent"]
        load_names.append(line["name"])
        load_vals.append(ld)
        load_colors.append(_line_color(ld))
    for idx, trafo in net.trafo.iterrows():
        ld = net.res_trafo.at[idx, "loading_percent"]
        load_names.append(trafo["name"])
        load_vals.append(ld)
        load_colors.append("#9b59b6")

    y = np.arange(len(load_names))
    ax3.barh(y, load_vals, color=load_colors, edgecolor="black", linewidth=0.8)
    ax3.set_yticks(y)
    ax3.set_yticklabels(load_names, fontsize=10)
    ax3.set_xlabel("Loading (%)")
    ax3.set_xlim(0, max(load_vals) * 1.3 + 5)
    ax3.axvline(80, color="orange", ls=":", alpha=0.6, label="80% threshold")
    ax3.axvline(100, color="red", ls="--", alpha=0.6, label="100% (overload)")
    ax3.legend(fontsize=8)

    for i, v in enumerate(load_vals):
        ax3.text(v + 1, i, f"{v:.1f}%", va="center", fontsize=9, fontweight="bold")

    fig.suptitle(f"Power Flow Results — {net.name}", fontsize=14, fontweight="bold", y=0.98)
    plt.savefig("multigraph_results.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Saved: multigraph_results.png")


# ── pandapower native plot ───────────────────────────────────────
def plot_pandapower_native(net: pp.Network):
    """
    Use pandapower's built-in simple_plot to render the network.
    This gives a quick schematic view with auto-generated coordinates.
    """
    fig, ax = plt.subplots(figsize=(10, 7))
    ppplot.simple_plot(
        net,
        plot_loads=True,
        plot_sgens=True,
        bus_size=0.5,
        ext_grid_size=0.7,
        load_size=1.5,
        sgen_size=1.5,
        ax=ax,
        show_plot=False,
    )
    ax.set_title(f"pandapower simple_plot — {net.name}", fontsize=13, fontweight="bold")
    plt.savefig("pp_native_plot.png", dpi=150, bbox_inches="tight")
    plt.show()
    print("Saved: pp_native_plot.png")


def main():
    net = create_network()

    print("Running power flow...")
    pp.runpp(net, algorithm="nr", calculate_voltage_angles=True)

    print_results(net)

    print("\nBuilding MultiGraph...")
    mg = build_multigraph(net)
    print(f"  {mg.number_of_nodes()} nodes, {mg.number_of_edges()} edges")

    for u, v, k, d in mg.edges(keys=True, data=True):
        print(f"  [{d['etype']:12s}] {mg.nodes[u]['label']} <-> {mg.nodes[v]['label']}  "
              f"({d['label']}, {d['loading']:.1f}%)")

    plot_results(net, mg)
    plot_pandapower_native(net)


if __name__ == "__main__":
    main()
