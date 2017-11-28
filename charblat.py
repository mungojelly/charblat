import curses
import time
import random
import copy


REFRESH_TIME = 0.25
DRIFT_TIME = 1
PROGRAM_CHANGE_TIME = 15
PAD_HEIGHT = 200
PAD_WIDTH = 500
INITIAL_ENERGY = 60000
LOW_ENERGY = 6000
PROGRAM_LENGTH = 52
MAX_STACK_LENGTH = 50
MAX_INSTRUCTION_STACK_LENGTH = 20
MAX_XY_STACK_LENGTH = 250
MAX_CONTEXT_STACK_LENGTH = 120


all_instructions = ['up', 'down', 'left', 'right',
                    'put_a', 'put_b', 'put_c', 'put_e', 'put_i',
                    'put_k', 'put_l', 'put_m',
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
                    'h_if_low_energy',
                    'skip_eight_if_h',
                    'push_instruction',
                    'pop_instruction',
                    'pop_instruction_if_j',
                    'i_to_j',
                    'shuffle_instruction_stack',
                    'move',
                    'go_up', 'go_down', 'go_left', 'go_right',
                    'k_up_l_down',
                    'increase_counter',
                    'decrease_counter',
                    'pop_instruction_if_counter_zero',
                    'reset_counter',
                    'move_if_m',
                    'remember_x', 'recall_x',
                    'remember_y', 'recall_y',
                    'push_x_stack',
                    'push_y_stack',
                    'pop_x_stack',
                    'pop_y_stack',
                    'push_context',
                    'pop_context',
                    'move_countdown',
]

distributions = [
    ['up', 'up', 'down', 'down',
     'left', 'left', 'left', 'left',
     'right', 'right', 'right', 'right',
     'h_if_low_energy', 'skip_eight_if_h',
     'put_a',
    ],
    ['increase_counter', 'decrease_counter',
     'pop_instruction_if_counter_zero',
     'push_instruction', 'reset_counter',
     'put_c', 'skip_if_c',
     'put_i', 'i_to_j',
     'pop_instruction_if_j',
     'move', 'move', 'move',
     'go_up', 'go_down',
     'go_left', 'go_right',
    ],
    ['move','move','go_left','go_right','up','down','push_context','pop_context',
     'put_a', 'put_m', 'move_if_m', 'put_i', 'i_to_j', 'put_c', 'skip_if_c',
     'h_if_low_energy', 'skip_eight_if_h', 'move_countdown', 'increase_counter',
    ]
]





def random_program():
    distribution = random.choice(distributions)
    # distribution = all_instructions
    program = []
    for instruction in range(PROGRAM_LENGTH):
        program.append(random.choice(distribution))
    return program


def run_instruction(program, pad, context, energy):
    if context.current_instruction >= len(program):
        context.current_instruction = 0
        return context
    instruction = program[context.current_instruction]
    contents = pad.instr(context.y, context.x, 1)
    if instruction == 'up':
        new_y = context.y - 1
        if new_y < 0:
            new_y = PAD_HEIGHT - 2
        context.y = new_y
    if instruction == 'down':
        new_y = context.y + 1
        if new_y > PAD_HEIGHT - 2:
            new_y = 0
        context.y = new_y
    if instruction == 'left':
        new_x = context.x - 1
        if new_x < 0:
            new_x = PAD_WIDTH - 2
        context.x = new_x
    if instruction == 'right':
        new_x = context.x + 1
        if new_x > PAD_WIDTH - 2:
            new_x = 0
        context.x = new_x
    if instruction == 'put_a':
        pad.addch(context.y, context.x, ord('a'))
    if instruction == 'put_b':
        pad.addch(context.y, context.x, ord('b'))
    if instruction == 'put_c':
        pad.addch(context.y, context.x, ord('c'))
    if instruction == 'put_e':
        pad.addch(context.y, context.x, ord('e'))
    if instruction == 'put_i':
        pad.addch(context.y, context.x, ord('i'))
    if instruction == 'put_k':
        pad.addch(context.y, context.x, ord('k'))
    if instruction == 'put_l':
        pad.addch(context.y, context.x, ord('l'))
    if instruction == 'put_m':
        pad.addch(context.y, context.x, ord('m'))
    if instruction == 'push':
        if len(context.stack) >= MAX_STACK_LENGTH:
            pass
        else:
            context.stack = context.stack + [(context.y, context.x)]
    if instruction == 'pop':
        if len(context.stack) == 0:
            pass
        else:
            (context.y, context.x) = context.stack.pop()
    if instruction == 'skip_if_c':
        if contents == b'c':
            context.current_instruction += 1
    if instruction == 'shuffle_stack':
        random.shuffle(context.stack)
    if instruction == 'turn_a_to_d':
        if contents == b'a':
            pad.addch(context.y, context.x, ord('d'))
    if instruction == 'restart_if_e':
        if contents == b'e':
            context.current_instruction = -1
    if instruction == 'check_if_stack':
        if len(context.stack) == 0:
            pad.addch(context.y, context.x, ord('f'))
        else:
            pad.addch(context.y, context.x, ord('g'))
    if instruction == 'skip_ten_if_g':
        if contents == b'g':
            context.current_instruction += 10
    if instruction == 'up_unless_e':
        if contents == b'e':
            pass
        else:
            new_y = context.y - 1
            if new_y < 0:
                new_y = PAD_HEIGHT - 2
            context.y = new_y
    if instruction == 'left_unless_e':
        if contents == b'e':
            pass
        else:
            new_x = context.x - 1
            if new_x < 0:
                new_x = PAD_WIDTH - 2
            context.x = new_x
    if instruction == 'empty_stack':
        context.stack = []
    if instruction == 'double_stack':
        context.stack = context.stack + context.stack
        while len(context.stack) > MAX_STACK_LENGTH:
            context.stack.pop()
    if instruction == 'h_if_low_energy':
        if energy < LOW_ENERGY:
            pad.addch(context.y, context.x, ord('h'))
    if instruction == 'skip_eight_if_h':
        if contents == b'h':
            context.current_instruction += 8
    if instruction == 'push_instruction':
        if len(context.instruction_stack) >= MAX_INSTRUCTION_STACK_LENGTH:
            pass
        else:
            context.instruction_stack = context.instruction_stack + \
                                        [context.current_instruction]
    if instruction == 'pop_instruction':
        if len(context.instruction_stack) == 0:
            pass
        else:
            context.current_instruction = context.instruction_stack.pop()
    if instruction == 'pop_instruction_if_j':
        if len(context.instruction_stack) == 0:
            pass
        elif contents != b'j':
            pass
        else:
            context.current_instruction = context.instruction_stack.pop()
    if instruction == 'i_to_j':
        if contents == b'i':
            pad.addch(context.y, context.x, ord('j'))
    if instruction == 'shuffle_instruction_stack':
        random.shuffle(context.instruction_stack)
    if instruction == 'move':
        if context.direction == 'up':
            new_y = context.y - 1
            if new_y < 0:
                new_y = PAD_HEIGHT - 2
            context.y = new_y
        if context.direction == 'down':
            new_y = context.y + 1
            if new_y > PAD_HEIGHT - 2:
                new_y = 0
            context.y = new_y
        if context.direction == 'left':
            new_x = context.x - 1
            if new_x < 0:
                new_x = PAD_WIDTH - 2
            context.x = new_x
        if context.direction == 'right':
            new_x = context.x + 1
            if new_x > PAD_WIDTH - 2:
                new_x = 0
            context.x = new_x
    if instruction == 'move_if_m':
        if contents == b'm':
            if context.direction == 'up':
                new_y = context.y - 1
                if new_y < 0:
                    new_y = PAD_HEIGHT - 2
                context.y = new_y
            if context.direction == 'down':
                new_y = context.y + 1
                if new_y > PAD_HEIGHT - 2:
                    new_y = 0
                context.y = new_y
            if context.direction == 'left':
                new_x = context.x - 1
                if new_x < 0:
                    new_x = PAD_WIDTH - 2
                context.x = new_x
            if context.direction == 'right':
                new_x = context.x + 1
                if new_x > PAD_WIDTH - 2:
                    new_x = 0
                context.x = new_x
    if instruction == 'move_countdown':
        context.counter -= 1
        if context.counter < 0:
            context.counter = 0
        else:
            if context.direction == 'up':
                new_y = context.y - 1
                if new_y < 0:
                    new_y = PAD_HEIGHT - 2
                context.y = new_y
            if context.direction == 'down':
                new_y = context.y + 1
                if new_y > PAD_HEIGHT - 2:
                    new_y = 0
                context.y = new_y
            if context.direction == 'left':
                new_x = context.x - 1
                if new_x < 0:
                    new_x = PAD_WIDTH - 2
                context.x = new_x
            if context.direction == 'right':
                new_x = context.x + 1
                if new_x > PAD_WIDTH - 2:
                    new_x = 0
                context.x = new_x
    if instruction == 'go_up':
        context.direction = 'up'
    if instruction == 'go_down':
        context.direction = 'down'
    if instruction == 'go_left':
        context.direction = 'left'
    if instruction == 'go_right':
        context.direction = 'right'
    if instruction == 'k_up_l_down':
        if contents == b'k':
            context.direction = 'up'
        if contents == b'l':
            context.direction = 'down'
    if instruction == 'increase_counter':
        context.counter += 1
    if instruction == 'decrease_counter':
        context.counter -= 1
        if context.counter < 0:
            context.counter = 0
    if instruction == 'pop_instruction_if_counter_zero':
        if len(context.instruction_stack) == 0:
            pass
        elif context.counter != 0:
            pass
        else:
            context.current_instruction = context.instruction_stack.pop()
    if instruction == 'reset_counter':
        context.counter = 0
    if instruction == 'remember_x':
        context.remembered_x = context.x
    if instruction == 'recall_x':
        context.x = context.remembered_x
        if (context.y == PAD_HEIGHT - 1) and (context.x == PAD_WIDTH - 1):
            context.y = 0
            context.x = 0
            # don't trigger this curses bug
    if instruction == 'remember_y':
        context.remembered_y = context.y
    if instruction == 'recall_y':
        context.y = context.remembered_y
        if (context.y == PAD_HEIGHT - 1) and (context.x == PAD_WIDTH - 1):
            context.y = 0
            context.x = 0
            # don't trigger this curses bug
    if instruction == 'push_x_stack':
        if len(context.x_stack) >= MAX_XY_STACK_LENGTH:
            pass
        else:
            context.x_stack = context.x_stack + [context.x]
    if instruction == 'push_y_stack':
        if len(context.y_stack) >= MAX_XY_STACK_LENGTH:
            pass
        else:
            context.y_stack = context.y_stack + [context.y]
    if instruction == 'pop_x_stack':
        if len(context.x_stack) == 0:
            pass
        else:
            context.x = context.x_stack.pop()
    if instruction == 'pop_y_stack':
        if len(context.y_stack) == 0:
            pass
        else:
            context.x = context.y_stack.pop()
    if instruction == 'push_context':
        if len(context.context_stack) >= MAX_CONTEXT_STACK_LENGTH:
            pass
        else:
            context.context_stack = context.context_stack + [copy.deepcopy(context)]  # lol
    if instruction == 'pop_context':
        if len(context.context_stack) == 0:
            pass
        else:
            context = context.context_stack.pop()
    context.current_instruction += 1
    return context


def run_program(program, pad, context, energy):
    while energy > 0:
        energy = energy - 1
        context = run_instruction(program, pad, context, energy)


def twiddle(original, amount, minimum, maximum):
    twiddled = original + random.randint(0 - amount, amount)
    if twiddled < minimum:
        twiddled = minimum
    if twiddled > maximum:
        twiddled = maximum
    return twiddled


class Context(object):
    pass


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
        context = Context()
        context.y = random.randint(0, PAD_HEIGHT - 2)
        context.x = random.randint(0, PAD_WIDTH - 2)
        context.remembered_y = y
        context.remembered_x = x
        context.stack = []
        context.current_instruction = random.randint(0, len(current_program))
        context.instruction_stack = []
        context.direction = 'right'
        context.counter = 0
        context.x_stack = []
        context.y_stack = []
        context.context_stack = []
        run_program(current_program,
                    pad,
                    context,
                    INITIAL_ENERGY)
        c = pad.getch()
        if c == ord('q'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
