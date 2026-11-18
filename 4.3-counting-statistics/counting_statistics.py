# =============================================================================
#  Activity 4.3 - The statistics of counting: Poisson and Gaussian
#  Detector: Geiger-Mueller Counter unit (GC 4 EDU) (USB data readout)
# =============================================================================
#  WHAT THIS SCRIPT DOES (for each data file)
#    1. Reads a long list of repeated counts, each taken over the same time.
#    2. Calculates the mean, variance and standard deviation.
#       For random (Poisson) counting, the variance should equal the mean.
#    3. Draws a histogram and compares it with the Poisson and Gaussian
#       predictions that have the SAME mean.
#    4. Carries out a chi-squared test: do the data really follow Poisson?
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python counting_statistics.py [file1.csv file2.csv ...]
#
#  YOUR DATA FILE
#    Columns:  interval, counts      (one row per counting interval)
#
#  PYTHON IDEAS YOU WILL MEET: lists of files, a "for" loop with zip(),
#  array methods (.mean(), .var()), counting with a comparison, a simple
#  loop that builds lists, and the statistics module of SciPy.
# =============================================================================

import sys
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy import stats           # probability distributions and statistical tests

HERE = Path(__file__).parent

# FILES is a LIST: several items inside square brackets, separated by commas.
# sys.argv[1:] is the list of file names you typed (it may be empty).
if len(sys.argv) > 1:
    FILES = sys.argv[1:]
else:
    FILES = [HERE / "background_10s.csv",
             HERE / "source_1s.csv"]

# One graph panel per file, side by side.
fig, axes = plt.subplots(1, len(FILES), figsize=(5.2 * len(FILES), 4))
axes = np.atleast_1d(axes)        # makes sure "axes" is a list even for one file

# zip() walks through two lists together: the first panel with the first file,
# the second panel with the second file, and so on.
for ax, f in zip(axes, FILES):

    # Read the "counts" column and turn it into a NumPy array called n.
    n = pd.read_csv(f, comment="#")["counts"].to_numpy()
    N = len(n)                    # len() = how many numbers are in the array

    # ---- STEP 1 - Descriptive statistics -------------------------------------
    mean = n.mean()               # the average number of counts per interval
    var = n.var(ddof=1)           # sample variance (ddof=1: divide by N-1, not N)
    sd = np.sqrt(var)             # standard deviation = square root of the variance
    print(f"=== {Path(f).name} ===")
    print(f"  number of intervals N = {N}")
    print(f"  mean  = {mean:.2f} +/- {sd/np.sqrt(N):.2f} counts per interval")
    print(f"  variance = {var:.2f}   ->  variance/mean = {var/mean:.2f} "
          f"(Poisson predicts 1.00)")
    print(f"  standard deviation = {sd:.2f};  sqrt(mean) = {np.sqrt(mean):.2f}")

    # ---- STEP 2 - Histogram: how often did each count value occur? -----------
    # np.arange(a, b) makes the whole numbers a, a+1, ..., b-1.
    k = np.arange(n.min(), n.max() + 1)      # every count value between min and max
    observed = []                            # start with an empty list
    for value in k:
        # (n == value) is True where the count equals "value"; .sum() counts the Trues.
        observed.append((n == value).sum())  # .append adds an item to the end of a list
    observed = np.array(observed)            # list -> array, so we can do maths on it

    # ---- STEP 3 - Poisson prediction with the same mean -----------------------
    # stats.poisson.pmf(k, mean) is the probability of exactly k counts.
    # Multiplying by N turns probabilities into the expected NUMBER of intervals.
    poisson = N * stats.poisson.pmf(k, mean)

    # ---- STEP 4 - Chi-squared test against Poisson -----------------------------
    # The test is only reliable if every bin expects at least 5 entries, so we
    # merge neighbouring bins until each one reaches 5.
    bins_obs = []                 # merged observed numbers
    bins_exp = []                 # merged expected numbers
    o_acc = 0                     # running totals ("accumulators")
    e_acc = 0
    for o, e in zip(observed, poisson):
        o_acc = o_acc + o
        e_acc = e_acc + e
        if e_acc >= 5:            # this merged bin is big enough: store it, start again
            bins_obs.append(o_acc)
            bins_exp.append(e_acc)
            o_acc = 0
            e_acc = 0
    if e_acc > 0:                 # anything left over goes into the last bin
        bins_obs[-1] = bins_obs[-1] + o_acc      # [-1] means "the last item"
        bins_exp[-1] = bins_exp[-1] + e_acc
    bins_obs = np.array(bins_obs)
    bins_exp = np.array(bins_exp)
    bins_exp = bins_exp * bins_obs.sum() / bins_exp.sum()   # make the totals equal

    chi2 = np.sum((bins_obs - bins_exp) ** 2 / bins_exp)
    dof = len(bins_obs) - 2       # degrees of freedom: bins - 1 (total) - 1 (mean)
    p = stats.chi2.sf(chi2, dof)  # p-value: chance of a chi^2 this big if Poisson is right
    print(f"  chi^2 = {chi2:.1f} for {dof} degrees of freedom, p-value = {p:.2f}")
    if p > 0.05:
        print("  -> consistent with Poisson (p > 0.05)\n")
    else:
        print("  -> NOT consistent with Poisson at the 5 % level\n")

    # ---- STEP 5 - Plot ----------------------------------------------------------
    ax.bar(k, observed, width=0.85, color="#C9D6EA", edgecolor="#3D5A98", label="measured")
    ax.plot(k, poisson, "o-", color="#D1495B", ms=4, lw=1.2, label="Poisson")
    # The Gaussian is a smooth curve, so we use 300 closely spaced x values.
    kk = np.linspace(k.min(), k.max(), 300)
    gauss = N * stats.norm.pdf(kk, mean, np.sqrt(mean))   # same mean, width sqrt(mean)
    ax.plot(kk, gauss, "--", color="#1B2A49", lw=1.2, label="Gaussian")
    ax.set_title(f"{Path(f).stem}\nmean = {mean:.1f}, var/mean = {var/mean:.2f}", fontsize=10)
    ax.set_xlabel("Counts in one interval")
    ax.set_ylabel("Number of intervals")
    ax.legend(frameon=False, fontsize=8)
    ax.grid(alpha=0.25)

fig.suptitle("4.3  Counting statistics", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "statistics.png", dpi=200)
print("Graph saved to statistics.png (next to this script)")
