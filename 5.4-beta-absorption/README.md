# Activity 5.4 – Beta absorption and the maximum beta energy of Y-90

*Radiation Detection Activity Book*, Chapter 5 (Universal Radiometer + GM Tube Probes), Section 5.4.
Instrument: Universal Radiometer + GM Tube Probes.

| File | What it is |
|---|---|
| `beta_absorption.py` | the analysis script |
| `beta_absorption.csv` | example data (20 rows, simulated) |
| `expected_output/` | what you should see: `output.txt` and `beta.png` |

## How to run it
1. Download the files of this folder (or the whole repository, see the [main page](https://github.com/Detectors4Education/radiation-activity-book)).
   Keep the script and its CSV file(s) **in the same folder**.
2. Open `beta_absorption.py` in **Thonny** (or any Python editor) and press **Run** (F5).
   Or, in a terminal opened in this folder: `python beta_absorption.py`
3. The results are printed, and the graph is saved as `beta.png` next to the script.

## Use your own measurements
Make a CSV file with exactly the same column names (first line below) and save it in this folder. Then either
replace the example file (keep its name), or type its name after the script name:
`python beta_absorption.py my_data.csv`

Columns (first line of the file):
- `beta_absorption.csv`: `absorber,thickness_mm,counts,time_s`

Lines that start with `#` are notes; the script skips them.

## Expected output (example data)
```
Background: 0.36 cps;  bremsstrahlung tail: 0.68 cps
Fit on (0.45, 0.95) g/cm^2:  ln(R) = 4.84 -4.87 x
Maximum range R_max = 1.076 +/- 0.008 g/cm^2 = 3.98 mm of aluminium
E_max (Katz-Penfold) = 2.24 +/- 0.02 MeV
Reference: Y-90 E_max = 2.28 MeV, Sr-90 E_max = 0.546 MeV

Graph saved to beta.png (next to this script)
```
![Expected graph](expected_output/beta.png)

[← All activities](https://github.com/Detectors4Education/radiation-activity-book)
