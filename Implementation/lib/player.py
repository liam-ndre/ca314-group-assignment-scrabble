#Player function

import re

class Player:
	def __init__(self, name=None):
		self.wildLetter = []
		self.word = None
		self.fullbonus = False
		self.passedLetter = []
		self.newLetter = []
		self.name = name
		self.score = 0
		self.letters = []

	def drawLetters(self, bag, amount=7):
		for r in range(amount):
			self.letters.append(self.pick(bag))
			if self.letters[-1] != '$':
				self.newLetter.append(self.letters[-1])
		self.letters = list(re.sub('[^A-Z@]', '', ''.join(self.letters)))

	def updateR(self, bag):
		self.newLetter = []

		if self.passedLetter:
			for letter in self.passedLetter:
				if letter in self.letters:
					self.requestRemoveFile(letter)
		else:
			aob = len(self.word.aob_list) #in word
			for letter in self.word.word: 
				self.requestRemoveFile(letter)
			if len(self.letters) == 0 and len(bag.bag) != 0:
				self.fullbonus = True

		if len(bag.bag) > 0:
			if self.passedLetter:
				self.drawLetters(bag, 7 - len(self.letters))
			else:
				self.drawLetters(bag, len(self.word.word) - aob)

		self.passedLetter = []

	def update_score(self, points=0):
		if points:
			self.score -= points
		else:
			self.score += self.word.calculate_total_points() #in word

			if self.fullbonus:
				self.score += 60

	def pick(self, bag):
		if bag:
			return bag.draw() #in bag

	def requestRemoveFile(self, l):
		if l not in self.wildLetter:
			if self.passedLetter and l in self.letters:
				self.letters.remove(l)
			if l in self.word.aob_list:
				self.word.aob_list.remove(l)
			if l in self.letters:
				self.letters.remove(l)
		else:
			self.letters.remove('@')
			self.wildLetter.remove(l)
