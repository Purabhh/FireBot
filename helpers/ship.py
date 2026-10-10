import random


def neighbors(cell, D):
    r, c = cell
    result = []
    if r > 0:
        result.append((r - 1, c))
    if r + 1 < D:
        result.append((r + 1, c))
    if c > 0:
        result.append((r, c - 1))
    if c + 1 < D:
        result.append((r, c + 1))
    return result


def open_cells(ship):
    D = len(ship)
    return [(r, c) for r in range(D) for c in range(D) if ship[r][c]]


def open_neighbor_count(ship, cell):
    D = len(ship)
    return sum(1 for (r, c) in neighbors(cell, D) if ship[r][c])


def dead_ends(ship):
    return [cell for cell in open_cells(ship)
            if open_neighbor_count(ship, cell) == 1]


def generate_ship(D, rng, stats=None):
    if D < 3:
        raise ValueError("D must be at least 3 so an interior cell exists")

    ship = [[False] * D for _ in range(D)]
    open_count = [[0] * D for _ in range(D)]
    candidates = []
    cand_index = {}

    def add_candidate(cell):
        if cell not in cand_index:
            cand_index[cell] = len(candidates)
            candidates.append(cell)

    def remove_candidate(cell):
        i = cand_index.pop(cell, None)
        if i is None:
            return
        last = candidates.pop()
        if i < len(candidates):
            candidates[i] = last
            cand_index[last] = i

    def open_cell(cell):
        r, c = cell
        ship[r][c] = True
        remove_candidate(cell)
        for (nr, nc) in neighbors(cell, D):
            open_count[nr][nc] += 1
            if not ship[nr][nc]:
                if open_count[nr][nc] == 1:
                    add_candidate((nr, nc))
                else:
                    remove_candidate((nr, nc))

    open_cell((rng.randrange(1, D - 1), rng.randrange(1, D - 1)))

    while candidates:
        open_cell(candidates[rng.randrange(len(candidates))])

    current = dead_ends(ship)
    before = len(current)

    while len(current) > before / 2:
        cell = rng.choice(current)
        closed = [n for n in neighbors(cell, D) if not ship[n[0]][n[1]]]
        if not closed:
            break
        nr, nc = rng.choice(closed)
        ship[nr][nc] = True
        current = dead_ends(ship)

    if stats is not None:
        stats["dead_ends_before"] = before
        stats["dead_ends_after"] = len(current)

    return ship


def print_ship(ship, bot=None, button=None, fire=set()):
    D = len(ship)
    lines = []
    for r in range(D):
        row = []
        for c in range(D):
            cell = (r, c)
            if cell == bot:
                row.append("R")
            elif cell == button:
                row.append("B")
            elif cell in fire:
                row.append("F")
            elif ship[r][c]:
                row.append(".")
            else:
                row.append("#")
        lines.append("".join(row))
    print("\n".join(lines))


if __name__ == "__main__":
    DEMO_D = 15
    DEMO_SEED = 440

    rng = random.Random(DEMO_SEED)
    stats = {}
    ship = generate_ship(DEMO_D, rng, stats=stats)

    print("D = %d, seed = %d" % (DEMO_D, DEMO_SEED))
    print_ship(ship)
    print()
    print("open cells:              %d / %d"
          % (len(open_cells(ship)), DEMO_D * DEMO_D))
    print("dead ends before cleanup: %d" % stats["dead_ends_before"])
    print("dead ends after cleanup:  %d (target was <= %.1f)"
          % (stats["dead_ends_after"], stats["dead_ends_before"] / 2))

