from tkinter import *
import random, platform
from lib.gui.gamePage import GamePage

class StartPage(Frame):
  def __init__(self, par, dictionary='./dics/sowpods.txt'): #go through the dictionary
    self.parent = par
    self.dictionary = dictionary

    self.challengeVar = IntVar()
    self.butVar = StringVar()
    self.timeVar = IntVar()
    self.pointVar = IntVar()

    Frame.__init__(self, par, bg='#824b30')
    self.grid(row=0, column=0, sticky=S+N+E+W)
    self.butVar.set('Start Game')
    self.play_ents = []

    self.drawH()
    self.draw_player_name()

    self.opt_cont = Frame(self, bg='#824b30')
    self.opt_cont.pack(side=TOP, padx=96)

    self.playerDraw()
    self.drawSecO()

  def drawH(self):
    Label(self, text='Game Settings', font=('lucida', 35), bg='#824b30', pady=40).pack(side=TOP)

  def drawSecO(self):
    cb = Checkbutton(self, bg="#824b30", text='Challenge Mode', variable=self.challengeVar)
    cb.pack(pady=15)
    cb.deselect()
    f1 = Frame(self, bg='#824b30')
    f1.pack()

    Label(f1, bg='#824b30', text='Time Limit:').pack(side=LEFT)

    Entry(f1, textvariable=self.timeVar, width=3).pack(side=LEFT)
    self.timeVar.set(0)

    f2 = Frame(self, bg='#824b30')
    f2.pack(pady=5)

    Label(f2, bg='#824b30', text='Point Limit:').pack(side=LEFT)

    Entry(f2, textvariable=self.timeVar, width=3).pack(side=LEFT)
    self.timeVar.set(0)

    f3 = Frame(self, bg='#824b30')
    f3.pack(pady=10)

    Button(f3, text="Back", command=self.destroy).pack(side=LEFT, padx=10)
    Button(f3, textvariable=self.butVar, command=self.optConstruct).pack(side=LEFT)
    
  def draw_player_name(self): pass
  def optConstruct(self): pass
  def playerDraw(self): pass


class LANStartPage(StartPage):
  def playerDraw(self):
    self.butVar.set('Start Game')
    f = Frame(self.opt_cont, pady=10, bg='#824b30')
    f.pack()
    self.nameVar = StringVar()

    Label(f, text='Enter Your Name:', bg='#824b30').pack(side=LEFT)

    ent = Entry(f, textvariable=self.nameVar)
    ent.pack(side=LEFT)
    ent.focus_set()

    self.play_var = IntVar()
    self.play_dict = {'2 players': 2,
                      '3 players': 3,
                      '4 players': 4
                     }

    pof = LabelFrame(self.opt_cont, bg='#824b30', pady=10, padx=10)
    pof.pack()

    for k, v in self.play_dict.items():
      r = Radiobutton(pof, bg="#824b30", text=k, variable=self.play_var, value=v)
      r.pack(anchor=NW)

    self.play_var.set(2)

  def optConstruct(self):

    self.options = {}
    self.options['names'] = [self.nameVar.get()]
    self.options['lan_mode'] = True
    self.options['time_limit'] = self.timeVar.get()
    self.options['play_num'] = self.play_var.get()
    self.options['chal_mode'] = bool(self.challengeVar.get())
    self.options['point_limit'] = self.pointVar.get()

    self.parent.master.set_geometry()

    self.parent.master.child = GamePage(self.parent, self.options)

    self.destroy()

class NormalStartPage(StartPage):
  def playerDraw(self):
    self.butVar.set('Next')

    self.play_var = IntVar()
    self.play_dict = {'2 players': 2,
                      '3 players': 3,
                      '4 players': 4}

    pof = LabelFrame(self.opt_cont, bg='#824b30', pady=10, padx=10)
    pof.pack()

    for k, v in self.play_dict.items():
      r = Radiobutton(pof, bg="#824b30", text=k, variable=self.play_var, value=v)
      r.pack(anchor=NW)

    self.play_var.set(2)

  def draw_name_fields(self):
    self.parent.master.geometry('900x500')  #not here
    self.parent.master.minsize(900, 500)  #not here

    t = Frame(self, pady=20, padx=10, bg='#824b30')
    t.pack()

    for p in range(1, self.play_var.get() + 1):
      var = StringVar()

      f = Frame(t, bg='#824b30')
      f.pack(side=TOP)

      Label(f, text='Enter Player {}\'s name:'.format(p), bg='#824b30').pack(side=LEFT)

      ent = Entry(f, textvariable=var)
      ent.pack(side=LEFT)

      if p == 1:
        ent.focus_set()

      self.play_ents.append(ent)

  def getNames(self):
    names = []
    for name in self.play_ents:
      names.append(name.get().strip().capitalize())
    self.options = {'names': names}
    random.shuffle(self.options['names'])

  def optConstruct(self):
    if self.play_ents:
      self.getNames()

      self.options['normal_mode'] = True
      self.options['time_limit'] = self.timeVar.get()
      self.options['play_num'] = self.play_var.get()
      self.options['chal_mode'] = bool(self.challengeVar.get())
      self.options['point_limit'] = self.pointVar.get()

      self.parent.master.set_geometry()

      GamePage(self.parent, self.options, self.dictionary)
      self.destroy()

    else: 
      self.draw_name_fields() #start the game
      self.butVar.set('Start Game') 
