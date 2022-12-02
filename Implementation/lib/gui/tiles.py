from tkinter import *
import sys

class Tiles(Label):
  def __init__(self, letter='', par=None):
    self.letter = StringVar()
    self.letter.set(letter)

    Label.__init__(self, par, textvariable=self.letter)
    self.config(bd=1,
                height=height,
                font=('times', 14, 'bold'),
                width=width,
                relief=SUNKEN)

class TileR(Tiles):
    def __init__(self, letter='', par=None):
        Tiles.__init__(self, letter, par)
        self.pack(side=LEFT)

class BoardTile(Tiles):
    def __init__(self, row, col, letter='', par=None):
        Tiles.__init__(self, par, letter)
        self.grid(row=row, column=col, sticky=W+E+N+S)
        self.name = None
        self.active = True


#this code supports mac 
if sys.platform == 'win32':
    width = 2
    height = 1
elif sys.platform == 'darwin':
    width = 4
    height = 2
else:
    width = 3
    height = 1
