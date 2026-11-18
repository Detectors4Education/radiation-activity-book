# =============================================================================
#  Activity 4.4 - The inverse-square law for gamma radiation
#  Detector: Geiger-Mueller Counter unit (GC 4 EDU) (handheld)
# =============================================================================
#  THE MODEL
#    A small (point) source gives a count rate
#                R(d) = k / (d + d0)^2  +  B
#    d  = the distance you measure (source to the FRONT of the counter)
#    d0 = an unknown extra distance to the "effective centre" of the GM tubes
#    B  = the background rate
#
#  WHAT THIS SCRIPT DOES
#    1. Reads distances and counts, and converts them to count rates
#       (with an optional dead-time correction using a known dead time tau).
#    2. LINEAR method: plots 1/sqrt(R - B) against d. This gives a straight line
#       whose gradient is 1/sqrt(k) and whose x-intercept is -d0.
#    3. NON-LINEAR method: fits k, d0 and B directly with SciPy's curve_fit.
#    4. Tests the power: fits R - B = k / (d + d0)^n and checks that n = 2.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python inverse_square.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  distance_cm, counts, time_s
#
#  PYTHON IDEAS YOU WILL MEET: settings at the top of a script, writing a
#  model as a function, curve_fit (fitting any formula), starting guesses,
#  and selecting array elements with a condition.
# =============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit      # fits any function to data

HERE = Path(__file__).parent
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = HERE / "inverse_square.csv"

# ---- Settings: change these to YOUR values -----------------------------------
TAU = 2.0e-4          # dead time in seconds, e.g. from the manual (put 0 to switch the correction off)
BACKGROUND = 0.35     # background rate in cps, measured separately with no source

# =============================================================================
#  STEP 1 - Read the data and make count rates
# =============================================================================
df = pd.read_csv(DATA_FILE, comment="#")
d = df.distance_cm.to_numpy(float)        # distances as an array of decimal numbers
m = df.counts / df.time_s                 # observed (measured) rate
dm = np.sqrt(df.counts) / df.time_s       # its Poisson uncertainty
# Dead-time correction: true rate = m / (1 - m*tau)
R = (m / (1 - m * TAU)).to_numpy()
dR = (dm / (1 - m * TAU) ** 2).to_numpy()

# =============================================================================
#  STEP 2 - Linear method: 1/sqrt(R - B) is a straight line in d
# =============================================================================
y = 1 / np.sqrt(R - BACKGROUND)
dy = 0.5 * dR / (R - BACKGROUND) ** 1.5   # uncertainty of y (error propagation)
coefficients, cov = np.polyfit(d, y, 1, w=1 / dy, cov="unscaled")
slope = coefficients[0]
icpt = coefficients[1]                    # intercept on the y axis
k_lin = 1 / slope**2                      # because slope = 1/sqrt(k)
d0_lin = icpt / slope                     # the line crosses y = 0 at d = -d0
print("Linear method  (1/sqrt(R-B) versus d)")
print(f"  k  = {k_lin:.0f} cps cm^2,   d0 = {d0_lin:.2f} cm\n")

# =============================================================================
#  STEP 3 - Non-linear fit of the full model
# =============================================================================
# The model is written as a Python function. The FIRST input must be the x
# values; the others (k, d0, B) are the parameters that curve_fit will adjust.
def model(d, k, d0, B):
    return k / (d + d0) ** 2 + B

# curve_fit needs:  the function, the x data, the y data,
#   p0    = starting guesses for the parameters (here: the linear-method results),
#   sigma = the error bars, and absolute_sigma=True to use them as real uncertainties.
# It returns the best parameters p and their covariance matrix pcov.
p, pcov = curve_fit(model, d, R, p0=[k_lin, d0_lin, BACKGROUND], sigma=dR,
                    absolute_sigma=True)
perr = np.sqrt(np.diag(pcov))             # uncertainties = square roots of the diagonal
# model(d, *p): the * "unpacks" the list p into the three inputs k, d0, B
chi2 = np.sum(((R - model(d, *p)) / dR) ** 2)
print("Non-linear fit  R = k/(d+d0)^2 + B")
names = ["k (cps cm^2)", "d0 (cm)", "B (cps)"]
for i in range(3):                        # i = 0, 1, 2
    print(f"  {names[i]:<13} = {p[i]:9.3f} +/- {perr[i]:.3f}")
print(f"  chi^2/ndf = {chi2:.1f}/{len(d)-3}\n")

# =============================================================================
#  STEP 4 - Is the power really 2?  Let n be a free parameter.
# =============================================================================
def model_n(d, k, d0, n):
    return k / (d + d0) ** n

pn, pncov = curve_fit(model_n, d, R - BACKGROUND, p0=[p[0], p[1], 2.0], sigma=dR,
                      absolute_sigma=True)
print(f"Free exponent fit: n = {pn[2]:.3f} +/- {np.sqrt(pncov[2,2]):.3f}  (expected 2)")

# =============================================================================
#  STEP 5 - Graphs
# =============================================================================
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))
dd = np.linspace(0, d.max() * 1.05, 200)
smooth = dd[dd > 0.5]                     # keep only distances above 0.5 cm (a condition selects elements)

# Left panel: the count rate on a log scale with the fitted model
a1.errorbar(d, R, yerr=dR, fmt="o", color="#D1495B", capsize=3, label="data")
a1.plot(smooth, model(smooth, *p), color="#1B2A49", label="fit $k/(d+d_0)^2+B$")
a1.set_yscale("log")
a1.set_xlabel("Distance d (cm)")
a1.set_ylabel("Count rate R (cps)")
a1.set_title("Count rate versus distance", fontsize=10)
a1.legend(frameon=False)

# Right panel: the straight-line (linearised) plot
a2.errorbar(d, y, yerr=dy, fmt="o", color="#D1495B", capsize=3, label="data")
x2 = np.linspace(-d0_lin * 1.2, d.max(), 50)
a2.plot(x2, slope * x2 + icpt, color="#1B2A49", label=f"line: x-intercept = {-d0_lin:.2f} cm")
a2.axhline(0, color="grey", lw=0.8)       # the x axis
a2.axvline(0, color="grey", lw=0.8)       # the y axis
a2.set_xlabel("Distance d (cm)")
a2.set_ylabel(r"$1/\sqrt{R-B}$  (cps$^{-1/2}$)")
a2.set_title("Linearised plot", fontsize=10)
a2.legend(frameon=False)

for a in (a1, a2):
    a.grid(alpha=0.3, which="both")
fig.suptitle("4.4  Inverse-square law", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "inverse_square.png", dpi=200)
print("\nGraph saved to inverse_square.png (next to this script)")
