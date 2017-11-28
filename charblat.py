import curses
import random


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
    while True:
        (maxy, maxx) = stdscr.getmaxyx()
        for y in range(0, maxy):
            for x in range(0, maxx):
                if (y == maxy - 1) and (x == maxx - 1):
                    pass  # don't trigger this curses bug
                else:
                    stdscr.addch(y, x, ord('a') + (x*x+y*y) % 26)
        c = stdscr.getch()
        if c == ord('q'):
            break


if __name__ == "__main__":
    curses.wrapper(main)
