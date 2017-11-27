import curses
import time
import random


REFRESH_TIME = 0.17


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
    pad = curses.newpad(1000, 1000)
    pad.nodelay(1)
    for y in range(0, 999):
        for x in range(0, 999):
            pad.addch(y, x, ord('a') + (x*x+y*y) % 26)
    current_column = 100
    time_refreshed = time.time()
    while True:
        if time.time() - time_refreshed > REFRESH_TIME:
            time_refreshed = time.time()
            current_column = current_column + 1
            if current_column > 900:
                current_column = 100
            (maxy, maxx) = stdscr.getmaxyx()
            pad.refresh(current_column, 0, 0, 0, maxy - 1, maxx - 1)
        for i in range(1000):
            origin_y = random.randint(0, 999)
            origin_x = random.randint(0, 999)
            target_y = twiddle(origin_y, 1, 0, 999)
            target_x = twiddle(origin_x, 1, 0, 999)
            origin_char = pad.instr(origin_y, origin_x, 1)
            if (target_y == 999) and (target_x == 999):
                pass  # don't trigger this curses bug
            else:
                pad.addch(target_y, target_x, origin_char)
        c = pad.getch()
        if c == ord('q'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
