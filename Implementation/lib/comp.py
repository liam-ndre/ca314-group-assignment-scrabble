import itertools, random

from lib.word import Word
from lib.player import Player

class opponentAI(Player):
  # function for move
  def move(self, bag, board, dic):
    self.wild_letters = []
    self.fullbonus = False
    self.is_passing = False

    if '@' in self.letters:
      for i in range(self.letters.count('@')):
        self.letters[self.letters.index('@')] = 'S'
        self.wild_letters.append('S')

    vocabulary = []  # words
    vocab_set = set()  # set of words

    for x in range(2, len(self.letters) + 1):
      vocab_set = vocab_set.union(self.permute(x, dic))

    for word in vocab_set:
      for tile in board.board.keys():
        word_d = Word(tile, 'd', word, board, dic)
        word_r = Word(tile, 'r', word, board, dic)

        if word_d.valid_word():
          vocabulary.append(word_d)

        if word_r.valid_word():
          vocabulary.append(word_r)

    if len(vocabulary) == 0:
      self.is_passing = True
      self.pass_letters(bag)
    else:
      self.word = vocabulary[0]

      for i in range(len(self.wild_letters)):
        if 'S' in self.word.word:
          self.word.wild_letters.append(self.word.range[self.word.word.index('S')])

      for word in vocabulary:
        for i in range(len(self.wild_letters)):
          if 'S' in word.word:
            word.wild_letters.append(word.range[word.word.index('S')])

        if word.calculate_total_points() > self.word.calculate_total_points():
          self.word = word

      for _ in self.wild_letters:
        self.letters[self.letters.index('S')] = '@'

      return self.word

  # function to pass letters
  def pass_letters(self, bag):
    passedLetters = random.sample(self.letters, 3)

    for l in passedLetters:
      self.letters.remove(l)

    bag.returnBack(passedLetters)
    self.drawLetters(bag, len(passedLetters))
  
  # function to permute vocabular/words
  def permute(self, n, dic):
    vocabulary = set()
    perms = itertools.permutations(self.letters, n)

    for perm in perms:
      if dic.validWord(''.join(perm)):
        vocabulary.add(''.join(perm))

    return vocabulary