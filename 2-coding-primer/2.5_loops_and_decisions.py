# 2.5_loops_and_decisions.py - repeating and deciding

background_cps = 0.4
readings_cps = [0.38, 0.45, 2.10, 0.41, 0.52, 3.75]

# A FOR LOOP repeats the indented lines once for every item in the list.
# The indentation (4 spaces) shows which lines belong to the loop.
for r in readings_cps:
    # IF ... ELSE makes a decision. The comparison r > 1.0 is either True or False.
    if r > 1.0:
        print(f"{r:5.2f} cps  -> well above background: a source is nearby!")
    else:
        print(f"{r:5.2f} cps  -> background level")

# range(n) gives the whole numbers 0, 1, ..., n-1. Useful for counting loops.
total = 0
for i in range(len(readings_cps)):
    total = total + readings_cps[i]
print(f"Mean reading: {total / len(readings_cps):.2f} cps")
