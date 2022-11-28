import pickle, re, platform

from tkinter import *
from tkinter import font
from tkinter.filedialog import askopenfilename
from tkinter.simpledialog import askstring
from tkinter.messagebox import showwarning

from PIL import ImageTk, Image    # adds image insertion

from lib.gui.game_page import GamePage
from lib.gui.start_page import NormalStartPage, LANStartPage

class EntryPage(Frame):
  def __init__(self, parent, dic='./dics/sowpods.txt'):
    self.parent = parent
    self.dict = dic

    Frame.__init__(self, parent, bg='#824b30')
    self.grid(row=0, column=0, sticky=S+N+E+W)

    self.parent.master.geometry("1100x600") #changes default window size
    self.draw()

  def draw(self):
    image1 = Image.open("lib/gui/imgs/Scrabble_logo.png")
    test = ImageTk.PhotoImage(image1)
    label1 = Label(image=test)
    label1.image = test
    Label(self, bg='#824b30', image = test).pack(side=TOP, padx=200, pady=100)    #adds scrabble logo image


    f = Frame(self, bg='#6C3E28',padx=275, pady=15)
    f.pack(side=TOP)
    f.option_add("*font", "lucida" "13")
    Button(f, text='Versus Computer', command=self.start_computer_game).pack(side=LEFT, padx=10, pady=15)
    Button(f, text='Start Local Game', command=self.start_normal_game).pack(side=LEFT, padx=10, pady=15)
    Button(f, text='Start LAN Game', command=self.start_lan_game).pack(side=LEFT, padx=10, pady=15)

    fb = Frame(self, bg='#6C3E28',padx=308, pady=15)
    fb.pack(side=TOP)
    fb.option_add("*font", "lucida" "13") #change fonts via tkinter
    Button(fb, text='Join Game (Auto-detect)', command=self.join_game).pack(side=LEFT, pady=15, padx=5)
    Button(fb, text='Join Game Via IP', command=self.join_via_ip).pack(side=LEFT, pady=15, padx=5)
    Button(fb, text='Load', command=self.load_game).pack(side=LEFT, pady=15, padx=5)


  def start_computer_game(self):
    self.parent.master.set_geometry()

    GamePage(self.parent, {'comp_mode': True, 'names': ['Player', 'Computer'], 'play_num': 2}, self.dict)

  def start_normal_game(self):
    self.parent.master.geometry("1100x600")
    self.parent.master.minsize(1100, 600)
    self.parent.master.maxsize(1100, 600)

    NormalStartPage(self.parent, self.dict)

  def start_lan_game(self):
    self.parent.master.geometry("1100x600")
    self.parent.master.minsize(1100, 600)
    self.parent.master.maxsize(1100, 600)
    LANStartPage(self.parent, self.dict)

  def load_game(self):
    filename = askopenfilename(initialdir='./saves', filetypes=(('Pickle Files', '*.pickle'),))

    if filename:
      file = open(filename, 'rb')
      data = pickle.load(file)

      options = {
                  'chal_mode': data['chal_mode'],
                  'comp_mode': data['comp_mode'],
                  'normal_mode': data['norm_mode'],
                  'time_limit': data['time_limit'],
                  'point_limit': data['point_limit'],
                  'play_num': data['play_num'],
                  'loading': True
                }

      self.parent.master.set_geometry()

      game = GamePage(self.master, options)

      game.cur_play_mark = data['cur_play_mark']
      game.players = data['players']
      game.bag = data['bag']
      game.board = data['board']
      game.op_score = data['op_score']
      game.seconds = data['seconds']
      game.minutes = data['minutes']
      game.turns = data['turns']

  def join_game(self):
    name = askstring('Enter Name', 'Enter Your Nickname:')

    if name:
      self.parent.master.set_geometry()
      self.parent.master.child = GamePage(self.parent, {'names': [name]})
    else:
      showwarning('Error: No Nickname', 'No Nickname Provided.\n\nPlease Try Again.')

  def join_via_ip(self):
    name = askstring('Enter Name', 'Enter Your Nickname:')

    if name:
      ip = askstring('Enter IP Address', 'Enter the Host IP Address:')
      p = '(25[0-5]|2[0-4][0-9]|1[0-9][0-9]|[1-9][0-9]|[0-9])'
      ip_p = p + '\.' + p + '\.' + p + '\.' + p

      if re.fullmatch(ip_p, ip):
        self.parent.master.set_geometry()
        self.parent.master.child = GamePage(self.parent, {'names': [name], 'ip': ip})
      else:
        showwarning('Error: Invalid', 'IP Address is Invalid.\n\nPlease Try Again.')
    else:
      showwarning('Error: No Nickname', 'No Nickname Provided.\n\nPlease Try Again.')