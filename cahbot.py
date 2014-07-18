#cards against humanity irc bot
#by amade and Bisukottishefu with help from the other Craftsmen

import random
#from path import path
from ircbot import IrcBot

class CahPlayer():
    def __init__(self, name):
        self.name = name
        self.deck = []
        self.points = 0

    def addCard(self, cards = []):
        for card in cards:
            self.deck.extend(card)

    def removeCard(self, card):
        return self.deck.pop(card)

    def getCards(self):
        return self.deck

    def changePoints(self, mod):
        self.points += mod

    def getPoints(self):
        return self.points

    def getName(self):
        return self.name

class CahBot(IrcBot):
    def __init__(self, name = 'CahBot', **kwargs):
        super().__init__(name, **kwargs)
        self.loopfuncs.append(self.receiveMsg)
        #variable definitions
        #self.game = False #whether a game is in progress
        self.phase = 0 #phases: 0:no game, 1:waiting for players to join game, 2:waiting for players to play cards, 3:waiting for players to vote on cards
        self.players = {}
        self.playedcards = {}
        self.votes = {}
        self.questions = []
        self.roundquestion = ""
        self.answers = []
        self.roundsleft = 0
        
    def receiveMsg(self):
        msg = self.m['msg'].lower()
        if msg == "!help" or msg == '!help ':
            self.say('List of commands (enter !help commandname (e.g. !help startcah) to view detailed help about that command):')
            self.say('!startcah !joingame !leavegame !loadquestions !loadanswers !startround !play !roundsleft !endround !vote !endcah')
        if msg[0:7] == '!help !':
            msg = msg[0:6] + msg[7:] #cut out the extra exclamation point - rest of this thread should proceed normally
        if msg == '!help startcah':
            self.say('Syntax: !startcah [rounds]')
            self.say('Begins a new game of Cards Against Humanity that will last for a specified number of rounds. If no number of rounds is specified, 5 rounds will be played. After entering this command, players can join the game with the !joingame command. Once players have joined, enter !startround to advance to the first round.')
        elif msg == '!help joingame':
            self.say('Syntax: !joingame')
        elif msg == '!help loadquestions':
            self.say('Syntax: !loadquestions [clear] [deck1 deck2 deck3 ...]')
            self.say('Enter clear as the first word after !loadquestions to overwrite the current loaded question decks. If no decks are specified, the default Cards Against Humanity deck will be loaded. This deck is also automatically loaded at the start of a game if no decks have been loaded yet. You can use !decks to obtain a list of available decks.')
        elif msg == '!help leavegame':
            self.say('Syntax: !leavegame')
            self.say('This command will delete you from the game as a player. Note that you stop showing up in the scores if you do this.')
        elif msg == '!help loadanswers':
            self.say('Syntax: !loadquestions [clear] [deck1 deck2 deck3 ...]')
            self.say('Enter clear as the first word after !loadquestions to overwrite the current loaded answer decks. If no decks are specified, the default Cards Against Humanity deck will be loaded. This deck is also automatically loaded at the start of a game if no decks have been loaded yet. You can use !decks to obtain a list of available decks.')
        elif msg[0:9] == '!startcah' and self.phase == 0: #start a new game if there is none
            msg = msg[10:]
            rounds = None
            if msg.isdigit():
                rounds = int(msg)
            self.startGame(rounds)
        elif self.phase < 2: #game is not in play or vote phase
            if msg[0:15] == '!loadquestions ':
                msg = msg[15:].split()
                clear = False
                if msg[0] == 'clear':
                    clear = True
                    msg = msg[1:]
                self.loadQuestionDecks(msg, clear)
            elif msg[0:13] == '!loadanswers ':
                msg = msg[13:].split()
                clear = False
                if msg[0] == 'clear':
                    clear = True
                    msg = msg[1:]
                self.loadAnswerDecks(msg, clear)
        elif self.phase != 0: #game is in progress
            if msg[0:10] == '!leavegame':
                self.removePlayer(self.m['sender'])
            if msg[0:7] == '!endcah':
                self.endGame()
            if msg[:11] == '!roundsleft':
                self.say("There are currently " + self.roundsleft + " rounds left.")
        if self.phase == 1: #waiting for players to join game
            #for now players can only join before the game starts. ideally this will change in the future
            if msg[0:9] == '!joingame':
                self.addPlayer(self.m['sender'])
            if msg[0:11] == '!startround':
                self.startRound()
        elif self.phase == 2: #waiting for players to play cards
            if msg[0:6] == '!play ':
                msg = msg[6:]
                player = self.players[self.m['sender']]
                if not player:
                    self.say('You aren\'t in this game!', self.m['sender'])
                msg = msg[6:]
                if msg.isdigit() and msg <= 5: #play card by number
                    card = player.removeCard(msg)
                    self.playedcards[player] = card
                    self.checkPhaseEnd()
                else: #play card by name
                    cards = player.getCards()
                    selected = None
                    for card in cards:
                        if card.lower() == msg:
                            selected = card
                            break
                    if not selected:
                        self.say('Could not find card "' + msg + '"', self.m['sender'])
                    else:
                        self.playedcards[player] = card
                        self.checkPhaseEnd()
                #else: #error
                    #self.say('Error in reading play. You may want to try entering !help play', self.m['sender'])
        elif self.phase == 3: #waiting for players to vote on cards
            if msg[0:6] == '!vote ':
                msg = msg[6:]
                if msg.isdigit(): #vote by number
                    self.votes[self.m['sender']] = msg
                    i = 1
                    pickedcard = ''
                    for player, card in self.playedcard:
                        i += 1
                        if i == msg:
                            pickedcard = card
                    if not len(pickedcard):
                        self.say('Couldn\'t find card ' + msg + '. Please confirm that your number corresponds to a played card.', self.m['sender'])
                    else:
                        self.say('Vote for "' + self.playedcard[msg] + '" acknowledged.', self.m['sender'])
                else: #didn't give us a number
                    self.say('Please vote by entering the number corresponding to your choice.', self.m['sender'])

    def addPlayer(self, playername):
        for name, player in self.players.items(): #ValueError: too many values to unpack (expected 2)
            if player.getName() == playername:
                self.say('You are already in this game.')
                return False
        self.players[playername] = CahPlayer(playername)
        self.dealCards([self.players[playername]], 5)

    def removePlayer(self, playername):
        del self.players[playername]

    def errorMsg(self, reason):
        self.say('/me softly poots a ' + reason + ' flavored poot')
        #the following should go in any exception catchin things:
        #reason = sys.exc_info()[0]
        #errorMsg(reason)
                  
    def startGame(self, rounds = 5):
        if(self.phase == 0):
            self.phase = 1
            if len(self.questions) == 0:
                self.loadQuestionDecks()
            if len(self.answers) == 0:
                self.loadAnswerDecks()
            self.say("A game of Cards Against Humanity / Apples to Apples / Tiramisu is starting! Enter !joingame to join, or !help for help.")
            #start a timer here that waits until the game starts

    def startRound(self):
        self.roundsleft -= 1
        self.say("A new round has started! The question for this round is:")
        self.roundquestion = random.choice(self.questions)
        self.questions.remove(self.roundquestion)
        self.say(self.roundquestion)
        self.phase = 2

    def checkPhaseEnd(self):
        end = True
        if phase == 2: #play cards phase: ends when all players have played a card
            for player in self.players:
                if not self.playedcard[player]:
                    end = False
                    break
            if end:
                self.endRound()
        elif phase == 3: #vote on cards phase: ends when all players have voted
            for player in self.players:
                if not self.votes[player]:
                    end = False
                    break
            if end:
                self.endVoting()

    def endRound(self):
        '''End the play cards phase and begin the voting phase'''
        count = 1
        self.say('The cards are in! Vote with !vote X where X is the number of your choice for the card you think best answers or completes this sentence:')
        self.say(self.roundquestion)
        self.questions.add(self.roundquestion) #replace this question in the deck of questions
        for player, card in self.playedcard.items():
            self.say(count + '. ' + card)
            count += 1

    def endVoting(self):
        '''End the voting phase and either start a new round or end the game'''
        votecount = {}
        for player, vote in self.votes.items():
            votecount[vote] += 1
        winners = []
        highest = 0
        for answer, tally in votecount.items():
            if tally > highest:
                highest = tally
                winners = [answer]
            elif tally == highest:
                winners.extend(answer)
        self.say('Winner(s) of this round:')
        for winner in winners:
            for player, card in self.playedcards.items():
                if card == winner:
                    self.players[player].changePoints(1) #give a point
                    self.say(player)
        for player, card in self.playedcards.items():
            self.answers.add(card)
            self.players[player].removeCard(card)
            self.dealCard(self.players[player], 1)
        if self.roundsleft > 0:
            self.startRound()
        else:
            self.endGame()

    def endGame(self):
        if self.phase != 0:
            self.announceScores()
            self.phase = 0
            self.players = {}
            self.roundsleft = 0
            self.say("Game over! Say !startcah to make a new one.")

    def announceScores(self):
        if(self.phase != 0):
            victors = []
            count = 1
            for player in self.players:
                victors += player
            self.say("Current scores:")
            while len(victors) > 0:
                winner = victors[0]
                for player in victors:
                    if player.getPoints() > winner.getPoints():
                        winner = player
                victors.remove(winner)
                self.say(count + ". " + victors.getName())
                count += 1

    def loadQuestionDecks(self, files = ["./CAH decks/questions/cardsagainsthumanity.txt"], clear = True):
        #load question decks for playing.
        if clear == True:
            self.questions = []
        for filenames in files:
            lines = open(filenames, 'r')
            self.questions.extend(lines.read().split("\n"))
            self.say("Loaded question deck " + filenames)

    def loadAnswerDecks(self, files = ["./CAH decks/answers/cardsagainsthumanity.txt"], clear = True):
        #load answer decks for playing.
        if clear == True:
            self.answers = []
        for filenames in files:
            lines = open(filenames, 'r')
            self.answers.extend(lines.read().split("\n"))
            self.say("Loaded answer deck " + filenames)

    def dealCards(self, players = [], number = 1):
        #deal number cards each to players
        for player in players:
            for i in range(number):
                card = random.choice(self.answers)
                self.answers.remove(card)
                player.addCard(card)
                self.say('You received this card: ' + card, player.getName())
            
    #def listDecks(self):
        #list the decks that can be loaded
        #for files in path('/CAH decks').files(pattern='*.txt'):
            #list decks here lol
        
if __name__ == "__main__":
    CahBot('CahBot').loop()
