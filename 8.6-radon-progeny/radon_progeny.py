# =============================================================================
#  Activity 8.6 - Catching radon "daughters" on a balloon: measuring a half-life
#  Equipment: a GM counter that gives counts per minute (GM Counter unit with
#             USB logging, or the DIY counter, see the book), balloon, stopwatch
# =============================================================================
#  A charged balloon collects the short-lived decay products of radon gas:
#  Pb-214 (half-life 26.8 min) and Bi-214 (half-life 19.9 min).
#
#  WHAT THIS SCRIPT DOES
#    1. Subtracts the background and converts counts to counts per minute (cpm).
#    2. LEVEL 1: fits a single exponential  A(t) = A0 * exp(-lambda t)  and
#       reports the APPARENT half-life.
#    3. LEVEL 2 (university): fits the two-step decay chain
#           Pb-214 -> Bi-214 -> (Po-214, almost instant)
#       with the known half-lives (Bateman equations), and finds how much of
#       each nuclide was on the balloon at t = 0.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python radon_progeny.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  time_min, counts, time_s
#    time_min = when each count STARTED (minutes after the balloon was placed on the tube)
#
#  >>> Put YOUR background measurement into BG_COUNTS and BG_TIME.
#
#  PYTHON IDEAS YOU WILL MEET: two models written as functions, curve_fit with
#  error bars, comparing models with chi-squared, and documentation strings.
# =============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

HERE = Path(__file__).parent
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = HERE / "radon_progeny.csv"

BG_COUNTS = 1310           # background counts measured without the balloon ...
BG_TIME = 3600             # ... in this many seconds

# =============================================================================
#  STEP 1 - Net count rate in cpm
# =============================================================================
df = pd.read_csv(DATA_FILE, comment="#")
# Use the MIDDLE of each counting interval as its time: start + half the length.
# The length is time_s seconds = time_s / 60 minutes, so half of it is time_s / 120.
t = df.time_min.to_numpy(float) + df.time_s.to_numpy() / 120
cpm = df.counts / df.time_s * 60               # counts per minute
dcpm = np.sqrt(df.counts) / df.time_s * 60
bg = BG_COUNTS / BG_TIME * 60                  # background in cpm
d_bg = np.sqrt(BG_COUNTS) / BG_TIME * 60
net = (cpm - bg).to_numpy()
dnet = np.sqrt(dcpm**2 + d_bg**2).to_numpy()
print(f"Background = {bg:.1f} cpm")

# =============================================================================
#  STEP 2 - LEVEL 1: one exponential
# =============================================================================
def single(t, A0, lam):
    """Simple exponential decay: starting rate A0, decay constant lam (per minute)."""
    return A0 * np.exp(-lam * t)

# Starting guesses: the first measured rate, and lambda = 0.02 per minute.
p1, c1 = curve_fit(single, t, net, p0=[net[0], 0.02], sigma=dnet, absolute_sigma=True)
lam = p1[1]
dlam = np.sqrt(c1[1, 1])
T1 = np.log(2) / lam                           # half-life = ln2 / lambda
dT1 = T1 * dlam / lam                          # same relative uncertainty as lambda
chi1 = np.sum(((net - single(t, *p1)) / dnet) ** 2)
print(f"\nLEVEL 1  apparent half-life = {T1:.1f} +/- {dT1:.1f} min "
      f"(chi^2/ndf = {chi1:.0f}/{len(t)-2})")

# =============================================================================
#  STEP 3 - LEVEL 2: the Pb-214 -> Bi-214 decay chain
# =============================================================================
lPb = np.log(2) / 26.8                         # decay constants from nuclear data (per minute)
lBi = np.log(2) / 19.9


def chain(t, NPb0, NBi0):
    """Total count rate from Pb-214 and Bi-214 (the detection efficiency is included in N).
    NPb0 and NBi0 are the numbers of atoms of each on the balloon at t = 0."""
    NPb = NPb0 * np.exp(-lPb * t)
    # Bi-214 decays, but is also made from Pb-214 (Bateman equation):
    NBi = (NBi0 * np.exp(-lBi * t)
           + NPb0 * lPb / (lBi - lPb) * (np.exp(-lPb * t) - np.exp(-lBi * t)))
    return lPb * NPb + lBi * NBi               # activity = lambda x N for each, added


p2, c2 = curve_fit(chain, t, net, p0=[3000, 3000], sigma=dnet, absolute_sigma=True)
chi2 = np.sum(((net - chain(t, *p2)) / dnet) ** 2)
e2 = np.sqrt(np.diag(c2))
print(f"LEVEL 2  N(Pb-214, t=0) = {p2[0]:.0f} +/- {e2[0]:.0f},  "
      f"N(Bi-214, t=0) = {p2[1]:.0f} +/- {e2[1]:.0f}  (x efficiency)")
print(f"         ratio Bi/Pb at t=0 = {p2[1]/p2[0]:.2f}   chi^2/ndf = {chi2:.0f}/{len(t)-2}")

# =============================================================================
#  STEP 4 - Graph
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4.5))
ax.errorbar(t, net, yerr=dnet, fmt="o", ms=3.5, color="#8C5E3C", capsize=2, label="net count rate")
tt = np.linspace(0, t.max(), 300)
ax.plot(tt, single(tt, *p1), "--", color="#D1495B",
        label=f"single exponential: $T_{{1/2}}$ = {T1:.1f} min")
ax.plot(tt, chain(tt, *p2), color="#1B2A49", label="Pb-214 → Bi-214 chain")
ax.set_yscale("log")
ax.set_xlabel("Time after collection (min)")
ax.set_ylabel("Net count rate (cpm)")
ax.grid(alpha=0.3, which="both")
ax.set_title("8.6  Decay of radon progeny collected on a balloon")
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(HERE / "radon.png", dpi=200)
print("\nGraph saved to radon.png (next to this script)")
