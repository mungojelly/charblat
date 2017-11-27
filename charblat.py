import curses
import time
import random


REFRESH_TIME = 0.25
DRIFT_TIME = 1
PROGRAM_CHANGE_TIME = 7
PAD_HEIGHT = 150
PAD_WIDTH = 250
INITIAL_ENERGY = 600
PROGRAM_LENGTH = 50
MAX_STACK_LENGTH = 30


instructions = ['up', 'down', 'left', 'right',
                'put_a', 'put_b', 'put_c',
                'push', 'pop',
                'skip_if_c',
                'shuffle_stack',
                'turn_a_to_d',
                'check_if_stack',
                'skip_ten_if_g',
                'up_unless_e',
                'left_unless_e',
                'empty_stack',
                'double_stack',
                ]


def random_program():
    program = []
    for instruction in range(PROGRAM_LENGTH):
        program.append(random.choice(instructions))
    return program


def run_instruction(program, current_instruction, pad, y, x, energy, stack):
    if current_instruction >= len(program):
        return (y, x, 0, stack)
    instruction = program[current_instruction]
    if instruction == 'up':
        new_y = y - 1
        if new_y < 0:
            new_y = PAD_HEIGHT - 2
        return (new_y, x, current_instruction + 1, stack)
    if instruction == 'down':
        new_y = y + 1
        if new_y > PAD_HEIGHT - 2:
            new_y = 0
        return (new_y, x, current_instruction + 1, stack)
    if instruction == 'left':
        new_x = x - 1
        if new_x < 0:
            new_x = PAD_WIDTH - 2
        return (y, new_x, current_instruction + 1, stack)
    if instruction == 'right':
        new_x = x + 1
        if new_x > PAD_WIDTH - 2:
            new_x = 0
        return (y, new_x, current_instruction + 1, stack)
    if instruction == 'put_a':
        pad.addch(y, x, ord('a'))
        return (y, x, current_instruction + 1, stack)
    if instruction == 'put_b':
        pad.addch(y, x, ord('b'))
        return (y, x, current_instruction + 1, stack)
    if instruction == 'put_c':
        pad.addch(y, x, ord('c'))
        return (y, x, current_instruction + 1, stack)
    if instruction == 'put_e':
        pad.addch(y, x, ord('e'))
        return (y, x, current_instruction + 1, stack)
    if instruction == 'push':
        if len(stack) >= MAX_STACK_LENGTH:
            return (y, x, current_instruction + 1, stack)
        return (y, x, current_instruction + 1, stack + [(y, x)])
    if instruction == 'pop':
        if len(stack) == 0:
            return (y, x, current_instruction + 1, stack)
        (new_y, new_x) = stack.pop()
        return (new_y, new_x, current_instruction + 1, stack)
    if instruction == 'skip_if_c':
        if pad.instr(y, x, 1) == b'c':
            return (y, x, current_instruction + 2, stack)
        return (y, x, current_instruction + 1, stack)
    if instruction == 'shuffle_stack':
        random.shuffle(stack)
        return (y, x, current_instruction + 1, stack)
    if instruction == 'turn_a_to_d':
        if pad.instr(y, x, 1) == b'a':
            pad.addch(y, x, ord('d'))
        return (y, x, current_instruction + 1, stack)
    if instruction == 'restart_if_e':
        if pad.instr(y, x, 1) == b'e':
            return (y, x, 0, stack)
        return (y, x, current_instruction + 1, stack)
    if instruction == 'check_if_stack':
        if len(stack) == 0:
            pad.addch(y, x, ord('f'))
        else:
            pad.addch(y, x, ord('g'))
        return (y, x, current_instruction + 1, stack)
    if instruction == 'skip_ten_if_g':
        if pad.instr(y, x, 1) == b'g':
            return (y, x, current_instruction + 11, stack)
        return (y, x, current_instruction + 1, stack)
    if instruction == 'up_unless_e':
        if pad.instr(y, x, 1) == b'e':
            return (y, x, current_instruction + 1, stack)
        new_y = y - 1
        if new_y < 0:
            new_y = PAD_HEIGHT - 2
        return (new_y, x, current_instruction + 1, stack)
    if instruction == 'left_unless_e':
        if pad.instr(y, x, 1) == b'e':
            return (y, x, current_instruction + 1, stack)
        new_x = x - 1
        if new_x < 0:
            new_x = PAD_WIDTH - 2
        return (y, new_x, current_instruction + 1, stack)
    if instruction == 'empty_stack':
        return (y, x, current_instruction + 1, [])
    if instruction == 'double_stack':
        new_stack = stack + stack
        while len(new_stack) > MAX_STACK_LENGTH:
            new_stack.pop()
        return (y, x, current_instruction + 1, new_stack)


def run_program(program, pad, y, x, current_instruction, energy, stack):
    if energy == 0:
        return True
    (new_y, new_x, next_instruction, stack) = run_instruction(program,
                                                              current_instruction,
                                                              pad,
                                                              y,
                                                              x,
                                                              energy,
                                                              stack)
    run_program(program, pad, new_y, new_x, next_instruction, energy - 1, stack)


def twiddle(original, amount, minimum, maximum):
    twiddled = original + random.randint(0 - amount, amount)
    if twiddled < minimum:
        twiddled = minimum
    if twiddled > maximum:
        twiddled = maximum
    return twiddled


def main(stdscr):
    curses.curs_set(0)  # make cursor invisible
    stdscr.nodelay(1)  # don't wait for input when calling getch
    stdscr.clear()
    pad = curses.newpad(PAD_HEIGHT, PAD_WIDTH)
    pad.nodelay(1)
    for y in range(0, PAD_HEIGHT):
        for x in range(0, PAD_WIDTH):
            if (y == PAD_HEIGHT - 1) and (x == PAD_WIDTH - 1):
                pass  # don't trigger this curses bug
            else:
                pad.addch(y, x, ord('a') + (x*x+y*y) % 26)
    current_column = 0
    column_direction = 1
    current_row = 0
    row_direction = 1
    time_refreshed = time.time()
    time_drifted = time.time()
    current_program = random_program()
    time_changed_program = time.time()
    while True:
        if time.time() - time_changed_program > PROGRAM_CHANGE_TIME:
            time_changed_program = time.time()
            current_program = random_program()
        if time.time() - time_refreshed > REFRESH_TIME:
            time_refreshed = time.time()
            (maxy, maxx) = stdscr.getmaxyx()
            pad.refresh(current_row, current_column, 0, 0, maxy - 1, maxx - 1)
        if time.time() - time_drifted > DRIFT_TIME:
            time_drifted = time.time()
            (maxy, maxx) = stdscr.getmaxyx()
            if (column_direction == 1) and ((current_column + maxx)
                                            >= PAD_WIDTH):
                column_direction = 0 - column_direction
            if (column_direction == -1) and (current_column == 0):
                column_direction = 0 - column_direction
            current_column = current_column + column_direction
            if (row_direction == 1) and ((current_row + maxy) >= PAD_HEIGHT):
                row_direction = 0 - row_direction
            if (row_direction == -1) and (current_row == 0):
                row_direction = 0 - row_direction
            current_row = current_row + row_direction
            pad.refresh(current_row, current_column, 0, 0, maxy - 1, maxx - 1)
        run_program(current_program,
                    pad,
                    random.randint(0, PAD_HEIGHT - 2),
                    random.randint(0, PAD_WIDTH - 2),
                    0,
                    INITIAL_ENERGY,
                    [])
        c = pad.getch()
        if c == ord('q'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
