import os
import cv2
import curses
import argparse
import time
import numpy as np
import color
import youtube_utils
from functools import lru_cache

# Suppress FFmpeg warnings
os.environ['FFREPORT'] = 'file=ffreport.log:level=24'

parser = argparse.ArgumentParser(description='ASCII Player')
parser.add_argument("--width", type=int, default=None,
                    help="width of the terminal window (auto if not set)")
parser.add_argument("--fps", type=int, default=30,
                    help="target FPS for playback")
parser.add_argument("--show", type=bool, default=False,
                    help="show the original video in an OpenCV window")
parser.add_argument("--inv", type=bool, default=True,
                    help="invert the shades")
parser.add_argument("--color", type=bool, default=False,
                    help="print colors if available in the terminal")
parser.add_argument("--embed", type=str, default="",
                    help="pass a txt file to embed as watermark")
parser.add_argument("video", type=str, help="path to video or webcam index")
args = parser.parse_args()

video = args.video
try:
    video = int(video)
except ValueError:
    pass

characters = [' ', '.', ',', '-', '~', ':', ';', '=', '!', '*', '#', '$', '@']
if args.inv:
    characters = characters[::-1]
char_range = int(255 / len(characters))

@lru_cache
def get_char(val):
    return characters[min(int(val / char_range), len(characters) - 1)]

def paint_screen(window, frame):
    for y in range(frame.shape[0]):
        for x in range(frame.shape[1]):
            try:
                window.addch(y, x, get_char(frame[y, x]))
            except (curses.error):
                pass

def paint_color_screen(window, grayscale_frame, frame, curses_color: color.CursesColor):
    for y in range(frame.shape[0]):
        for x in range(frame.shape[1]):
            try:
                color_pair = curses_color.get_color(tuple(frame[y, x]))
                window.addch(y, x,
                             get_char(grayscale_frame[y, x]),
                             curses.color_pair(color_pair))
            except (curses.error):
                pass

def paint_embedding(window: curses.window, embedding: str, embedding_height: int, grayscale_frame):
    for line_idx, line in enumerate(embedding.split("\n")):
        line_len = len(line)
        width = grayscale_frame.shape[1]
        height = grayscale_frame.shape[0]
        try:
            window.addstr(
                height - embedding_height + line_idx,
                width - line_len,
                line
            )
        except:
            pass

fps = 0

try:
    if type(video) is str \
       and not os.path.isfile(video) \
       and not youtube_utils.is_youtube_url(video):
        print("failed to find video at:", args.video)
        exit(1)

    if youtube_utils.is_youtube_url(video):
        video = youtube_utils.get_youtube_video_url(video)

    cap = cv2.VideoCapture(video)
    ok, frame = cap.read()
    if not ok:
        print("could not extract frame from video")
        exit(1)

    # Auto-detect terminal size
    try:
        term_size = os.get_terminal_size()
        term_width = term_size.columns
        term_height = term_size.lines
    except OSError:
        term_width = 80
        term_height = 24

    # Compute width/height based on video ratio
    default_width = args.width or term_width - 2
    ratio = default_width / frame.shape[1]
    width = min(default_width, term_width - 1)
    height = int(frame.shape[0] * ratio * 3 / 5)
    height = min(height, term_height - 1)

    print(f"Video shape: {frame.shape}")
    print(f"Using terminal size width={width} height={height}")

    curses.initscr()
    curses.curs_set(0)
    if args.color and curses.can_change_color():
        curses.start_color()
        curses.use_default_colors()
        curses_color = color.CursesColor()
    window = curses.newwin(height, width, 0, 0)

    embedding = ""
    if args.embed != "":
        with open(args.embed, "r") as f:
            embedding = f.read()
    embedding_height = len(embedding.split("\n"))

    frame_count = 0
    target_frame_time = 1.0 / args.fps
    start_time = time.perf_counter()
    next_frame_time = start_time

    while True:
        current_time = time.perf_counter()
        
        # Wait for the next frame time
        sleep_time = next_frame_time - current_time
        if sleep_time > 0:
            time.sleep(sleep_time)
        
        ok, orig_frame = cap.read()
        if not ok:
            break

        frame = cv2.resize(orig_frame, (width, height))
        grayscale_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        
        if args.show:
            cv2.imshow("frame", orig_frame)
            cv2.waitKey(1)

        if args.color and curses.can_change_color():
            paint_color_screen(window, grayscale_frame,
                               frame.astype(np.int32), curses_color)
        else:
            paint_screen(window, grayscale_frame)

        paint_embedding(window, embedding, embedding_height, grayscale_frame)
        window.refresh()
        
        # Update timing for next frame
        frame_count += 1
        next_frame_time += target_frame_time
        
        # Calculate FPS every second
        elapsed_time = current_time - start_time
        if elapsed_time >= 1.0:
            fps = frame_count / elapsed_time
            print(f"Current FPS: {fps:.1f}", end='\r')
            frame_count = 0
            start_time = current_time

finally:
    cap.release()
    cv2.destroyAllWindows()
    curses.endwin()
    print(f"\nPlayed at {fps:.1f} fps")