# 2.8_reading_data.py - reading a table of measurements with pandas
from pathlib import Path
import numpy as np
import pandas as pd       # pandas, nicknamed pd, handles tables

HERE = Path(__file__).parent                      # the folder of this script
FILE = HERE / "absorber.csv"

# Read the CSV file into a table (a "DataFrame"). Lines starting with # are skipped.
df = pd.read_csv(FILE, comment="#")
print(df)                                         # look at your data first!

# A column is used like df.column_name (or df["column_name"]).
df["rate"] = df.counts / df.time_s                # make a new column
df["d_rate"] = np.sqrt(df.counts) / df.time_s

# Select rows with a condition, e.g. only absorbers of 3 mm or more.
thick = df[df.thickness_mm >= 3]
print("\nRows with 3 mm or more:")
print(thick[["thickness_mm", "rate", "d_rate"]].round(2))
