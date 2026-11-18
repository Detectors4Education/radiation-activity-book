# =============================================================================
#  Activity 3.2 - Gamma-ray attenuation in lead and aluminium
#  Detector: Scintillation Counter unit
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Reads your counts for each absorber thickness from a CSV file.
#    2. Turns the counts into count RATES (counts per second) and subtracts
#       the background.
#    3. Fits the straight line  ln(R) = ln(R0) - mu * x  to the data.
#    4. Prints mu (the linear attenuation coefficient), mu/rho and the
#       half-value layer (HVL), each with its uncertainty.
#    5. Draws the graph and saves it next to this script.
#
#  HOW TO RUN IT
#    - In Thonny: open this file and press the green "Run" button.
#    - In a terminal, from this folder:
#          python gamma_attenuation.py               (example data)
#          python gamma_attenuation.py my_data.csv   (your own data)
#
#  YOUR DATA FILE (CSV = "comma-separated values", e.g. saved from a spreadsheet)
#    Columns:  material, thickness_mm, counts, time_s
#    Example lines:
#        background,0,1203,300
#        lead,2,10011,60
#    One row must have material = background.
#
#  PYTHON IDEAS YOU WILL MEET (see the chapter "Introduction to scientific
#  programming"): importing libraries, variables, dictionaries, reading a CSV
#  file with pandas, NumPy arrays, a "for" loop, a straight-line fit, f-strings
#  for printing, and Matplotlib graphs.
# =============================================================================

# --- Libraries ---------------------------------------------------------------
# A library is a ready-made toolbox. "import ... as ..." loads it and gives it
# a short nickname, so we can write np.sqrt(...) instead of numpy.sqrt(...).
import sys                        # lets us read the file name typed after the script name
from pathlib import Path          # handles folder and file names on any computer
import numpy as np                # fast maths on whole columns of numbers
import pandas as pd               # reads and handles tables (like a spreadsheet)
import matplotlib.pyplot as plt   # draws graphs

# =============================================================================
#  STEP 0 - Settings you may change
# =============================================================================
# HERE is the folder that contains this script. Building paths from it means the
# script finds its data even if you start it from another folder.
HERE = Path(__file__).parent

# If you typed a file name after the script name, use it; otherwise use the
# example data. sys.argv is the list of words typed on the command line:
# sys.argv[0] is the script itself, sys.argv[1] is the first extra word.
if len(sys.argv) > 1:
    DATA_FILE = sys.argv[1]
else:
    DATA_FILE = HERE / "attenuation.csv"

# A dictionary {key: value} stores values we can look up by name,
# e.g. DENSITY["lead"] gives 11.35.
DENSITY = {"lead": 11.35, "aluminium": 2.70}          # densities in g/cm^3
NIST_MU_RHO = {"lead": 0.111, "aluminium": 0.0748}    # reference mu/rho in cm^2/g at 662 keV (NIST XCOM)
COLOURS = {"lead": "#1B2A49", "aluminium": "#0E7C86"} # colours for the graph (hex codes)

# =============================================================================
#  STEP 1 - Read the data
# =============================================================================
# pd.read_csv reads the file into a table called a DataFrame (here named df).
# comment="#" tells pandas to ignore lines that start with #, which we use for notes.
df = pd.read_csv(DATA_FILE, comment="#")
# Always look at your data first! .head() shows the first 5 rows of the table.
print("First rows of the data table:")
print(df.head(), "\n")            # "\n" adds an empty line afterwards

# =============================================================================
#  STEP 2 - Background rate and its uncertainty
# =============================================================================
# df[df.material == "background"] keeps only the rows whose material is
# "background". .iloc[0] takes the first (and only) such row.
bg = df[df.material == "background"].iloc[0]

# Count rate = counts / counting time  (unit: counts per second, cps)
R_bg = bg.counts / bg.time_s
# Counting statistics (Poisson): the uncertainty of N counts is sqrt(N),
# so the uncertainty of the RATE is sqrt(N) / t.
dR_bg = np.sqrt(bg.counts) / bg.time_s

# An f-string (f"...") puts the values of variables inside {braces} into text.
# ":.3f" means "show 3 digits after the decimal point".
print(f"Background rate: {R_bg:.3f} +/- {dR_bg:.3f} cps\n")

# Prepare an empty figure (fig) with one set of axes (ax) to draw on later.
fig, ax = plt.subplots(figsize=(7, 4.5))

# =============================================================================
#  STEPS 3 to 6 are repeated for each material: a "for" loop
# =============================================================================
# The indented block below runs twice: first with material = "lead",
# then with material = "aluminium".
for material in ["lead", "aluminium"]:

    # Keep only the rows for this material.
    d = df[df.material == material]
    if d.empty:                   # no rows for this material? skip to the next one
        continue

    # .to_numpy() turns a table column into a NumPy array, so that we can do
    # maths on all the numbers at once (one line works on every row).
    x = d.thickness_mm.to_numpy() / 10.0          # thickness in cm (mm / 10)
    counts = d.counts.to_numpy()
    t = d.time_s.to_numpy()
    R = counts / t                                # gross count rate (cps)
    dR = np.sqrt(counts) / t                      # its uncertainty (cps)

    # ---- STEP 3 - Net rate = gross rate minus background ---------------------
    R_net = R - R_bg
    # Independent uncertainties add "in quadrature": sqrt(a^2 + b^2).
    # In Python, ** means "to the power of", so dR**2 is dR squared.
    dR_net = np.sqrt(dR**2 + dR_bg**2)

    # ---- STEP 4 - Take the natural logarithm ----------------------------------
    # ln(R) = ln(R0) - mu*x is a straight line: y = a + b*x with b = -mu.
    y = np.log(R_net)             # np.log is the NATURAL log (ln)
    dy = dR_net / R_net           # uncertainty of ln(R) is sigma(R) / R

    # ---- STEP 5 - Weighted straight-line fit  y = a + b*x ----------------------
    # np.polyfit(x, y, 1) fits a polynomial of degree 1 (a straight line).
    #   w = 1/dy        gives more weight to the more precise points
    #   cov="unscaled"  also returns the covariance matrix, from which we get the
    #                   uncertainties of the fitted values (based on OUR error bars)
    # It returns the coefficients highest power first: [b, a].
    coefficients, cov = np.polyfit(x, y, 1, w=1 / dy, cov="unscaled")
    b = coefficients[0]           # gradient (slope)
    a = coefficients[1]           # intercept
    db = np.sqrt(cov[0, 0])       # uncertainty of the gradient

    mu = -b                       # the gradient is -mu
    dmu = db
    hvl = np.log(2) / mu          # half-value layer: HVL = ln2 / mu
    dhvl = np.log(2) / mu**2 * dmu    # its uncertainty (error propagation)
    mu_rho = mu / DENSITY[material]   # mass attenuation coefficient mu/rho
    dmu_rho = dmu / DENSITY[material]

    # Goodness of fit: chi-squared compares the points with the line, in units
    # of their error bars. chi^2 / ndf (degrees of freedom) should be close to 1.
    y_line = a + b * x
    chi2 = np.sum(((y - y_line) / dy) ** 2)
    ndf = len(x) - 2              # number of points minus 2 fitted values (a and b)

    print(f"=== {material.upper()} ===")
    print(f"  mu      = {mu:.3f} +/- {dmu:.3f} cm^-1")
    print(f"  mu/rho  = {mu_rho:.4f} +/- {dmu_rho:.4f} cm^2/g "
          f"(NIST narrow-beam value {NIST_MU_RHO[material]} cm^2/g)")
    print(f"  HVL     = {hvl:.3f} +/- {dhvl:.3f} cm")
    print(f"  chi^2/ndf = {chi2:.1f}/{ndf} = {chi2/ndf:.2f}\n")

    # ---- STEP 6 - Plot the data points and the fitted line --------------------
    colour = COLOURS[material]
    # errorbar draws points with error bars; fmt="o" means round markers.
    ax.errorbar(x, R_net, yerr=dR_net, fmt="o", ms=5, capsize=3, color=colour,
                label=f"{material}: data")
    # 100 evenly spaced x values from 0 to the largest thickness, for a smooth line
    xx = np.linspace(0, x.max(), 100)
    ax.plot(xx, np.exp(a + b * xx), "-", color=colour, lw=1.5,
            label=f"{material}: fit, $\\mu$ = {mu:.3f} cm$^{{-1}}$")

# =============================================================================
#  STEP 7 - Finish and save the graph (outside the loop: done once)
# =============================================================================
ax.set_yscale("log")              # a log axis turns the exponential into a straight line
ax.set_xlabel("Absorber thickness x (cm)")
ax.set_ylabel("Net count rate R (cps)")
ax.set_title("3.2  Attenuation of 662 keV gamma rays")
ax.grid(True, which="both", alpha=0.3)
ax.legend(frameon=False)
fig.tight_layout()                # tidy the spacing
fig.savefig(HERE / "attenuation.png", dpi=200)
print("Graph saved to attenuation.png (next to this script)")
