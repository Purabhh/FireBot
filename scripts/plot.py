import csv
from pathlib import Path

import matplotlib.pyplot as plt

ROOT = Path(__file__).resolve().parents[1]
IN_CSV = ROOT / "results" / "results.csv"
OUT_PNG = ROOT / "results" / "success_vs_q.png"


def read_rows(path):
    with open(path, newline="") as f:
        return list(csv.DictReader(f))


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
        plt.plot(qs, ys, marker="o", label=bot)

    plt.xlabel("q (flammability)")
    plt.ylabel("Success rate")
    plt.title("Bot success rate vs flammability (D=%s)" % D)
    plt.ylim(0, 1)
    plt.legend()
    plt.savefig(OUT_PNG)
    print("saved %s" % OUT_PNG)
    plt.show()


if __name__ == "__main__":
    main()

