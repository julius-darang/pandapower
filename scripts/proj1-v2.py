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

from matplotlib.lines import Line2D
# Line2D lets us manually create legend entries (the small colored shapes
# and lines shown in the legend box). We need this because pandapower's
# collections don't produce legend handles automatically.


# =============================================================================
# BUILD THE NETWORK
# =============================================================================

load = 3.0  # MW
# We define the load as a variable so it's easy to change later and see how it 
# affects the results. This is the active power consumed by the load at bus2.
line_km = 1.0
# The length of the line connecting bus1 and bus2. Longer lines have higher
# resistance and reactance, which causes more voltage drop and reduces the
# voltage at bus2. We can experiment with different lengths to see the effect.

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
#   length_km=line_km         → the cable is line_km km long
#   std_type="NAYY 4x50 SE" → a standard cable type defined in pandapower's
#                              built-in library; it specifies resistance (r),
#                              reactance (x), capacitance (c), and current
#                              rating automatically.
#   geodata=[(0,1),(0,0)] → the path of the line on the plot (start and end).

pp.create_load(net, bus=bus2, p_mw=load, q_mvar=0.2, name="Load")
# Attaches a load to bus2.
#   p_mw=load   → consumes the amount of active (real) power defined by the load variable
#   q_mvar=0.2 → consumes 0.2 megavar of reactive power
# Loads are passive consumers; they draw power from the network.

pp.runpp(net)
# Runs the AC power flow (load flow) calculation.
# pandapower solves the set of nonlinear power-flow equations (Newton-Raphson
# by default) and fills in result tables:
#   net.res_bus  → voltage magnitude (vm_pu) and angle (va_degree) per bus
#   net.res_line → power flows, current, and loading % per line
#   net.res_load, net.res_ext_grid, etc.


# =============================================================================
# FIGURE LAYOUT
# =============================================================================
# We use TWO overlapping axes on the same figure:
#
#   ax_host → covers the entire figure; invisible (no ticks/borders).
#             Used only as a fixed coordinate system [0..1, 0..1] so we can
#             place the title and legend at exact figure-relative positions,
#             independent of how the network plot scales.
#
#   ax_net  → a smaller "viewport" inset inside the figure where the actual
#             network diagram is drawn. Its position and size are set manually
#             in figure-fraction units so the symbols stay a consistent size.

fig = plt.figure(figsize=(5, 6))
# Creates a blank figure that is 5 inches wide and 6 inches tall.

ax_host = fig.add_axes([0, 0, 1, 1])
# Adds the host axis.
# [left, bottom, width, height] — all in figure fractions (0 to 1).
# [0, 0, 1, 1] means: start at the bottom-left corner, span the full width
# and full height of the figure.

ax_host.set_xlim(0, 1)
ax_host.set_ylim(0, 1)
# Sets the data coordinate system of ax_host to [0..1] on both axes.
# This makes it easy to position the legend/title using simple fractions
# (e.g., x=0.5 is exactly the horizontal centre of the figure).

ax_host.axis("off")
# Hides all axis decorations (ticks, tick labels, spine borders) on ax_host.
# It becomes completely invisible — purely a coordinate anchor.

ax_net = fig.add_axes([0.15, 0.18, 0.70, 0.65])
# Adds the network viewport axis.
# [0.15, 0.18, 0.70, 0.65] means:
#   left   = 15% from the left edge
#   bottom = 18% from the bottom edge
#   width  = 70% of the figure width
#   height = 65% of the figure height
# This leaves room at the top for the title and at the bottom for the legend.


# =============================================================================
# DRAW THE NETWORK INTO THE VIEWPORT
# =============================================================================

line_loading_pct = net.res_line.loc[0, "loading_percent"]
# Reads the loading percentage of line 0 (our only line) from the load-flow
# results. "loading_percent" = actual current / rated current × 100.
# A value > 100% means the line is overloaded.

line_color = "#090909"
# Sets the line color to near-black.
# The commented-out alternative "#d9534f" (red) / "#5cb85c" (green) would
# color the line red if overloaded and green if within limits — useful for
# visual N-1 contingency checking. It's left commented for now.

lc = plot.create_line_collection(net, color=line_color, linewidths=2.5, zorder=1)
# Creates a matplotlib "collection" of all lines in the network, ready to be
# drawn. Collections are efficient for rendering many similar objects at once.
#   color=line_color → all lines drawn in near-black
#   linewidths=2.5   → line thickness in points
#   zorder=1         → drawn first (furthest back in the z-stack)

bc = plot.create_bus_collection(net, size=0.028, color="#2e6f95", zorder=2)
# Creates circles for every bus.
#   size=0.028   → radius in data coordinates
#   color=...    → steel blue fill
#   zorder=2     → drawn on top of the lines

egc = plot.create_ext_grid_collection(net, size=0.065, zorder=3)
# Creates the standard external grid symbol (a square with diagonal lines)
# at the slack bus location.
#   size=0.065 → symbol size in data coordinates
#   zorder=3   → drawn on top of everything else so it's clearly visible

load_c = plot.create_load_collection(net, size=0.065, zorder=3)
# Creates the standard load symbol (a downward-pointing triangle) at bus2.

plot.draw_collections([lc, bc, egc, load_c], ax=ax_net, plot_colorbars=False)
# Actually renders all four collections onto ax_net in the order given.
#   plot_colorbars=False → suppresses automatic colorbar legends that
#                          pandapower would otherwise add.

ax_net.set_aspect("equal", adjustable="datalim")
# Forces equal scaling on both axes so circles appear as circles (not ovals)
# and vertical/horizontal distances are true to the geodata coordinates.
# "adjustable='datalim'" tells matplotlib to shrink the visible data range
# to achieve equal aspect, rather than stretching the axes box itself.

ax_net.set_xlim(-0.35, 0.35)
ax_net.set_ylim(-0.30, 1.30)
# Manually sets the visible data range so there's breathing room around the
# network symbols and the annotation labels don't get clipped.

ax_net.axis("off")
# Hides ticks and borders on the network axis — we don't want coordinate
# numbers cluttering the diagram.


# =============================================================================
# LABELS (annotations placed relative to network data coordinates)
# =============================================================================
# annotate() draws text near a specific (x, y) data point.
# xy=(...) is the anchor point in data coordinates.
# xytext=(...) is the offset in points (1/72 inch) from the anchor.

vm1 = net.res_bus.loc[bus1, "vm_pu"]
# Reads the voltage magnitude at bus1 from load-flow results.
# vm_pu is in per-unit: 1.0 pu = exactly nominal voltage (20 kV here).

ax_net.annotate(
    f"Slack Bus\n{vm1:.4f} pu",   # label text; \n = newline; :.4f = 4 decimal places
    xy=(0, 1),                    # anchor: bus1's geodata position
    textcoords="offset points",   # interpret xytext as a pixel offset
    xytext=(16, 0),               # shift 16 pts to the right, 0 pts up
    ha="left", va="center",       # horizontal align left, vertical align center
    fontsize=9, fontweight="bold", color="#222222",
)

vm2 = net.res_bus.loc[bus2, "vm_pu"]
# Same as above for bus2. Voltage will be slightly below 1.0 pu due to the
# resistive and reactive voltage drop across the line.

ax_net.annotate(
    f"Load Bus\n{vm2:.4f} pu",
    xy=(0, 0),                    # anchor: bus2's geodata position
    textcoords="offset points",
    xytext=(16, 0),               # also shifted right
    ha="left", va="center",
    fontsize=9, fontweight="bold", color="#222222",
)

ax_net.annotate(
    f"Load\n{load:.1f} MW / 0.2 MVAR",
    xy=(0, 0),                    # also anchored at bus2
    textcoords="offset points",
    xytext=(-16, -26),            # shifted LEFT and DOWN — below the load symbol
    ha="right", va="top",
    fontsize=8, color="#444444",
)

p_from = net.res_line.loc[0, "p_from_mw"]
# Active power (MW) flowing OUT of bus1 (from_bus) into the line.

q_from = net.res_line.loc[0, "q_from_mvar"]
# Reactive power (MVAR) flowing out of bus1 into the line.

ax_net.annotate(
    f"Line 1-2\n{line_loading_pct:.1f}% loaded\nP={p_from:.3f} MW\nQ={q_from:.3f} MVAR",
    xy=(0, 0.5),                  # midpoint of the line (halfway between y=0 and y=1)
    textcoords="offset points",
    xytext=(-16, 0),              # shifted LEFT of the line
    ha="right", va="center",
    fontsize=8, color=line_color, fontweight="bold",
)


# =============================================================================
# TITLE & LEGEND (anchored to ax_host's fixed [0..1] coordinate system)
# =============================================================================

ax_host.set_title(
    "Two-Bus Network — Topology",
    fontsize=13, fontweight="bold", pad=10,
)
# Adds a title above ax_host. Because ax_host spans the full figure, this
# title appears at the very top of the figure. "pad=10" adds 10 pts of space
# between the axes edge and the title text.

legend_handles = [
    # Each Line2D here is a fake "artist" — it's not plotted on the figure,
    # it just describes what the legend entry should look like.

    Line2D([0], [0], marker="s", linestyle="", color="#333333",
           markerfacecolor="none", markersize=8, label="External grid (slack)"),
    # marker="s" → square marker (approximates the ext_grid symbol)
    # linestyle="" → no connecting line, just the marker
    # markerfacecolor="none" → hollow (unfilled) square

    Line2D([0], [0], marker="o", linestyle="", color="#2e6f95",
           markersize=8, label="Bus"),
    # Circle marker in steel blue to represent a bus.

    Line2D([0], [0], marker="v", linestyle="", color="#333333",
           markerfacecolor="none", markersize=8, label="Load"),
    # Downward triangle (≈ load symbol), hollow.

    Line2D([0], [0], color=line_color, linewidth=2,
           label=f"Line ({line_loading_pct:.1f}% loaded)"),
    # A plain horizontal line segment to represent the cable.
    # The label dynamically shows the computed loading percentage.
]

ax_host.legend(
    handles=legend_handles,      # use our manually built entries
    loc="lower center",          # place inside ax_host at the bottom-center
    bbox_to_anchor=(0.5, 0.01),  # fine-tune: centered horizontally, 1% up from bottom
    ncol=2,                      # arrange legend entries in 2 columns
    frameon=False,               # no box/border around the legend
    fontsize=8.5,
)

fig.suptitle(
    "Two-Bus Network — Load Flow Results",
    fontsize=13, fontweight="bold", y=0.9,
)
# fig.suptitle adds a "super title" for the whole figure (not tied to any axis).
# y=0.9 positions it at 90% of the figure height — just above ax_net.
# Note: this creates a second title. ax_host.set_title() is the top-most one;
# fig.suptitle() sits just below it. You could remove one to avoid duplication.


# =============================================================================
# WATERMARK & SAVE
# =============================================================================

fig.text(0.98, 0.02, "@juliusdarang", ha="right", va="bottom",
         fontsize=7, color="#888888", alpha=0.7, style="italic")

plt.savefig("outputs/proj1-v2.png", dpi=150, bbox_inches="tight")
# Saves the figure to disk as a PNG image.
#   dpi=150           → 150 dots per inch — good balance of quality and file size
#   bbox_inches="tight" → trims extra whitespace around the figure edges

plt.show()
# Displays the figure in an interactive window (if runnßing in an IDE or
# Jupyter notebook). Has no effect if running in a headless environment.

print("saved → outputs/proj1-v2.png")
# Simple confirmation message printed to the console.