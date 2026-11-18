# 2.7_numpy_arrays.py - maths on a whole column of numbers at once
import numpy as np        # NumPy, nicknamed np

counts = np.array([1043, 987, 1012, 1001, 968, 1025])   # six 10-second counts
time_s = 10

rates = counts / time_s              # divides EVERY number in the array
d_rates = np.sqrt(counts) / time_s   # square root of every number

print("Rates (cps):      ", rates)
print("Uncertainties:    ", np.round(d_rates, 1))
print(f"Mean rate:          {rates.mean():.2f} cps")
print(f"Standard deviation: {rates.std(ddof=1):.2f} cps")
print(f"Poisson predicts:   {np.sqrt(counts.mean()) / time_s:.2f} cps")

# Comparisons work on whole arrays too, and give True/False for each element.
high = rates > 101
print("Which rates are above 101 cps?", high)
print("The high rates are:", rates[high])   # keep only the True ones
