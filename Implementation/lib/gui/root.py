import sys

from tkinter import *
from tkinter.messagebox import askyesno

from lib.gui.entry_page import EntryPage

class Root(Tk):
  def __init__(self, dic='./dics/sowpods.txt'):
    Tk.__init__(self)
    self.title('PyScrabble')
    self.config(bg='azure')
    self.protocol('WM_DELETE_WINDOW', self.quit_game)

    self.dict = dic

    self.child = None

    ws = self.winfo_screenwidth()
    x = int((ws/2) - (900/2))

    self.geometry('900x500+{}+{}'.format(x, 0))
    self.minsize(900, 500)

    self.draw_menu()
    self.draw_container()

    EntryPage(self.container, self.dict)

  def draw_menu(self):
    top = Menu(self)
    self.config(menu=top)

    game_m = Menu(top)
    game_m.add_command(label='MainMenu', underline=0, command=self.MainMenu)
    game_m.add_command(label='Quit', underline=0, command=self.quit_game)

    about_m = Menu(top)
    about_m.add_command(label='Game Manual', underline=0, command=self.render_info_page)

    top.add_cascade(label='Settings', menu=game_m, underline=0)
    top.add_cascade(label='Information', menu=about_m, underline=0)

  def draw_container(self):
    self.container = Frame(self, bg='azure')
    self.container.pack(side=TOP, fill=BOTH, expand=YES)
    self.container.grid_rowconfigure(0, weight=1)
    self.container.grid_columnconfigure(0, weight=1)

  def render_info_page(self):
    info_page = Toplevel(self)
    info_page.minsize(900, 500)
    info_page.maxsize(900, 500)

    info = Text(info_page, height=40, width=90)
    scroll = Scrollbar(info_page, command=info.yview)

    info.configure(yscrollcommand=scroll.set)

    info.tag_configure('bold', font=('lucida', 15, 'bold'))
    info.tag_configure('title', font=('lucida', 21, 'bold', 'italic'), justify='center')
    info.tag_configure('italic', font=('lucida', 13, 'italic'))
    info.tag_configure('underline', font=('lucida', 12, 'italic', 'underline'))

    info.insert(END, 'BASIC INFO\n\n', 'title')
    info.insert(END, 'Blank Tile\n\n', 'bold')
    info.insert(END, 'Place a blank tile on the spot of the letter you want to replace it with. Once submitted, it will promp you what letter would you like to choose.\n\n\n')
    info.insert(END, 'Challenge Mode\n\n', 'bold')
    info.insert(END, 'The challenge mode will follow the double challenge rule. A player may challenge the words that the player before has placed on the board. If the word is not valid, the previous player\'s turn will be passed and points will be subtracted. If the words are valid, the turn of the player who has challenged will be passed.\n\n\n')
    info.insert(END, 'Multiplayer on a Local Machine\n\n', 'bold')
    info.insert(END, 'A game of 2, 3 or 4 players can be played on a single computer. The letters of the players will be concealed to prevent other players from cheating\' unintentionally.')
    info.insert(END, 'It is shown in red font above the board whose turn it is.\n\n\n')
    info.insert(END, 'Playing vs Computer\n\n', 'bold')
    info.insert(END, 'Computer goes through the letters available and picks the valid move with the most points.\n\n\n')
    info.insert(END, 'Save Game\n\n', 'bold')
    info.insert(END, 'If a game is saved during a LAN multiplayer game, it can be later loaded as a normal multiplayer game on a single machine.\n\n\n')
    info.insert(END, 'LAN Game\n\n', 'bold')
    info.insert(END, 'Join Game (Auto) & Join Game (IP)', 'underline')
    info.insert(END, ' will not find the hosted game on networks like campus wifi due to the 256 ip limit being exceed.')

    info.pack(side=LEFT, padx=20)
    scroll.pack(side=RIGHT, fill=Y)


  def MainMenu(self):
    if askyesno('Main Menu', 'Are you sure you want to return to menu?'):
      self.geometry('900x500')
      self.minsize(900, 500)

      self.container.destroy()

      self.draw_container()

      EntryPage(self.container, self.dict)

  def quit_game(self):
    if askyesno('Quit Game', 'Are you sure you would like to quit the game?'):
      if self.child:
        self.child.destroy()

      self.quit()

  def set_geometry(self):
    if sys.platform == 'darwin':
      self.geometry('1100x800')
      self.minsize(1100, 800)
    elif sys.platform == 'win32':
      self.geometry('1100x600')
      self.minsize(1100, 600)
    else:
      self.geometry('1100x800')
      self.minsize(1100, 800)