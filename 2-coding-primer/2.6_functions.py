# 2.6_functions.py - writing your own functions

# "def" defines a FUNCTION: a named recipe. The inputs go in brackets.
# "return" sends the answer back to whoever called the function.
def count_rate(counts, time_s):
    """Return the count rate (cps) and its Poisson uncertainty."""
    rate = counts / time_s
    uncertainty = counts ** 0.5 / time_s
    return rate, uncertainty


def inverse_square(rate_1, d_1, d_2):
    """Predict the count rate at distance d_2 from the rate at distance d_1."""
    return rate_1 * (d_1 / d_2) ** 2


# Now USE (call) the functions as often as we like.
r, dr = count_rate(1200, 60)
print(f"Rate = {r:.1f} +/- {dr:.1f} cps")

for d in [20, 40, 80]:
    print(f"At {d} cm we expect {inverse_square(r, 10, d):6.2f} cps")
