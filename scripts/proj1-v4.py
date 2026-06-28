import pandapower as pp
import pandapower.plotting as plot
import matplotlib.pyplot as plt
import matplotlib.gridspec as gridspec
import matplotlib.animation as animation
from matplotlib.lines import Line2D
import numpy as np

loads = np.arange(1.0, 10.0, 2.0)
lengths = np.arange(0.5, 5.5, 0.5)

fig = plt.figure(figsize=(15, 6))
gs = gridspec.GridSpec(1, 3, figure=fig, wspace=0.35,
                       left=0.05, right=0.97, top=0.88, bottom=0.12)
ax_topo = fig.add_subplot(gs[0, 0])
ax_vp = fig.add_subplot(gs[0, 1])
ax_loading = fig.add_subplot(gs[0, 2])

total_frames = len(loads) * len(lengths)

def update(frame):
    li = frame // len(loads)
    lo = frame % len(loads)
    length_val = lengths[li]
    load_val = loads[lo]

    for ax in [ax_topo, ax_vp, ax_loading]:
        ax.clear()

    net = pp.create_empty_network()
    bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus", geodata=(0, 1))
    bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus", geodata=(0, 0))
    pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")
    pp.create_line(net, from_bus=bus1, to_bus=bus2,
                   length_km=length_val, std_type="NAYY 4x50 SE", name="Line 1-2",
                   geodata=[(0, 1), (0, 0)])
    pp.create_load(net, bus=bus2, p_mw=load_val, q_mvar=0.2, name="Load")
    pp.runpp(net)

    line_loading_pct = net.res_line.loc[0, "loading_percent"]
    line_color = "#d9534f" if line_loading_pct > 100 else "#5cb85c"
    vm1 = net.res_bus.loc[bus1, "vm_pu"]
    vm2 = net.res_bus.loc[bus2, "vm_pu"]
    p_from = net.res_line.loc[0, "p_from_mw"]
    q_from = net.res_line.loc[0, "q_from_mvar"]

    # Topology
    lc = plot.create_line_collection(net, color=line_color, linewidths=2.5, zorder=1)
    bc = plot.create_bus_collection(net, size=0.028, color="#2e6f95", zorder=2)
    egc = plot.create_ext_grid_collection(net, size=0.065, zorder=3)
    load_c = plot.create_load_collection(net, size=0.065, zorder=3)
    plot.draw_collections([lc, bc, egc, load_c], ax=ax_topo, plot_colorbars=False)
    ax_topo.set_aspect("equal", adjustable="datalim")
    ax_topo.set_xlim(-0.35, 0.35)
    ax_topo.set_ylim(-0.35, 1.35)
    ax_topo.axis("off")
    ax_topo.set_title("Network Topology", fontweight="bold", fontsize=11)

    ax_topo.annotate(f"Slack Bus\n{vm1:.4f} pu", xy=(0, 1),
                     textcoords="offset points", xytext=(16, 0),
                     ha="left", va="center", fontsize=9, fontweight="bold", color="#222222")
    ax_topo.annotate(f"Load Bus\n{vm2:.4f} pu", xy=(0, 0),
                     textcoords="offset points", xytext=(16, 0),
                     ha="left", va="center", fontsize=9, fontweight="bold", color="#222222")
    ax_topo.annotate(f"Load\n{load_val:.1f} MW / 0.2 MVAR", xy=(0, 0),
                     textcoords="offset points", xytext=(-16, -26),
                     ha="right", va="top", fontsize=8, color="#444444")
    ax_topo.annotate(f"Line 1-2\n{line_loading_pct:.1f}% loaded\nP={p_from:.3f} MW\nQ={q_from:.3f} MVAR",
                     xy=(0, 0.5), textcoords="offset points", xytext=(-16, 0),
                     ha="right", va="center", fontsize=8, color=line_color, fontweight="bold")

    legend_handles = [
        Line2D([0], [0], marker="s", linestyle="", color="#333333",
               markerfacecolor="none", markersize=8, label="External grid (slack)"),
        Line2D([0], [0], marker="o", linestyle="", color="#2e6f95",
               markersize=8, label="Bus"),
        Line2D([0], [0], marker="v", linestyle="", color="#333333",
               markerfacecolor="none", markersize=8, label="Load"),
        Line2D([0], [0], color=line_color, linewidth=2,
               label=f"Line ({line_loading_pct:.1f}% loaded)"),
    ]
    ax_topo.legend(handles=legend_handles, loc="lower center",
                   bbox_to_anchor=(0.5, -0.08), ncol=2, frameon=False, fontsize=8)

    # Voltage profile
    bus_names = net.bus["name"].tolist()
    vm_vals = net.res_bus["vm_pu"].tolist()
    x_pos = range(len(bus_names))
    ax_vp.axhspan(0.95, 1.05, color="#cdeccd", alpha=0.5, label="Normal band (±5%)")
    ax_vp.plot(x_pos, vm_vals, "-o", color="#2e6f95", markersize=7, linewidth=2)
    for x, v in zip(x_pos, vm_vals):
        ax_vp.annotate(f"{v:.4f}", (x, v), textcoords="offset points",
                       xytext=(0, 8), ha="center", fontsize=8)
    ax_vp.set_xticks(list(x_pos))
    ax_vp.set_xticklabels(bus_names, fontsize=9)
    ax_vp.set_ylabel("Voltage [p.u.]", fontsize=9)
    ax_vp.set_title("Voltage Profile", fontweight="bold", fontsize=11)
    ax_vp.set_ylim(0.85, 1.05)
    ax_vp.spines[["top", "right"]].set_visible(False)
    ax_vp.grid(axis="y", alpha=0.3)
    ax_vp.legend(loc="lower left", frameon=False, fontsize=7.5)

    # Line loading
    line_names = net.line["name"].tolist()
    loadings = net.res_line["loading_percent"].tolist()
    bar_colors = ["#d9534f" if l > 100 else "#5cb85c" for l in loadings]
    bars = ax_loading.bar(line_names, loadings, color=bar_colors, width=0.5)
    ax_loading.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
    ax_loading.axhline(100, color="#999999", linestyle="--", linewidth=1)
    ax_loading.set_ylabel("Loading [%]", fontsize=9)
    ax_loading.set_title("Line Loading", fontweight="bold", fontsize=11)
    ax_loading.set_ylim(0, 200)
    ax_loading.spines[["top", "right"]].set_visible(False)
    ax_loading.grid(axis="y", alpha=0.3)
    plt.setp(ax_loading.get_xticklabels(), fontsize=9)

    fig.suptitle(f"Two-Bus Network — Load = {load_val:.1f} MW, Line = {length_val:.1f} km",
                 fontsize=14, fontweight="bold", y=0.98)
    return []

fig.text(0.98, 0.02, "@juliusdarang", ha="right", va="bottom",
         fontsize=7, color="#888888", alpha=0.7, style="italic")

ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=600, repeat=True)

ani = animation.FuncAnimation(fig, update, frames=total_frames, interval=600, repeat=True)
ani.save("outputs/proj1-v4.gif", writer="pillow", dpi=150)
print("saved → outputs/proj1-v4.gif")