import curses
import time
import random


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
    while True:
        current_column = current_column + 1
        if current_column > 900:
            current_column = 100
        (maxy, maxx) = stdscr.getmaxyx()
        pad.refresh(current_column, 0, 0, 0, maxy - 1, maxx - 1)
        for i in range(100000):
            origin_y = random.randint(0, 999)
            origin_x = random.randint(0, 999)
            target_y = origin_y + random.randint(-1, 1)
            if target_y == -1:
                target_y = 999
            if target_y == 1000:
                target_y = 0
            target_x = origin_x + random.randint(-1, 1)
            if target_x == -1:
                target_x = 999
            if target_x == 1000:
                target_x = 0
            origin_char = pad.instr(origin_y, origin_x, 1)
            if (target_y == 999) and (target_x == 999):
                pass  # don't trigger this curses bug
            else:
                pad.addch(target_y, target_x, origin_char)
        time.sleep(0.1)
        c = pad.getch()
        if c == ord('q'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
