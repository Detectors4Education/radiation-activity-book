# 2.4_lists_and_dictionaries.py - storing many values

# A LIST keeps several values in order, inside square brackets.
distances_cm = [10, 20, 30, 40]
counts = [4012, 1035, 466, 258]

# Positions in a list start at 0, not 1!
print("First distance:", distances_cm[0], "cm")
print("Last count:", counts[-1])          # -1 means "the last one"
print("Number of measurements:", len(counts))

# Add a new value to the end of a list with .append()
distances_cm.append(50)
counts.append(170)
print("Distances now:", distances_cm)

# A DICTIONARY stores values under names ("keys"), inside curly brackets.
half_life_years = {"Cs-137": 30.1, "Co-60": 5.27, "Am-241": 432}
print("Half-life of Co-60:", half_life_years["Co-60"], "years")

# Text values are called STRINGS. True and False are BOOLEANS.
source = "Cs-137"
is_sealed = True
print(source, "is sealed:", is_sealed)
