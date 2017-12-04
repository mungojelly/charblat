import curses
import math
import time
import random
import sys


GRID_WIDTH = 100
GRID_HEIGHT = 30
DISPLAY_REFRESH_TIME = 0.05
DISPLAY_REFRESH_VARIABILITY = 0.02
PROGRAM_REFRESH_TIME = 5
PROGRAM_LENGTH = 150
NUMBER_OF_CHARACTERS = 126 - 33
CHECK_BORINGNESS_TIME = 0.5
BORING_CHARACTER_LIMIT = 87
MAX_SKIP = 10
CHECK_LOCS_TOUCHED_TIME = 0.2
MIN_LOCS_TOUCHED = 101
MAX_LOCS_TOUCHED = 2000
locs_touched = {}
MORE_MOVEMENT = 10
MORE_WRITING = 10
CENTERINESS = 0
JUMPINESS = 0
CHAR_STACK_MAX_DEPTH = 100
READINGNESS = 2000
WRITINGNESS = 2000
MORE_SPACES = 500
INITIAL_MAX_MOVES = 5
STACK_SWAPPINESS = 50
SAMENESS_SAMPLE_SIZE = 200
SAMENESS_SAMPLE_TIME = 0.5
GLITCH_CHANCE = 1000
MOVE_UNLESSES = 2
LOC_STACK_MAX_DEPTH = 200
REMEMBERINESS = 50
RECALLINESS = 50

CHARS = []
for i in range(NUMBER_OF_CHARACTERS):
    CHARS.append(ord(' ') + i)


def reset_character_stats():
    global character_stats
    character_stats = {}
    for i in range(NUMBER_OF_CHARACTERS):
        character_stats[ord(' ') + i] = 0


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
            row.append(ord(' '))
        grid.append(row)
    return grid


def empty_world():
    world = {}
    world['grid'] = empty_grid()
    world['y'] = math.floor(GRID_HEIGHT / 2)
    world['x'] = math.floor(GRID_WIDTH / 2)
    world['skips'] = 0
    world['char stack'] = []
    world['max moves'] = INITIAL_MAX_MOVES
    world['loc stack'] = []
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


for _ in range(MORE_WRITING):
    for char in CHARS:
        INSTRUCTIONS.append(char_putter(char))


for _ in range(MORE_SPACES):
    INSTRUCTIONS.append(char_putter(ord(' ')))


def north(world):
    if world['max moves'] > 0:
        world['max moves'] -= 1
        world['y'] -= 1
        if world['y'] < 0:
            world['y'] = GRID_HEIGHT - 1


def south(world):
    if world['max moves'] > 0:
        world['max moves'] -= 1
        world['y'] += 1
        if world['y'] > GRID_HEIGHT - 1:
            world['y'] = 0


def west(world):
    if world['max moves'] > 0:
        world['max moves'] -= 1
        world['x'] -= 1
        if world['x'] < 0:
            world['x'] = GRID_WIDTH - 1


def east(world):
    if world['max moves'] > 0:
        world['max moves'] -= 1
        world['x'] += 1
        if world['x'] > GRID_WIDTH - 1:
            world['x'] = 0


for _ in range(MORE_MOVEMENT):
    INSTRUCTIONS.append(north)
    INSTRUCTIONS.append(south)
    INSTRUCTIONS.append(east)
    INSTRUCTIONS.append(west)


def north_unless(world, char):
    target_y = world['y'] - 1
    if target_y < 0:
        target_y = GRID_HEIGHT - 1
    target_x = world['x']
    if world['grid'][target_y][target_x] == char:
        pass
    else:
        north(world)


def south_unless(world, char):
    target_y = world['y'] + 1
    if target_y > GRID_HEIGHT - 1:
        target_y = 0
    target_x = world['x']
    if world['grid'][target_y][target_x] == char:
        pass
    else:
        south(world)


def east_unless(world, char):
    target_x = world['x'] + 1
    if target_x > GRID_WIDTH - 1:
        target_x = 0
    target_y = world['y']
    if world['grid'][target_y][target_x] == char:
        pass
    else:
        east(world)


def west_unless(world, char):
    target_x = world['x'] - 1
    if target_x < 0:
        target_x = GRID_WIDTH - 1
    target_y = world['y']
    if world['grid'][target_y][target_x] == char:
        pass
    else:
        west(world)


for _ in range(MOVE_UNLESSES):
    for char in CHARS:
        INSTRUCTIONS.append(lambda world: north_unless(world, char))
        INSTRUCTIONS.append(lambda world: south_unless(world, char))
        INSTRUCTIONS.append(lambda world: east_unless(world, char))
        INSTRUCTIONS.append(lambda world: west_unless(world, char))


def slightly_towards_center(world):
    vertical_center = math.floor(GRID_HEIGHT / 2)
    horizontal_center = math.floor(GRID_WIDTH / 2)
    vertical_average = (vertical_center + (world['y'] * 3)) / 4
    horizontal_average = (horizontal_center + (world['x'] * 3)) / 4
    world['y'] = math.floor(vertical_average)
    world['x'] = math.floor(horizontal_average)


for _ in range(CENTERINESS):
    INSTRUCTIONS.append(slightly_towards_center)


def random_jump(world):
    if world['max moves'] > 0:
        world['max moves'] -= 1
        world['y'] = random.randint(0, GRID_HEIGHT - 1)
        world['x'] = random.randint(0, GRID_WIDTH - 1)


for _ in range(JUMPINESS):
    INSTRUCTIONS.append(random_jump)


def skip_if(world, char, skips):
    if world['grid'][world['y']][world['x']] == char:
        world['skips'] = skips


def skipper(char, skips):
    return lambda world: skip_if(world, char, skips)


for skips in range(MAX_SKIP):
    for char in CHARS:
        INSTRUCTIONS.append(skipper(char, skips))


def read_char(world):
    world['char stack'].append(world['grid'][world['y']][world['x']])
    while len(world['char stack']) > CHAR_STACK_MAX_DEPTH:
        world['char stack'] = world['char stack'][1:]


for _ in range(READINGNESS):
    INSTRUCTIONS.append(read_char)


def write_char(world):
    if len(world['char stack']) == 0:
        pass
    else:
        world['grid'][world['y']][world['x']] = world['char stack'].pop()


for _ in range(WRITINGNESS):
    INSTRUCTIONS.append(write_char)


def remember_loc(world):
    world['loc stack'].append((world['y'], world['x']))
    while len(world['loc stack']) > LOC_STACK_MAX_DEPTH:
        world['loc stack'] = world['loc stack'][1:]


for _ in range(REMEMBERINESS):
    INSTRUCTIONS.append(remember_loc)


def recall_loc(world):
    if len(world['loc stack']) == 0:
        pass
    else:
        new_loc = world['loc stack'].pop()
        world['y'] = new_loc[0]
        world['x'] = new_loc[1]


for _ in range(RECALLINESS):
    INSTRUCTIONS.append(recall_loc)


def swap_top_two_char_stack(world):
    if len(world['char stack']) > 1:
        first = world['char stack'].pop()
        second = world['char stack'].pop()
        world['char stack'].append(first)
        world['char stack'].append(second)


for _ in range(STACK_SWAPPINESS):
    INSTRUCTIONS.append(swap_top_two_char_stack)


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
    world['max moves'] = INITIAL_MAX_MOVES
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
    refresh_display = time.time()
    program = random_program()
    program_refreshed = time.time()
    boringness_checked = time.time()
    reset_character_stats()
    global locs_touched
    locs_touched = {}
    locs_touched_checked = time.time()
    sameness_sampled = time.time()
    sameness_sample = {}
    while True:
        if random.randint(0, GLITCH_CHANCE) == 0:
            glitcher = random.choice(INSTRUCTIONS)
            glitcher(world)
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
        if time.time() > (sameness_sampled + SAMENESS_SAMPLE_TIME):
            sameness_sampled = time.time()
            sameness = True
            for sample in sameness_sample.keys():
                if world['grid'][sample[0]][sample[1]] != sameness_sample[sample]:
                    sameness = False
#            print(sameness, file=sys.stderr)
            if sameness:
                program[most_used_character()] = random_code()
                reset_character_stats()
            sameness_sample = {}
            for sample in range(SAMENESS_SAMPLE_SIZE):
                target = (random.randint(0, GRID_HEIGHT - 1),
                          random.randint(0, GRID_WIDTH - 1))
                sameness_sample[target] = world['grid'][target[0]][target[1]]
        if time.time() > refresh_display:
            refresh_display = time.time() + DISPLAY_REFRESH_TIME + \
                              (random.random() * DISPLAY_REFRESH_VARIABILITY)
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
