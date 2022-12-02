import threading, re, os, pickle, queue, sys, platform
from tkinter import *
from tkinter.messagebox import askyesno, showwarning, showinfo
from tkinter.simpledialog import askstring
from tkinter.filedialog import asksaveasfilename
import lib.lan as lh
from lib.dic import Dict
from lib.bag import Bag
from lib.word import Word
from lib.board import Board
from lib.comp import opponentAI
from lib.player import Player
from lib.gui.tiles import BoardTile, TileR

class GamePage(Frame):
  def __init__(self, parent, options, dic='./dics/sowpods.txt'):
    Frame.__init__(self, parent, bg='#6C3E28')
    self.grid(row=0, column=0, sticky=S+N+E+W)

    self.dict = Dict(dic)
    self.bag = Bag()
    self.board = Board()

    self.set_variables()

    if options.get('play_num', False):
      self.joined_lan = False
      self.resolve_options(options)
    else:
      self.joined_lan = True
      self.thread = threading.Thread(target=lh.join_lan_game, args=(options, self.queue))
      self.thread.start()
      self.resolve_options(options)

    self.run()

  def run(self):
    if self.server_not_found or self.lan_cancelled:
      self.destroy()
    else:
      self.draw_main_frame()
      self.draw_info_frame()
      self.initialize_game()

  def set_variables(self):
    self.word = None
    self.thread = None
    self.winner = None
    self.cur_player = None
    self.start_tile = None

    self.time_up = False
    self.game_over = False
    self.chal_failed = False
    self.is_challenged = False  
    self.letters_passed = False 
    self.server_not_found = False 
    self.lan_cancelled = False 

    self.first_turn = True
    self.game_online = True
    self.may_proceed = True

    self.turns = 0 
    self.seconds = 0
    self.own_mark = 0 
    self.op_score = 0 
    self.pass_num = 0
    self.cur_play_mark = 0

    self.gui_board = {}
    self.used_spots = {}
    self.placed_tiles = {}

    self.rack = []
    self.losers = []
    self.raw_word = []
    self.wild_tiles = []
    self.prev_words = []  
    self.spots_buffer = []  
    self.empty_rack_tiles = []
    self.wild_tiles_clone = [] 
    self.prev_spots_buffer = []

    self.queue = queue.Queue()

    self.bag_info = StringVar()
    self.time_info = StringVar()
    self.status_info = StringVar()
    self.words_info = StringVar()

  def resolve_options(self, options):
    if self.joined_lan:
      search = True

      if not options.get('ip', None):
        search = askyesno('Searching...',
                 'Will try to find a hosted game. This might take a while depending on the computer.\n\nClick OK to start.')

      if search:

        try:
          self.options, self.own_mark = self.queue.get()
        except:
          self.options = options
          self.server_not_found = True
      else:
        self.options = options
        self.lan_cancelled = True
    else:
      self.options = options

    self.chal_mode = self.options.get('chal_mode', False)
    self.comp_mode = self.options.get('comp_mode', False)
    self.norm_mode = self.options.get('normal_mode', False)
    self.lan_mode = self.options.get('lan_mode', False)
    self.time_limit = self.options.get('time_limit', 0)
    self.point_limit = self.options.get('point_limit', 0)
    self.players = self.options.get('names', [])
    self.play_num = self.options.get('play_num', 0)
    self.loading = self.options.get('loading', False)

    self.minutes = self.time_limit

  def draw_main_frame(self):
    out_f = Frame(self, padx=30, bg='#6C3E28')
    out_f.pack(side=LEFT)

    l = Label(out_f, textvariable=self.status_info)
    l.config(bg='#6C3E28', fg='#FF4500', font=('times', 25, 'italic'))
    l.pack(side=TOP, pady=15)

    if self.lan_mode and not self.joined_lan:
      self.status_info.set('... Waiting for player(s) ...')

    board_f = Frame(out_f)
    board_f.pack(side=TOP)

    row_num = 0
    row_name = 15

    while row_num < 15:
      col_num = 0
      col_name = 'a'

      while col_num < 15:
        tile = BoardTile(row_num, col_num, board_f)
        tile.bind('<1>', self.place_tile)
        tile.name = col_name + str(row_name)
        self.determine_tile_background(tile)

        self.gui_board[tile.name] = tile

        col_num += 1
        col_name = chr(ord(col_name) + 1)

      row_num += 1
      row_name -= 1

    rack = Frame(out_f, pady=15, bg='#6C3E28')
    rack.pack(side=TOP)

    for i in range(7):
      tile = TileR(rack)
      tile.bind('<1>', self.place_tile)
      tile['bg'] = '#BE975B'


      if self.norm_mode:
        tile['fg'] = '#BE975B'

      self.rack.append(tile)

    button_f = Frame(out_f, bg='#6C3E28')
    button_f.pack(side=TOP)

    self.sub = Button(button_f, text='Submit')
    self.sub.config(command=self.process_word)
    self.sub.pack(side=LEFT, padx=5)

    self.pas = Button(button_f, text='Pass')
    self.pas.config(command=self.pass_letters)
    self.pas.pack(side=LEFT, padx=5)

    if self.chal_mode:
      self.chal = Button(button_f, text='Challenge')
      self.chal.config(command=self.challenge)
      self.chal.pack(side=LEFT, padx=5)

    if self.norm_mode:
      Button(button_f, text='Reveal', command=self.reveal_tile).pack()

  def determine_tile_background(self, tile):
    if tile.name in 'a1 a8 a15 h15 o15 h1 o8 o1'.split():
      tile['bg'] = '#ff3300'
    elif tile.name in 'h8 b2 c3 d4 e5 b14 c13 d12 e11 n2 m3 l4 k5 n14 m13 l12 k11'.split():
      tile['bg'] = '#ff99cc'
    elif tile.name in 'b6 b10 n6 n10 f2 f6 f10 f14 j2 j6 j10 j14'.split():
      tile['bg'] = '#3366ff'
    elif tile.name in 'a4 a12 c7 c9 d1 d8 d15 g3 g7 g9 g13 h4 h12 o4 o12 m7 m9 l1 l8 l15 i3 i7 i9 i13'.split():
      tile['bg'] = '#b3c6ff'
    else:
      tile['bg'] = '#ffd6cc'

  def reveal_tile(self):
    for tile in self.rack:
      tile['fg'] = 'black'

  def draw_info_frame(self):
    info_frame = Frame(self, bg='#824b30')
    info_frame.pack(side=LEFT, fill=BOTH)

    self.sav = Button(info_frame, text='Save Game')
    self.sav.config(command=self.save_game)
    self.sav.pack(side=TOP, pady=50)

    cont_f = Frame(info_frame, bg='#824b30')
    cont_f.pack(side=TOP, pady=40, fill=X)

    options = {'font': ('times', 16, 'italic'), 'bg': '#824b30', 'fg': '#004d00'}

    if self.time_limit:
      l = Label(cont_f, textvariable=self.time_info)
      l.config(font=('times', 16, 'italic'), bg='#004d00', fg='#824b30')
      l.pack(anchor=NW)

    Label(cont_f, textvariable=self.bag_info, **options).pack(pady=10)

    play_f = LabelFrame(cont_f, pady=5, padx=5, bg='#824b30')
    play_f.pack(anchor=NW)


    self.pl1_info = StringVar()
    Label(play_f, textvariable=self.pl1_info, **options).pack(anchor=NW)

    self.pl2_info = StringVar()
    Label(play_f, textvariable=self.pl2_info, **options).pack(anchor=NW)

    if self.play_num >= 3:
      self.pl3_info = StringVar()
      Label(play_f, textvariable=self.pl3_info, **options).pack(anchor=NW)

    if self.play_num == 4:
      self.pl4_info = StringVar()
      Label(play_f, textvariable=self.pl4_info, **options).pack(anchor=NW)

    Label(cont_f, text='Words:', **options).pack(anchor=NW, pady=10)


    m = Message(cont_f, textvariable=self.words_info)
    m.config(font=('times', 15, 'italic'), anchor=NW, bg='#824b30', fg='#004d00')
    m.pack(anchor=NW, fill=X)

  def set_word_info(self, words):
    message = ''

    for word in words:
      message = message + ('{} {}\n'.format(word, words[word]))

    if self.cur_player.full_bonus:
      message = message + ('\nBonus 60\n')
      self.cur_player.full_bonus = False

    self.words_info.set(message[:-1])


  def undo_placement(self):
    for t1, t2 in zip(self.empty_rack_tiles, self.placed_tiles.values()):
      t1.letter.set(t2.letter.get())
      t2.letter.set('')
      t1['bg'] = '#BE975B'

      self.determine_tile_background(t2)

    self.placed_tiles = {}
    self.may_proceed = False

  def initialize_game(self):
    self.check_game_over()


    if self.lan_mode and not self.joined_lan:
      self.thread = threading.Thread(target=lh.langame, args=(self.options, self.queue, self.bag))
      self.thread.start()

      self.initialize_players()
    elif self.joined_lan:
      self.players, self.bag = self.queue.get()
      self.init_turn()
    elif self.loading:

      self.master.master.after(1000, self.load_board)
    else:
      self.initialize_players()

  def countdown(self):
    if self.seconds == 0:
      self.seconds = 59
      self.minutes -= 1
    else:
      self.seconds -= 1

    if self.seconds >= 0 and self.minutes >= 0:
      if self.seconds > 9:
        seconds = str(self.seconds)
      else:
        seconds = '0' + str(self.seconds)

      self.time_info.set('{}:{} Left'.format(self.minutes, seconds))
      self.master.master.after(1000, self.countdown)
    else:
      self.time_up = True

      self.end_game()

  def initialize_players(self):
    if self.lan_mode and len(self.players) < self.play_num:
      self.master.master.after(1000, self.initialize_players)
    else:

      for i in range(self.play_num):
        pl = Player(self.players[i])
        pl.drawLetters(self.bag)
        self.players.append(pl)


        if self.comp_mode:
          self.opponent = opponentAI()
          self.opponent.drawLetters(self.bag)
          self.players.append(self.opponent)

          break


      del self.players[:self.play_num]

      if self.lan_mode:
        self.queue.put(self.players)

      self.init_turn()


  def load_board(self):
    spots = []
    letters = []

    for spot, letter in self.board.board.items():
      if re.fullmatch('[A-Z@]', letter):
        spots.append(spot)
        letters.append(letter)

    for spot, letter in self.gui_board.items():
      if spot in spots:
        self.gui_board[spot].letter.set(letters[spots.index(spot)])
        self.gui_board[spot].active = False
        self.gui_board[spot]['bg'] = '#BE975B'

        self.used_spots[spot] = self.gui_board[spot]

    for spot in spots:
      del self.gui_board[spot]

    self.init_turn()

  def init_turn(self):
    self.turns += 1

    if self.lan_mode and not self.first_turn:
      if self.own_mark == self.cur_play_mark:
        self.disable_board()

        if self.letters_passed:
          self.queue.put((self.own_mark, self.bag, self.game_online))
        elif not self.chal_failed:
          self.queue.put((self.own_mark,
                          self.word,
                          self.w_range,
                          self.placed_tiles,
                          self.prev_spots_buffer,
                          self.players,
                          self.bag,
                          self.board,
                          self.game_online))
        else:

          self.queue.put((self.own_mark, False, None, None, self.game_online))


        while not self.queue.empty():
          continue
      elif not self.is_challenged:
        self.enable_board()
    elif self.joined_lan and self.first_turn:
      self.disable_board()

    self.placed_tiles = {}
    self.empty_rack_tiles = []
    self.spots_buffer = []
    self.start_tile = None

    if not self.comp_mode and not self.loading and not self.first_turn:
      self.cur_play_mark = (self.cur_play_mark + 1) % self.play_num

    self.cur_player = self.players[self.cur_play_mark]

    self.update_info()
    self.decorate_rack()

    if self.time_limit and self.first_turn:
      self.countdown()

    self.loading = False
    self.first_turn = False
    self.chal_failed = False

    if self.lan_mode and self.own_mark != self.cur_play_mark:
      self.process_word()

    if self.comp_mode and self.turns % 2 == 0:
      self.wait_comp()

  def update_info(self):
    if self.comp_mode:
      self.status_info.set('... Player\'s Turn ...')
      self.bag_info.set('{} Tiles in Bag'.format(len(self.bag.bag)))
      self.pl1_info.set('{}: {}'.format(self.players[0].name, self.players[0].score))
      self.pl2_info.set('Computer: {}'.format(self.players[1].score))
    else:
      if self.lan_mode and self.own_mark == self.cur_play_mark:
        name = 'Your'
      else:
        name = self.cur_player.name + '\'s'

      self.status_info.set('... {} Turn ...'.format(name))

      self.pl1_info.set('{}: {}'.format(self.players[0].name, self.players[0].score))
      self.pl2_info.set('{}: {}'.format(self.players[1].name, self.players[1].score))

      if self.play_num >= 3:
        self.pl3_info.set('{}: {}'.format(self.players[2].name, self.players[2].score))

      if self.play_num == 4:
        self.pl4_info.set('{}: {}'.format(self.players[3].name, self.players[3].score))

      self.bag_info.set('{} Tiles in Bag'.format(len(self.bag.bag)))

  def decorate_rack(self):

    if self.is_challenged:
      player = self.players[self.own_mark]
    else:
      player = self.cur_player


    if not self.lan_mode or self.lan_mode and self.own_mark == self.cur_play_mark:
      for letter, tile in zip(player.letters, self.rack):
        if letter == '@':
          tile.letter.set(' ')
        else:
          tile.letter.set(letter)

        tile['bg'] = '#BE975B'


        if self.norm_mode:
          tile['fg'] = '#BE975B'


      if len(self.bag.bag) == 0:

        for tile in self.rack[len(player.letters):]:
          tile.letter.set('')
          tile['bg'] = '#cccccc'

    elif self.joined_lan and self.first_turn:
      for letter, tile in zip(self.players[self.own_mark].letters, self.rack):
        if letter == '@':
          tile.letter.set(' ')
        else:
          tile.letter.set(letter)

        tile['bg'] = '#BE975B'


  def disable_board(self):
    self.sub.config(state=DISABLED)
    self.pas.config(state=DISABLED)
    self.sav.config(state=DISABLED)

    if self.lan_mode and self.chal_mode:
      self.chal.config(state=DISABLED)

    for spot in self.gui_board.values():
      spot.active = False


  def enable_board(self):
    self.sub.config(state=NORMAL)
    self.pas.config(state=NORMAL)
    self.sav.config(state=NORMAL)

    if self.lan_mode and self.chal_mode:
      self.chal.config(state=NORMAL)

    for spot in self.gui_board.values():
      spot.active = True

  def wait_comp(self):
    self.disable_board()

    self.pl1_info.set('Player: {}'.format(self.cur_player.score))
    self.bag_info.set('{} Tiles in Bag'.format(len(self.bag.bag)))
    self.status_info.set('... Computer\'s Turn ...')

    args = (self.queue, self.opponent, self.bag, self.board, self.dict)
    t = threading.Thread(target=self.get_comp_move, args=args)
    t.start()

    self.process_comp_word()

  def get_comp_move(self, queue, opponent, bag, board, dic):
    word = opponent.move(bag, board, dic)
    queue.put(word)

  def process_comp_word(self):
    if self.queue.empty():
      self.master.master.after(1000, self.process_comp_word)
    else:
      word = self.queue.get()

      if self.opponent.is_passing:
        self.pass_num += 1
      else:
        self.pass_num = 0

        for spot, letter in zip(word.range, word.word):
          if self.gui_board.get(spot, False):
            self.gui_board[spot].letter.set(letter)
            self.gui_board[spot]['bg'] = '#BE975B'
            self.gui_board[spot].active = False

            self.used_spots[spot] = self.gui_board[spot]

            del self.gui_board[spot]

        self.opponent.updateR(self.bag)
        self.opponent.update_score()

        self.set_word_info(word.words)
        self.decorate_rack()

        self.board.place(word.word, word.range)

      self.enable_board()
      self.init_turn()

  def place_tile(self, event):
    start_t_name = type(self.start_tile).__name__
    end_tile = event.widget
    end_t_name = type(end_tile).__name__
    end_t_letter = end_tile.letter

    if start_t_name == 'RackTile' and self.start_tile.letter.get() != '':
      if end_t_name == 'BoardTile' and end_tile.active:
        if end_t_letter.get() == '':
          end_t_letter.set(self.start_tile.letter.get())
          end_tile['bg'] = self.start_tile['bg']

          self.placed_tiles[end_tile.name] = end_tile
          self.spots_buffer.append(end_tile.name)
          self.empty_rack_tiles.append(self.start_tile)

          self.start_tile['bg'] = '#cccccc'
          self.start_tile.letter.set('')
          self.start_tile = None
        else:
          temp = end_t_letter.get()
          end_t_letter.set(self.start_tile.letter.get())
          self.start_tile.letter.set(temp)
          self.start_tile = None
      elif end_t_name == 'RackTile':
        temp = end_t_letter.get()
        end_t_letter.set(self.start_tile.letter.get())

        if end_tile in self.empty_rack_tiles:
          self.empty_rack_tiles.append(self.start_tile)
          del self.empty_rack_tiles[self.empty_rack_tiles.index(end_tile)]

          end_tile['bg'] = '#BE975B'
          self.start_tile['bg'] = '#cccccc'

        self.start_tile.letter.set(temp)
        self.start_tile = None
      else:
        self.start_tile = None
    elif start_t_name == 'BoardTile' and self.start_tile.letter.get() != '' and self.start_tile.active:
      if end_t_name == 'RackTile' and end_t_letter.get() == '':
        del self.placed_tiles[self.start_tile.name]
        del self.empty_rack_tiles[self.empty_rack_tiles.index(end_tile)]

        self.spots_buffer.remove(self.start_tile.name)

        end_t_letter.set(self.start_tile.letter.get())
        end_tile['bg'] = '#BE975B'

        self.determine_tile_background(self.start_tile)

        self.start_tile.letter.set('')
        self.start_tile = None
      elif end_t_name == 'BoardTile' and end_tile.active:
        if end_t_letter.get() == '':
          end_t_letter.set(self.start_tile.letter.get())
          end_tile['bg'] = self.start_tile['bg']

          self.update_buffer_letters(end_tile)
          self.determine_tile_background(self.start_tile)

          del self.placed_tiles[self.start_tile.name]

          self.placed_tiles[end_tile.name] = end_tile

          self.start_tile.letter.set('')
          self.start_tile = None
        elif end_t_letter.get() == self.start_tile.letter.get():
          self.start_tile = None
        else:
          temp = end_t_letter.get()
          end_t_letter.set(self.start_tile.letter.get())
          self.start_tile.letter.set(temp)

          self.update_buffer_letters(end_tile)

          self.placed_tiles[self.start_tile.name] = self.start_tile
          self.placed_tiles[end_tile.name] = end_tile
          self.start_tile = None
    else:
      self.start_tile = end_tile

  def update_buffer_letters(self, tile):
    for spot in self.spots_buffer:
      if spot == self.start_tile.name:
        self.spots_buffer.remove(spot)
        self.spots_buffer.append(tile.name)

  def get_lan_move(self):
    if self.queue.empty():
      self.may_proceed = False
      self.master.master.after(1000, self.process_word)
    else:
      pack = self.queue.get()


      if len(pack) == 3:
        self.bag = pack[1]
        self.pass_num += 1

        self.init_turn()

      elif type(pack[1]) == type(True):

        if pack[1]:
          self.is_challenged = True
          self.challenge(pack)
          self.master.master.after(1000, self.process_word)
        else:
          self.challenge()
      else:
        self.may_proceed = True
        self.is_challenged = False

        self.word, self.w_range, received_tiles, self.prev_spots_buffer, self.players, self.bag, self.board = pack[1:-1]

        self.word.new = True


        for spot, letter in received_tiles.items():
          self.placed_tiles[spot] = self.gui_board[spot]
          self.placed_tiles[spot].letter.set(letter)
          self.placed_tiles[spot].active = False

  def determine_direction(self):

    if len(self.w_range) == 1:

      r = chr(ord(self.w_range[0][0]) + 1) + self.w_range[0][1:]
      l = chr(ord(self.w_range[0][0]) - 1) + self.w_range[0][1:]

      if self.board.board.get(r, False) and re.fullmatch('[A-Z@]', self.board.board[r]):
        self.direction = 'r'
      elif self.board.board.get(l, False) and re.fullmatch('[A-Z@]', self.board.board[l]):
        self.direction = 'r'
      else:
        self.direction = 'd'
    else:

      check1 = self.w_range[0][0]
      check2 = self.w_range[-1][0]


      if check1 == check2:

        digits = sorted([int(x[1:]) for x in self.w_range])
        self.w_range = [check1 + str(x) for x in digits]
        self.w_range.reverse()

        self.direction = 'd'
      else:
        self.direction = 'r'

  def set_raw_word(self):
    for spot in self.w_range:
      self.raw_word.append(self.placed_tiles[spot].letter.get())
      self.set_aob_list(spot)


    offset = 0
    length = len(self.w_range)

    for spot, index, letter in self.aob_list:
      if index < 0:
        index = 0
      elif index > length:
        index = length - 1

      self.raw_word.insert(index + offset, letter)
      self.w_range.insert(index + offset, spot)

      offset += 1

    self.raw_word = ''.join(self.raw_word)

    if ' ' in self.raw_word:
      self.change_wild_tile()

  def get_norm_move(self):
    self.raw_word = []
    self.may_proceed = True


    self.aob_list = []

    self.w_range = sorted(self.placed_tiles)

    self.determine_direction()
    self.set_raw_word()


    aob_list = [x[2] for x in self.aob_list]

    self.word = Word(self.w_range[0], self.direction, self.raw_word, self.board, self.dict, aob_list, self.chal_mode)


    if not self.valid_sorted_letters():
      self.may_proceed = False

  def process_word(self):
    if self.lan_mode and self.own_mark != self.cur_play_mark:
      self.get_lan_move()
    elif self.placed_tiles:
      self.get_norm_move()

    if self.may_proceed and type(self.word) != type(None) and self.word.new and self.word.valid_word():
      self.cur_player.word = self.word
      self.pass_num = 0
      self.wild_tiles = []
      self.prev_words = []

      for spot in self.w_range:
        if spot in self.placed_tiles:
          self.placed_tiles[spot].active = False
          self.used_spots[spot] = self.gui_board[spot]

          del self.gui_board[spot]

      if not self.lan_mode or self.own_mark == self.cur_play_mark:
        self.cur_player.updateR(self.bag)
        self.cur_player.update_score()
        self.prev_spots_buffer = self.spots_buffer.copy()

      self.decorate_rack()

      self.board.place(self.word.word, self.w_range)

      self.set_word_info(self.word.words)

      self.prev_words.append(self.word.word)
      self.prev_words.extend([x[0] for x in self.word.extra_words])

      if self.lan_mode and self.own_mark != self.cur_play_mark:
        for tile in self.placed_tiles.values():
          tile['bg'] = '#BE975B'

      if self.lan_mode:
        self.placed_tiles = {spot:tile.letter.get() for spot, tile in self.placed_tiles.items()}

      self.init_turn()
    else:
      if self.wild_tiles:
        for tile in self.wild_tiles:
          tile.letter.set(' ')

        self.wild_tiles = []

  def set_aob_list(self, spot):
    flag = True

    if self.direction == 'd':

      bef = spot[0] + str(int(spot[1:]) + 1)
      aft = spot[0] + str(int(spot[1:]) - 1)
      check = [x[0] for x in self.aob_list if x[0] == aft or x[0] == bef]

      while flag and not check:

        if aft not in self.gui_board and int(aft[1:]) in range(1, 16):
          self.aob_list.append((aft, self.w_range.index(spot) + 1, self.used_spots[aft].letter.get()))
          aft = aft[0] + str(int(aft[1:]) - 1)
        elif bef not in self.gui_board and int(bef[1:]) in range(1, 16):
          self.aob_list.insert(0, (bef, self.w_range.index(spot) - 1, self.used_spots[bef].letter.get()))
          bef = bef[0] + str(int(bef[1:]) + 1)
        else:
          flag = False
    else:

      bef = chr(ord(spot[0]) - 1) + spot[1:]
      aft = chr(ord(spot[0]) + 1) + spot[1:]
      check = [x[0] for x in self.aob_list if x[0] == aft or x[0] == bef]

      while flag and not check:

        if aft not in self.gui_board and ord(aft[0]) in range(97, 112):
          self.aob_list.append((aft, self.w_range.index(spot) + 1, self.used_spots[aft].letter.get()))
          aft = chr(ord(aft[0]) + 1) + aft[1:]
        elif bef not in self.gui_board and ord(bef[0]) in range(97, 112):
          self.aob_list.insert(0, (bef, self.w_range.index(spot) - 1, self.used_spots[bef].letter.get()))
          bef = chr(ord(bef[0]) - 1) + bef[1:]
        else:
          flag = False

  def valid_sorted_letters(self):
    if self.direction == 'd':

      check1 = int(self.w_range[0][1:])

      check2 = self.w_range[0][0]


      for spot in self.w_range[1:]:

        if int(spot[1:]) != check1 - 1:
          return False


        if spot[0] != check2:
          return False

        check1 -= 1
    else:

      check1 = ord(self.w_range[0][0])

      check2 = self.w_range[0][1:]

      for spot in self.w_range[1:]:

        if ord(spot[0]) != check1 + 1:
          return False


        if spot[1:] != check2:
          return False

        check1 += 1

    return True

  def change_wild_tile(self):

    letter = askstring('Set Wild Tile', 'Enter letter(s):') or '0'
    letter = re.sub('[^A-Z]', '', letter.upper())

    if letter:
      if re.fullmatch('[A-Z]+', letter):
        self.raw_word = re.sub(' ', letter[0], self.raw_word, 1)

        if ' ' in self.raw_word:
          self.raw_word = re.sub(' ', letter[1], self.raw_word, 1)

        for spot in self.w_range:
          try:
            if self.placed_tiles[spot].letter.get() == ' ':
              self.wild_tiles.append(self.placed_tiles[spot])

              if self.chal_mode:
                self.wild_tiles_clone = self.wild_tiles.copy()

              self.board.wild_letters_on_board.append(self.placed_tiles[spot].name)
          except KeyError:
            continue

        for i, tile in enumerate(self.wild_tiles):
          tile.letter.set(letter[i])
          self.cur_player.wild_letters.append(letter[i])
    else:
      self.undo_placement()

  def pass_letters(self):
    letters = askstring('Pass Letters', 'Enter letters to pass:')

    if letters:
      self.letters_passed = True

      for tile in self.gui_board.values():
        if tile.letter.get() != '':
          self.empty_rack_tiles[0].letter.set(tile.letter.get())
          self.empty_rack_tiles[0]['bg'] = '#BE975B'
          del self.empty_rack_tiles[0]

          tile.letter.set('')
          self.determine_tile_background(tile)

      passed_letters = list(re.sub('[^A-Z ]', '', letters.upper()))

      if passed_letters:

        if ' ' in passed_letters and '@' in self.cur_player.letters:
          count1 = self.cur_player.letters.count('@')
          count2 = passed_letters.count(' ')

          for i in range(count2):
            passed_letters.remove(' ')
            passed_letters.append('@')

            if i == count1 - 1:
              break


        while ' ' in passed_letters:
          passed_letters.remove(' ')

        self.cur_player.passed_letters = passed_letters
        self.bag.returnBack(passed_letters)

        self.cur_player.updateR(self.bag)
        self.decorate_rack()

        self.pass_num += 1

        if self.comp_mode:
          self.wait_comp()
        else:
          self.init_turn()

  def challenge(self, pack=None):
    for word in self.prev_words:
      if not self.dict.validWord(word):
        self.players[self.cur_play_mark - 1].update_score(self.word.points)


        if len(self.players[self.cur_play_mark - 1].new_letters) == 7:
          self.players[self.cur_play_mark - 1].update_score(60)


        for letter in self.players[self.cur_play_mark - 1].new_letters:
          self.players[self.cur_play_mark - 1].letters.remove(letter)
          self.bag.returnBack([letter])


        for spot in self.prev_spots_buffer:
          if spot in self.used_spots:
            for tile in self.wild_tiles_clone:
              if spot == tile.name:
                self.board.wild_letters_on_board.remove(spot)
                self.used_spots[spot].letter.set('')
                self.players[self.cur_play_mark - 1].letters.append('@')


            if self.used_spots[spot].letter.get():
              self.players[self.cur_play_mark - 1].letters.append(self.used_spots[spot].letter.get())
              self.used_spots[spot].letter.set('')

            self.board.board[spot] = ' '

            self.used_spots[spot].active = True
            self.determine_tile_background(self.used_spots[spot])

            self.gui_board[spot] = self.used_spots[spot]

            del self.used_spots[spot]

        self.prev_words = []
        self.prev_spots_buffer = []

        if self.lan_mode:
          if self.is_challenged:
            self.players = pack[2]
            self.bag = pack[3]
            self.decorate_rack()
          else:
            self.queue.put((self.own_mark, True, self.players, self.bag))

        self.update_info()

        return True

    if self.lan_mode:
      self.chal_failed = True

    self.init_turn()

    return False

  def check_game_over(self):
    if len(self.bag.bag) == 0:
      for pl in self.players:
        if len(pl.letters) == 0:
          self.end_game()

          return

      self.master.master.after(1000, self.check_game_over)
    elif self.pass_num == 3 * self.play_num:
      self.end_game()
    elif self.point_limit:
      for pl in self.players:
        if type(pl) != type('') and pl.score >= self.point_limit:
          self.end_game()

          return

      self.master.master.after(1000, self.check_game_over)
    else:
      self.master.master.after(1000, self.check_game_over)

  def end_game(self):
    if not self.game_over:
      self.game_over = True

      if self.chal_mode and len(self.bag.bag) == 0 and [pl for pl in self.players if len(pl.letters) == 0]:
        text = 'Will you challenge any of \'{}\'?'.format(', '.join(self.prev_words))
        challenged = askyesno('Challenge', text) and self.challenge()
      else:
        challenged = False

      if not challenged:
        self.determine_winner()

        if self.time_up:
          rea = 'Time Is Up'
        else:
          rea = 'Game Is Over'

        mes = '{} has won with {} points!'.format(self.winner[0].name, self.winner[1])

        self.game_online = False

        self.show_end_game_popup(rea, mes)
      else:
        self.game_over = False

        self.check_game_over()

  def show_end_game_popup(self, reason, message):
    pop = Toplevel(self)
    pop.title(reason)

    self.master.master.update()
    x = self.master.master.winfo_rootx() + 200
    pop.geometry('+{}+{}'.format(x, 300))

    pop.protocol('WM_DELETE_WINDOW', lambda: self.quit_game(pop))

    Label(pop, text=message, font=('times', 30, 'italic')).pack(side=TOP, padx=50, pady=30)

    info_f = Frame(pop)
    info_f.pack(side=TOP)


    for player, subt in self.losers:
      if subt > 0:
        text = '{} {} points for {} left on rack...'.format(player.name, -subt, ', '.join(player.letters))
        Label(info_f, text=text).pack(side=TOP)

    button_f = Frame(pop)
    button_f.pack(side=TOP, pady=20)

    Button(button_f, text='Quit', command=lambda: self.quit_game(pop)).pack(side=LEFT, padx=15)
    Button(button_f, text='Restart', command=self.restart_game).pack(side=LEFT)

    pop.grab_set()
    pop.focus_set()
    pop.wait_window()

  def determine_winner(self):
    bonus_getter = None
    bonus = 0

    for player in self.players:
      if len(player.letters) == 0:
        bonus_getter = player
      else:
        subt = 0

        try:
          for letter in player.letters:
            subt += self.word.letter_points[letter]
            player.update_score(self.word.letter_points[letter])
        except AttributeError:
          pass

        bonus += subt

      self.losers.append((player, subt))

    if bonus_getter:
      bonus_getter.score += bonus

    scores = [player.score for player in self.players]
    points = max(scores)
    winner = self.players[scores.index(points)]

    self.winner = (winner, points)

    if len(self.winner[0].letters) == 0:
      del self.losers[scores.index(points)]

  def quit_game(self, win):
    self.game_online = False

    win.destroy()
    self.destroy()
    self.master.master.quit()

  def restart_game(self):
    self.game_online = False

    self.master.master.geometry('704x420')
    self.master.master.minsize(704, 420)

    self.destroy()

  def save_game(self):
    if not os.path.exists('./saves'):
      os.mkdir('./saves')

    filename = asksaveasfilename(initialdir='saves', defaultextension='.pickle')

    if filename:
      data = {}
      data['play_num'] = self.play_num
      data['players'] = self.players
      data['pass_num'] = self.pass_num
      data['cur_play_mark'] = self.cur_play_mark
      data['chal_mode'] = self.chal_mode
      data['comp_mode'] = self.comp_mode
      data['norm_mode'] = self.norm_mode or self.lan_mode
      data['point_limit'] = self.point_limit
      data['time_limit'] = self.time_limit
      data['bag'] = self.bag
      data['board'] = self.board
      data['op_score'] = self.op_score
      data['seconds'] = self.seconds
      data['minutes'] = self.minutes
      data['turns'] = self.turns

      file = open(filename, 'wb')
      pickle.dump(data, file)


  def destroy(self):
    if self.server_not_found:
      showwarning('Game Not Found', 'There are no hosted games.')
      
      self.server_not_found = False
      self.restart_game()
    elif self.lan_cancelled:
      self.lan_cancelled = False
      self.restart_game()

    if self.lan_mode:
      
      self.queue.put([self.own_mark, False])
      self.thread.join()

    super().destroy()