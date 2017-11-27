import curses


def main(stdscr):
    curses.curs_set(0)  # make cursor invisible
    stdscr.nodelay(1)  # don't wait for input when calling getch
    stdscr.clear()
    while True:
        c = stdscr.getch()
        if c != -1:
            break  # quit on any keypress


if __name__ == "__main__":
    curses.wrapper(main)
