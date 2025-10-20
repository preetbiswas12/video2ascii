# ASCII Player

This player plays video on a terminal using ascii characters

A good example are high contrast videos like `bad apple`, you can download it from youtube with `youtube-dl` from [Bad Apple](https://www.youtube.com/watch?v=FtutLA63Cp8) or just use the url directly in the command line and the player will stream it to your terminal.

## Install dependencies

`pip3 install -r requirements.txt`

## Usage

After having a file you can play it like this:

```python
python3 player.py <path_to_video or youtube_video_url or video_input_device_index>
```

The player uses your own terminal window dimensions by default and if u want to change just use the --width flag to set a custom width in characters.

```python


The default framerate is 30 fps. This can also be changed using the `--fps` flag. If it's set too high it will just go as fast as it can.

You can choose to display the original video with `opencv` with `--show true`

You can also choose to invert the shades of the ascii video with `--inv true`

You can also choose to use actual colors with `--color true`. You might need to `reset` the terminal afterwards since it overrides default colors.

### Webcam Usage (under construction)

To use your webcam as video source simply specify the video input device index, most likely it is `0` unless you have multiple ones in which case  you  can just bruteforce your way through until you find it.
## Running on a raspberrypi

For best results run on a raspberrypi5 with the cython version as that gets the best framerate at higher resolutions.

### Install dependencies

Install the `Picamera2` and `opencv` dependencies via apt:

```sudo
sudo apt install python3-opencv python3-picamera2
```

Create a virtual environment that still has access to the system packages an install the remaining dependencies:

```sudo
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip3 install -r requirements_rpi.txt
```

```python
python3 -m venv .venv --system-site-packages
source .venv/bin/activate
pip3 install -r requirements_rpi.txt
```
