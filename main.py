import asyncio
import curses
import random
import fire_animation
import curses_tools


async def blink(canvas, row, column, offset_tics, symbol):
    while True:
        for _ in range(offset_tics):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_DIM)
        for _ in range(20000):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3000):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol, curses.A_BOLD)
        for _ in range(5000):
            await asyncio.sleep(0)

        canvas.addstr(row, column, symbol)
        for _ in range(3000):
            await asyncio.sleep(0)


def get_rocket_frames(file):
    with open(file, "r") as my_file:
        file_content = my_file.read()
    return file_content


def run_spaceship(canvas, row, frame1, column, col_max, row_max):

    canvas.nodelay(True)
    rows_direction, columns_direction, _ = curses_tools.read_controls(canvas)
    frame_rows, frame_cols = curses_tools.get_frame_size(frame1)

    if row + rows_direction + frame_rows < row_max\
            and row + rows_direction - frame_rows > 0\
            and column + columns_direction + frame_cols < col_max\
            and column + columns_direction - frame_cols > 0:
        row += rows_direction
        column += columns_direction

    return row, column


async def animate_spaceship(canvas, row, column, frame1, frame2, col_max, row_max):
    while True:

        curses_tools.draw_frame(canvas, row, column, frame1)
        for _ in range(5000):
            await asyncio.sleep(0)

        curses_tools.draw_frame(canvas, row, column, frame1, negative=True)
        await asyncio.sleep(0)

        curses_tools.draw_frame(canvas, row, column, frame2)
        for _ in range(5000):
            await asyncio.sleep(0)

        curses_tools.draw_frame(canvas, row, column, frame2, negative=True)
        await asyncio.sleep(0)

        row, column = run_spaceship(canvas, row, frame1, column, col_max, row_max)


def main(canvas):
    row_max, col_max = canvas.getmaxyx()
    row, column = row_max/2, col_max/2
    stars = ('+', '*', '.', ':')
    frame1 = get_rocket_frames('rocket_frame_1.txt')
    frame2 = get_rocket_frames('rocket_frame_2.txt')
    coroutines = [
        fire_animation.fire(canvas, row, column+2, rows_speed=-0.003),
        animate_spaceship(canvas, row, column, frame1, frame2, col_max, row_max)
    ]
    for star in range(50):
        coroutines.append(blink(
            canvas, random.randint(1, row_max-2),
            random.randint(1, col_max-2),
            random.randint(1, 10000),
            symbol=random.choice(stars)

        ))
    canvas.border()
    curses.curs_set(False)
    while True:

        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        canvas.refresh()


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
