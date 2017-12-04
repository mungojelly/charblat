import curses
import math
import time
import random
import sys


GRID_WIDTH = 100
GRID_HEIGHT = 30

DISPLAY_REFRESH_TIME = 0.05
DISPLAY_REFRESH_VARIABILITY = 0.02

PROGRAM_REFRESH_TIME = 7

PROGRAM_LENGTH = 1000
CODE_LENGTH = 50

INITIAL_ENERGY = 5000
LOW_ENERGY = 1000

MORE_DRAWING = 2
MORE_SPACES = 50
MORE_MOVEMENT = 20

NUMBER_OF_CHARACTERS = 126 - 33
#NUMBER_OF_CHARACTERS = 20

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


CONDITIONS = []


def is_energy_low(world):
    return world['energy'] < LOW_ENERGY


CONDITIONS.append(is_energy_low)


def is_energy_high(world):
    return world['energy'] > LOW_ENERGY


CONDITIONS.append(is_energy_high)


def is_char_under_cursor(char, world):
    return world['grid'][world['y']][world['x']] == char


for char in CHARS:
    CONDITIONS.append(lambda world: is_char_under_cursor(char, world))


def is_y_zero(world):
    return world['y'] == 0


CONDITIONS.append(is_y_zero)


def is_x_zero(world):
    return world['x'] == 0


CONDITIONS.append(is_x_zero)


def random_code():
    code = []
    for _ in range(CODE_LENGTH):
        code.append(random.choice(INSTRUCTIONS))
    return code


def random_program():
    program = []
    for _ in range(PROGRAM_LENGTH):
        routine = {}
        routine['condition'] = random.choice(CONDITIONS)
        routine['code'] = random_code()
        program.append(routine)
    return program


def run_routine(routine, world):
    condition = routine['condition']
    while world['energy'] > 0:
        print(world['energy'], file=sys.stderr)
        world['energy'] -= 1
        if condition(world):
            print("hi", file=sys.stderr)
            for instruction in routine['code']:
                instruction(world)
        else:
            break


def run_program(program, world):
    for routine in program:
        if world['energy'] > 0:
            run_routine(routine, world)
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
    program = random_program()
    program_refreshed = time.time()
    while True:
        world['energy'] = INITIAL_ENERGY
        while world['energy'] > 0:
            run_program(program, world)
        if time.time() > (program_refreshed + PROGRAM_REFRESH_TIME):
            program_refreshed = time.time()
            program = random_program()
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
        time.sleep(0.001)


if __name__ == "__main__":
    curses.wrapper(main)
