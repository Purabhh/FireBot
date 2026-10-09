# The bots for CS 440 Project 1. Each is built with (ship, button); next_move
# returns an open neighbor of bot_pos, or bot_pos itself to stay in place.

from collections import deque

from helpers.ship import neighbors

INF = float("inf")


# Shortest path from start to goal inclusive, or None. Never enters a blocked
# or closed cell; start may be in blocked since the bot is already standing there.
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


# BFS from every source at once: {cell: steps to the nearest source}.
def multi_source_bfs(ship, sources, blocked=frozenset()):
    D = len(ship)
    dist = {}
    frontier = deque()
    # A source is where the search starts, so it counts even if it is blocked.
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


# Follow the prev-pointers back from goal and return the forward path.
def reconstruct(prev, goal):
    path = []
    cell = goal
    while cell is not None:
        path.append(cell)
        cell = prev[cell]
    path.reverse()
    return path


# Shared setup and the "take one step along a path" helper.
class BaseBot:

    def __init__(self, ship, button):
        self.ship = ship
        self.button = button
        self.D = len(ship)

    def next_move(self, bot_pos, fire_cells):
        raise NotImplementedError

    # path[0] is the current cell, so the move is path[1] when there is one.
    @staticmethod
    def first_step(path, bot_pos):
        if path is not None and len(path) > 1:
            return path[1]
        return bot_pos


# Plans once against the initial fire, then follows that plan and ignores the fire.
class Bot1(BaseBot):

    def __init__(self, ship, button):
        super().__init__(ship, button)
        self.plan = None       # remaining steps, current cell excluded

    def next_move(self, bot_pos, fire_cells):
        if self.plan is None:
            path = bfs(self.ship, bot_pos, self.button, set(fire_cells))
            self.plan = deque(path[1:]) if path is not None else deque()
        if self.plan:
            return self.plan.popleft()
        return bot_pos


# Replans every step, avoiding the cells that are burning right now.
class Bot2(BaseBot):

    def next_move(self, bot_pos, fire_cells):
        path = bfs(self.ship, bot_pos, self.button, set(fire_cells))
        return self.first_step(path, bot_pos)


# Replans every step, also avoiding cells next to the fire, and falls back to
# Bot2's search when that is too cautious to find anything.
class Bot3(BaseBot):

    def next_move(self, bot_pos, fire_cells):
        fire = set(fire_cells)

        risky = set(fire)
        for cell in fire:
            for (r, c) in neighbors(cell, self.D):
                if self.ship[r][c]:
                    risky.add((r, c))
        risky.discard(self.button)   # the button itself is never off limits

        path = bfs(self.ship, bot_pos, self.button, risky)
        if path is not None and len(path) > 1:
            return path[1]

        path = bfs(self.ship, bot_pos, self.button, fire)
        return self.first_step(path, bot_pos)


# For each cell within `limit` of the button, the closest the fire ever gets
# along the best of that cell's shortest paths to the button.
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
        # Every shortest path from here steps to a neighbor one closer to the
        # button, and those are already scored because d is increasing.
        best = max(safety[n] for n in neighbors(cell, D)
                   if button_dist.get(n, -1) == d - 1)
        safety[cell] = min(fire_dist.get(cell, INF), best)
    return safety


# Takes a shortest path to the button like Bot2, but among the equally short
# paths it walks the one that keeps the most room between itself and the fire.
class Bot4(BaseBot):

    def next_move(self, bot_pos, fire_cells):
        if bot_pos == self.button:
            return bot_pos

        fire = set(fire_cells)
        fire_dist = multi_source_bfs(self.ship, fire)
        button_dist = multi_source_bfs(self.ship, [self.button], blocked=fire)
        if bot_pos not in button_dist:
            return bot_pos       # no fire-free route left, so hold position

        here = button_dist[bot_pos]
        safety = safety_map(self.ship, button_dist, fire_dist, here)
        steps = [n for n in neighbors(bot_pos, self.D)
                 if button_dist.get(n, -1) == here - 1]
        if not steps:
            return bot_pos

        # Safest route first, then the step physically farthest from the fire;
        # sorting beforehand makes any remaining tie deterministic.
        return max(sorted(steps), key=lambda n: (safety[n], fire_dist.get(n, INF)))


ALL_BOTS = [Bot1, Bot2, Bot3, Bot4]
BOTS_BY_NAME = {cls.__name__: cls for cls in ALL_BOTS}
