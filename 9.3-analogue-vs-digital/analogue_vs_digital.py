# =============================================================================
#  Activity 9.3 - Digital or analogue?  Precision and response time
#  Equipment: GM Puzzle Set with the DIGITAL DISPLAY and the ANALOGUE DISPLAY
#             both connected to the Signal Discriminator, one check source
# =============================================================================
#  WHAT THIS SCRIPT DOES
#    1. Reads the needle readings of the Analogue Display (converted to cps),
#       taken once per second, while the source was put next to the tube at t = 0.
#    2. Fits the step response  r(t) = r0 + (r1 - r0) * (1 - exp(-t / tau))
#       to find the TIME CONSTANT tau of the analogue display.
#    3. Compares the wobble of the settled needle with the theory
#       sigma_r = sqrt(r / (2 tau)).
#    4. Compares this with repeated counts from the Digital Display.
#
#  HOW TO RUN IT
#    Thonny: open the file and press "Run".
#    Terminal:  python analogue_vs_digital.py
#
#  YOUR DATA FILES (in the same folder as this script)
#    G2_analogue_step.csv    columns: time_s, reading_cps
#    G2_digital_repeats.csv  columns: gate_s, counts
#
#  PYTHON IDEAS YOU WILL MEET: np.where (choose between two formulas),
#  curve_fit, standard deviation, groupby, and shading a band on a graph.
# =============================================================================

from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit

HERE = Path(__file__).parent
step = pd.read_csv(HERE / "analogue_step.csv", comment="#")
reps = pd.read_csv(HERE / "digital_repeats.csv", comment="#")

# =============================================================================
#  STEP 1 - The step-response model
# =============================================================================
def step_model(t, r0, r1, tau):
    """Needle reading after the true rate jumps from r0 to r1 at t = 0.
    np.where(condition, A, B) gives A where the condition is True, otherwise B:
    before t = 0 the reading is r0; afterwards it rises towards r1."""
    return np.where(t < 0, r0, r0 + (r1 - r0) * (1 - np.exp(-t / tau)))


t = step.time_s.to_numpy(float)
r = step.reading_cps.to_numpy(float)

# Starting guesses: 0.5 cps before, the largest reading after, and tau = 5 s.
p, cov = curve_fit(step_model, t, r, p0=[0.5, r.max(), 5])
r0 = p[0]
r1 = p[1]
tau = p[2]
errors = np.sqrt(np.diag(cov))
dr0 = errors[0]
dr1 = errors[1]
dtau = errors[2]
print(f"Before the source: r0  = {r0:.2f} +/- {dr0:.2f} cps")
print(f"Final reading:     r1  = {r1:.1f} +/- {dr1:.1f} cps")
print(f"Time constant:     tau = {tau:.1f} +/- {dtau:.1f} s")
print(f"Time to reach 95 % of the final value: 3*tau = {3*tau:.0f} s\n")

# =============================================================================
#  STEP 2 - How much does the settled needle wobble?
# =============================================================================
settled = r[t > 5 * tau]                  # keep only readings taken after 5 time constants
sd_meas = settled.std(ddof=1)             # measured wobble (standard deviation)
sd_theory = np.sqrt(r1 / (2 * tau))       # expected wobble
print(f"Analogue Display after settling: mean {settled.mean():.1f} cps, scatter {sd_meas:.2f} cps")
print(f"   theory sqrt(r/(2 tau)) = {sd_theory:.2f} cps  -> relative {100*sd_theory/r1:.1f} %")
print("   (readings 1 s apart are NOT independent, so the measured")
print("    scatter is only a rough check of the formula)\n")

# =============================================================================
#  STEP 3 - Digital Display: repeated counts
# =============================================================================
print("Digital Display, repeated measurements:")
# groupby("gate_s") gives one group for the 10 s counts and one for the 100 s counts.
for g, grp in reps.groupby("gate_s"):
    rate = grp.counts / g                         # count rates for this gate time
    poisson_sd = np.sqrt(grp.counts.mean()) / g   # what Poisson statistics predict
    rel = 100 / np.sqrt(grp.counts.mean())        # relative uncertainty in %
    print(f"   gate {g:4d} s: mean {rate.mean():6.2f} cps, scatter {rate.std(ddof=1):5.2f} cps,"
          f" Poisson predicts {poisson_sd:5.2f} cps  ({rel:.1f} %)")
print("\nAn analogue display with time constant tau is about as precise as a")
print(f"digital count lasting 2*tau = {2*tau:.0f} s, but it never 'finishes' a measurement.")

# =============================================================================
#  STEP 4 - Graph
# =============================================================================
fig, ax = plt.subplots(figsize=(7.5, 4))
ax.plot(t, r, "o", ms=3.5, color="#3D5A98", label="needle readings")
tt = np.linspace(t.min(), t.max(), 500)
ax.plot(tt, step_model(tt, *p), color="#E07A1F", lw=2,
        label=rf"fit: $\tau$ = {tau:.1f} $\pm$ {dtau:.1f} s")
ax.axvline(0, color="grey", ls=":", lw=1)
# axhspan shades a horizontal band: here, the expected wobble around r1
ax.axhspan(r1 - sd_theory, r1 + sd_theory, color="#E07A1F", alpha=0.12,
           label=r"expected wobble $\pm\sqrt{r/2\tau}$")
ax.annotate("source placed\nnext to the tube", (0, r1 * 0.15), xytext=(8, r1 * 0.12), fontsize=8,
            arrowprops=dict(arrowstyle="->", color="grey"))
ax.set_xlabel("Time (s)")
ax.set_ylabel("Analogue Display reading (cps)")
ax.set_title("9.3  Step response of the Analogue Display")
ax.legend(frameon=False, fontsize=8, loc="lower right")
ax.grid(alpha=0.3)
fig.tight_layout()
fig.savefig(HERE / "analogue.png", dpi=200)
print("\nGraph saved to analogue.png (next to this script)")
