# Radiation Detection Activity Book – scripts and data

The Python scripts, example data and expected results for the *Radiation Detection Activity Book*
(Detectors4Education). Every folder belongs to one section of the book and carries the same number.

## Get the files
- **Everything at once (recommended):** click the green **Code** button above, then **Download ZIP**, or use
  this link: <https://github.com/Detectors4Education/radiation-activity-book/archive/refs/heads/main.zip>. Unzip the file into a folder of your own
  (for example `Documents/radiation`). Do not run the scripts from inside the zip file.
- **One activity:** open its folder below. Click a file, then the **Download raw file** button (↓, top right of the
  file). Save the script and its CSV file(s) into the same folder.
- **On a phone:** scan the QR code in the book. You can read every script, data file and expected result in the
  browser; to run a script, use a computer.

## Run a script
1. Install Python 3 with the libraries NumPy, pandas, Matplotlib and SciPy. The easiest way is **Thonny**
   (<https://thonny.org>): in Thonny choose *Tools → Manage packages* and install `numpy`, `pandas`, `matplotlib`
   and `scipy`. In a terminal you can instead type `pip install -r requirements.txt`.
2. Open the script in Thonny and press **Run** (F5).
3. Compare what you see with the folder `expected_output`.

## Contents
| Section | Activity | Instrument | Script |
|---|---|---|---|
| 2 | [Introduction to scientific programming (examples)](2-coding-primer) | – | `2.3_first_steps.py` … |
| 3.2 | [Gamma-ray attenuation: how good is a shield?](3.2-gamma-attenuation) | Scintillation Counter unit | `gamma_attenuation.py` |
| 3.3 | [Natural radioactivity: potassium-40 and detection limits](3.3-potassium-detection-limit) | Scintillation Counter unit | `potassium_detection_limit.py` |
| 4.3 | [The statistics of counting: Poisson and Gaussian](4.3-counting-statistics) | Geiger-Müller Counter unit | `counting_statistics.py` |
| 4.4 | [How does radiation spread out? The inverse-square law](4.4-inverse-square) | Geiger-Müller Counter unit | `inverse_square.py` |
| 5.3 | [Finding the operating voltage: the GM plateau](5.3-gm-plateau) | Universal Radiometer + GM Tube Probes | `gm_plateau.py` |
| 5.4 | [Beta absorption and the maximum beta energy of Y-90](5.4-beta-absorption) | Universal Radiometer + GM Tube Probes | `beta_absorption.py` |
| 6.2 | [How far do alpha particles go? Range in air](6.2-alpha-range) | Universal Radiometer + Scintillation Probe | `alpha_range.py` |
| 6.3 | [Who sees what? Identifying radiation with two probes and two absorbers](6.3-response-matrix) | Universal Radiometer + Scintillation Probe | `response_matrix.py` |
| 7.2 | [Speedometer and odometer: dose versus dose rate](7.2-dose-vs-dose-rate) | Personal Dosimeter | `dose_vs_dose_rate.py` |
| 7.3 | [Time, distance, shielding: planning a task with ALARA](7.3-alara-planner) | Personal Dosimeter | `alara_planner.py` |
| 8.5 | [Build it, check it, trust it: assembly, commissioning and calibration](8.5-cross-calibration) | DIY Geiger-Müller Set | `cross_calibration.py` |
| 8.6 | [Catching radon daughters on a balloon: measuring a half-life](8.6-radon-progeny) | DIY Geiger-Müller Set | `radon_progeny.py` |
| 9.2 | [Build the measurement chain: what does each piece do?](9.2-puzzle-detection) | GM Puzzle Set | `puzzle_detection.py` |
| 9.3 | [Digital or analogue? Precision and response time](9.3-analogue-vs-digital) | GM Puzzle Set | `analogue_vs_digital.py` |
| – | [Teacher folder](teacher) | – | `make_example_data.py` |

The example data are **simulated** (made by `teacher/make_example_data.py`), so every script can be tried before
real measurements are made. Replace them with your own data, using the same column names.

Every data file is also printed as a table in the appendix of the book (Section 10.3), for readers of a printed copy.

See the file `LICENSE` for the terms of use.
