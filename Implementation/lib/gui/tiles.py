from tkinter import *
import sys

class Tiles(Label):
  def __init__(self, let='', par=None):
    self.let = StringVar()
    self.let.set(let)

    Label.__init__(self, par, textvariable=self.let)
    self.config(bd=1,
                height=height,
                font=('times', 14, 'bold'),
                width=width,
                relief=SUNKEN)

class TileR(Tiles):
    def __init__(self, let='', par=None):
        Tiles.__init__(self, let, par)
        self.pack(side=LEFT)

class BoardTile(Tiles):
    def __init__(self, row, col, let='', par=None):
        Tiles.__init__(self, par, let)
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
