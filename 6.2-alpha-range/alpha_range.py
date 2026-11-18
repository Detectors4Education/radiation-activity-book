# =============================================================================
#  Activity 6.2 - The range of alpha particles in air
#  Equipment: Universal Radiometer + Scintillation Probe (ZnS(Ag) + PMT),
#             Am-241 source, distance stand
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Converts counts into net count rates.
#    2. Corrects for GEOMETRY: the further away the probe, the smaller the
#       fraction of directions (solid angle) it covers, even without any air.
#    3. Fits the corrected curve with a smooth step (the "erfc" function).
#       The 50 % point of the step is the MEAN RANGE; its width is the STRAGGLING.
#    4. Converts the range to standard air (15 C, 101.325 kPa) and estimates the
#       alpha energy with Geiger's rule  R = 0.318 E^(3/2).
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python alpha_range.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  source, distance_cm, counts, time_s   (one row: source = background)
#
#  >>> Change T_LAB and P_LAB to the temperature and pressure of YOUR laboratory.
#
#  PYTHON IDEAS YOU WILL MEET: a special function from SciPy (erfc), fitting
#  with curve_fit, starting guesses worked out from the data, and np.maximum.
# =============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit
from scipy.special import erfc            # the "complementary error function", a smooth step

HERE = Path(__file__).parent
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = HERE / "alpha_range.csv"

# ---- Settings ------------------------------------------------------------------
PROBE_RADIUS = 2.3        # cm: radius of the sensitive ZnS(Ag) area (46 mm photocathode)
T_LAB = 22.0              # temperature in YOUR laboratory (degrees C)   <-- change!
P_LAB = 101.3             # air pressure in YOUR laboratory (kPa)        <-- change!

# =============================================================================
#  STEP 1 - Net count rates
# =============================================================================
df = pd.read_csv(DATA_FILE, comment="#")
bg = df[df.source == "background"].iloc[0]
R_b = bg.counts / bg.time_s
d = df[df.source != "background"]
x = d.distance_cm.to_numpy(float)                       # distances (cm)
net = (d.counts / d.time_s).to_numpy() - R_b            # net rates
dnet = (np.sqrt(d.counts) / d.time_s).to_numpy()        # their uncertainties

# =============================================================================
#  STEP 2 - Geometry correction
# =============================================================================
# Fraction of all directions covered by a disc of radius r at distance x:
#     omega = 0.5 * (1 - x / sqrt(x^2 + r^2))
omega = 0.5 * (1 - x / np.sqrt(x**2 + PROBE_RADIUS**2))
y = net / omega               # rate per unit solid angle: removes the geometry effect
dy = dnet / omega

# =============================================================================
#  STEP 3 - Fit a smooth step:  y = A/2 * erfc((x - Rm) / (sqrt(2)*s))
# =============================================================================
def step(x, A, Rm, s):
    """A = height of the step, Rm = mean range (50 % point), s = straggling width."""
    return 0.5 * A * erfc((x - Rm) / (np.sqrt(2) * s))

# Starting guesses: the height is the largest y; the 50 % point is the x where
# y is closest to half the maximum; the width is about 0.2 cm.
A_guess = y.max()
Rm_guess = x[np.argmin(abs(y - y.max() / 2))]
s_guess = 0.2
# np.maximum(dy, 1e-3) replaces any tiny error bar by 0.001, so no point gets
# an impossibly large weight in the fit.
p, cov = curve_fit(step, x, y, p0=[A_guess, Rm_guess, s_guess],
                   sigma=np.maximum(dy, 1e-3), absolute_sigma=True)
A = p[0]
Rm = p[1]
s = p[2]
errors = np.sqrt(np.diag(cov))
dRm = errors[1]
ds = errors[2]
print(f"Mean range in lab air  R_m   = {Rm:.3f} +/- {dRm:.3f} cm")
print(f"Straggling width       sigma = {abs(s):.3f} +/- {ds:.3f} cm")
print(f"Extrapolated range     R_e   = R_m + sqrt(pi/2)*sigma = {Rm + np.sqrt(np.pi/2)*abs(s):.2f} cm")

# =============================================================================
#  STEP 4 - Convert to standard air and estimate the energy
# =============================================================================
# The range is inversely proportional to the density of the air, and the
# density is proportional to p/T (ideal gas; T in kelvin = deg C + 273.15).
R_std = Rm * (P_LAB / 101.325) * (288.15 / (T_LAB + 273.15))
E = (R_std / 0.318) ** (2 / 3)            # Geiger's rule, rearranged for E
print(f"Range in standard air (15 C, 101.325 kPa) = {R_std:.2f} cm")
print(f"Alpha energy from Geiger's rule           = {E:.2f} MeV")
print("Reference: Am-241 emits 5.486 MeV alphas (range ~4.1 cm in standard air)")
print(f"-> energy apparently lost before leaving the source ~ {5.486 - E:.1f} MeV")

# =============================================================================
#  STEP 5 - Graphs
# =============================================================================
fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 4))

# Left: the measured net rate
a1.errorbar(x, net, yerr=dnet, fmt="o", color="#7B4FA0", capsize=2)
a1.set_yscale("log")
a1.set_title("Measured net rate", fontsize=10)
a1.set_xlabel("Source-probe distance (cm)")
a1.set_ylabel("Net rate (cps)")

# Right: the geometry-corrected rate with the fitted step
xx = np.linspace(x.min(), x.max(), 300)
a2.errorbar(x, y, yerr=dy, fmt="o", color="#7B4FA0", capsize=2, label="geometry-corrected")
a2.plot(xx, step(xx, *p), color="#1B2A49", lw=1.5, label="erfc fit")
a2.axvline(Rm, color="#D1495B", ls=":", lw=2, label=f"mean range {Rm:.2f} cm")
a2.set_title("Rate per unit solid angle", fontsize=10)
a2.set_xlabel("Source-probe distance (cm)")
a2.set_ylabel("Net rate / (Ω/4π)  (cps)")
a2.legend(frameon=False, fontsize=8)

for a in (a1, a2):
    a.grid(alpha=0.3, which="both")
fig.suptitle("6.2  Range of Am-241 alpha particles in air", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "alpha_range.png", dpi=200)
print("\nGraph saved to alpha_range.png (next to this script)")
