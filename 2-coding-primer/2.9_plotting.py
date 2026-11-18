# 2.9_plotting.py - a clear graph with error bars
from pathlib import Path
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt   # Matplotlib, nicknamed plt, draws graphs

HERE = Path(__file__).parent
df = pd.read_csv(HERE / "absorber.csv", comment="#")
rate = df.counts / df.time_s
d_rate = np.sqrt(df.counts) / df.time_s

fig, ax = plt.subplots(figsize=(6, 4))            # a figure with one set of axes
ax.errorbar(df.thickness_mm, rate, yerr=d_rate,   # x, y and the error bars
            fmt="o", capsize=3, label="measured")
ax.set_xlabel("Aluminium thickness (mm)")         # ALWAYS label axes, with units
ax.set_ylabel("Count rate (cps)")
ax.set_title("Beta particles through aluminium")
ax.grid(alpha=0.3)
ax.legend()
fig.tight_layout()
fig.savefig(HERE / "2.9_plot.png", dpi=200)       # save the graph as a picture
print("Graph saved as 2.9_plot.png")
