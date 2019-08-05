import os
import asyncio


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
