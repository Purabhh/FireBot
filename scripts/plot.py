# Plots the results CSV from experiments.py. Only reads the CSV, never runs the
# simulation.

import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "results" / "results.csv"
OUT_PNG = ROOT / "results" / "success_vs_q.png"


# Read every row of the CSV as a dict.
def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


# Success rate per bot per q, as {bot: {q: rate}}.
def success_rates(rows):
    wins = {}
    games = {}
    for row in rows:
        bot = row["bot"]
        q = float(row["q"])
        wins.setdefault(bot, {}).setdefault(q, 0)
        games.setdefault(bot, {}).setdefault(q, 0)
        wins[bot][q] += int(row["success"])
        games[bot][q] += 1

    rates = {}
    for bot in games:
        rates[bot] = {q: wins[bot][q] / games[bot][q] for q in games[bot]}
    return rates


def main():
    rows = read_rows(IN_CSV)
    rates = success_rates(rows)
    D = rows[0]["D"]

    for bot in sorted(rates):
        qs = sorted(rates[bot])
        ys = [rates[bot][q] for q in qs]
        plt.plot(qs, ys, marker="o", label=bot)   # one line per bot

    plt.xlabel("q (flammability)")                        # label the x-axis
    plt.ylabel("Success rate")                            # label the y-axis
    plt.title("Bot success rate vs flammability (D=%s)" % D)   # title on top
    plt.ylim(0, 1)                                        # a rate is 0 to 1
    plt.legend()                                          # box naming each line
    plt.savefig(OUT_PNG)                                  # save the figure
    print("saved %s" % OUT_PNG)
    plt.show()                                            # open a window


if __name__ == "__main__":
    main()
