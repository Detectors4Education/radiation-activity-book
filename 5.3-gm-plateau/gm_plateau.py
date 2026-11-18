# =============================================================================
#  Activity 5.3 - Finding the operating voltage: the GM plateau
#  Equipment: Universal Radiometer + GM Tube Probes (black ~400 V, red ~800 V)
# =============================================================================
#  WHAT THIS SCRIPT DOES (for each probe)
#    1. Converts counts to count rates and plots rate against applied voltage.
#    2. Finds the starting voltage (the first point clearly above background).
#    3. Fits a straight line to the PLATEAU region that YOU choose.
#    4. Calculates the plateau slope in "% per 100 V".
#    5. Suggests an operating voltage about one third of the way along the
#       plateau: safely above the "knee", but far from breakdown.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python gm_plateau.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  probe, voltage_V, counts, time_s
#    probe is "black" or "red".
#
#  >>> IMPORTANT: run the script once, look at YOUR graph, then change the
#  >>> PLATEAU settings below to match the flat part of your own curves.
#
#  PYTHON IDEAS YOU WILL MEET: tuples (a pair of numbers), grouping a table
#  with groupby(), combining conditions with & ("and"), and labelling a graph.
# =============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt

HERE = Path(__file__).parent
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = HERE / "plateau.csv"

# ---- Settings to change after looking at your graph ---------------------------
# (400, 580) is a TUPLE: a fixed pair of values. Here: plateau start and end (volts).
PLATEAU = {"black": (400, 580), "red": (775, 975)}
COLOURS = {"black": "#1B2A49", "red": "#D1495B"}

df = pd.read_csv(DATA_FILE, comment="#")
fig, ax = plt.subplots(figsize=(8, 4.5))

# groupby("probe") splits the table into one smaller table per probe.
# Each time round the loop, "probe" is the name ("black" or "red") and
# "d" is the part of the table for that probe.
for probe, d in df.groupby("probe"):
    V = d.voltage_V.to_numpy(float)                 # voltages
    R = (d.counts / d.time_s).to_numpy()            # count rates
    dR = (np.sqrt(d.counts) / d.time_s).to_numpy()  # their uncertainties

    # ---- STEP 1 - Starting voltage --------------------------------------------
    # R[:2] means "the first two values" (positions 0 and 1). Below the starting
    # voltage the rate is just background, so we average these two.
    base = R[:2].mean()
    t = d.time_s.iloc[0]                            # counting time of one point
    threshold = base + 5 * np.sqrt(base / t) + 1    # 5 sigma above background, plus 1 cps
    # (R > threshold) is an array of True/False. np.argmax gives the position of
    # the FIRST True, so V[...] is the first voltage above the threshold.
    start = V[np.argmax(R > threshold)]

    # ---- STEP 2 - Straight-line fit on the plateau -----------------------------
    v1, v2 = PLATEAU[probe]                         # unpack the tuple into two variables
    # & means "and": keep points with voltage >= v1 AND <= v2 (brackets are needed)
    sel = (V >= v1) & (V <= v2)
    coefficients, cov = np.polyfit(V[sel], R[sel], 1, w=1 / dR[sel], cov="unscaled")
    b = coefficients[0]                             # gradient (cps per volt)
    a = coefficients[1]                             # intercept
    db = np.sqrt(cov[0, 0])
    Vmid = 0.5 * (v1 + v2)                          # middle of the plateau
    R_mid = a + b * Vmid                            # rate in the middle of the plateau
    # Plateau slope: % change in rate for a 100 V change in voltage
    slope_pct = 100 * b * 100 / R_mid
    dslope = 100 * db * 100 / R_mid

    # ---- STEP 3 - Suggested operating voltage ---------------------------------
    V_op = v1 + (v2 - v1) / 3                       # one third of the way along
    print(f"=== {probe} probe ===")
    print(f"  starting voltage        ~ {start:.0f} V")
    print(f"  plateau used            : {v1}-{v2} V  (length {v2-v1} V)")
    print(f"  plateau count rate      ~ {R_mid:.1f} cps")
    print(f"  plateau slope           = {slope_pct:.1f} +/- {dslope:.1f} % per 100 V")
    print(f"  suggested operating V   ~ {V_op:.0f} V\n")

    # ---- STEP 4 - Draw this probe's curve --------------------------------------
    # .get(probe, "grey") looks up the colour, or uses grey for an unknown probe name
    colour = COLOURS.get(probe, "grey")
    ax.errorbar(V, R, yerr=dR, fmt="o-", ms=4, lw=1, capsize=2, color=colour,
                label=f"{probe} probe")
    ax.plot(V[sel], a + b * V[sel], color=colour, lw=4, alpha=0.3)   # wide, pale band
    ax.axvline(V_op, color=colour, ls=":", lw=1.5)                   # dotted vertical line
    ax.annotate(f"operate ≈ {V_op:.0f} V", (V_op, R_mid * 0.45), rotation=90,
                color=colour, fontsize=8, ha="right")

ax.set_xlabel("Applied voltage (V)")
ax.set_ylabel("Count rate (cps)")
ax.set_title("5.3  GM plateau curves (shaded band = fitted plateau)")
ax.grid(alpha=0.3)
ax.legend(frameon=False)
fig.tight_layout()
fig.savefig(HERE / "plateau.png", dpi=200)
print("Graph saved to plateau.png (next to this script)")
