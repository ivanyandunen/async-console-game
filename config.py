import os
import asyncio
from curses_tools import draw_frame


coroutines = []
TIC_TIMEOUT = .1
year = 1957


async def sleep(tics):
    for _ in range(int(tics)):
        await asyncio.sleep(0)


def get_frames(frames_dir):
    frames = []

    for file in os.listdir(f"images/{frames_dir}"):
        with open(f"images/{frames_dir}/{file}", "r") as my_file:
            frame = my_file.read()
            frames.append(frame)

    return frames


async def show_gameover(canvas, row, column, frame):
    while True:
        draw_frame(canvas, row, column, frame)
        await asyncio.sleep(0)
        draw_frame(canvas, row, column, frame, negative=True)
