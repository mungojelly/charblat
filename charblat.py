import curses
import time
import random


REFRESH_TIME = 0.23
PAD_HEIGHT = 500
PAD_WIDTH = 700


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
    while True:
        if time.time() - time_refreshed > REFRESH_TIME:
            time_refreshed = time.time()
            (maxy, maxx) = stdscr.getmaxyx()
            if (column_direction == 1) and ((current_column + maxx) >= PAD_WIDTH):
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
        for i in range(1000):
            origin_y = random.randint(0, PAD_HEIGHT - 1)
            origin_x = random.randint(0, PAD_WIDTH - 1)
            target_y = twiddle(origin_y, 1, 0, PAD_HEIGHT - 1)
            target_x = twiddle(origin_x, 1, 0, PAD_WIDTH - 1)
            origin_char = pad.instr(origin_y, origin_x, 1)
            if (target_y == PAD_HEIGHT - 1) and (target_x == PAD_WIDTH - 1):
                pass  # don't trigger this curses bug
            else:
                pad.addch(target_y, target_x, origin_char)
        c = pad.getch()
        if c == ord('q'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
