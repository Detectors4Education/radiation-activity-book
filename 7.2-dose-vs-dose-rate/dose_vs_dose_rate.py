# =============================================================================
#  Activity 7.2 - Dose versus dose rate
#  Equipment: Personal Dosimeter, gamma check source, metre rule, stopwatch
# =============================================================================
#  THE KEY IDEA
#    dose = dose rate x time        (D = D_dot * t)
#    so a graph of accumulated dose against time should be a straight line
#    whose GRADIENT is the dose rate.
#
#  WHAT THIS SCRIPT DOES (for each of the two positions)
#    1. Fits a straight line to accumulated dose (uSv) against time (h).
#    2. Compares the gradient with the average dose-rate reading on the display.
#    3. Checks the inverse-square law between the two positions.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python dose_vs_dose_rate.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  time_min, dose_uSv_pos1, rate_uSvh_pos1, dose_uSv_pos2, rate_uSvh_pos2
#
#  >>> Change DIST to the distances you actually used.
#
#  PYTHON IDEAS YOU WILL MEET: building column names with f-strings, an
#  unweighted straight-line fit, a dictionary that stores pairs of values,
#  and np.hypot for combining two uncertainties.
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
    DATA_FILE = HERE / "dose_vs_time.csv"

DIST = {"pos1": 10, "pos2": 20}           # source-to-dosimeter distances in cm (change!)
COL = {"pos1": "#2E8B57", "pos2": "#E07A1F"}

df = pd.read_csv(DATA_FILE, comment="#")
t_h = df.time_min.to_numpy() / 60         # time in hours (minutes / 60)
fig, ax = plt.subplots(figsize=(7, 4.5))
gradients = {}                            # will hold (gradient, uncertainty) for each position

for pos in ["pos1", "pos2"]:
    # f"dose_uSv_{pos}" becomes "dose_uSv_pos1" the first time and "dose_uSv_pos2" the second.
    D = df[f"dose_uSv_{pos}"].to_numpy()
    rates = df[f"rate_uSvh_{pos}"].to_numpy()

    # ---- STEP 1 - Straight-line fit  D = D_dot * t + c --------------------------
    # No weights here: all dose readings have the same display resolution.
    # cov=True asks polyfit to estimate the uncertainties from the scatter of the points.
    coefficients, cov = np.polyfit(t_h, D, 1, cov=True)
    g = coefficients[0]                   # gradient = dose rate (uSv/h)
    c = coefficients[1]                   # intercept (should be about 0)
    dg = np.sqrt(cov[0, 0])
    gradients[pos] = (g, dg)

    # ---- STEP 2 - Average of the displayed dose-rate readings ---------------------
    mean_rate = rates.mean()
    sem_rate = rates.std(ddof=1) / np.sqrt(len(rates))   # standard error of the mean
    print(f"=== {pos} ({DIST[pos]} cm) ===")
    print(f"  gradient of D(t)      = {g:.2f} +/- {dg:.2f} uSv/h")
    print(f"  mean displayed rate   = {mean_rate:.2f} +/- {sem_rate:.2f} uSv/h")
    # How many combined uncertainties apart are the two values?
    # np.hypot(a, b) = sqrt(a^2 + b^2)
    diff = (g - mean_rate) / np.hypot(dg, sem_rate)
    print(f"  difference            = {diff:.1f} combined standard uncertainties\n")

    ax.plot(df.time_min, D, "o", color=COL[pos], label=f"{pos}: {DIST[pos]} cm")
    ax.plot(df.time_min, g * t_h + c, "-", color=COL[pos], lw=1.2, label=f"fit: {g:.2f} µSv/h")

# =============================================================================
#  STEP 3 - Inverse-square check
# =============================================================================
# gradients["pos1"][0] is the first item of the stored pair: the gradient itself.
ratio = gradients["pos1"][0] / gradients["pos2"][0]
expected = (DIST["pos2"] / DIST["pos1"]) ** 2
print(f"Dose-rate ratio pos1/pos2 = {ratio:.2f}; inverse-square law predicts {expected:.2f}")
print("(Real sources and detectors are not points, so expect some difference.)")

ax.set_xlabel("Time (min)")
ax.set_ylabel("Accumulated dose (µSv)")
ax.set_title("7.2  Accumulated dose increases linearly with time")
ax.grid(alpha=0.3)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(HERE / "dose.png", dpi=200)
print("\nGraph saved to dose.png (next to this script)")
