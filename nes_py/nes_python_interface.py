# -*- coding: utf-8 -*-
"""NES learning environment for python

Author: Daniel Pipkin (with credits to Ben Goodrich and Ehren J. Brav)

This partially implements a python version of the NES learning
environment interface.

The idea is to make Ehren J. Brav's interface into a pip-able package
to use in a openai/gym environment.

"""

from ctypes import *
import numpy as np
from numpy.ctypeslib import as_ctypes
import os

nes_lib = cdll.LoadLibrary(os.path.join(os.path.dirname(__file__), 'libfceux.so'))

class NESInterface(object):
    """Interface class for FCEUX emulator.

    """
    def __init__(self, rom):
        nes_lib.NESInterface.argtypes = [c_char_p]
        nes_lib.NESInterface.restype = c_void_p
        byte_string_rom = rom.encode('utf-8')
        self.obj = nes_lib.NESInterface(byte_string_rom)
        self.width, self.height = self.getScreenDims()

    def act(self, action):
        nes_lib.act.argtypes = [c_void_p, c_int]
        nes_lib.act.restype = c_int
        return nes_lib.act(self.obj, int(action))

    def game_over(self):
        nes_lib.gameOver.argtypes = [c_void_p]
        nes_lib.gameOver.restype = c_bool
        return nes_lib.gameOver(self.obj)

    def reset_game(self):
        nes_lib.resetGame.argtypes = [c_void_p]
        nes_lib.resetGame.restype = None
        nes_lib.resetGame(self.obj)

    def getLegalActionSet(self):
        nes_lib.getNumLegalActions.argtypes = [c_void_p]
        nes_lib.getNumLegalActions.restype = c_int
        act_size = nes_lib.getNumLegalActions(self.obj)
        act = np.zeros(shape=(act_size,), dtype=c_int)
        nes_lib.getLegalActionSet.argtypes = [c_void_p, c_void_p]
        nes_lib.getLegalActionSet.restype = None
        nes_lib.getLegalActionSet(self.obj, as_ctypes(act))
        return act

    def getMinimalActionSet(self):
        return self.getLegalActionSet()

    def getFrameNumber(self):
        nes_lib.getFrameNumber.argtypes = [c_void_p]
        nes_lib.getFrameNumber.restype = c_int
        return nes_lib.getFrameNumber(self.obj)

    def lives(self):
        nes_lib.lives.argtypes = [c_void_p]
        nes_lib.lives.restype = c_int
        return nes_lib.lives(self.obj)

    def getEpisodeFrameNumber(self):
        nes_lib.getEpisodeFrameNumber.argtypes = [c_void_p]
        nes_lib.getEpisodeFrameNumber.restype = c_int
        return nes_lib.getEpisodeFrameNumber(self.obj)

    def getScreenDims(self):
        nes_lib.getScreenHeight.argtypes = [c_void_p]
        nes_lib.getScreenHeight.restype = c_int
        nes_lib.getScreenWidth.argtypes = [c_void_p]
        nes_lib.getScreenWidth.restype = c_int
        width = nes_lib.getScreenWidth(self.obj)
        height = nes_lib.getScreenHeight(self.obj)
        return (width, height)

    def getScreen(self, screen_data=None):
        if(screen_data is None):
            screen_data = np.zeros(self.width*self.height, dtype=np.uint8)

        nes_lib.getScreen.argtypes = [c_void_p, c_void_p, c_int]
        nes_lib.getScreen.restype = None
        nes_lib.getScreen(self.obj, as_ctypes(screen_data), c_int(screen_data.size))
        return screen_data

    def getScreenRBG(self, screen_data=None):
        if(screen_data is None):
            screen_data = np.empty((self.height, self.width, 1), dtype=np.uint8)

        nes_lib.getScreen.argtypes = [c_void_p, c_void_p, c_int]
        nes_lib.getScreen.restype = None

        nes_lib.getScreen(self.obj, as_ctypes(screen_data), c_int(screen_data.size))

        rgb_screen = np.empty((self.height, self.width, 3), dtype=np.uint8)
        nes_lib.fillRGBfromPalette.argtypes = [c_void_p, c_void_p, c_void_p, c_int]
        nes_lib.fillRGBfromPalette.restype = None
        nes_lib.fillRGBfromPalette(self.obj, as_ctypes(screen_data), as_ctypes(rgb_screen), c_int(screen_data.size))
        return rgb_screen

    def getScreenGrayscale(self, screen_data=None):
        if(screen_data is None):
            screen_data = np.empty((self.height, self.width, 1), dtype=np.uint8)
        nes_lib.getScreen.argtypes = [c_void_p, c_void_p, c_int]
        nes_lib.getScreen.restype = None
        nes_lib.getScreen(self.obj, as_ctypes(screen_data[:]), c_int(screen_data.size))
        return screen_data

    def getRAMSize(self):
        return nes_lib.getRAMSize(self.obj)

    def getRAM(self, ram=None):
        if (ram is None):
            ram_size = nes_lib.getRAMSize(self.obj)
            ram = np.zeros(ram_size, dtype=np.uint8)
        nes_lib.getRAM(self.obj, as_ctypes(ram))
        return ram

    def saveScreenPNG(self, filename):
        return nes_lib.saveScreenPNG(self.obj, filename)

    def saveState(self):
        nes_lib.saveState.argtypes = [c_void_p]
        nes_lib.saveState.restype = None
        return nes_lib.saveState(self.obj)

    def loadState(self):
        nes_lib.loadState.argtypes = [c_void_p]
        nes_lib.loadState.restype = c_bool
        return nes_lib.loadState(self.obj)

    def cloneState(self):
        return nes_lib.cloneState(self.obj)

    def restoreState(self, state):
        nes_lib.restoreState(self.obj, state)

    def cloneSystemState(self):
        return nes_lib.cloneSystemState(self.obj)

    def restoreSystemState(self, state):
        nes_lib.restoreSystemState(self.obj, state)

    def deleteState(self, state):
        nes_lib.deleteState(state)

    def encodeStateLen(self, state):
        return nes_lib.encodeStateLen(state)

    def encodeState(self, state, buf=None):
        if buf == None:
            length = nes_lib.encodeStateLen(state)
            buf = np.zeros(length, dtype=np.uint8)
        nes_lib.encodeState(state, as_ctypes(buf), c_int(len(buf)))

    def decodeState(self, serialized):
        return nes_lib.decodeState(as_ctypes(serialized), len(serialized))

    def __del__(self):
        nes_lib.delete_NES.argtypes = [c_void_p]
        nes_lib.delete_NES.restype = None
        nes_lib.delete_NES(self.obj)
