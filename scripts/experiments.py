# Batch experiments for CS 440 Project 1. Every bot plays the identical setup
# within a trial, and every setup is seeded from BASE_SEED, so reruns match.

import csv
import hashlib
import random
import sys
import time
from collections import deque
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))   # so "helpers" imports work however this is run

from helpers.ship import generate_ship, neighbors, open_cells
from helpers.bots import ALL_BOTS, BOTS_BY_NAME
from scripts.run_once import run_game

D = 40
Q_VALUES = [round(0.05 * i, 2) for i in range(21)]     # 0.00 .. 1.00
TRIALS_PER_Q = 200
OUT_CSV = ROOT / "results" / "results.csv"
BASE_SEED = 440

CSV_FIELDS = [
    "trial_id", "D", "q", "bot", "success", "steps", "end_reason", "seed",
    "bot_to_button_dist", "fire_to_button_dist",
]


# A stable 64-bit seed for one trial. SHA-256 rather than hash(), whose string
# hashing is randomized per run and would break reproducibility.
def trial_seed(base_seed, q, trial):
    key = "%d|%.6f|%d" % (base_seed, q, trial)
    return int.from_bytes(hashlib.sha256(key.encode()).digest()[:8], "big")


# BFS distance on the empty ship at t=0, ignoring fire. -1 if unreachable.
def grid_distance(ship, start, goal):
    size = len(ship)
    if start == goal:
        return 0
    dist = {start: 0}
    frontier = deque([start])
    while frontier:
        cell = frontier.popleft()
        for n in neighbors(cell, size):
            if n in dist or not ship[n[0]][n[1]]:
                continue
            dist[n] = dist[cell] + 1
            if n == goal:
                return dist[n]
            frontier.append(n)
    return -1


# Build one setup and run every bot on it; returns a list of CSV rows.
def run_trial(d, q, trial_id, seed, bot_names):
    rng = random.Random(seed)
    ship = generate_ship(d, rng)
    placement = tuple(rng.sample(open_cells(ship), 3))
    bot_start, button, fire_start = placement
    fire_seed = rng.randrange(2 ** 32)

    bot_to_button = grid_distance(ship, bot_start, button)
    fire_to_button = grid_distance(ship, fire_start, button)

    rows = []
    for name in bot_names:
        try:
            result = run_game(ship, BOTS_BY_NAME[name], q, placement, fire_seed)
        except NotImplementedError:
            continue       # bot not designed yet
        rows.append({
            "trial_id": trial_id,
            "D": d,
            "q": "%.2f" % q,
            "bot": name,
            "success": int(result["success"]),
            "steps": result["steps"],
            "end_reason": result["end_reason"],
            "seed": seed,
            "bot_to_button_dist": bot_to_button,
            "fire_to_button_dist": fire_to_button,
        })
    return rows


# True unless next_move raises NotImplementedError on a throwaway ship.
def bot_is_implemented(bot_class, probe_d=10):
    ship = generate_ship(probe_d, random.Random(0))
    cells = open_cells(ship)
    try:
        bot_class(ship, cells[-1]).next_move(cells[0], frozenset())
    except NotImplementedError:
        return False
    return True


# Success rate per bot for one q value's worth of rows.
def summarize(rows):
    totals = {}
    for row in rows:
        wins, n = totals.get(row["bot"], (0, 0))
        totals[row["bot"]] = (wins + row["success"], n + 1)
    return {bot: wins / n for bot, (wins, n) in sorted(totals.items())}


# Run the whole sweep and write out_csv.
def run_experiments(D, q_values, trials_per_q, bots, out_csv, base_seed):
    bot_names = []
    for bot_class in bots:
        if bot_is_implemented(bot_class):
            bot_names.append(bot_class.__name__)
        else:
            print("skipping %s: next_move raises NotImplementedError"
                  % bot_class.__name__)

    print("D=%d bots=%s %d q values %d trials per q (%d games)\n"
          % (D, ",".join(bot_names), len(q_values), trials_per_q,
             len(q_values) * trials_per_q * len(bot_names)))

    started = time.time()
    all_rows = []
    for q_index, q in enumerate(q_values):
        rows = []
        for trial in range(trials_per_q):
            trial_id = q_index * trials_per_q + trial
            seed = trial_seed(base_seed, q, trial)
            rows.extend(run_trial(D, q, trial_id, seed, bot_names))
        all_rows.extend(rows)

        rates = summarize(rows)
        print("[%2d/%2d] q=%.2f  %s  (%.1f s elapsed)"
              % (q_index + 1, len(q_values), q,
                 "  ".join("%s %.3f" % pair for pair in rates.items()),
                 time.time() - started))

    Path(out_csv).parent.mkdir(parents=True, exist_ok=True)
    with open(out_csv, "w", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print("\nwrote %d rows to %s in %.1f s"
          % (len(all_rows), out_csv, time.time() - started))
    return all_rows


if __name__ == "__main__":
    run_experiments(
        D=D,
        q_values=Q_VALUES,
        trials_per_q=TRIALS_PER_Q,
        bots=ALL_BOTS,
        out_csv=OUT_CSV,
        base_seed=BASE_SEED,
    )
