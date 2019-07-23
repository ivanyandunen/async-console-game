from curses_tools import draw_frame, get_frame_size
from obstacles import Obstacle, show_obstacles
import asyncio
from config import coroutines, sleep, year
from explosion import explode
from game_scenario import get_garbage_delay_tics, PHRASES
import random


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


async def fill_orbit_with_garbage(canvas, column, garbage_frame):
    coroutines.append(fly_garbage(canvas, column, garbage_frame))


async def count_garbage_amount(canvas, coroutines, row_max, col_max, garbage_frames):
    global year
    year = 1957
    info_zone = canvas.derwin(row_max - 4, col_max - 60)
    phrase = PHRASES[year]
    x, y = info_zone.getmaxyx()
    while True:
        delay = get_garbage_delay_tics(year)
        if delay:
            await sleep(delay)
        else:
            await sleep(0)
        await fill_orbit_with_garbage(
            canvas,
            random.randint(1, col_max-2),
            random.choice(garbage_frames)
        )
        year += 1
        if PHRASES.get(year):
            phrase = PHRASES[year]
            info_zone.addstr(x - 2, y - 50, f'Year: {year}, {phrase}')
        else:
            info_zone.addstr(x - 2, y - 50, f'Year: {year}, {phrase}')
