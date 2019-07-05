import asyncio
import curses
import random
import fire_animation
import curses_tools
import time
from space_garbage import fly_garbage


TIC_TIMEOUT = .1


async def sleep(tics):
    for _ in range(int(tics)):
        await asyncio.sleep(0)


async def blink(canvas, row, column, offset_tics, symbol):
    while True:
        await sleep(offset_tics)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        await sleep(2)

        canvas.addstr(row, column, symbol)
        await sleep(.3)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        await sleep(.5)

        canvas.addstr(row, column, symbol)
        await sleep(.3)


def get_frame(file):
    with open(file, "r") as my_file:
        file_content = my_file.read()
    return file_content


def run_spaceship(canvas, row, frame1, column, col_max, row_max):
    border = 1
    rows_direction, columns_direction, _ = curses_tools.read_controls(canvas)
    frame_rows, frame_cols = curses_tools.get_frame_size(frame1)

    if row + rows_direction + frame_rows >= row_max:
        row = row_max - frame_rows - border
    elif row + rows_direction <= 0:
        row = border
    else:
        row += rows_direction

    if column + columns_direction + frame_cols >= col_max:
        column = col_max - frame_cols - border
    elif column + columns_direction <= 0:
        column = border
    else:
        column += columns_direction

    return row, column


async def animate_spaceship(canvas, row, column, frame1, frame2, col_max, row_max):
    while True:

        curses_tools.draw_frame(canvas, row, column, frame1)
        await sleep(2)

        curses_tools.draw_frame(canvas, row, column, frame1, negative=True)

        curses_tools.draw_frame(canvas, row, column, frame2)
        await sleep(1)

        curses_tools.draw_frame(canvas, row, column, frame2, negative=True)

        row, column = run_spaceship(canvas, row, frame1, column, col_max, row_max)


def main(canvas):
    row_max, col_max = canvas.getmaxyx()
    row, column = row_max/2, col_max/2
    stars = ('+', '*', '.', ':')
    rocket_frame1 = get_frame('rocket_frame_1.txt')
    rocket_frame2 = get_frame('rocket_frame_2.txt')
    garbage_frame = get_frame('hubble.txt')
    coroutines = [
        fire_animation.fire(canvas, row, column+2, rows_speed=-0.3),
        animate_spaceship(canvas, row, column, rocket_frame1, rocket_frame2, col_max, row_max),
        fly_garbage(canvas, 10, garbage_frame)
    ]
    for star in range(50):
        coroutines.append(blink(
            canvas, random.randint(1, row_max-2),
            random.randint(1, col_max-2),
            random.randint(1, 10),
            symbol=random.choice(stars)
        ))
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    while True:

        for coroutine in coroutines:
            try:
                coroutine.send(None)

            except StopIteration:
                coroutines.remove(coroutine)

        canvas.refresh()
        canvas.border()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
