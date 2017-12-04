import curses
import math
import time
import random
import sys


GRID_WIDTH = 100
GRID_HEIGHT = 30

DISPLAY_REFRESH_TIME = 0.05
DISPLAY_REFRESH_VARIABILITY = 0.02

PROGRAM_REFRESH_TIME = 2

PROGRAM_LENGTH = 100
INITIAL_ENERGY = 200

MORE_DRAWING = 2
MORE_SPACES = 70
MORE_MOVEMENT = 20

NUMBER_OF_CHARACTERS = 126 - 33

CHARS = []
for i in range(NUMBER_OF_CHARACTERS):
    CHARS.append(ord(' ') + i)


def empty_grid():
    grid = []
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
            row.append(ord(' '))
        grid.append(row)
    return grid


def empty_world():
    world = {}
    world['grid'] = empty_grid()
    world['y'] = math.floor(GRID_HEIGHT / 2)
    world['x'] = math.floor(GRID_WIDTH / 2)
    world['energy'] = 0
    return world


INSTRUCTIONS = []


def char_put(world, char):
    world['grid'][world['y']][world['x']] = char


def char_putter(char):
    return lambda world: char_put(world, char)


for _ in range(MORE_DRAWING):
    for char in CHARS:
        INSTRUCTIONS.append(char_putter(char))


for _ in range(MORE_SPACES):
    INSTRUCTIONS.append(char_putter(ord(' ')))


def north(world):
    world['y'] -= 1
    if world['y'] < 0:
        world['y'] = GRID_HEIGHT - 1


def south(world):
    world['y'] += 1
    if world['y'] > GRID_HEIGHT - 1:
        world['y'] = 0


def west(world):
    world['x'] -= 1
    if world['x'] < 0:
        world['x'] = GRID_WIDTH - 1


def east(world):
    world['x'] += 1
    if world['x'] > GRID_WIDTH - 1:
        world['x'] = 0


for _ in range(MORE_MOVEMENT):
    INSTRUCTIONS.append(north)
    INSTRUCTIONS.append(south)
    INSTRUCTIONS.append(east)
    INSTRUCTIONS.append(west)


def random_code():
    code = []
    for instruction in range(PROGRAM_LENGTH):
        code.append(random.choice(INSTRUCTIONS))
    return code


def run_program(program, world):
    world['energy'] = INITIAL_ENERGY
    for instruction in program:
        if world['energy'] > 0:
            instruction(world)
        else:
            break


def main(stdscr):
    curses.curs_set(0)  # make cursor invisible
    stdscr.nodelay(1)  # don't wait for input when calling getch
    stdscr.clear()
    world = empty_world()
    gridmaxy = len(world['grid'])
    gridmaxx = len(world['grid'][0])
    refresh_display = time.time()
    program = random_code()
    program_refreshed = time.time()
    while True:
        run_program(program, world)
        if time.time() > (program_refreshed + PROGRAM_REFRESH_TIME):
            program_refreshed = time.time()
            program = random_code()
        if time.time() > refresh_display:
            refresh_display = time.time() + DISPLAY_REFRESH_TIME + \
                              (random.random() * DISPLAY_REFRESH_VARIABILITY)
            (maxy, maxx) = stdscr.getmaxyx()
            for y in range(0, maxy):
                for x in range(0, maxx):
                    if (y == maxy - 1) and (x == maxx - 1):
                        pass  # don't trigger this curses bug
                    else:
                        char_to_put = world['grid'][y % gridmaxy][x % gridmaxx]
                        stdscr.addch(y, x, char_to_put)
            c = stdscr.getch()
            if c == ord('q'):
                break
        time.sleep(0.01)


if __name__ == "__main__":
    curses.wrapper(main)
