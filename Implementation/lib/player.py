#Player function

import re

class Player:
	def __init__(self, name=None):
		self.wildLetter = []
		self.word = None
		self.bonus = False
		self.passedLetter = []
		self.newLetter = []
		self.name = name
		self.score = 0
		self.letters = []

	def drawLetters(self, scrabbleBag, amount=7):
		for r in range(amount):
			self.letters.append(self.pick(scrabbleBag))
			if self.letters[-1] != '$':
				self.newLetter.append(self.letters[-1])
		self.letters = list(re.sub('[^A-Z@]', '', ''.join(self.letters)))
	
	def requestRemoveFile(self, l):
		if l not in self.wildLetter:
			if self.passedLetter and l in self.letters:
				self.letters.remove(l)
			elif l in self.word.aob_list:
				self.word.aob_list.remove(l)
			else:
				self.letters.remove(l)
		else:
			self.letters.remove('@')
			self.wildLetter.remove(l)

	def updateR(self, scrabbleBag):
		self.newLetter = []

		if self.passed_letters:
			for letter in self.passed_letters:
				if letter in self.letters:
					self.requestRemoveFile(letter)
		else:
			aob = len(self.word.aob_list) #in word
			for letter in self.word.word: 
				self.requestRemoveFile(letter)
			if len(self.letters) == 0 and len(scrabbleBag.scrabbleBag) != 0:
				self.full_bonus = True

		if len(scrabbleBag.scrabbleBag) > 0:
			if self.passed_letters:
				self.drawLetters(scrabbleBag, 7 - len(self.letters))
			else:
				self.drawLetters(scrabbleBag, len(self.word.word) - aob)

		self.passed_letters = []

	def update_score(self, points=0):
		if points:
			self.score -= points
		else:
			self.score += self.word.calculate_total_points() #in word

			if self.full_bonus:
				self.score += 60

	def pick(self, scrabbleBag):
		if scrabbleBag:
			return scrabbleBag.draw() #in bag
