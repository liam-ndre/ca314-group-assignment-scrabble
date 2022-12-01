from collections import defaultdict

class Dict:
  def __init__(self, dic):
    vocabulary = open(dic).read().splitlines()

    self.dict = defaultdict(lambda: False)
    
    for vocab in vocabulary:
      self.dict[vocab] = True

  def validWord(self, vocab):
    return self.dict[vocab]
