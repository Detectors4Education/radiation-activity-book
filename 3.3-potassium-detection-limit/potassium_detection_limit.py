# =============================================================================
#  Activity 3.3 - Natural radioactivity: potassium-40 and detection limits
#  Detector: Scintillation Counter unit
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Calculates from theory how many K-40 atoms decay each second in one
#       gram of potassium chloride (KCl).
#    2. Reads your counts for an empty container, for several masses of KCl and
#       for "unknown" samples, all counted in the SAME container and position.
#    3. Works out the Currie decision threshold L_C and detection limit L_D.
#    4. Fits a CALIBRATION line: net count rate against mass of KCl.
#    5. Uses the calibration to estimate how much KCl the unknowns contain.
#    6. Draws the calibration graph.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python potassium_detection_limit.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  sample, mass_g, counts, time_s
#    Rows:     one row with sample = empty_container (the background),
#              several rows with sample = KCl (different masses),
#              any other name is treated as an unknown sample.
#
#  PYTHON IDEAS YOU WILL MEET: constants and scientific notation (6.022e23),
#  new table columns, filtering rows, a weighted straight-line fit, a "for"
#  loop over table rows, "if ... else", and formatted printing.
# =============================================================================

import sys                        # reads the optional file name you type
from pathlib import Path          # builds file paths that work on any computer
import numpy as np                # maths on arrays of numbers
import pandas as pd               # tables (DataFrames)
import matplotlib.pyplot as plt   # graphs

HERE = Path(__file__).parent      # the folder that contains this script
if len(sys.argv) > 1:             # a file name was typed after the script name
    DATA_FILE = sys.argv[1]
else:                             # otherwise use the example data
    DATA_FILE = HERE / "potassium.csv"

# =============================================================================
#  STEP 1 - Theory: how active is one gram of KCl?
# =============================================================================
# Numbers like 6.022e23 are written in scientific notation: 6.022 x 10^23.
N_A = 6.022e23                    # Avogadro constant (atoms per mole)
M_K = 39.098                      # molar mass of potassium (g/mol)
M_KCl = 74.551                    # molar mass of KCl (g/mol)
ABUND_K40 = 1.17e-4               # fraction of natural potassium atoms that are K-40
T_HALF_S = 1.248e9 * 3.156e7      # half-life of K-40: 1.248e9 years x seconds per year

lam = np.log(2) / T_HALF_S        # decay constant lambda = ln2 / T_half (per second)

# One gram of KCl contains (1 / M_KCl) moles, i.e. (1 / M_KCl) * N_A potassium
# atoms (one K atom per KCl unit). A fraction ABUND_K40 of these is K-40.
atoms_K40_per_g_KCl = (1 / M_KCl) * N_A * ABUND_K40
# Activity A = lambda * N (decays per second, unit becquerel Bq)
A_spec = lam * atoms_K40_per_g_KCl
print(f"Theory: specific activity of KCl = {A_spec:.1f} Bq/g\n")

# =============================================================================
#  STEP 2 - Read the data and convert counts to rates
# =============================================================================
df = pd.read_csv(DATA_FILE, comment="#")   # lines starting with # are notes

# You can add a new column to the table by giving it a name. The calculation
# is done for every row at once.
df["rate"] = df.counts / df.time_s                  # count rate (cps)
df["d_rate"] = np.sqrt(df.counts) / df.time_s       # Poisson uncertainty of the rate

# The background is the row whose sample is "empty_container".
bg = df[df["sample"] == "empty_container"].iloc[0]
R_b = bg.rate                     # background rate
dR_b = bg.d_rate                  # its uncertainty
t_b = bg.time_s                   # background counting time

# Net rate = rate - background, for every row. Uncertainties add in quadrature.
df["net"] = df.rate - R_b
df["d_net"] = np.sqrt(df.d_rate**2 + dR_b**2)

# =============================================================================
#  STEP 3 - Currie limits: when can we say "something is there"?
# =============================================================================
# B = background counts (counted for the same time as the samples).
B = bg.counts
L_C = 2.33 * np.sqrt(B)           # decision threshold: above this, we say "detected"
L_D = 2.71 + 4.65 * np.sqrt(B)    # detection limit: the smallest signal we reliably detect
print(f"Background: {R_b:.3f} +/- {dR_b:.3f} cps  ({B} counts in {t_b:.0f} s)")
print(f"Currie decision threshold L_C = {L_C:.0f} counts = {L_C/t_b:.3f} cps net")
print(f"Currie detection limit    L_D = {L_D:.0f} counts = {L_D/t_b:.3f} cps net\n")

# =============================================================================
#  STEP 4 - Calibration line: net rate = k * mass + c
# =============================================================================
cal = df[df["sample"] == "KCl"]   # only the KCl rows
m = cal.mass_g.to_numpy()         # masses (x values)
y = cal.net.to_numpy()            # net rates (y values)
dy = cal.d_net.to_numpy()         # their uncertainties

# Weighted straight-line fit (see Activity 3.2 for details).
coefficients, cov = np.polyfit(m, y, 1, w=1 / dy, cov="unscaled")
k = coefficients[0]               # gradient: extra cps per gram of KCl
c = coefficients[1]               # intercept: should be close to zero
dk = np.sqrt(cov[0, 0])           # uncertainty of k
dc = np.sqrt(cov[1, 1])           # uncertainty of c
print(f"Calibration: net rate = ({k*1000:.2f} +/- {dk*1000:.2f}) x 10^-3 cps/g * m "
      f"+ ({c:.3f} +/- {dc:.3f}) cps")

# Counts per decay = detection efficiency (as a fraction; x 100 for per cent)
eff = k / A_spec
print(f"Overall detection efficiency = {eff*100:.3f} % of K-40 decays\n")
# The mass that would give a net rate equal to the detection limit:
m_min = (L_D / t_b - c) / k
print(f"Smallest detectable mass of KCl (this geometry) ~ {m_min:.0f} g\n")

# =============================================================================
#  STEP 5 - The unknown samples
# =============================================================================
# ~ means "NOT". isin([...]) is True for rows whose sample is in the list, so
# this keeps every row that is neither the background nor a KCl calibration row.
unk = df[~df["sample"].isin(["empty_container", "KCl"])]

# Print a table header. "<20" means "left-aligned in 20 characters",
# ">18" means "right-aligned in 18 characters".
print(f"{'sample':<20}{'net rate (cps)':>18}{'detected?':>11}{'KCl-equiv. (g)':>18}{'KCl fraction':>14}")

# iterrows() gives us the table one row at a time. "_" is the row number,
# which we do not need; r is the row itself.
for _, r in unk.iterrows():
    net_counts = r.net * r.time_s             # net counts in this measurement
    detected = net_counts > L_C               # True or False
    m_eq = (r.net - c) / k                    # mass of KCl that gives the same rate
    dm = np.sqrt((r.d_net / k) ** 2 + (m_eq * dk / k) ** 2)   # its uncertainty
    frac = m_eq / r.mass_g                    # fraction of the sample that "is" KCl
    if detected:
        print(f"{r['sample']:<20}{r.net:>9.3f} +/- {r.d_net:.3f}{'yes':>9}"
              f"{m_eq:>11.0f} +/- {dm:<4.0f}{frac*100:>11.0f} %")
    else:
        # Below the decision threshold we cannot quote a value, only an upper limit.
        m_lim = (L_D / r.time_s - c) / k
        print(f"{r['sample']:<20}{r.net:>9.3f} +/- {r.d_net:.3f}{'no':>9}"
              f"{'< ' + format(m_lim, '.0f'):>11}{'':7}{'< ' + format(m_lim/r.mass_g*100, '.0f'):>11} %")

# =============================================================================
#  STEP 6 - Graph
# =============================================================================
fig, ax = plt.subplots(figsize=(7, 4.5))
ax.errorbar(m, y, yerr=dy, fmt="o", color="#0E7C86", capsize=3, label="KCl calibration")
mm = np.linspace(0, m.max() * 1.05, 50)       # x values for the fitted line
ax.plot(mm, k * mm + c, color="#0E7C86", lw=1.5, label="weighted linear fit")
# A horizontal dashed line at the detection limit (converted to a rate)
ax.axhline(L_D / t_b, color="#D1495B", ls="--", lw=1.2, label="Currie detection limit $L_D$")
for _, r in unk.iterrows():                   # one square marker per unknown sample
    ax.errorbar(r.mass_g, r.net, yerr=r.d_net, fmt="s", ms=6, capsize=3,
                label=f"unknown: {r['sample']}")
ax.set_xlabel("Mass of sample in container (g)")
ax.set_ylabel("Net count rate (cps)")
ax.set_title("3.3  K-40 calibration and detection limit")
ax.grid(alpha=0.3)
ax.legend(frameon=False, fontsize=8)
fig.tight_layout()
fig.savefig(HERE / "potassium.png", dpi=200)
print("\nGraph saved to potassium.png (next to this script)")
