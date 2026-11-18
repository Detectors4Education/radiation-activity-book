# =============================================================================
#  Activity 5.4 - Beta absorption and the maximum beta energy
#  Equipment: Universal Radiometer + GM Tube Probe, Sr-90/Y-90 source,
#             aluminium absorbers
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Converts absorber thickness (mm) into AREAL DENSITY (g/cm^2).
#    2. Subtracts the background and plots the net rate on a log scale.
#    3. Finds the level of the bremsstrahlung "tail" (thick absorbers: all the
#       betas are stopped, only X-rays and gamma rays get through).
#    4. Fits a straight line to the last part of the beta curve and finds where
#       it meets the tail level. This is the maximum RANGE, R_max.
#    5. Converts R_max into the maximum beta energy E_max with the Katz-Penfold
#       range-energy formula, solved by the computer.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python beta_absorption.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  absorber, thickness_mm, counts, time_s   (one row: absorber = background)
#
#  >>> Change FIT_RANGE and TAIL_START after looking at your own graph. <<<
#
#  PYTHON IDEAS YOU WILL MEET: a weighted mean, solving an equation numerically
#  (brentq), a "lambda" (a one-line function), and random sampling to find an
#  uncertainty.
# =============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import brentq         # finds where a function equals zero

HERE = Path(__file__).parent
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = HERE / "beta_absorption.csv"

# ---- Settings ------------------------------------------------------------------
RHO_AL = 2.70                 # density of aluminium (g/cm^3)
FIT_RANGE = (0.45, 0.95)      # g/cm^2: the last, straight part of the beta curve
TAIL_START = 1.15             # g/cm^2: from here on, only bremsstrahlung and gamma rays


def katz_penfold_range(E):
    """Maximum range (g/cm^2) of electrons with energy E (MeV); valid 0.01-2.5 MeV."""
    return 0.412 * E ** (1.265 - 0.0954 * np.log(E))


# =============================================================================
#  STEP 1 - Read, convert, subtract the background
# =============================================================================
df = pd.read_csv(DATA_FILE, comment="#")
bg = df[df.absorber == "background"].iloc[0]
R_b = bg.counts / bg.time_s
dR_b = np.sqrt(bg.counts) / bg.time_s

d = df[df.absorber != "background"]              # != means "not equal to"
# areal density (g/cm^2) = thickness (cm) x density (g/cm^3); thickness in cm = mm / 10
x = d.thickness_mm.to_numpy() / 10 * RHO_AL
R = (d.counts / d.time_s).to_numpy()
dR = (np.sqrt(d.counts) / d.time_s).to_numpy()
net = R - R_b
dnet = np.sqrt(dR**2 + dR_b**2)

# =============================================================================
#  STEP 2 - Level of the tail (bremsstrahlung + gamma)
# =============================================================================
tail = x >= TAIL_START                           # True for the thick absorbers
# Weighted mean: each point counts with weight 1/sigma^2, so precise points count more.
w = 1 / dnet[tail] ** 2
tail_level = np.sum(net[tail] * w) / np.sum(w)
print(f"Background: {R_b:.2f} cps;  bremsstrahlung tail: {tail_level:.2f} cps")

# =============================================================================
#  STEP 3 - Straight line through the end of the beta curve
# =============================================================================
# On a log scale the end of the curve is roughly straight:  ln(R) = a + b*x
sel = (x >= FIT_RANGE[0]) & (x <= FIT_RANGE[1])  # FIT_RANGE[0] is the first number of the pair
y = np.log(net[sel])
dy = dnet[sel] / net[sel]
coefficients, cov = np.polyfit(x[sel], y, 1, w=1 / dy, cov="unscaled")
b = coefficients[0]
a = coefficients[1]
# {b:+.2f} shows the sign (+ or -) in front of the number
print(f"Fit on {FIT_RANGE} g/cm^2:  ln(R) = {a:.2f} {b:+.2f} x")

# =============================================================================
#  STEP 4 - Range: where the fitted line meets the tail level
# =============================================================================
# Solve  a + b * R_max = ln(tail_level)  for R_max:
R_max = (np.log(tail_level) - a) / b

# Uncertainty: draw 5000 random pairs (b, a) that the fit allows (they follow
# the fit's covariance matrix), and see how much R_max changes.
rng = np.random.default_rng(0)                   # fixed seed: repeatable results
samples = rng.multivariate_normal([b, a], cov, 5000)
b_s = samples[:, 0]                              # first column: all the b values
a_s = samples[:, 1]                              # second column: all the a values
R_s = (np.log(tail_level) - a_s) / b_s
dR_max = R_s.std()
print(f"Maximum range R_max = {R_max:.3f} +/- {dR_max:.3f} g/cm^2 "
      f"= {R_max/RHO_AL*10:.2f} mm of aluminium")

# =============================================================================
#  STEP 5 - Energy from range: solve katz_penfold_range(E) = R_max for E
# =============================================================================
def energy(Rm):
    # brentq(f, low, high) finds the E between 0.01 and 2.5 MeV where f(E) = 0.
    # "lambda E: ..." is a quick one-line function of E.
    return brentq(lambda E: katz_penfold_range(E) - Rm, 0.01, 2.5)

E_max = energy(R_max)
E_s = []                                         # energies for the random samples
for r in R_s:
    if 0.01 < r < 1.2:                           # only ranges inside the formula's limits
        E_s.append(energy(r))
print(f"E_max (Katz-Penfold) = {E_max:.2f} +/- {np.std(E_s):.2f} MeV")
print("Reference: Y-90 E_max = 2.28 MeV, Sr-90 E_max = 0.546 MeV")

# =============================================================================
#  STEP 6 - Graph
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.errorbar(x, net, yerr=dnet, fmt="o", color="#E07A1F", capsize=3, label="net count rate")
xx = np.linspace(FIT_RANGE[0] - 0.1, R_max + 0.05, 50)
ax.plot(xx, np.exp(a + b * xx), color="#1B2A49", lw=1.5, label="fit to end of beta curve")
ax.axhline(tail_level, color="grey", ls="--", label="bremsstrahlung tail")
ax.axvline(R_max, color="#D1495B", ls=":", lw=2, label=f"$R_{{max}}$ = {R_max:.2f} g/cm$^2$")
ax.set_yscale("log")
ax.set_xlabel("Areal density of aluminium (g/cm$^2$)")
ax.set_ylabel("Net count rate (cps)")
ax.set_title(f"5.4  Beta absorption in aluminium   →   $E_{{max}}$ ≈ {E_max:.2f} MeV")
ax.grid(alpha=0.3, which="both")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(HERE / "beta.png", dpi=200)
print("\nGraph saved to beta.png (next to this script)")
