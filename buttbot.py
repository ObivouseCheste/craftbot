#from amde with butts

from ircbot import IrcBot
import random

class ButtBot(IrcBot):
	''' does the butts '''
	def __init__(self, **kwargs):
		super().__init__(**kwargs)
		self.dobutt = True
		self.loopfuncs += [self.butt, self.tipbutt]

	def makebutt(self, w):
		if len(w) > 3:
			if(w[-3:] == "ing"):
				return "butting"
			if(w[-2:] == "'s"):
				return "butt's"
			if(w[-1:] == "s"):
				return "butts"
		return "butt"

	def dobuttmsg(self):
		if self.dobutt:
			self.dobutt = False
			return True
		if random.randrange(10) == 0:
			return True
		return False
	
	def butt(self):
		msg = self.m['msg']
		if self.dobuttmsg() == True:
			newmsg = []
			mybool = False
			for w in msg.split():
				if random.randrange(4) == 0:
					w = self.makebutt(w)
					mybool = True
				newmsg.append(w)
			if mybool == True:
				self.say(' '.join(newmsg), self.m['target'])

	def tipbutt(self):
		if "thank you, buttbot" in self.m['msg'].lower() or "thank you buttbot" in self.m['msg'].lower():
			self.say("\u0001ACTION tips butt\u0001", self.m['target'])
		else:
			if "buttbot" in self.m['msg'].lower():
				self.dobutt = True

if __name__ == "__main__":
	ButtBot(name="buttbot").loop()
