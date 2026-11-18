# 2.10_fitting.py - fitting a model to data and getting uncertainties
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.optimize import curve_fit   # fits ANY formula to data

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "absorber.csv", comment="#")
x = df.thickness_mm.to_numpy(float)
R = (df.counts / df.time_s).to_numpy()
dR = (np.sqrt(df.counts) / df.time_s).to_numpy()

# 1. Write the model as a function. The first input is x; the rest are the
#    parameters that the computer will adjust.
def model(x, R0, mu):
    return R0 * np.exp(-mu * x)

# 2. Fit. p0 = starting guesses; sigma = error bars.
best, cov = curve_fit(model, x, R, p0=[100, 0.3], sigma=dR, absolute_sigma=True)
errors = np.sqrt(np.diag(cov))          # uncertainties of the parameters
print(f"R0 = {best[0]:.1f} +/- {errors[0]:.1f} cps")
print(f"mu = {best[1]:.4f} +/- {errors[1]:.4f} per mm")

# 3. Check the fit: chi-squared per degree of freedom should be close to 1.
chi2 = np.sum(((R - model(x, *best)) / dR) ** 2)
print(f"chi^2 / ndf = {chi2:.1f} / {len(x) - 2}")

# 4. Draw the data and the fitted curve.
xx = np.linspace(0, x.max(), 200)
fig, ax = plt.subplots(figsize=(6, 4))
ax.errorbar(x, R, yerr=dR, fmt="o", capsize=3, label="data")
ax.plot(xx, model(xx, *best), label=f"fit: mu = {best[1]:.3f} /mm")
ax.set_yscale("log")
ax.set_xlabel("Aluminium thickness (mm)")
ax.set_ylabel("Count rate (cps)")
ax.legend()
ax.grid(alpha=0.3, which="both")
fig.tight_layout()
fig.savefig(HERE / "2.10_fit.png", dpi=200)
print("Graph saved as 2.10_fit.png")
