import asyncio
import curses
import random
import fire_animation
import curses_tools
import time
from space_garbage import obstacles, obstacles_in_last_collisions, fill_orbit_with_garbage, show_message
from config import TIC_TIMEOUT
from physics import update_speed
from explosion import explode
from game_scenario import PHRASES, show_gameover
from globs import coroutines, year
from auxiliary import get_frames, sleep


spaceship_frame = get_frames('rocket')[0]
gameover_frame = get_frames('gameover')[0]


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


async def run_spaceship(canvas, row, column, col_max, row_max):
    border = 1
    frame_rows, frame_cols = curses_tools.get_frame_size(spaceship_frame)
    row_speed = column_speed = 0
    while True:
        rows_direction, columns_direction, space = curses_tools.read_controls(canvas)
        row_speed, column_speed = update_speed(
            row_speed,
            column_speed,
            rows_direction,
            columns_direction
        )

        if row + row_speed + frame_rows >= row_max:
            row = row_max - frame_rows - border
        elif row + row_speed <= 0:
            row = border
        else:
            row += row_speed

        if column + column_speed + frame_cols >= col_max:
            column = col_max - frame_cols - border
        elif column + column_speed <= 0:
            column = border
        else:
            column += column_speed

        if space and year >= 2020:
            coroutines.append(fire_animation.fire(canvas, row, column+2))

        for obstacle in obstacles:
            if obstacle.has_collision(row, column):
                await explode(canvas, row, column)
                coroutines.append(show_gameover(
                    canvas,
                    row,
                    column,
                    gameover_frame
                ))
                return

        curses_tools.draw_frame(canvas, row, column, spaceship_frame)
        old_frame = spaceship_frame
        await asyncio.sleep(0)
        curses_tools.draw_frame(canvas, row, column, old_frame, negative=True)


async def animate_spaceship(spaceship_frames):
    global spaceship_frame
    while True:
        for frame in spaceship_frames:
            spaceship_frame = frame
            await asyncio.sleep(0)


def main(canvas):
    global coroutines, year
    row_max, col_max = canvas.getmaxyx()
    row, column = row_max/2, col_max/2
    info_zone = canvas.derwin(row_max - 4, col_max - 60)
    stars = ('+', '*', '.', ':')
    spaceship_frames = get_frames('rocket')
    garbage_frames = get_frames('garbage')
    coroutines.append(animate_spaceship(spaceship_frames))
    coroutines.append(run_spaceship(
        canvas,
        row,
        column,
        col_max,
        row_max
    ))
    coroutines.append(show_message(canvas, row_max, col_max))
    coroutines.append(fill_orbit_with_garbage(
        canvas,
        coroutines,
        col_max,
        garbage_frames
    ))

    for star in range(50):
        coroutines.append(blink(
            canvas, random.randint(1, row_max-2),
            random.randint(1, col_max-2),
            random.randint(1, 10),
            symbol=random.choice(stars)
        ))
    info_zone.border()
    canvas.border()
    canvas.nodelay(True)
    curses.curs_set(False)
    while True:
        for coroutine in coroutines:
            try:
                coroutine.send(None)
            except StopIteration:
                coroutines.remove(coroutine)
        year += 1
        canvas.refresh()
        info_zone.refresh()
        info_zone.border()
        canvas.border()
        time.sleep(TIC_TIMEOUT)


if __name__ == '__main__':
    curses.update_lines_cols()
    curses.wrapper(main)
