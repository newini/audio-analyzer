#!/bin/env python3
# -*- coding: utf-8 -*-
# visualizer_terminal.py

__author__      = "Eunchong Kim"
__copyright__   = "Copyright 2021, Eunchong Kim"
__credits__     = ["Eunchong Kim"]
__license__     = "GPL"
__version__     = "1.0.0"
__maintainer__  = "Eunchong Kim"
__email__       = "chariskimec@gmail.com"
__status__      = "Production"

#================================================
# Imports
import pyaudio
import numpy as np
import curses

#================================================
# Global variables
SIZE = 2**16 # 16 bit = 2 bytes per frame
RATE = 44100 # Hz, frames per second
CHUNK = 2**10 # number of data points to read at a time

#================================================
# Load pyaudio
pyaudio_obj = pyaudio.PyAudio()
stream = pyaudio_obj.open(
        channels=2,
        format=pyaudio.paInt16,
        frames_per_buffer=CHUNK,
        input=True,
        rate=RATE,
        )

#================================================
# Get sound data with CHUNK frames
# and calculate max and min in L, R
def getWavePoint():
    rawdata = np.frombuffer(
            stream.read(CHUNK, exception_on_overflow = False),
            dtype=np.int16)
    rawdata_l = rawdata[0::2]
    rawdata_r = rawdata[1::2]
    max_l = abs( np.max(rawdata_l) / (SIZE/2) )
    min_l = abs( np.min(rawdata_l) / (SIZE/2) )
    max_r = abs( np.max(rawdata_r) / (SIZE/2) )
    min_r = abs( np.min(rawdata_r) / (SIZE/2) )
    return max_l.item(), min_l.item(), max_r.item(), min_l.item() # return float, instead of numpy.float

#================================================
# Format sound max and min to string in size of max wave height
# and append to data list
# and check the length of data, not to overflow the wave length
def updateWaveList(data_l, data_r, h, w):
     # Get Wave Point
    max_l, min_l, max_r, min_r = getWavePoint()

    # Convert to string
    str_l = ' '*round((1-max_l) * h)+'█'*round(max_l * h)+'-'+'█'*round(min_l * h)+' '*round((1-min_l) * h)
    str_r = ' '*round((1-max_r) * h)+'█'*round(max_r * h)+'-'+'█'*round(min_r * h)+' '*round((1-min_r) * h)
    arr_l = [ c for c in str_l ]
    arr_r = [ c for c in str_r ]

    # Append to array and change length
    data_l.append(arr_l)
    data_r.append(arr_r)
    if len(data_l) >= w:
        data_l.pop(0)
    if len(data_r) >= w:
        data_r.pop(0)

#================================================
# Initialize curses window
# and loop to draw wave
def drawWave(stdscr):
    # Initialize key
    k = 0

    # not wait for the user input getch()
    stdscr.nodelay(True)

    # Clear and refresh the screen for a blank canvas
    stdscr.clear()
    stdscr.refresh()

    # Start colors in curses
    curses.start_color()
    curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
    curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
    curses.init_pair(3, curses.COLOR_BLACK, curses.COLOR_WHITE)

    # init LR data
    data_l = []
    data_r = []

    # Get height width
    height, width = stdscr.getmaxyx()

    # calculate wave height and lenght
    wave_height_max = (height-2-3-2) // 4 # Header: 2, center lines: 3, footer: 2
    wave_length = width - 12

    # Loop
    while (k != ord('q')):
        # Update wave data
        updateWaveList(data_l, data_r, wave_height_max, wave_length)

        # Rotate 270 countclock direction
        # TODO add more detail
        rot_l = np.rot90( np.array(data_l), 3 )
        rot_r = np.rot90( np.array(data_r), 3 )

        #---------------------------------------------------
        # Render
        #---------------------------------------------------
        # Render text at top
        top_str = "PyAudio LR terminal visualizer. Width: {}, Height: {}".format(width, height)
        stdscr.addstr(0, 0, top_str, curses.color_pair(1))

        # Render Left pannel line
        for i in range(height-4):
            stdscr.addstr(2+i, 10, '|')
        stdscr.addstr(height//4, 4, 'L')
        stdscr.addstr((height//4)*3, 4, 'R')

        # Render L wave
        for i in range(wave_height_max*2+1):
            output = ''.join( rot_l[i].tolist() )
            stdscr.addstr(2+i, 11, output, curses.color_pair(2))

        # Render center line
        output = '-'*(width-1)
        stdscr.addstr(height//2, 0, output)

        # Render R wave
        for i in range(wave_height_max*2+1):
            output = ''.join( rot_l[i].tolist() )
            stdscr.addstr(height//2+1+i, 11, output, curses.color_pair(2))

        # Render status bar at bottom
        statusbarstr = "Press 'q' to exit | STATUS BAR | "
        stdscr.attron(curses.color_pair(3))
        stdscr.addstr(height-1, 0, statusbarstr)
        stdscr.addstr(height-1, len(statusbarstr), " " * (width - len(statusbarstr) - 1))
        stdscr.attroff(curses.color_pair(3))

        # Refresh the screen
        stdscr.refresh()

        # Get key input
        k = stdscr.getch()

#================================================
# Just for test
def testPyaudio():
    data_l = []
    data_r = []
    for i in range(1000):
        updateWaveList(data_l, data_r, 10, 10)
        rot_l = np.rot90( np.array(data_l), 3 )
        rot_r = np.rot90( np.array(data_r), 3 )
        #print(rot_l)
        print(rot_l.shape)


def main():
    curses.wrapper(drawWave)
    #testPyaudio()


if __name__ == "__main__":
    main()
