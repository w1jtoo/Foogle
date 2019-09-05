from ctypes.wintypes import SMALL_RECT
from ctypes import windll, byref
import curses
import curses.ascii
import cmd

# TODO construct the app sketch (only the methods and funcs)

curses.initscr()
win = curses.newwin(30, 50, 0, 0)
curses.noecho()


def fill_in_the_background():
    for y in range(0, 29):
        for x in range(0, 49):
            win.addch(y, x, 176)


def get_console_size() -> (int, int):
    # cmd.Cmd.
    # return
    pass


# control cmd size

STDOUT = -11

hdl = windll.kernel32.GetStdHandle(STDOUT)
rect = SMALL_RECT(0, 50, 50, 80)  # (left, top, right, bottom)
windll.kernel32.SetConsoleWindowInfo(hdl, True, byref(rect))
# end

result = ''
curses.start_color()
curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_BLUE)
win.bkgd(' ', curses.color_pair(1))

while 1:
    fill_in_the_background()
    pressed_char = win.getch()

    # TODO find the soluions

    if pressed_char == 17:  # 17 is a number of ctrl + Q
        break
    elif pressed_char == 8:  # 8 is a number of BACKSPACE
        win.delch()
    elif pressed_char == 9:  # 9 is a number of TAB
        draw_the_words()
    else:
        if not chr(pressed_char).isprintable():
            continue
        result += chr(pressed_char)
        win.addch(pressed_char)

print(result)


def draw_the_words():
    pass
