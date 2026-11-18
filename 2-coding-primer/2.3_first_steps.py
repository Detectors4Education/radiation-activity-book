# 2.3_first_steps.py - your first scientific program
# Everything after a # is a COMMENT: Python ignores it, but people read it.

# print() shows text on the screen. Text goes inside quotation marks.
print("Hello, radiation detectives!")

# A VARIABLE is a name for a value. The = sign means "store this value".
counts = 1200          # number of counts recorded by the detector
time_s = 60            # counting time in seconds

# Python does arithmetic with + - * / and ** (to the power of).
rate = counts / time_s
print("Count rate:", rate, "counts per second")

# Variables can be changed and reused.
counts = counts + 300  # add 300 more counts
print("New total:", counts)

# An f-string puts variables into text: write f before the quotes and the
# variable names in {curly brackets}. ":.2f" means "2 decimal places".
uncertainty = counts ** 0.5            # square root of the counts
print(f"N = {counts} +/- {uncertainty:.2f} counts")
