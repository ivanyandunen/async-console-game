from curses_tools import draw_frame, get_frame_size
from obstacles import Obstacle, show_obstacles
import asyncio
from auxiliary import sleep
from explosion import explode
from game_scenario import get_garbage_delay_tics, PHRASES
import random
import globs


obstacles = []
obstacles_in_last_collisions = []


async def fly_garbage(canvas, column, garbage_frame, speed=0.5):
    """Animate garbage, flying from top to bottom. Сolumn position will stay
    same, as specified on start."""
    rows_number, columns_number = canvas.getmaxyx()

    column = max(column, 0)
    column = min(column, columns_number - 1)

    row = 0

    rows_size, columns_size = get_frame_size(garbage_frame)
    obstacle = Obstacle(row, column, rows_size, columns_size)
    obstacles.append(obstacle)

    try:
        while row < rows_number:
            draw_frame(canvas, row, column, garbage_frame)
            await asyncio.sleep(0)
            draw_frame(canvas, row, column, garbage_frame, negative=True)
            row += speed
            obstacle.row = row

            if obstacle in obstacles_in_last_collisions:
                obstacles_in_last_collisions.remove(obstacle)
                await explode(canvas, row, column)
                return
    finally:
        obstacles.remove(obstacle)


async def show_message(canvas, row_max, col_max):
    info_zone = canvas.derwin(row_max - 4, col_max - 60)
    phrase = PHRASES[globs.year]
    x, y = info_zone.getmaxyx()
    while True:
        if PHRASES.get(globs.year):
            phrase = PHRASES[globs.year]
            info_zone.addstr(x - 2, y - 50, f'Year: {int(globs.year)}  {phrase}')
        else:
            info_zone.addstr(x - 2, y - 50, f'Year: {int(globs.year)}  {phrase}')
        await asyncio.sleep(0)


async def fill_orbit_with_garbage(canvas, col_max, garbage_frames):
    while True:
        delay = get_garbage_delay_tics(globs.year)
        if delay:
            await sleep(delay)
        else:
            await sleep(25)
        globs.coroutines.append(fly_garbage(
            canvas,
            random.randint(1, col_max-2),
            random.choice(garbage_frames)
        ))
        await asyncio.sleep(0)
