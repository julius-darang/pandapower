import pandapower as pp
import matplotlib.pyplot as plt

# ── Build the network ────────────────────────────────────────────────
net = pp.create_empty_network()

bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus")
bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus")

pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")
pp.create_line(net, from_bus=bus1, to_bus=bus2,
               length_km=1.0, std_type="NAYY 4x50 SE", name="Line 1-2")
pp.create_load(net, bus=bus2, p_mw=1.0, q_mvar=0.2, name="Load")

pp.runpp(net)

print(net.res_bus)
print(net.res_line)

# ── Build display-ready tables ──────────────────────────────────────
bus_rows = [
    [net.bus.loc[i, "name"],
     f"{net.res_bus.loc[i, 'vm_pu']:.4f}",
     f"{net.res_bus.loc[i, 'va_degree']:.3f}",
     f"{net.res_bus.loc[i, 'p_mw']:.3f}",
     f"{net.res_bus.loc[i, 'q_mvar']:.3f}"]
    for i in net.res_bus.index
]
bus_cols = ["Bus", "Vm [p.u.]", "Va [deg]", "P [MW]", "Q [MVAr]"]

line_rows = [
    [net.line.loc[i, "name"],
     f"{net.res_line.loc[i, 'p_from_mw']:.3f}",
     f"{net.res_line.loc[i, 'q_from_mvar']:.3f}",
     f"{net.res_line.loc[i, 'pl_mw']:.4f}",
     f"{net.res_line.loc[i, 'loading_percent']:.1f}"]
    for i in net.res_line.index
]
line_cols = ["Line", "P from [MW]", "Q from [MVAr]", "Losses [MW]", "Loading [%]"]

# ── Render as two clean matplotlib tables ───────────────────────────
HEADER_COLOR = "#52a052"
HEADER_TEXT = "white"
ROW_COLORS = ["#f5f7f9", "#ffffff"]

fig, (ax_bus, ax_line) = plt.subplots(2, 1, figsize=(7.5, 3.4))

for ax, title, cols, rows in [
    (ax_bus, "Bus Results", bus_cols, bus_rows),
    (ax_line, "Line Results", line_cols, line_rows),
]:
    ax.axis("off")
    ax.set_title(title, fontweight="bold", fontsize=11, loc="left", pad=8)

    tbl = ax.table(cellText=rows, colLabels=cols, loc="center", cellLoc="center")
    tbl.auto_set_font_size(False)
    tbl.set_fontsize(9.5)
    tbl.scale(1, 1.7)

    n_cols = len(cols)
    for (row, col), cell in tbl.get_celld().items():
        cell.set_edgecolor("#dddddd")
        if row == 0:
            cell.set_facecolor(HEADER_COLOR)
            cell.set_text_props(color=HEADER_TEXT, fontweight="bold")
        else:
            cell.set_facecolor(ROW_COLORS[row % 2])
        if col == 0:
            cell.set_text_props(ha="left")
            cell.PAD = 0.04

fig.suptitle("Two-Bus Network — Load Flow Results", fontweight="bold", fontsize=12)
plt.tight_layout()

fig.text(0.98, 0.02, "@juliusdarang", ha="right", va="bottom",
         fontsize=7, color="#888888", alpha=0.7, style="italic")

plt.savefig("outputs/proj1-v1.png", dpi=150, bbox_inches="tight")
plt.show()
print("saved → outputs/proj1-v1.png")