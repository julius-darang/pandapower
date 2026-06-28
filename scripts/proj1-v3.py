# ─────────────────────────────────────────────────────────────────────────────
# IMPORTS
# ─────────────────────────────────────────────────────────────────────────────

import pandapower as pp
# pandapower is the main library for power system modeling and load flow
# analysis. "pp" is just a short alias so we don't have to type "pandapower"
# every time.

import pandapower.plotting as plot
# This sub-module gives us functions to draw the network visually
# (lines, buses, symbols for generators and loads, etc.).

import matplotlib.pyplot as plt
# matplotlib is the standard Python plotting library. We use it to create
# the figure, axes, save the image, and display it.

import matplotlib.gridspec as gridspec
# gridspec is a matplotlib sub-module that lets us define a grid of subplots
# with custom proportions. Unlike plt.subplots() which gives equal-sized panels,``
# GridSpec lets us control the relative width and height of each panel, and even
# merge cells together. We use it here to create a clean 1-row, 3-column layout.

from matplotlib.lines import Line2D
# Line2D lets us manually create legend entries (the small colored shapes
# and lines shown in the legend box). We need this because pandapower's
# collections don't produce legend handles automatically.


# =============================================================================
# BUILD THE NETWORK
# =============================================================================

load = 3.0  # MW
# We define the load as a variable so it's easy to change and experiment with.
# Increasing this value will cause more voltage drop on the line and higher
# line loading — try values like 5.0 or 8.0 to see the line turn red.

line_km = 1.0
# The length of the cable in kilometres. Longer lines have higher total
# resistance and reactance (since R = r_ohm_per_km × length_km), which means
# more voltage drop and power loss. Try 5.0 or 10.0 to see the effect.

net = pp.create_empty_network()
# Creates a blank pandapower network object. Think of this as an empty
# spreadsheet — it holds tables for buses, lines, loads, generators, etc.,
# all currently empty. Everything we create next gets stored inside "net".

bus1 = pp.create_bus(net, vn_kv=20, name="Slack Bus", geodata=(0, 1))
# Adds the first bus to the network.
#   vn_kv=20      → nominal voltage is 20 kV (medium-voltage level)
#   name=...      → just a human-readable label
#   geodata=(0,1) → x=0, y=1 coordinates used for plotting (not electrical)
# Returns the integer index (0) of this bus in net.bus; we store it in bus1.

bus2 = pp.create_bus(net, vn_kv=20, name="Load Bus", geodata=(0, 0))
# Adds the second bus at coordinates (0, 0) — directly below bus1 on the plot.
# Returns index 1; stored in bus2.

pp.create_ext_grid(net, bus=bus1, vm_pu=1.0, name="Grid Connection")
# Connects an external grid (infinite power source / slack bus) to bus1.
#   vm_pu=1.0 → holds bus1 voltage at exactly 1.0 per-unit (= 20 kV).
# The slack bus is the reference point for the load flow; it absorbs or
# supplies whatever active and reactive power the network needs to balance.

pp.create_line(net, from_bus=bus1, to_bus=bus2,
               length_km=line_km, std_type="NAYY 4x50 SE", name="Line 1-2",
               geodata=[(0, 1), (0, 0)])
# Adds a power line connecting bus1 → bus2.
#   length_km=line_km       → cable length driven by our variable above
#   std_type="NAYY 4x50 SE" → a standard cable type from pandapower's built-in
#                              library; it specifies resistance (r_ohm_per_km),
#                              reactance (x_ohm_per_km), capacitance, and rated
#                              current automatically — no need to enter manually.
#   geodata=[(0,1),(0,0)]   → the visual path of the line on the topology plot.

pp.create_load(net, bus=bus2, p_mw=load, q_mvar=0.2, name="Load")
# Attaches a load to bus2.
#   p_mw=load  → consumes the active (real) power set by our load variable
#   q_mvar=0.2 → consumes 0.2 megavar of reactive power (fixed for simplicity)
# Loads are passive consumers; they draw power from the network.

pp.runpp(net)
# Runs the AC power flow (load flow) calculation.
# pandapower solves the set of nonlinear power-flow equations (Newton-Raphson
# by default) and fills in result tables:
#   net.res_bus  → voltage magnitude (vm_pu) and angle (va_degree) per bus
#   net.res_line → power flows, current, and loading % per line
#   net.res_load, net.res_ext_grid, etc.
# Everything after this line can safely read from net.res_* tables.


# =============================================================================
# SHARED RESULT VALUES (computed once, reused across all three panels)
# =============================================================================

line_loading_pct = net.res_line.loc[0, "loading_percent"]
# Reads the loading percentage of line index 0 (our only line).
# loading_percent = (actual current / rated current) × 100.
# A value > 100% means the line is thermally overloaded.

line_color = "#d9534f" if line_loading_pct > 100 else "#5cb85c"
# Picks the line color based on loading status.
# "#d9534f" is a red used when the line exceeds its rated capacity.
# "#5cb85c" is a green for normal operation.
# This same color is reused in the topology diagram, its annotations, and legend.

vm1 = net.res_bus.loc[bus1, "vm_pu"]
# Voltage magnitude at bus1 in per-unit. Since bus1 is the slack bus held
# at 1.0 pu by the external grid, this will always read exactly 1.0000.

vm2 = net.res_bus.loc[bus2, "vm_pu"]
# Voltage magnitude at bus2. This will be slightly below 1.0 pu because
# current flowing through the line's resistance and reactance causes a
# voltage drop. The higher the load or line length, the lower this value.

p_from = net.res_line.loc[0, "p_from_mw"]
# Active power (MW) flowing out of bus1 into the line. This is slightly
# higher than the load's 1.0 MW because some power is lost as heat in the
# cable's resistance (I² × R losses).

q_from = net.res_line.loc[0, "q_from_mvar"]
# Reactive power (MVAR) flowing out of bus1 into the line. Similarly
# slightly higher than the load's 0.2 MVAR due to reactive losses.


# =============================================================================
# FIGURE & GRIDSPEC LAYOUT — 1 row, 3 equal columns
# =============================================================================

fig = plt.figure(figsize=(15, 6))
# Creates a blank figure 15 inches wide and 6 inches tall.
# 15 inches gives enough horizontal room for three panels side by side
# without squishing any of them. At dpi=150 this produces a 2250×900 px image.

fig.suptitle(
    "Two-Bus Network — Load Flow Results",
    fontsize=14, fontweight="bold", y=0.98,
)
# fig.suptitle() adds a single title for the entire figure, sitting above
# all three panels. y=0.98 positions it just inside the top edge of the figure
# (in figure-fraction units where 0=bottom, 1=top).

gs = gridspec.GridSpec(
    1, 3,
    # 1 row, 3 columns — each column will hold one panel.
    figure=fig,
    wspace=0.35,
    # wspace is the horizontal gap between columns, expressed as a fraction
    # of the average axis width. 0.35 = 35% gap, enough room to prevent
    # labels from overlapping between panels.
    left=0.05, right=0.97,
    # Outer left and right margins of the entire grid in figure fractions.
    # left=0.05 leaves a small gap on the left; right=0.97 uses nearly all
    # the right side.
    top=0.88, bottom=0.12,
    # Outer top and bottom margins. top=0.88 leaves room for the suptitle above;
    # bottom=0.12 leaves room for x-axis labels and the topology legend below.
)

ax_topo    = fig.add_subplot(gs[0, 0])
# Creates the topology axis in row 0, column 0 (leftmost panel).

ax_vp      = fig.add_subplot(gs[0, 1])
# Creates the voltage profile axis in row 0, column 1 (middle panel).

ax_loading = fig.add_subplot(gs[0, 2])
# Creates the line loading axis in row 0, column 2 (rightmost panel).


# =============================================================================
# PANEL 1 — TOPOLOGY DIAGRAM (left panel)
# =============================================================================

lc = plot.create_line_collection(net, color=line_color, linewidths=2.5, zorder=1)
# Creates a matplotlib LineCollection for all lines in the network.
# Collections are efficient batches of similar shapes drawn in one call.
#   color=line_color → near-black or red depending on loading status
#   linewidths=2.5   → line thickness in screen points (1 pt = 1/72 inch)
#   zorder=1         → drawn first, behind all other elements

bc = plot.create_bus_collection(net, size=0.028, color="#2e6f95", zorder=2)
# Creates filled circles at each bus location.
#   size=0.028  → radius in data coordinates (the same units as geodata)
#   color=...   → steel blue
#   zorder=2    → drawn on top of the line

egc = plot.create_ext_grid_collection(net, size=0.065, zorder=3)
# Creates the standard external grid symbol (a square with a cross inside)
# at bus1's geodata position.
#   size=0.065 → symbol half-width in data coordinates
#   zorder=3   → on top of everything so it's clearly visible

load_c = plot.create_load_collection(net, size=0.065, zorder=3)
# Creates the standard load symbol (downward-pointing triangle) at bus2.

plot.draw_collections([lc, bc, egc, load_c], ax=ax_topo, plot_colorbars=False)
# Renders all four collections onto ax_topo in the z-order defined above.
# plot_colorbars=False suppresses any automatic colorbar pandapower might add
# (useful when collections are colored by a continuous variable, not needed here).

ax_topo.set_aspect("equal", adjustable="datalim")
# Forces equal scaling on both axes so circles look like circles and not ovals,
# and so the vertical cable isn't stretched or compressed horizontally.
# adjustable="datalim" achieves equal aspect by shrinking the visible data range
# rather than distorting the axes box shape itself.

ax_topo.set_xlim(-0.35, 0.35)
ax_topo.set_ylim(-0.30, 1.30)
# Manually clamps the visible data range. The network only spans x=0, y=0..1
# but we add margins on all sides so annotation text isn't clipped at the edges.

ax_topo.axis("off")
# Hides axis ticks, tick labels, and border lines — this is a diagram,
# not a coordinate chart, so we don't want numbers showing.

ax_topo.set_title("Network Topology", fontweight="bold", fontsize=11, pad=8)
# Title for just this panel. pad=8 adds 8 pts of vertical space between the
# top of the axes and the title text.

ax_topo.annotate(
    f"Slack Bus\n{vm1:.4f} pu",
    # Text to display. \n inserts a line break; :.4f formats to 4 decimal places.
    xy=(0, 1),
    # Anchor point in data coordinates — bus1's geodata position.
    textcoords="offset points",
    # Tells matplotlib that xytext is measured in screen points (not data units).
    xytext=(16, 0),
    # Shifts the label 16 pts to the right of the anchor, 0 pts vertically.
    ha="left", va="center",
    # Horizontal alignment: text starts at the left edge of the anchor point.
    # Vertical alignment: text is centred vertically on the anchor.
    fontsize=9, fontweight="bold", color="#222222",
)

ax_topo.annotate(
    f"Load Bus\n{vm2:.4f} pu",
    xy=(0, 0),
    # Anchor at bus2's geodata position.
    textcoords="offset points",
    xytext=(16, 0),
    # Also shifted right so it sits beside the bus circle.
    ha="left", va="center",
    fontsize=9, fontweight="bold", color="#222222",
)

ax_topo.annotate(
    f"Load\n{load:.1f} MW / 0.2 MVAR",
    xy=(0, 0),
    # Also anchored at bus2 — the load symbol hangs below bus2.
    textcoords="offset points",
    xytext=(-16, -26),
    # Shifted LEFT (so it doesn't collide with the bus label) and DOWN
    # (so it sits below the load triangle symbol).
    ha="right", va="top",
    fontsize=8, color="#444444",
)

ax_topo.annotate(
    f"Line 1-2\n{line_loading_pct:.1f}% loaded\nP={p_from:.3f} MW\nQ={q_from:.3f} MVAR",
    xy=(0, 0.5),
    # Anchor at the visual midpoint of the line (halfway between y=0 and y=1).
    textcoords="offset points",
    xytext=(-16, 0),
    # Shifted LEFT of the line so the label doesn't overlap the cable itself.
    ha="right", va="center",
    fontsize=8, color=line_color, fontweight="bold",
    # Uses the same color as the line (red if overloaded, black otherwise)
    # so the label is visually connected to the element it describes.
)

legend_handles = [
    # Each Line2D below is a "proxy artist" — it never appears on the plot itself.
    # It only exists to define what one legend row should look like.

    Line2D([0], [0], marker="s", linestyle="", color="#333333",
           markerfacecolor="none", markersize=8, label="External grid (slack)"),
    # marker="s"          → square shape (approximates the ext_grid box symbol)
    # linestyle=""        → no line connecting the marker, just the shape
    # markerfacecolor="none" → hollow interior (unfilled square)

    Line2D([0], [0], marker="o", linestyle="", color="#2e6f95",
           markersize=8, label="Bus"),
    # Filled blue circle to represent a bus node.

    Line2D([0], [0], marker="v", linestyle="", color="#333333",
           markerfacecolor="none", markersize=8, label="Load"),
    # Downward-pointing triangle (≈ the load symbol), hollow interior.

    Line2D([0], [0], color=line_color, linewidth=2,
           label=f"Line ({line_loading_pct:.1f}% loaded)"),
    # A short horizontal line segment in the line's color.
    # The label text dynamically inserts the computed loading percentage.
]

ax_topo.legend(
    handles=legend_handles,
    # Use our manually built proxy artists instead of auto-detected ones.
    loc="lower center",
    # Place the legend at the bottom-center of ax_topo's bounding box.
    bbox_to_anchor=(0.5, -0.08),
    # Fine-tunes the anchor point: 0.5 = horizontally centred,
    # -0.08 = 8% below the bottom edge of the axes (outside the plot area).
    ncol=2,
    # Arrange the four legend entries in 2 columns (2 rows of 2).
    frameon=False,
    # No border box drawn around the legend.
    fontsize=8,
)


# =============================================================================
# PANEL 2 — VOLTAGE PROFILE (middle panel)
# =============================================================================
# Shows voltage magnitude at each bus as a connected line-and-marker chart.
# A green shaded band marks the acceptable operating range (±5% of nominal).

bus_names = net.bus["name"].tolist()
# Extracts the "name" column from net.bus as a Python list.
# Result: ["Slack Bus", "Load Bus"]

vm_vals = net.res_bus["vm_pu"].tolist()
# Extracts computed voltage magnitudes from the results table.
# Result: [1.0, <value slightly below 1.0>]

x_pos = range(len(bus_names))
# Creates integer positions 0, 1, ... for each bus along the x-axis.
# matplotlib plots data at numeric x positions; we then replace the tick
# labels with bus names using set_xticklabels() below.

ax_vp.axhspan(0.95, 1.05, color="#cdeccd", alpha=0.5, label="Normal band (±5%)")
# axhspan draws a horizontal rectangle spanning the full width of the plot.
#   0.95, 1.05 → the y-coordinates of the bottom and top of the band
#   color="#cdeccd" → light green fill
#   alpha=0.5       → 50% transparent so the grid lines show through
#   label=...       → this text will appear in the legend for this band

ax_vp.plot(x_pos, vm_vals, "-o", color="#2e6f95", markersize=7, linewidth=2)
# Draws the voltage profile as a line connecting the bus voltages.
#   "-o"  → format string: solid line ("-") with circle markers ("o") at each point
#   color → steel blue to match the bus circles in the topology panel
#   markersize=7  → diameter of each circle marker in points
#   linewidth=2   → thickness of the connecting line in points

for x, v in zip(x_pos, vm_vals):
    ax_vp.annotate(f"{v:.4f}", (x, v),
                   textcoords="offset points", xytext=(0, 8),
                   ha="center", fontsize=8)
# Loops over every bus and places its exact voltage value as text above its marker.
# zip(x_pos, vm_vals) pairs each integer x-position with its voltage value.
# xytext=(0, 8) shifts the label 8 pts straight up from the marker centre.
# ha="center" ensures the text is horizontally centred over the marker.

ax_vp.set_xticks(list(x_pos))
# Explicitly places tick marks at positions 0 and 1 on the x-axis.
# Without this, matplotlib might add extra ticks or space them differently.

ax_vp.set_xticklabels(bus_names, fontsize=9)
# Replaces the default numeric tick labels ("0", "1") with the actual bus names.
# This is why we needed integer x_pos — we place data at integers then relabel.

ax_vp.set_ylabel("Voltage [p.u.]", fontsize=9)
ax_vp.set_title("Voltage Profile", fontweight="bold", fontsize=11, pad=12)
# pad=12 adds 12 pts of vertical space between the axes top and the title,
# giving the annotated voltage values room to breathe.

ax_vp.set_ylim(min(vm_vals) - 0.02, max(vm_vals) + 0.03)
# Sets the y-axis range dynamically based on the actual voltage values.
# -0.02 below the minimum ensures the bottom marker isn't sitting on the axis edge.
# +0.03 above the maximum leaves space for the annotated value text above the marker.

ax_vp.spines[["top", "right"]].set_visible(False)
# "spines" are the four border lines around the axes box (top, right, bottom, left).
# Hiding the top and right spines gives a cleaner, more modern chart appearance.
# The bottom and left spines remain as the x and y axis lines.

ax_vp.grid(axis="y", alpha=0.3)
# Adds faint horizontal grid lines at each y-axis tick.
# axis="y" means only horizontal lines (no vertical ones — those would be distracting).
# alpha=0.3 makes them very faint so they guide the eye without cluttering the chart.

ax_vp.legend(loc="lower left", frameon=False, fontsize=7.5)
# Shows the legend entry for the green normal-band defined by axhspan above.
# loc="lower left" places it in the lower-left corner of the panel.
# frameon=False removes the box border around the legend block.


# =============================================================================
# PANEL 3 — LINE LOADING (right panel)
# =============================================================================
# Shows each line's current loading as a percentage of its rated thermal limit.
# Green = within safe limits; red = overloaded (thermal limit exceeded).

line_names = net.line["name"].tolist()
# Extracts line names from net.line. Result: ["Line 1-2"]

loadings = net.res_line["loading_percent"].tolist()
# Extracts computed loading percentages. Result: e.g. [62.3]

bar_colors = ["#d9534f" if l > 100 else "#5cb85c" for l in loadings]
# List comprehension that assigns a color to each bar based on its loading value.
# "#d9534f" is red (overloaded); "#5cb85c" is green (within limits).
# For each loading value l in the list, we check if l > 100 and pick accordingly.
# With one line, this produces a single-element list like ["#5cb85c"].

bars = ax_loading.bar(line_names, loadings, color=bar_colors, width=0.5)
# Draws one vertical bar per line.
#   line_names → x-axis categories (bar labels)
#   loadings   → bar heights (the loading percentage values)
#   color=bar_colors → each bar gets its own color from the list above
#   width=0.5  → bars are 50% of the available slot width (narrower than default 0.8)
#                for a cleaner look when there are only a few bars

ax_loading.bar_label(bars, fmt="%.1f%%", padding=3, fontsize=9)
# Automatically places a text label directly above each bar showing its value.
#   fmt="%.1f%%" → formats the number to 1 decimal place then appends a literal "%"
#                  (the double "%%" is needed because "%" is a special character
#                  in Python format strings — one "%" escapes the other)
#   padding=3    → adds 3 pts of gap between the top of the bar and the label text

ax_loading.axhline(100, color="#999999", linestyle="--", linewidth=1)
# Draws a dashed horizontal line across the entire plot at y=100%.
# This is the thermal capacity limit — any bar reaching this line is at full load,
# and any bar exceeding it is overloaded. The dashed style clearly distinguishes
# it from the solid grid lines.

ax_loading.annotate(
    "100% limit",
    (len(line_names) - 0.5, 100),
    # x position: half a unit to the left of the last bar's right edge,
    # so the label sits inside the right side of the plot area.
    # y position: exactly at the 100% dashed line.
    textcoords="offset points",
    xytext=(0, 5),
    # Shifts the label 5 pts above the dashed line so it doesn't overlap it.
    ha="right", fontsize=7.5, color="#777777",
    # ha="right" right-aligns the text at the anchor point.
    # Light grey color to match the dashed line and keep it visually secondary.
)

ax_loading.set_ylabel("Loading [%]", fontsize=9)
ax_loading.set_title("Line Loading", fontweight="bold", fontsize=11, pad=12)

ax_loading.set_ylim(0, max(110, max(loadings) * 1.3))
# Sets the y-axis lower bound to 0 (loading can't be negative).
# Upper bound is whichever is larger:
#   110  → ensures the dashed 100% line and its label are always fully visible,
#           even when loading is low (e.g. 30%)
#   max(loadings) * 1.3 → adds 30% headroom above the tallest bar for cases
#           where loading exceeds 100% and the bar_label text needs space above it

ax_loading.spines[["top", "right"]].set_visible(False)
# Same as the voltage profile panel — hides top and right border lines
# for a consistent, clean look across all three panels.

ax_loading.grid(axis="y", alpha=0.3)
# Faint horizontal grid lines only, matching the style of the voltage profile panel.

plt.setp(ax_loading.get_xticklabels(), fontsize=9)
# plt.setp() is a convenience function that applies a property to a list of objects.
# ax_loading.get_xticklabels() returns a list of Text objects (the bar name labels).
# This sets all of their font sizes to 9 in one call, equivalent to looping over
# each label and calling label.set_fontsize(9) individually.


# =============================================================================
# WATERMARK & SAVE
# =============================================================================

fig.text(0.98, 0.02, "@juliusdarang", ha="right", va="bottom",
         fontsize=7, color="#888888", alpha=0.7, style="italic")

plt.savefig("outputs/proj1-v3.png", dpi=150, bbox_inches="tight")
# Saves the full three-panel figure to a PNG file.
#   dpi=150             → 150 dots per inch; at 15 inches wide this gives a
#                         2250-pixel-wide image — sharp without being oversized
#   bbox_inches="tight" → automatically trims any extra whitespace padding
#                         around the outer edges of the figure before saving

plt.show()
# Opens an interactive preview window (works in IDEs and Jupyter notebooks).
# In a headless server environment this does nothing and can be safely removed.

print("saved → outputs/proj1-v3.png")
# Prints a confirmation to the console so you know the file was written
# and where to find it.