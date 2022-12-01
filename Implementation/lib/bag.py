import random

class Bag:
	def __init__(self):
		self.srabbleBag = []
		self.insertinBag()

	def insertinBag(self):
		self.srabbleBag.extend(['Q','Z','J','X','K'])
		
		for i in range(2): self.srabbleBag.extend(['F','H','V','W','Y','B','C','M','P','@'])
		for i in range(3): self.srabbleBag.extend(['G'])
		for i in range(4): self.srabbleBag.extend(['D','U','S','L'])
		for i in range(6): self.srabbleBag.extend(['T','R','N'])
		for i in range(8): self.srabbleBag.extend(['O'])
		for i in range(9): self.srabbleBag.extend(['I','A'])
		for i in range(12): self.srabbleBag.extend(['E'])
	def returnBack(self, let):
		self.srabbleBag.extend(let)

	def draw(self):
		random.shuffle(self.srabbleBag)
		try:
			return self.srabbleBag.pop()
		except IndexError:
			return '$'
