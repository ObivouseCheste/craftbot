#a set of ircbot games
#by cheemo

import random
from ircbot import IrcBot

class GuessBot(IrcBot):
    ''' guess a number between 1 and 100! '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs.append(self.guessgame)
        self.mynum = 0
    def guessgame(self):
        msg = self.m['msg']
        if msg == "!initiate guess":
            print("Game initiation received")
            self.loopfuncs.append(self.guess)
            self.mynum = random.randrange(1,101)
            print("My number is " + str(self.mynum))
            self.loopfuncs.remove(self.guessgame)
            self.say("I've thought of a number between 1 and 100. Guess with '!guess <number>'!", self.m['target'])
    def guess(self):
        msg = self.m['msg']
        if msg[0:7] == "!guess ":
            msg = msg[7:]
            try:
                if int(msg) == self.mynum:
                    self.loopfuncs.remove(self.guess)
                    self.loopfuncs.append(self.guessgame)
                    self.say("That's correct!", self.m['target'])
                elif int(msg) > 100:
                    self.say("That's WAY too high. Do you need some !help?", self.m['target'])
                elif int(msg) > self.mynum and int(msg) < 101:
                    self.say("Bit too high.", self.m['target'])
                elif int(msg) < self.mynum and int(msg) > 0:
                    self.say("Bit too low.", self.m['target'])
            except:
                self.say("I'm afraid you didn't give me a number.")
class AcrotopiaBot(IrcBot):
    ''' acrotopia bot. gives from 4 to 7 random letters and players make an
    acronym from them'''
    ''' !initiate begins the game. !play <acronym submission> submits.
    !endsubmit begins voting. !vote <number> votes.'''

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs.append(self.acrogame)
    def acrogame(self):
        letters = list("abcdefghijklmnopqrstuvwxyz")
        if self.m['msg'] == "!initiate acrotopia":
            self.sequence = []
            self.players = []
            self.submits = []
            self.points = []
            print("Game initiation received")
            self.loopfuncs.append(self.submit)
            self.loopfuncs.remove(self.acrogame)
            ''' remove ability to start a new game and then get 4-7 letters '''
            for i in range(1,random.randrange(5,9)):
                self.sequence.append(letters[random.randrange(0,26)])
            self.say("Let's play Acrotopia! Just give me an acronym made from my"
            +" sequence: " + " ".join(self.sequence))
            self.say("To submit your acronym, just begin your message with !play"
            +" and I'll check if it's valid.")
    def submit(self):
        msg = self.m['msg']
        sent = self.m['sender']
        if msg[0:6] == "!play ":
            msg = msg[6:]
            if sent not in self.players:
                attempt = msg.split(" ")
                i = 0
                for word in attempt: #check if their submission checks out
                    checker = list(word)
                    if checker[0] != self.sequence[i]:
                        self.say("Sorry, friend, that's not an appropriate submi"+
                            "ssion.", self.m['target'])
                        return
                    else:
                        i += 1
                self.players.append(sent)
                self.submits.append(msg)
                self.points.append(0)
                self.say("Hey, nice submission! Got it, %s." % sent, self.m['target'])
                self.loopfuncs.append(self.end)
            else:
                attempt = msg.split(" ")
                i = 0
                for word in attempt:
                    checker = list(word)
                    if checker[0] != self.sequence[i]:
                        self.say("Sorry, but you can't replace your old submissi"
                            +"on; this one's not valid.", self.m['target'])
                        return
                    else:
                        i += 1
                self.submits.pop(self.players.index(sent))
                self.points.pop(self.players.index(sent))
                self.players.pop(self.players.index(sent))
                self.say("Nice resubmission. I'm sure it's better.", self.m['target'])
                self.submits.append(msg)
                self.players.append(sent)
                self.points.append(0)

    def end(self):
        if self.m['msg'] == "!endsubmit":
            self.loopfuncs.remove(self.submit)
            self.loopfuncs.remove(self.end)
            self.say("Alright! The submission phase is over. Here's all I have: ")

            for i in range(len(self.players)):
                print(self.players[i])
                self.say("%s. '%s'" % (str(i+1),  self.submits[i]))
            self.say("Vote for a submission by saying !vote <number>.")
            self.loopfuncs.append(self.vote)
    def vote(self):
        msg = self.m['msg']
        sent = self.m['sender']
        voters = []
        if msg[0:6] == "!vote ":
            msg = msg[6:]
            if sent not in voters:
                try:
                    if int(msg) > len(self.points):
                        self.say("That's not a valid vote.", self.m['target'])
                        return
                    else:
                        voters.append(self.m['sender'])
                        self.points[int(msg)-1] += 1
                        self.loopfuncs.append(self.endvote)
                        self.say("Thanks for the vote.", self.m['target'])
                        return
                except:
                    self.say("That's not a valid vote.", self.m['target'])
            else:
                self.say("You've already voted.", self.m['target'])
    def endvote(self):
        if self.m['msg'] == "!endvote":
            self.loopfuncs.remove(self.endvote)
            self.loopfuncs.remove(self.vote)
            self.loopfuncs.append(self.acrogame)
            self.say("Voting has ended and the results are in!")
            for i in range(len(self.players)):
                self.say("%s points: %s's '%s'." % (str(self.points[i]), self.players[i], self.submits[i]))
            return

if __name__ == "__main__":
    class GameBot(AcrotopiaBot, GuessBot):
        ''' all games '''
        pass
    GameBot(name="cmengamebot").loop()
