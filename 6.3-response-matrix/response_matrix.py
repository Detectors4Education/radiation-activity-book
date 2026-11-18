# =============================================================================
#  Activity 6.3 - Who sees what?  Identifying radiation with two detectors
#  Equipment: Universal Radiometer + Scintillation Probe (ZnS(Ag)) and
#             GM Tube Probe; paper and 3 mm aluminium absorbers
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Calculates the net count rate for every detector / source / absorber.
#    2. Builds a "response matrix": the fraction transmitted through paper and
#       through aluminium (compared with no absorber), for each detector.
#    3. Applies simple decision rules to say which radiation each source emits.
#    4. Draws a grouped bar chart on a log scale.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python response_matrix.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  detector, source, absorber, counts, time_s
#    detector is ZnS or GM; absorber is one of: none, paper, Al_3mm.
#    Background rows have source = background and absorber = none.
#
#  PYTHON IDEAS YOU WILL MEET: grouping by two columns, looking values up with
#  .map(), a function that returns True/False, nested "if" decisions, and
#  joining words into a sentence with ", ".join(...).
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
    DATA_FILE = HERE / "response_matrix.csv"

df = pd.read_csv(DATA_FILE, comment="#")
df["rate"] = df.counts / df.time_s                  # count rate of every row
df["drate"] = np.sqrt(df.counts) / df.time_s        # its uncertainty

# =============================================================================
#  STEP 1 - Subtract the background of the right detector
# =============================================================================
# Table of the two background rows, labelled by detector ("ZnS" and "GM").
bg = df[df.source == "background"].set_index("detector")
df = df[df.source != "background"].copy()           # the rest; .copy() makes a separate table
# .map(bg.rate) looks up, for every row, the background rate of THAT row's detector.
df["net"] = df.rate - df.detector.map(bg.rate)
df["dnet"] = np.sqrt(df.drate**2 + df.detector.map(bg.drate) ** 2)


def significant(row):
    """Returns True if the net rate is more than 3 standard deviations above zero."""
    return row.net > 3 * row.dnet


# =============================================================================
#  STEP 2 - Response matrix
# =============================================================================
print(f"{'source':<11}{'det.':<5}{'none (cps)':>14}{'paper/none':>12}{'Al/none':>10}")
results = {}            # we store the results here, keyed by (source, detector)

# groupby with TWO columns: each group is one source seen by one detector.
for (src, det), g in df.groupby(["source", "detector"]):
    g = g.set_index("absorber")                     # rows labelled none / paper / Al_3mm
    r0 = g.loc["none"]                              # the row without absorber
    if significant(r0):
        # transmission = rate with absorber / rate without absorber
        t_paper = g.loc["paper"].net / r0.net
        t_al = g.loc["Al_3mm"].net / r0.net
    else:
        # nothing was seen, so a transmission makes no sense: use "not a number"
        t_paper = np.nan
        t_al = np.nan
    results[(src, det)] = {"seen": significant(r0), "paper": t_paper, "al": t_al, "rate": r0.net}

    # Print "-" instead of a number when nothing was detected.
    if np.isfinite(t_paper):
        tp = f"{t_paper:.2f}"
    else:
        tp = "-"
    if np.isfinite(t_al):
        ta = f"{t_al:.2f}"
    else:
        ta = "-"
    print(f"{src:<11}{det:<5}{r0.net:>8.2f}+/-{r0.dnet:<5.2f}{tp:>10}{ta:>10}")

# =============================================================================
#  STEP 3 - Decision rules
# =============================================================================
#  alpha        : seen by ZnS(Ag), stopped by paper
#  beta         : seen by GM, passes paper, almost all stopped by 3 mm Al (Al/none < 0.1)
#  beta + gamma : part (10-60 %) of the GM rate passes 3 mm Al
#  gamma        : seen by GM, and most of the rate passes 3 mm Al        (Al/none > 0.6)
print("\nIdentification:")
for src in df.source.unique():                      # each source name once
    zns = results[(src, "ZnS")]
    gm = results[(src, "GM")]
    found = []                                      # list of radiation types found
    if zns["seen"] and zns["paper"] < 0.1:
        found.append("alpha")
    if gm["seen"] and gm["paper"] > 0.5:
        if gm["al"] < 0.1:
            found.append("beta")
        elif gm["al"] < 0.6:                        # elif = "else, if ..."
            found = found + ["beta", "gamma"]
        else:
            found.append("gamma")
    if found:                                       # a non-empty list counts as True
        answer = ", ".join(found)                   # e.g. ["beta", "gamma"] -> "beta, gamma"
    else:
        answer = "nothing significant"
    print(f"  {src:<11} -> {answer}")

# =============================================================================
#  STEP 4 - Grouped bar chart
# =============================================================================
sources = list(df.source.unique())
absorbers = ["none", "paper", "Al_3mm"]
colours = {"none": "#7B4FA0", "paper": "#E07A1F", "Al_3mm": "#0E7C86"}
fig, axes = plt.subplots(1, 2, figsize=(11, 4), sharey=True)

for ax, det in zip(axes, ["ZnS", "GM"]):
    # enumerate gives a counter i (0, 1, 2) together with each absorber name
    for i, ab in enumerate(absorbers):
        vals = []
        for s in sources:
            row = df[(df.source == s) & (df.detector == det) & (df.absorber == ab)]
            # a log axis cannot show zero or negative values, so use at least 0.01
            vals.append(max(row.net.iloc[0], 0.01))
        positions = np.arange(len(sources)) + (i - 1) * 0.27    # shift each absorber's bars sideways
        ax.bar(positions, vals, 0.27, color=colours[ab], label=ab)
    ax.set_xticks(range(len(sources)))
    ax.set_xticklabels(sources, rotation=20)
    ax.set_yscale("log")
    ax.set_title(f"{det} probe", fontsize=10)
    ax.grid(alpha=0.3, axis="y")

axes[0].set_ylabel("Net count rate (cps)")
axes[1].legend(title="absorber", frameon=False)
fig.suptitle("6.3  Detector response matrix", fontsize=11)
fig.tight_layout()
fig.savefig(HERE / "response.png", dpi=200)
print("\nGraph saved to response.png (next to this script)")
