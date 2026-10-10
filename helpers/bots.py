from collections import deque

from helpers.ship import neighbors

INF = float("inf")


def bfs(ship, start, goal, blocked):
    D = len(ship)
    if not ship[start[0]][start[1]] or not ship[goal[0]][goal[1]]:
        return None
    if start == goal:
        return [start]
    if goal in blocked:
        return None

    prev = {start: None}
    frontier = deque([start])
    while frontier:
        current = frontier.popleft()
        for cell in neighbors(current, D):
            if cell in prev:
                continue
            if not ship[cell[0]][cell[1]] or cell in blocked:
                continue
            prev[cell] = current
            if cell == goal:
                return reconstruct(prev, goal)
            frontier.append(cell)
    return None


def multi_source_bfs(ship, sources, blocked=frozenset()):
    D = len(ship)
    dist = {}
    frontier = deque()
    for cell in sources:
        if ship[cell[0]][cell[1]]:
            dist[cell] = 0
            frontier.append(cell)

    while frontier:
        current = frontier.popleft()
        for cell in neighbors(current, D):
            if cell in dist or not ship[cell[0]][cell[1]] or cell in blocked:
                continue
            dist[cell] = dist[current] + 1
            frontier.append(cell)
    return dist


def reconstruct(prev, goal):
    path = []
    cell = goal
    while cell is not None:
        path.append(cell)
        cell = prev[cell]
    path.reverse()
    return path


class BaseBot:

    def __init__(self, ship, button):
        self.ship = ship
        self.button = button
        self.D = len(ship)

    def next_move(self, bot_pos, fire_cells):
        raise NotImplementedError

    @staticmethod
    def first_step(path, bot_pos):
        if path is not None and len(path) > 1:
            return path[1]
        return bot_pos


class Bot1(BaseBot):

    def __init__(self, ship, button):
        super().__init__(ship, button)
        self.plan = None

    def next_move(self, bot_pos, fire_cells):
        if self.plan is None:
            path = bfs(self.ship, bot_pos, self.button, set(fire_cells))
            self.plan = deque(path[1:]) if path is not None else deque()
        if self.plan:
            return self.plan.popleft()
        return bot_pos


class Bot2(BaseBot):

    def next_move(self, bot_pos, fire_cells):
        path = bfs(self.ship, bot_pos, self.button, set(fire_cells))
        return self.first_step(path, bot_pos)


class Bot3(BaseBot):

    def next_move(self, bot_pos, fire_cells):
        fire = set(fire_cells)

        risky = set(fire)
        for cell in fire:
            for (r, c) in neighbors(cell, self.D):
                if self.ship[r][c]:
                    risky.add((r, c))
        risky.discard(self.button)

        path = bfs(self.ship, bot_pos, self.button, risky)
        if path is not None and len(path) > 1:
            return path[1]

        path = bfs(self.ship, bot_pos, self.button, fire)
        return self.first_step(path, bot_pos)


def safety_map(ship, button_dist, fire_dist, limit):
    D = len(ship)
    cells = sorted((c for c in button_dist if button_dist[c] <= limit),
                   key=lambda c: button_dist[c])

    safety = {}
    for cell in cells:
        d = button_dist[cell]
        if d == 0:
            safety[cell] = fire_dist.get(cell, INF)
            continue
        best = max(safety[n] for n in neighbors(cell, D)
                   if button_dist.get(n, -1) == d - 1)
        safety[cell] = min(fire_dist.get(cell, INF), best)
    return safety


class Bot4(BaseBot):

    def next_move(self, bot_pos, fire_cells):
        if bot_pos == self.button:
            return bot_pos

        fire = set(fire_cells)
        fire_dist = multi_source_bfs(self.ship, fire)
        button_dist = multi_source_bfs(self.ship, [self.button], blocked=fire)
        if bot_pos not in button_dist:
            return bot_pos

        here = button_dist[bot_pos]
        safety = safety_map(self.ship, button_dist, fire_dist, here)
        steps = [n for n in neighbors(bot_pos, self.D)
                 if button_dist.get(n, -1) == here - 1]
        if not steps:
            return bot_pos

        return max(sorted(steps), key=lambda n: (safety[n], fire_dist.get(n, INF)))


ALL_BOTS = [Bot1, Bot2, Bot3, Bot4]
BOTS_BY_NAME = {cls.__name__: cls for cls in ALL_BOTS}

