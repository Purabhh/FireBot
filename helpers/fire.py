# Fire spread for CS 440 Project 1. The fire is a set of burning cells and
# burning cells never go out.

from helpers.ship import neighbors


# How many of a cell's neighbors are burning.
def burning_neighbor_count(cell, fire_cells, D):
    return sum(1 for n in neighbors(cell, D) if n in fire_cells)


# One time step of fire spread; returns the new set of burning cells.
def spread_fire(ship, fire_cells, q, rng):
    D = len(ship)

    # Only open, non-burning cells touching the fire can ignite this step.
    candidates = set()
    for cell in fire_cells:
        for (r, c) in neighbors(cell, D):
            if ship[r][c] and (r, c) not in fire_cells:
                candidates.add((r, c))

    new_fire = set(fire_cells)
    # Sorted order plus one draw per candidate keeps the fire reproducible, and
    # K comes from the state at the start of the step, so the update is simultaneous.
    for cell in sorted(candidates):
        k = burning_neighbor_count(cell, fire_cells, D)
        p = 1.0 - (1.0 - q) ** k
        if rng.random() < p:
            new_fire.add(cell)
    return new_fire
