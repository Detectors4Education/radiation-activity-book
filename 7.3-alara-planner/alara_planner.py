# =============================================================================
#  Activity 7.3 - Time, distance, shielding: planning a task with ALARA
#  Equipment: Personal Dosimeter, gamma check source, lead sheets
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Fits the dose rates measured at different DISTANCES with
#              D_dot(d) = k / d^2 + background
#    2. Fits the dose rates behind different LEAD thicknesses with
#              D_dot(x) = D_dot(0) * exp(-mu x) + background
#    3. Uses both models to predict the dose for different ways of doing the
#       same job (the "scenarios", which you design yourself below).
#    4. Compares each dose with the annual dose limit for the public (1 mSv).
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python alara_planner.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  series, distance_cm, lead_mm, dose_rate_uSvh
#    series is "distance" or "shield_lead".
#
#  >>> Write your own plans in the list "scenarios" in STEP 3.
#
#  PYTHON IDEAS YOU WILL MEET: curve_fit with one-line (lambda) models, a
#  function with a default value, a list of tuples, and reversing a list.
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
    DATA_FILE = HERE / "dose_rates.csv"

BG = 0.12                  # background dose rate (uSv/h), measured far from the source

df = pd.read_csv(DATA_FILE, comment="#")

# =============================================================================
#  STEP 1 - Distance model:  D_dot = k / d^2 + BG
# =============================================================================
dist = df[df.series == "distance"]
# "lambda d, k: k / d**2 + BG" is a short function with inputs d and k.
# curve_fit finds the k that makes it match the measured dose rates.
best, best_cov = curve_fit(lambda d, k: k / d**2 + BG,
                           dist.distance_cm, dist.dose_rate_uSvh, p0=[500])
k = best[0]                # curve_fit returns an array of parameters; we take the only one
print(f"Distance model:  D_dot = {k:.0f}/d^2 + {BG} uSv/h   (d in cm)")

# =============================================================================
#  STEP 2 - Shielding model (all measured at the same distance)
# =============================================================================
sh = df[df.series == "shield_lead"]
d_sh = sh.distance_cm.iloc[0]          # that fixed distance
best, best_cov = curve_fit(lambda x, D0, mu: D0 * np.exp(-mu * x) + BG,
                           sh.lead_mm, sh.dose_rate_uSvh, p0=[1.0, 0.1])
D0 = best[0]               # dose rate without lead (minus background)
mu = best[1]               # attenuation coefficient of lead (per mm)
print(f"Shield model at {d_sh} cm: D_dot = {D0:.2f} exp(-{mu:.3f} x) + {BG}  (x in mm)")
print(f"  -> half-value layer of lead = {np.log(2)/mu:.1f} mm\n")


def dose_rate(d_cm, lead_mm=0.0):
    """Predicted dose rate (uSv/h) at a distance d_cm behind lead_mm of lead.
    lead_mm=0.0 is a DEFAULT value: if you leave it out, no lead is assumed."""
    return (k / d_cm**2) * np.exp(-mu * lead_mm) + BG


# =============================================================================
#  STEP 3 - Scenarios: (description, distance in cm, lead in mm, time in minutes)
# =============================================================================
# The job: read a scale next to the source. Each line is one TUPLE; together they
# form a LIST. Change these, or add lines, to test your own plans!
scenarios = [
    ("A  quick, but close (10 cm)",          10,  0, 10),
    ("B  slow and close",                    10,  0, 30),
    ("C  use tongs: 30 cm",                  30,  0, 12),
    ("D  tongs + 10 mm lead",                30, 10, 15),
    ("E  remote camera: 100 cm",            100,  0, 20),
]
print(f"{'scenario':<34}{'rate (uSv/h)':>13}{'dose (uSv)':>12}{'% of 1 mSv':>12}")
names = []
doses = []
# Each tuple is unpacked into four variables at the start of the loop.
for name, d_cm, x_mm, minutes in scenarios:
    r = dose_rate(d_cm, x_mm)              # dose rate for this plan
    D = r * minutes / 60                   # dose = rate x time (time in hours)
    names.append(name)
    doses.append(D)
    # 1 mSv = 1000 uSv, so the percentage of the limit is D / 1000 * 100
    print(f"{name:<34}{r:>13.2f}{D:>12.3f}{D/1000*100:>11.4f} %")

best_plan = names[int(np.argmin(doses))]   # argmin = position of the smallest dose
print(f"\nLowest-dose plan: {best_plan}")
print("Remember: background alone gives about the same dose rate everywhere -")
print("compare each plan with doing nothing for the same time!")

# =============================================================================
#  STEP 4 - Graphs
# =============================================================================
fig, (a1, a2) = plt.subplots(1, 2, figsize=(11, 4))

# Left: the distance measurements and the model, on log-log axes
dd = np.linspace(8, 110, 200)
a1.plot(dist.distance_cm, dist.dose_rate_uSvh, "o", color="#2E8B57", label="measured")
a1.plot(dd, dose_rate(dd), color="#1B2A49", label="$k/d^2$ + background")
a1.set_xscale("log")
a1.set_yscale("log")
a1.set_xlabel("Distance (cm)")
a1.set_ylabel("Dose rate (µSv/h)")
a1.legend(frameon=False)
a1.set_title("Distance", fontsize=10)
a1.grid(alpha=0.3, which="both")

# Right: one bar per scenario. [::-1] reverses a list, so scenario A ends up at the top.
a2.barh(names[::-1], doses[::-1], color="#2E8B57")
a2.set_xlabel("Dose for the task (µSv)")
a2.set_title("Scenario comparison", fontsize=10)
a2.grid(alpha=0.3, axis="x")

fig.suptitle("7.3  ALARA planning: time, distance, shielding", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "alara.png", dpi=200)
print("\nGraph saved to alara.png (next to this script)")
