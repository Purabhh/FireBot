# CS 440 Project 1: This Ship is on Fire

A bot has to reach the button on a burning ship before the fire reaches it.
Four bot strategies are simulated across flammability values `q` from 0 to 1.

## Layout

```
project1/
  helpers/          simulation core, reused by later projects
    ship.py         grid generation, neighbors, open_cells, print_ship
    fire.py         one time step of fire spread
    bots.py         bfs, multi_source_bfs, Bot1 through Bot4
  scripts/          things you actually run
    run_once.py     run_game, plus a watchable single game
    experiments.py  the full sweep, writes the CSV
    plot.py         reads the CSV and draws the figure
  results/
    results.csv     one row per (trial, bot)
    success_vs_q.png
```

## Running

From the project root:

```bash
python helpers/ship.py        # print a D=15 ship and its dead-end counts
python scripts/run_once.py    # watch one D=20 game, Bot2 at q=0.3
python scripts/experiments.py # the full sweep, about 15 minutes with 4 bots
python scripts/plot.py        # redraw the figure from results.csv
```

`python -m scripts.experiments` works too. Each script puts the project root on
`sys.path` itself, so none of this depends on where you launch it from.

Needs Python 3 and, for `plot.py` only, matplotlib.

## Conventions

- The grid is D x D, cells are `(row, col)` tuples.
- `ship[r][c]` is `True` for open, `False` for blocked.
- Neighbors are up, down, left and right only.
- Anything random takes an `rng` argument (a `random.Random`). The global
  `random` module is never called directly.

## Reproducibility

A trial's seed is a SHA-256 of `(BASE_SEED, q, trial index)`, so the same
`BASE_SEED` replays the same ships, placements and fires. Within a trial every
bot plays one identical setup and one identical fire seed, so the bots are
compared on the same games rather than on separate luck.

## Tuning

- The sweep: `D`, `Q_VALUES`, `TRIALS_PER_Q`, `OUT_CSV`, `BASE_SEED` at the top
  of `scripts/experiments.py`.
- The watchable game: `DEMO_D`, `DEMO_Q`, `DEMO_SEED`, `DEMO_BOT` in the
  `__main__` block of `scripts/run_once.py`.

## Bot summary

| Bot | Strategy |
| --- | --- |
| Bot1 | Plans once against the initial fire, then walks that plan blindly. |
| Bot2 | Replans every step, avoiding the cells currently on fire. |
| Bot3 | Replans every step, also avoiding cells adjacent to fire, falling back to Bot2's search when nothing safe exists. |
| Bot4 | Replans every step and always takes a shortest path, but among the equally short paths it takes the one that stays farthest from the fire. |

Bot4 costs two BFS passes plus one sweep over the cells nearer the button than
the bot is, so it is never slower than Bot2 in steps taken and never longer in
route length, only in compute.

## CSV columns

`trial_id`, `D`, `q`, `bot`, `success`, `steps`, `end_reason`, `seed`,
`bot_to_button_dist`, `fire_to_button_dist`.

`end_reason` is one of `button`, `walked_into_fire`, `caught_by_fire`,
`timeout`. The two distances are BFS distances on the empty ship at t=0,
ignoring fire, which is what makes failure analysis possible later.
