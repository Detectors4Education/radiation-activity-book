# =============================================================================
#  Activity 8.5 - Commissioning and cross-calibrating your DIY GM counter
#  Equipment: DIY Geiger-Mueller Set GC DIY 4 EDU (built), GM Counter unit as
#             the reference instrument, gamma check source, granite sample
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Turns the dose shown by the DIY counter (bottom line of its display)
#       into a dose RATE in uSv/h, with an uncertainty from counting statistics.
#    2. Fits the straight line  D_diy = a * D_ref + c,  where D_ref is the dose
#       rate shown by the reference counter.
#       a is the CALIBRATION RATIO (ideally 1); c is a small offset.
#    3. Turns the line round, so that you can correct any DIY reading.
#    4. Plots the calibration, with the residuals (data minus line) underneath.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python cross_calibration.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  position, reference_uSvh, diy_dose_uSv, time_s
#    diy_dose_uSv = increase of the DIY counter's bottom line (cumulative dose)
#                   during the time time_s
#
#  PYTHON IDEAS YOU WILL MEET: a weighted fit, residuals, two graphs that share
#  an x axis, and writing labels next to points (annotate).
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
    DATA_FILE = HERE / "cross_calibration.csv"

NOMINAL_S = 80        # cpm per uSv/h quoted for the GM 4 EDU tubes by the manufacturer
                      # (used here only to estimate how many counts were behind each reading)

# =============================================================================
#  STEP 1 - Read the data and convert the DIY dose into a dose rate
# =============================================================================
df = pd.read_csv(DATA_FILE, comment="#")
rate = df.diy_dose_uSv / df.time_s * 3600             # DIY dose rate in uSv/h
# Roughly how many pulses did the tube count? N = (uSv/h) x (cpm per uSv/h) x minutes
N = np.maximum(rate * NOMINAL_S * df.time_s / 60, 1)
drate = rate / np.sqrt(N)                              # square-root rule: sigma/value = 1/sqrt(N)
D = df.reference_uSvh.to_numpy()                       # reference dose rates

# =============================================================================
#  STEP 2 - Weighted straight-line fit  D_diy = a * D_ref + c
# =============================================================================
coefficients, cov = np.polyfit(D, rate, 1, w=1 / drate, cov="unscaled")
a = coefficients[0]                                   # gradient = calibration ratio
c = coefficients[1]                                   # intercept = offset
da = np.sqrt(cov[0, 0])
dc = np.sqrt(cov[1, 1])
resid = rate - (a * D + c)                            # residuals: data minus line
chi2 = np.sum((resid / drate) ** 2)
print(f"Calibration ratio  a = {a:.3f} +/- {da:.3f}   (a perfect counter gives 1)")
print(f"Offset             c = {c:.3f} +/- {dc:.3f} uSv/h")
print(f"chi^2/ndf = {chi2:.1f}/{len(D)-2}")
print("Note: the reference dose rates also have uncertainties, so chi^2 may be large.\n")

# =============================================================================
#  STEP 3 - The correction for your DIY counter
# =============================================================================
# Rearranging D_diy = a*D_ref + c for D_ref gives  D_ref = (D_diy - c) / a
print("Correction for your DIY counter:")
print(f"   true dose rate (uSv/h) = (DIY reading - {c:.3f}) / {a:.3f}")
print(f"   e.g. a DIY reading of 1.00 uSv/h  ->  {(1.00 - c)/a:.2f} uSv/h")
print(f"Your tube is {abs(a-1)*100:.0f} % {'more' if a > 1 else 'less'} sensitive than the display assumes.")

# =============================================================================
#  STEP 4 - Graph with residuals
# =============================================================================
# Two panels above each other that share the x axis; the top one is 3 times taller.
fig, (a1, a2) = plt.subplots(2, 1, figsize=(7, 5.5), sharex=True,
                             gridspec_kw={"height_ratios": [3, 1]})

a1.errorbar(D, rate, yerr=drate, fmt="o", color="#2E8B57", capsize=3, label="DIY counter")
DD = np.linspace(0, D.max() * 1.05, 50)
a1.plot(DD, a * DD + c, color="#1B2A49", label=f"fit: a = {a:.2f}")
a1.plot(DD, DD, "--", color="grey", label="perfect agreement (a = 1)")
# Write each position's name next to its point.
for i in range(len(df)):
    label = df.position[i].replace("_", " ")         # "source_10cm" -> "source 10cm"
    a1.annotate(label, (D[i], rate[i]), textcoords="offset points", xytext=(5, -10), fontsize=7)
a1.set_ylabel("DIY dose rate (µSv/h)")
a1.legend(frameon=False, fontsize=8)
a1.grid(alpha=0.3)
a1.set_title("8.5  Cross-calibration of the DIY counter")

a2.errorbar(D, resid, yerr=drate, fmt="o", color="#2E8B57", capsize=3)
a2.axhline(0, color="grey")
a2.grid(alpha=0.3)
a2.set_xlabel("Reference dose rate (µSv/h)")
a2.set_ylabel("Residual (µSv/h)")

fig.tight_layout()
fig.savefig(HERE / "calibration.png", dpi=200)
print("\nGraph saved to calibration.png (next to this script)")
