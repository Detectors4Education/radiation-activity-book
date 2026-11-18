# =============================================================================
#  Activity 9.2 - Building the measurement chain with the GM Puzzle Set
#  Equipment: Geiger-Mueller Counter Puzzle Piece Set (Power Supply, High
#             Voltage Generator, Geiger-Mueller Tube, Signal Discriminator,
#             Buzzer, Digital Display, Analogue Display), weak samples
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Turns the counts from the DIGITAL DISPLAY into count rates (cps).
#    2. Subtracts the background and works out the uncertainty.
#    3. Decides for every sample whether radiation was really DETECTED:
#       the net rate must be more than 3 standard uncertainties above zero.
#    4. Estimates how long you would have to count to detect each sample.
#    5. Draws a bar chart of the net rates with error bars.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python puzzle_detection.py [my_data.csv]
#
#  YOUR DATA FILE
#    Columns:  sample, counts, time_s
#    Example lines:
#        background,252,600
#        KCl_salt_substitute_500g,224,300
#    One row must be called "background".
#
#  PYTHON IDEAS YOU WILL MEET: a function with a default value, "if" inside a
#  loop, infinity (np.inf), choosing colours with a condition, and a
#  horizontal bar chart.
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
    DATA_FILE = HERE / "puzzle_samples.csv"

K = 3.0          # "detected" means: net rate > K x its uncertainty (the 3-sigma rule)

df = pd.read_csv(DATA_FILE, comment="#")

# =============================================================================
#  STEP 1 - Background
# =============================================================================
bg = df[df["sample"] == "background"].iloc[0]
Rb = bg.counts / bg.time_s                    # background rate (cps)
dRb = np.sqrt(bg.counts) / bg.time_s          # Poisson: the uncertainty of N counts is sqrt(N)
print(f"Background: {Rb:.3f} +/- {dRb:.3f} cps  ({Rb*60:.1f} cpm)\n")

# =============================================================================
#  STEP 2 - Every sample: gross rate, net rate and significance
# =============================================================================
samples = df[df["sample"] != "background"].copy()
samples["R"] = samples.counts / samples.time_s                  # gross rate
samples["dR"] = np.sqrt(samples.counts) / samples.time_s
samples["net"] = samples.R - Rb                                 # net rate
samples["dnet"] = np.sqrt(samples.dR**2 + dRb**2)               # uncertainties add in quadrature
samples["z"] = samples.net / samples.dnet                       # how many sigmas above zero?


def time_to_detect(net, Rb, k=K):
    """Counting time t (s) for which net / sigma_net = k, if the background is
    counted for the same time t. Uses sigma_net^2 = (net + 2*Rb) / t.
    k=K means: if you do not give k, the value K (3) is used."""
    if net <= 0:
        return np.inf             # infinity: a sample with no net signal is never detected
    return k**2 * (net + 2 * Rb) / net**2


print(f"{'sample':28s} {'net rate (cps)':>18s} {'z':>6s}  verdict    t needed for 3 sigma")
for _, s in samples.iterrows():
    if s.z > K:
        verdict = "DETECTED"
    else:
        verdict = "not seen"
    t3 = time_to_detect(s.net, Rb)
    if np.isinf(t3):
        t3s = "-"
    else:
        t3s = f"{t3:8.0f} s"
    print(f"{s['sample']:28s} {s.net:8.3f} +/- {s.dnet:5.3f} {s.z:6.1f}  {verdict:9s}  {t3s}")

# =============================================================================
#  STEP 3 - Bar chart
# =============================================================================
labels = []
colours = []
for _, s in samples.iterrows():
    labels.append(s["sample"].replace("_", " "))
    if s.z > K:
        colours.append("#2E8B57")             # green = detected
    else:
        colours.append("#A0A8B5")             # grey = not seen

fig, ax = plt.subplots(figsize=(7.5, 4))
y = np.arange(len(samples))                   # one bar position per sample: 0, 1, 2, ...
ax.barh(y, samples.net, xerr=K * samples.dnet, color=colours, capsize=4)
ax.axvline(0, color="#1B2A49", lw=0.8)
ax.set_yticks(y, labels, fontsize=8)
# "symlog" is a log scale that also allows zero and negative values near zero
ax.set_xscale("symlog", linthresh=0.5)
ax.set_xlabel("Net count rate above background (cps)   [error bars: 3 sigma]")
ax.set_title("9.2  What did the GM Puzzle chain detect?   green = detected")
ax.grid(axis="x", alpha=0.3)
fig.tight_layout()
fig.savefig(HERE / "detection.png", dpi=200)
print("\nGraph saved to detection.png (next to this script)")
