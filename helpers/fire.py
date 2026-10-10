from helpers.ship import neighbors


def burning_neighbor_count(cell, fire_cells, D):
    return sum(1 for n in neighbors(cell, D) if n in fire_cells)


def spread_fire(ship, fire_cells, q, rng):
    D = len(ship)

    candidates = set()
    for cell in fire_cells:
        for (r, c) in neighbors(cell, D):
            if ship[r][c] and (r, c) not in fire_cells:
                candidates.add((r, c))

    new_fire = set(fire_cells)
    for cell in sorted(candidates):
        k = burning_neighbor_count(cell, fire_cells, D)
        p = 1.0 - (1.0 - q) ** k
        if rng.random() < p:
            new_fire.add(cell)
    return new_fire

