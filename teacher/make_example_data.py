"""
make_example_data.py  --  generates the SIMULATED example data sets used in the
activity book (one CSV file in each activity folder of the repository).

These numbers are NOT measurements made with the kit. They are produced from
simple physical models plus Poisson counting noise so that every student script
can be run and tested before real data are collected. Teachers may change the
model parameters below to create fresh practice data sets.
"""
from pathlib import Path
import numpy as np
from scipy.special import erfc

rng = np.random.default_rng(2026)
REPO = Path(__file__).resolve().parent.parent          # the top folder of the repository
FOLDER = {
    "attenuation.csv": "3.2-gamma-attenuation",
    "potassium.csv": "3.3-potassium-detection-limit",
    "background_10s.csv": "4.3-counting-statistics",
    "source_1s.csv": "4.3-counting-statistics",
    "inverse_square.csv": "4.4-inverse-square",
    "plateau.csv": "5.3-gm-plateau",
    "beta_absorption.csv": "5.4-beta-absorption",
    "alpha_range.csv": "6.2-alpha-range",
    "response_matrix.csv": "6.3-response-matrix",
    "dose_vs_time.csv": "7.2-dose-vs-dose-rate",
    "dose_rates.csv": "7.3-alara-planner",
    "cross_calibration.csv": "8.5-cross-calibration",
    "radon_progeny.csv": "8.6-radon-progeny",
    "puzzle_samples.csv": "9.2-puzzle-detection",
    "analogue_step.csv": "9.3-analogue-vs-digital",
    "digital_repeats.csv": "9.3-analogue-vs-digital",
    "absorber.csv": "2-coding-primer"
}


def path_for(name):
    """the data file goes into the folder of its activity"""
    return REPO / FOLDER[name] / name



def pois(rate, t):
    """Poisson-distributed number of counts for a true rate (cps) and time t (s)."""
    return int(rng.poisson(max(rate, 0.0) * t))


def write(name, header, rows, comment=None):
    with open(path_for(name), "w") as f:
        if comment:
            for line in comment.strip().splitlines():
                f.write("# " + line + "\n")
        f.write(",".join(header) + "\n")
        for r in rows:
            f.write(",".join(str(x) for x in r) + "\n")


# ---------------------------------------------------------------- Activity 3.2
rows = [["background", 0, pois(4.0, 300), 300]]
for x in range(0, 22, 2):                       # lead, mm
    rows.append(["lead", x, pois(4.0 + 180 * np.exp(-1.18 * x / 10), 60), 60])
for x in range(0, 55, 5):                       # aluminium, mm
    rows.append(["aluminium", x, pois(4.0 + 180 * np.exp(-0.196 * x / 10), 60), 60])
write("attenuation.csv", ["material", "thickness_mm", "counts", "time_s"], rows,
      "Activity 3.2: gamma attenuation - Cs-137, Scintillation Counter unit - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 3.3
bg_A2 = 6.05                                    # cps, empty container
rows = [["empty_container", 0, pois(bg_A2, 600), 600]]
for m in [50, 100, 150, 200, 250, 300]:          # KCl calibration masses (g)
    rows.append(["KCl", m, pois(bg_A2 + 0.2 + 0.0232 * m, 600), 600])
for name, m, net in [("salt_mix_unknown", 250, 1.70), ("table_salt_NaCl", 250, 0.0),
                     ("dried_banana", 100, 0.06)]:
    rows.append([name, m, pois(bg_A2 + net, 600), 600])
write("potassium.csv", ["sample", "mass_g", "counts", "time_s"], rows,
      "Activity 3.3: natural K-40 - Scintillation Counter unit, fixed beaker geometry - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 4.3
with open(path_for("background_10s.csv"), "w") as f:
    f.write("# Activity 4.3: background, 10 s intervals, GM Counter unit - SIMULATED EXAMPLE DATA\n")
    f.write("interval,counts\n")
    for i, c in enumerate(rng.poisson(4.2, 200), 1):
        f.write(f"{i},{c}\n")
with open(path_for("source_1s.csv"), "w") as f:
    f.write("# Activity 4.3: Cs-137 source, 1 s intervals, GM Counter unit - SIMULATED EXAMPLE DATA\n")
    f.write("interval,counts\n")
    for i, c in enumerate(rng.poisson(48.0, 300), 1):
        f.write(f"{i},{c}\n")

# ---------------------------------------------------------------- Activity 4.4
tau = 2.0e-4                                    # dead time of the counter (s)
def meas(r):
    return r / (1 + r * tau)                    # non-paralysable dead-time model
rows = []
for d in [2, 3, 4, 5, 6, 8, 10, 12, 15, 20, 25, 30]:
    r = 1500 / (d + 0.8) ** 2 + 0.35
    rows.append([d, pois(meas(r), 60), 60])
write("inverse_square.csv", ["distance_cm", "counts", "time_s"], rows,
      "Activity 4.4: inverse-square law, Cs-137, GM Counter unit - SIMULATED EXAMPLE DATA\n"
      "distance measured from source to the front face of the counter")

# ---------------------------------------------------------------- Activity 5.3
def plateau_rate(V, V_start, V_knee, R_pl, slope_per_100V, V_end):
    """Counting curve of a GM tube: steep rise, flat plateau, then discharge."""
    if V < V_start:
        return 0.0
    rise = R_pl * (1 - np.exp(-(V - V_start) / ((V_knee - V_start) / 3)))
    r = rise * (1 + slope_per_100V / 100 * (V - V_knee) / 100)
    if V > V_end:
        r *= np.exp((V - V_end) / 25)
    return r
rows = []
for V in range(300, 641, 20):
    rows.append(["black", V, pois(plateau_rate(V, 355, 400, 55.0, 2.0, 600) + 0.3, 60), 60])
for V in range(700, 1026, 25):
    rows.append(["red", V, pois(plateau_rate(V, 720, 775, 64.0, 1.8, 990) + 0.3, 60), 60])
write("plateau.csv", ["probe", "voltage_V", "counts", "time_s"], rows,
      "Activity 5.3: GM plateau, Universal Radiometer + GM probes, Cs-137 - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 5.4
rows = [["background", 0, pois(0.39, 600), 600]]
for t in [0, 0.1, 0.2, 0.4, 0.6, 0.8, 1.0, 1.25, 1.5, 1.75, 2.0, 2.5, 3.0, 3.5,
          4.0, 4.5, 5.0, 6.0, 7.0]:             # aluminium, mm
    x = t / 10 * 2.70                            # areal density g/cm^2
    soft = 95 * np.exp(-x / 0.025)               # Sr-90 betas, absorbed first
    hard = 150 * np.exp(-4.75 * x) * np.clip(1 - x / 1.15, 0, 1) ** 0.5
    tail = 0.64
    rate = 0.39 + soft + hard + tail
    T = 120 if rate > 3 else 600
    rows.append(["Al", t, pois(rate, T), T])
write("beta_absorption.csv", ["absorber", "thickness_mm", "counts", "time_s"], rows,
      "Activity 5.4: beta absorption, Sr-90/Y-90, Universal Radiometer + red GM probe - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 6.2
rows = [["background", 0, pois(0.05, 600), 600]]
a = 2.3
for d in np.arange(0.5, 5.01, 0.25):
    omega = 0.5 * (1 - d / np.sqrt(d**2 + a**2))
    rate = 0.05 + 3200 * omega * 0.5 * erfc((d - 3.2) / (np.sqrt(2) * 0.13))
    rows.append(["Am-241", round(d, 2), pois(rate, 60), 60])
write("alpha_range.csv", ["source", "distance_cm", "counts", "time_s"], rows,
      "Activity 6.2: alpha range in air, Am-241, Universal Radiometer + ZnS(Ag) probe - SIMULATED EXAMPLE DATA\n"
      "lab: 22 C, 101.3 kPa")

# ---------------------------------------------------------------- Activity 6.3
bgr = {"ZnS": 0.05, "GM": 0.40}
true = {   # net rate without absorber, transmission through paper and through 3 mm Al
    ("Am-241", "ZnS"): (120.0, 0.0, 0.0), ("Am-241", "GM"): (2.2, 0.92, 0.84),
    ("Sr-90", "ZnS"): (0.3, 0.9, 0.03), ("Sr-90", "GM"): (95.0, 0.96, 0.01),
    ("Cs-137", "ZnS"): (0.10, 0.9, 0.5), ("Cs-137", "GM"): (41.5, 0.92, 0.20),
    ("Co-60", "ZnS"): (0.10, 0.9, 0.8), ("Co-60", "GM"): (14.0, 1.0, 0.81),
    ("unknown_X", "ZnS"): (85.0, 0.0, 0.0), ("unknown_X", "GM"): (0.0, 1.0, 1.0)}
rows = [[det, "background", "none", pois(b, 600), 600] for det, b in bgr.items()]
for (src, det), (r0, tp, tal) in true.items():
    for ab, f in [("none", 1.0), ("paper", tp), ("Al_3mm", tal)]:
        rows.append([det, src, ab, pois(bgr[det] + r0 * f, 60), 60])
write("response_matrix.csv", ["detector", "source", "absorber", "counts", "time_s"], rows,
      "Activity 6.3: detector response, ZnS(Ag) probe vs red GM probe - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 7.2
rows = []
D1 = D2 = 0.0
for t in range(0, 61, 5):
    if t > 0:
        D1 += 5.1 * 5 / 60 + rng.normal(0, 0.01)
        D2 += 1.46 * 5 / 60 + rng.normal(0, 0.005)
    rows.append([t, f"{D1:.2f}", f"{rng.normal(5.2, 0.45):.2f}",
                 f"{D2:.2f}", f"{rng.normal(1.46, 0.14):.2f}"])
write("dose_vs_time.csv", ["time_min", "dose_uSv_pos1", "rate_uSvh_pos1",
                              "dose_uSv_pos2", "rate_uSvh_pos2"], rows,
      "Activity 7.2: accumulated dose vs time, Personal Dosimeter - SIMULATED EXAMPLE DATA\n"
      "pos1 = 10 cm, pos2 = 20 cm from a Cs-137 source")

# ---------------------------------------------------------------- Activity 7.3
rows = []
for d in [10, 15, 20, 30, 40, 60, 80, 100]:
    rows.append(["distance", d, 0, f"{(520 / d**2 + 0.12) * rng.normal(1, 0.04):.2f}"])
for x in [0, 2, 4, 6, 8, 10, 15, 20]:
    rows.append(["shield_lead", 20, x, f"{1.30 * np.exp(-0.117 * x) * rng.normal(1, 0.04) + 0.12:.2f}"])
write("dose_rates.csv", ["series", "distance_cm", "lead_mm", "dose_rate_uSvh"], rows,
      "Activity 7.3: dose-rate survey for ALARA planning, Personal Dosimeter - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 8.5
# The DIY display shows dose; its tube is assumed 15 % more sensitive than the
# firmware expects. Counting noise from about 80 cpm per uSv/h.
rows = []
for name, Dref, T in [("background_lab", 0.12, 900), ("granite_slab", 0.30, 600), ("source_40cm", 0.85, 300),
                      ("source_25cm", 2.0, 300), ("source_15cm", 5.4, 300), ("source_10cm", 11.8, 300)]:
    true_diy = 1.15 * Dref + 0.02                            # uSv/h shown by the DIY counter
    n = pois(true_diy * 80 / 60, T)                         # pulses counted
    dose = n / (80 * 60) * (1.0)                            # uSv shown on the bottom line
    rows.append([name, f"{rng.normal(Dref, 0.02 + 0.04*Dref):.2f}", f"{dose:.3f}", T])
write("cross_calibration.csv", ["position", "reference_uSvh", "diy_dose_uSv", "time_s"], rows,
      "Activity 8.5: cross-calibration of the DIY GM counter against the GM Counter unit - SIMULATED EXAMPLE DATA\n"
      "diy_dose_uSv = increase of the DIY counter's cumulative-dose line during time_s")

# ---------------------------------------------------------------- Activity 8.6
lPb, lBi = np.log(2) / 26.8, np.log(2) / 19.9   # per minute
NPb0, NBi0 = 9000.0, 7000.0                     # atoms x efficiency (arbitrary)
rows = []
for t in range(0, 121, 2):
    NPb = NPb0 * np.exp(-lPb * t)
    NBi = NBi0 * np.exp(-lBi * t) + NPb0 * lPb / (lBi - lPb) * (np.exp(-lPb * t) - np.exp(-lBi * t))
    cpm = 0.35 * (lPb * NPb + lBi * NBi) + 22    # 35 % efficiency, 22 cpm background
    rows.append([t, pois(cpm / 60, 60), 60])
write("radon_progeny.csv", ["time_min", "counts", "time_s"], rows,
      "Activity 8.6: radon progeny on a balloon, counts per 1-minute interval - SIMULATED EXAMPLE DATA\n"
      "time_min = start of each 1-minute count after the balloon was placed on the tube\n"
      "background measured separately: 1310 counts in 3600 s")

# ---------------------------------------------------------------- Activity 9.2
rows = [["background", pois(0.42, 600), 600]]
for name, net in [("KCl_salt_substitute_500g", 0.30), ("granite_tile", 0.12),
                  ("uranium_glass_bead", 2.6), ("Cs137_check_source_10cm", 14.0),
                  ("table_salt_NaCl_500g", 0.0)]:
    rows.append([name, pois(0.42 + net, 300), 300])
write("puzzle_samples.csv", ["sample", "counts", "time_s"], rows,
      "Activity 9.2: GM Puzzle Set: Digital Display counts, background and samples - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- Activity 9.3
tau_true, r_bg, r_src = 6.0, 0.42, 18.0
t_end = 90.0
def pulse_train(t0, t1, rate):                  # Poisson pulse times in [t0, t1)
    n = rng.poisson(rate * (t1 - t0))
    return np.sort(rng.uniform(t0, t1, n))
ev = np.concatenate([pulse_train(-60.0, 0.0, r_bg), pulse_train(0.0, t_end, r_bg + r_src)])
rows = []
for ts in np.arange(-10, 91, 1.0):              # one reading of the display per second
    past = ev[ev <= ts]
    y = np.sum(np.exp(-(ts - past) / tau_true)) / tau_true   # RC-filtered pulse train
    rows.append([f"{ts:.0f}", f"{y:.1f}"])
write("analogue_step.csv", ["time_s", "reading_cps"], rows,
      "Activity 9.3: GM Puzzle Set: Analogue Display needle readings, source placed at t = 0 - SIMULATED EXAMPLE DATA\n"
      "reading_cps = needle reading converted to counts per second, read once per second")
rows = [[10, pois(r_bg + r_src, 10)] for _ in range(20)]
rows += [[100, pois(r_bg + r_src, 100)] for _ in range(5)]
write("digital_repeats.csv", ["gate_s", "counts"], rows,
      "Activity 9.3: GM Puzzle Set: repeated Digital Display counts, same source position - SIMULATED EXAMPLE DATA")

# ---------------------------------------------------------------- primer
write("absorber.csv", ["thickness_mm", "counts", "time_s"],
      [[0, 6020, 60], [1, 4410, 60], [2, 3270, 60], [3, 2400, 60],
       [4, 1790, 60], [5, 1300, 60], [6, 980, 60]],
      "Example data for the programming introduction: aluminium absorbers, beta source")

print("example data written into the activity folders of", REPO)
