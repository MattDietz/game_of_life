import random
import time

import pygame
import pygame.locals


CONF = {
    "width": 1600,
    "height": 1050
}

GRID_SLICE = 8
LIVE_START = 0.70
MIN_FLOOD_SIZE = 50

# Defaults 2, 3, 3
UNDERPOPULATE = 2
OVERCROWD = 6
REBIRTH = 3


def init_grid(grid_width, grid_height):
    grid = []
    for y in xrange(grid_height):
        grid.append([])
        for x in xrange(grid_width):
            live = random.random() > LIVE_START
            grid[y].append(live)
    return grid


def _get_adjacent_score(grid, x, y, grid_width, grid_height):
    score = 0
    for i in xrange(y - 1, y + 2):
        if i < 0 or i == grid_height:
            continue
        for j in xrange(x - 1, x + 2):
            if i == y and j == x:
                continue
            if j < 0 or j == grid_width:
                continue
            score += grid[i][j]
    return score


def iterate_game(old_grid):
    # Any live cell with fewer than two live neighbours dies
    # Any live cell with two or three live neighbours lives on
    # Any live cell with more than three live neighbours dies
    # Any dead cell with exactly three live neighbours becomes a live cell
    new_grid = []
    for y in xrange(grid_height):
        new_grid.append([])
        for x in xrange(grid_width):
            score = _get_adjacent_score(old_grid, x, y, grid_width,
                                        grid_height)
            if old_grid[y][x]:
                if score < UNDERPOPULATE or score > OVERCROWD:
                    new_grid[y].append(0)
                else:
                    new_grid[y].append(1)
            else:
                # The real game specifies exactly 3, but we'd like
                # "caves" to "grow"
                # if score == REBIRTH
                if score > REBIRTH:
                    new_grid[y].append(1)
                else:
                    new_grid[y].append(0)
    return new_grid


def draw_grid(screen, grid, grid_width, grid_height):
    for y in xrange(grid_height):
        for x in xrange(grid_width):
            rect = pygame.Rect(x * GRID_SLICE, y * GRID_SLICE, GRID_SLICE,
                               GRID_SLICE)
            color = pygame.color.THECOLORS["black"]
            if grid[y][x] == 1:
                color = pygame.color.THECOLORS["red"]
            elif grid[y][x] == 2:
                color = pygame.color.THECOLORS["blue"]
            pygame.draw.rect(screen, color, rect)


def flood(grid, grid_width, grid_height):
    flood_grid = []

    def _check_append(current, cell_x, cell_y):
        if cell_x < 0 or cell_x == grid_width:
            return
        if cell_y < 0 or cell_y == grid_height:
            return
        if grid[cell_y][cell_x]:
            return
        if flood_grid[cell_y][cell_x]:
            return

        current.append((cell_x, cell_y))

    for y in xrange(grid_height):
        flood_grid.append([])
        for x in xrange(grid_width):
            flood_grid[y].append(grid[y][x])

    current_flood = []
    for y in xrange(grid_height):
        for x in xrange(grid_width):
            if grid[y][x] == 1:
                continue

            if flood_grid[y][x]: # already flooded
                continue

            # Four way flood
            current_flood.append((x, y))
            flooded_list = []

            while len(current_flood) > 0:
                cell_x, cell_y = current_flood.pop()

                _check_append(current_flood, cell_x - 1, cell_y)
                _check_append(current_flood, cell_x + 1, cell_y)
                _check_append(current_flood, cell_x, cell_y - 1)
                _check_append(current_flood, cell_x, cell_y + 1)

                flood_grid[cell_y][cell_x] = 1
                flooded_list.append((cell_x, cell_y))

            if len(flooded_list) <= MIN_FLOOD_SIZE:
                for cell_x, cell_y in flooded_list:
                    grid[cell_y][cell_x] = 1


def run_game(screen, grid_width, grid_height):
    grid = init_grid(grid_width, grid_height)
    clock = pygame.time.Clock()
    paused = False
    draw_once = False
    while True:
        for event in pygame.event.get():
            if event.type == pygame.locals.QUIT:
                return
            if event.type == pygame.locals.KEYDOWN:
                if event.key == pygame.locals.K_ESCAPE:
                    return
                if event.key == pygame.locals.K_SPACE:
                    paused = not paused
                if event.key == pygame.locals.K_f:
                    paused = True
                    flood(grid, grid_width, grid_height)
                    paused = False
                    draw_once = True
                if event.key == pygame.locals.K_c:
                    grid = init_grid(grid_width, grid_height)

        pygame.event.pump()
        if not paused:
            screen.fill(pygame.color.THECOLORS["black"])
            if not draw_once:
                grid = iterate_game(grid)

            draw_grid(screen, grid, grid_width, grid_height)
            pygame.display.flip()
        clock.tick(60)
        if draw_once:
            draw_once = False
            paused = True


if __name__ == "__main__":
    pygame.init()
    screen = pygame.display.set_mode((CONF['width'], CONF['height']), 0)
    grid_width = CONF["width"] / GRID_SLICE
    grid_height = CONF["height"] / GRID_SLICE
    run_game(screen, grid_width, grid_height)
