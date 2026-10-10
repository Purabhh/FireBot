import random
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from helpers.ship import generate_ship, neighbors, open_cells, print_ship
from helpers.fire import spread_fire
from helpers import bots


def run_game(ship, bot_class, q, placement, fire_seed, verbose=False):
    D = len(ship)
    bot_start, button, fire_start = placement

    bot_pos = bot_start
    fire_cells = {fire_start}
    fire_rng = random.Random(fire_seed)
    bot = bot_class(ship, button)
    max_steps = 10 * D * D

    if verbose:
        print("step 0: bot=%s button=%s fire=%s" % (bot_start, button, fire_start))
        print_ship(ship, bot=bot_pos, button=button, fire=fire_cells)
        print()

    for step in range(1, max_steps + 1):
        target = bot.next_move(bot_pos, frozenset(fire_cells))
        if target != bot_pos and target not in neighbors(bot_pos, D):
            raise ValueError("%s jumped from %s to %s"
                             % (bot_class.__name__, bot_pos, target))
        if not ship[target[0]][target[1]]:
            raise ValueError("%s moved into blocked cell %s"
                             % (bot_class.__name__, target))
        bot_pos = target

        if bot_pos == button:
            return finish(ship, True, step, "button",
                          bot_pos, button, fire_cells, verbose)

        if bot_pos in fire_cells:
            return finish(ship, False, step, "walked_into_fire",
                          bot_pos, button, fire_cells, verbose)

        fire_cells = spread_fire(ship, fire_cells, q, fire_rng)

        if bot_pos in fire_cells:
            return finish(ship, False, step, "caught_by_fire",
                          bot_pos, button, fire_cells, verbose)

        if verbose:
            print("step %d: bot=%s, %d burning" % (step, bot_pos, len(fire_cells)))
            print_ship(ship, bot=bot_pos, button=button, fire=fire_cells)
            print()

    return finish(ship, False, max_steps, "timeout",
                  bot_pos, button, fire_cells, verbose)


def finish(ship, success, steps, end_reason, bot_pos, button, fire_cells, verbose):
    if verbose:
        print("step %d: %s" % (steps, end_reason))
        print_ship(ship, bot=bot_pos, button=button, fire=fire_cells)
        print()
    return {"success": success, "steps": steps, "end_reason": end_reason}


if __name__ == "__main__":
    DEMO_D = 20
    DEMO_Q = 0.3
    DEMO_SEED = 440
    DEMO_BOT = bots.Bot2

    rng = random.Random(DEMO_SEED)
    ship = generate_ship(DEMO_D, rng)
    placement = tuple(rng.sample(open_cells(ship), 3))
    fire_seed = rng.randrange(2 ** 32)

    print("D=%d q=%.2f bot=%s setup seed=%d fire seed=%d\n"
          % (DEMO_D, DEMO_Q, DEMO_BOT.__name__, DEMO_SEED, fire_seed))
    result = run_game(ship, DEMO_BOT, DEMO_Q, placement, fire_seed, verbose=True)
    print("result: %s" % result)

