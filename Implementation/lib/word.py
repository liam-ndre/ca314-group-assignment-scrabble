import re

# creates a class called Word
class Word:
  def __init__(self, start, direction, word, board, dictionary, aob=[], chal=False):
    self.start = start
    self.direction = direction
    self.word = word
    self.board = board
    self.dict = dictionary
    self.aob_list = aob
    self.challenge_mode = chal

    self.points = 0
    self.words = {}
    self.new = True
    self.valid = False
    self.extra_words = []
    self.wild_letters = []

    self.range = self.__set_range()
    self.letter_points = self.__set_letter_points()

  # function to calculate the points of a word
  def __set_letter_points(self):
    points = {}

    for letter in 'LSUNRTOAIE':
      points[letter] = 1

    for letter in 'GD':
      points[letter] = 2

    for letter in 'BCMP':
      points[letter] = 3

    for letter in 'FHVWY':
      points[letter] = 4

    for letter in 'JX':
      points[letter] = 8

    for letter in 'QZ':
      points[letter] = 10

    points['K'] = 5
    points['@'] = 0

    return points

  # function to process extra words
  def process_extra_words(self):
    check_list = []
    aob_list = self.aob_list.copy()

    for letter_index, square in enumerate(self.range):
      extra_word = [[self.word[letter_index]], [square]]

      if self.board.board[square] in aob_list and self.board.square_taken(square, self.direction):
        del aob_list[aob_list.index(self.board.board[square])]
        check_list.append(True)
      elif not self.board.square_taken(square, self.direction):
        check_list.append(True)
      else:
        self.extra_words.append(self.__set_extra_word(square, extra_word))

        if self.challenge_mode or self.dict.validWord(self.extra_words[-1][0]):
          check_list.append(True)
        else:
          self.invalid_word = self.extra_words[-1][0]
          self.extra_words = []
          check_list.append(False)

    return not (False in check_list)

  # function to calculate the total points
  def calculate_total_points(self):
    if not self.range:
      self.points = 0
      return self.points

    bonus = self.board.calculate_bonus(self.range)
    self.word_bonus = bonus.get('word', None)
    self.letter_bonus = bonus.get('letter', None)

    self.points = self.__calculate_word_points(self.word, self.range)

    for word, word_range in self.extra_words:
      self.points += self.__calculate_word_points(word, word_range)

    return self.points

  # function to validate the move made
  def valid_move(self):
    if not self.range:
      return False

    for square in self.range:
      if self.aob_list:
        return True
      elif self.board.square_taken(square, self.direction):
        return True

    if self.start == 'h8':
      return True

    return False

  # function to validate the word
  def valid_word(self):
    if self.valid:
      return True
    else:
      if not self.valid_move():
        return False

      if not self.challenge_mode:
        if not self.dict.validWord(self.word):
          return False

      if not self.process_extra_words():
        return False

      self.new = False
      self.valid = True

      return True

  def __set_range(self):
    if self.direction == "r":
      squares = self.__set_range_to_right()
    else:
      squares = self.__set_range_to_down()

    for s in squares:
      if not re.fullmatch('[a-o]1[0-5]|[a-o][1-9]', s):
        return False

    if not self.board.valid_range(squares, self.word, self.direction):
      return False

    return squares

  def __set_range_to_right(self):
    last = chr((ord(self.start[0]) + len(self.word)))

    if len(self.start) == 2:
      letter_range = range(ord(self.start[0]), ord(last))

      return list(map(lambda x: chr(x) + self.start[1], letter_range))

    else:
      letter_range = range(ord(self.start[0]), ord(last))

      return list(map(lambda x: chr(x) + self.start[1:], letter_range))

  def __set_range_to_down(self):
    if len(self.start) == 2:
      last = int(self.start[1]) - len(self.word)
      number_range = range(int(self.start[1]), last, -1)

      return list(map(lambda x: self.start[0] + str(x), number_range))
    else:
      last = int(self.start[1:]) - len(self.word)
      number_range = range(int(self.start[1:]), last, -1)

      return list(map(lambda x: self.start[0] + str(x), number_range))

  def __set_up_or_left_extra_word(self, square, extra_word):
    while self.board.taken(square, self.direction, self.board.up_or_left):
      square = self.board.up_or_left(square, self.direction)
      extra_word[0].insert(0, self.board.board[square])
      extra_word[1].insert(0, square)

  def __set_down_or_right_extra_word(self, square, extra_word):
    while self.board.taken(square, self.direction, self.board.down_or_right):
      square = self.board.down_or_right(square, self.direction)
      extra_word[0].append(self.board.board[square])
      extra_word[1].append(square)

  def __set_extra_word(self, square, extra_word):
    self.__set_up_or_left_extra_word(square, extra_word)
    self.__set_down_or_right_extra_word(square, extra_word)
    extra_word[0] = ''.join(extra_word[0])

    return extra_word

  def __calculate_word_points(self, word, word_range):
    word_points = 0

    for letter, square in zip(word, word_range):
      if square in self.wild_letters:
        continue
      elif square in self.board.wild_letters_on_board:
        continue
      else:
        if self.letter_bonus:
          word_points += self.letter_bonus.get(square, 1) * self.letter_points[letter]
        else:
          word_points += self.letter_points[letter]

    if self.word_bonus:
      for square in word_range:
        if square != 'h8' or not self.aob_list:
          word_points *= self.word_bonus.get(square, 1)

    self.words[word] = word_points

    return word_points