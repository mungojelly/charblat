import curses
import math
import time
import random
import sys


GRID_WIDTH = 50
GRID_HEIGHT = 20
DISPLAY_REFRESH_TIME = 0.05
PROGRAM_REFRESH_TIME = 1.7
PROGRAM_LENGTH = 300
NUMBER_OF_CHARACTERS = 126 - 33
CHECK_BORINGNESS_TIME = 0.2
BORING_CHARACTER_LIMIT = 78
MAX_SKIP = 100
CHECK_LOCS_TOUCHED_TIME = 0.2
MIN_LOCS_TOUCHED = 51
MAX_LOCS_TOUCHED = 300
locs_touched = {}
MORE_MOVEMENT = 3

CHARS = []
for i in range(NUMBER_OF_CHARACTERS):
    CHARS.append(ord('!') + i)


def reset_character_stats():
    global character_stats
    character_stats = {}
    for i in range(NUMBER_OF_CHARACTERS):
        character_stats[ord('!') + i] = 0


def most_used_character():
    global character_stats
    sorted_stats = list(reversed(sorted(character_stats.items(),
                                        key=lambda kv: kv[1])))
    return sorted_stats[0][0]
#    print(sorted_stats[0], file=sys.stderr)


def empty_grid():
    grid = []
    for y in range(GRID_HEIGHT):
        row = []
        for x in range(GRID_WIDTH):
            row.append(ord('!'))
        grid.append(row)
    return grid


def empty_world():
    world = {}
    world['grid'] = empty_grid()
    world['y'] = math.floor(GRID_HEIGHT / 2)
    world['x'] = math.floor(GRID_WIDTH / 2)
    world['skips'] = 0
    return world


INSTRUCTIONS = []


def char_put(world, char):
    loc_touched = (world['y'], world['x'])
    if loc_touched in locs_touched.keys():
        locs_touched[loc_touched] += 1
    else:
        locs_touched[loc_touched] = 1
    world['grid'][world['y']][world['x']] = char


def char_putter(char):
    return lambda world: char_put(world, char)


for char in CHARS:
    INSTRUCTIONS.append(char_putter(char))


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


def skip_if(world, char, skips):
    if world['grid'][world['y']][world['x']] == char:
        world['skips'] = skips


def skipper(char, skips):
    return lambda world: skip_if(world, char, skips)


for skips in range(MAX_SKIP):
    for char in CHARS:
        INSTRUCTIONS.append(skipper(char, skips))


def random_code():
    code = []
    for instruction in range(PROGRAM_LENGTH):
        code.append(random.choice(INSTRUCTIONS))
    return code


def random_program():
    program = {}
    for char in CHARS:
        program[char] = random_code()
    return program


def run_program(program, world):
    char_under_cursor = world['grid'][world['y']][world['x']]
    character_stats[char_under_cursor] += 1
#    print(character_stats, file=sys.stderr)
    code = program[char_under_cursor]
    for instruction in code:
        if world['skips'] > 0:
            world['skips'] -= 1
        else:
            instruction(world)


def main(stdscr):
    curses.curs_set(0)  # make cursor invisible
    stdscr.nodelay(1)  # don't wait for input when calling getch
    stdscr.clear()
    world = empty_world()
    gridmaxy = len(world['grid'])
    gridmaxx = len(world['grid'][0])
    display_refreshed = time.time()
    program = random_program()
    program_refreshed = time.time()
    boringness_checked = time.time()
    reset_character_stats()
    global locs_touched
    locs_touched = {}
    locs_touched_checked = time.time()
    while True:
        run_program(program, world)
        if time.time() > (program_refreshed + PROGRAM_REFRESH_TIME):
            program_refreshed = time.time()
            program[random.randint(0, len(program) - 1)] = random_code()
            reset_character_stats()
        if time.time() > (boringness_checked + CHECK_BORINGNESS_TIME):
            boringness_checked = time.time()
            boring_characters = 0
            for char in character_stats.items():
                if char[1] == 0:
                    boring_characters += 1
#            print("boring_characters: {}".format(boring_characters), file=sys.stderr)
            if boring_characters > BORING_CHARACTER_LIMIT:
                program[most_used_character()] = random_code()
                reset_character_stats()
        if time.time() > (locs_touched_checked + CHECK_LOCS_TOUCHED_TIME):
#            print("checking locs touched", file=sys.stderr)
            locs_touched_checked = time.time()
            if (len(locs_touched) < MIN_LOCS_TOUCHED or
                len(locs_touched) > MAX_LOCS_TOUCHED):
#                print("{}, boring".format(len(locs_touched)), file=sys.stderr)
                program[most_used_character()] = random_code()
                reset_character_stats()
#            else:
#                print("{}, interesting".format(len(locs_touched)), file=sys.stderr)
            locs_touched = {}
        if time.time() > (display_refreshed + DISPLAY_REFRESH_TIME):
            display_refreshed = time.time()
            (maxy, maxx) = stdscr.getmaxyx()
            for y in range(0, maxy):
                for x in range(0, maxx):
                    if (y == maxy - 1) and (x == maxx - 1):
                        pass  # don't trigger this curses bug
                    else:
#                        print(y, file=sys.stderr)
#                        print(x, file=sys.stderr)
                        char_to_put = world['grid'][y % gridmaxy][x % gridmaxx]
#                        print("char_to_put: {}".format(char_to_put), file=sys.stderr)
                        stdscr.addch(y, x, char_to_put)
            c = stdscr.getch()
            if c == ord('q'):
                break
#        time.sleep(0.0001)


if __name__ == "__main__":
    curses.wrapper(main)
