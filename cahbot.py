#cards against humanity, irc bot, recoding
#by amde with coding and support from the craftsmen

import random
#from path import path
from ircbot import IrcBot

class CahPlayer:
    def __init__(self, name):
        self.name = name
        self.hand = []
        self.points = 0
        self.playedcard = ''
        self.playedcardnum = 5 #number of last played card, so that the new one can be placed in the hand in this position
        self.vote = '' #vote cast
        self.votes = 0 #votes received

    def __eq__(self, other):
        return self.name == other

    def __ne__(self, other):
        return self.name != other

    def __ge__(self, other):
        if isInstance(other, CahPlayer):
            return self.points >= other.points

class CahBot(IrcBot):
    def __init__(self, name = 'CahBot', **kwargs):
        super().__init__(name, **kwargs)
        self.loopfuncs.append(self.receiveMsg)
        #variable definitions
        self.phase = 0 #0 = no game; 1 = wait for player join; 2 = wait for players to play cards; 3 = wait for players to vote on cards
        self.roundsleft = 0
        self.players = [] #list of players (CahPlayer class)
        self.questions = [] #list of questions players can answer
        self.answers = [] #list of answers players can receive to play
        self.currentquestion = "" #the current round question
        self.votingdict = {} #dictionary mapping player names to numbers
        self.reversedict = {} #dictionary mapping numbers back to player names

    def receiveMsg(self):
        '''Message handler. See IrcBot.loop'''
        msg = self.m['msg']
        if msg[0:5] == '!help':
            msg = msg[6:]
            #remove extra leading ! if present
            if len(msg) > 0 and msg[0] == '!':
                msg = msg[1:]
            if not msg.strip(): #message consists only of whitespace: display general help
                self.say('Function list: !startcah [rounds], !joingame, !leavegame, !hand, !roundsleft, !play [card], !endround, !vote [number], !endvote, !scores, !endgame, !loadquestions [*clear deck1 deck2...], !loadanswers [*clear deck1 deck2...]', self.m['target'])
                self.say('Enter !help [function name] to learn more about a function, e.g. !help startcah', self.m['target'])
            elif msg[0:8] == 'startcah':
                self.say('Syntax: !startcah [rounds]. Starts a new game of Cards Against Humanity with the specified number of rounds (5 if not specified). Example: !startcah 15', self.m['target'])
            elif msg[0:8] == 'joingame':
                self.say('Syntax: !joingame. Adds you to the current game. Example: !joingame', self.m['target'])
            elif msg[0:4] == 'hand':
                self.say('Syntax: !hand. Shows you all cards currently in your hand. Example: !hand', self.m['target'])
            elif msg[0:10] == 'roundsleft':
                self.say('Syntax: !roundsleft. Shows you how many rounds are left in the current game.', self.m['target'])
            elif msg[0:10] == 'startround':
                self.say('Syntax: !startround. Begins a round by giving the players a question and allowing them to play cards to answer it. Example: !startround', self.m['target'])
            elif msg[0:4] == 'play':
                self.say('Syntax: !play [card]. Plays the specified card as an answer to the round question. The card can either be the number corresponding to the card\'s position in your hand (try !hand) or the text of the card itself (make sure to be exact). Example: !play 1', self.m['target'])
            elif msg[0:8] == 'endround':
                self.say('Syntax:: !endround. Causes the current round to come to an end, beginning a voting round for the best answer. Example: !endround', self.m['target'])
            elif msg[0:4] == 'vote':
                self.say('Syntax: !vote [number]. Casts your vote for an answer with the specified number. Please don\'t vote for yourself! Example: !vote 1', self.m['target'])
            elif msg[0:7] == 'endvote':
                self.say('Syntax: !endvote. Forces voting to come to an end, causing the next round to start or the game to end, depending on if there are rounds left (try !roundsleft). Example: !endvote', self.m['target'])
            elif msg[0:6] == 'scores':
                self.say('Syntax: !scores. Shows you the current scores of all active players. Example: !scores', self.m['target'])
            elif msg[0:7] == 'endgame':
                self.say('Syntax: !endgame. Forces an end to the current game. Example: !endgame', self.m['target'])
            elif msg[0:13] == 'loadquestions':
                self.say('Syntax: !loadquestions [*clear deck1 deck2...]. Use "clear" as the first word if you want to clear the current decks, and attempt to load a deck for each word specified other than clear, if applicable. Example: !loadanswers clear cardsagainsthumanity craftsmen', self.m['target'])
            elif msg[0:11] == 'loadanswers':
                self.say('Syntax: !loadanswers [*clear deck1 deck2...]. Use "clear" as the first word if you want to clear the current decks, and attempt to load a deck for each word specified other than clear, if applicable. Example: !loadanswers clear cardsagainsthumanity craftsmen', self.m['target'])
        elif msg[0:9] == '!startcah':
            self.startGame(msg[10:])
        elif msg[0:9] == '!joingame':
            self.addPlayer(self.m['sender'])
        elif msg[0:10] == '!leavegame':
            self.removePlayer(self.m['sender'])
        elif msg[0:5] == '!hand':
            self.getHand(self.m['sender'])
        elif msg[0:11] == '!roundsleft':
            self.getRoundsLeft(self.m['target'])
        elif msg[0:11] == '!startround':
            self.startAnsweringRound()
        elif msg[0:5] == '!play':
            self.playCard(self.m['sender'], msg[6:])
        elif msg[0:9] == '!endround' or msg[0:10] == '!startvote':
            self.startVotingRound()
        elif msg[0:5] == '!vote':
            self.vote(self.m['sender'], msg[6:])
        elif msg[0:8] == '!endvote':
            self.endVoting()
        elif msg[0:7] == '!scores':
            self.say('Current scores:')
            self.displayScores()
        elif msg[0:8] == '!endgame':
            self.endGame()
        elif msg[0:14] == '!loadquestions':
            msg = msg[15:].split()
            clear = msg[0] == 'clear'
            if clear:
                msg = msg[1:]
            self.loadQuestionDecks(msg, clear)
        elif msg[0:12] == '!loadanswers':
            msg = msg[13:].split()
            clear = msg[0] == 'clear'
            if clear:
                msg = msg[1:]
            self.loadAnswerDecks(msg, clear)

    def loadQuestionDecks(self, files = ['cardsagainsthumanity'], clear = True):
        #load question decks for playing.
        if clear == True:
            self.questions = []
        for filenames in files:
            try:
                lines = open('./CAH decks/questions/' + filenames + '.txt', 'r')
                self.questions.extend(lines.read().split("\n"))
                self.say('Loaded question deck: ' + filenames)
            except:
                self.say('Could not find file "' + filenames + '"')

    def loadAnswerDecks(self, files = ['cardsagainsthumanity'], clear = True):
        #load answer decks for playing.
        if clear == True:
            self.answers = []
        for filenames in files:
            try:
                lines = open('./CAH decks/answers/' + filenames + '.txt', 'r')
                self.answers.extend(lines.read().split("\n"))
                self.say('Loaded answer deck: ' + filenames)
            except:
                self.say('Could not find file "' + filenames + '"')

    def addPlayer(self, name):
        '''Add a player to the game.'''
        if self.phase == 0: #no game in progress
            self.say('There is not currently a game in progress! Use !startcah [rounds] to start a new game.', self.m['target'])
            return
        for player in self.players:
            if player == name:
                self.say('You are already in this game!', name)
                return
        player = CahPlayer(name)
        self.players.append(player)
        self.dealCard(name, 5) #deal initial hand

    def removePlayer(self, name):
        '''Remove a player from the game.'''
        for player in self.players:
            if player == name:
                #return hand to deck
                for card in player.hand:
                    self.answers.append(card)
                self.players.remove(player)
                self.say('You have been removed from this game.', name)
                return
        self.say('You are not in this game!', name)

    def dealCard(self, name, num = 1, *pos):
        '''Deal cards to a player.'''
        playerObj = None
        for player in self.players:
            if player == name:
                playerObj = player
                break
        if not playerObj: #player not found
            self.say('You are not in this game!', name)
            return
        for i in range(num):
            card = random.choice(self.answers)
            self.answers.remove(card)
            playerObj.hand.append(card)
            self.say('Dealt card: (#' + str(len(playerObj.hand)) + ') ' + card, name)

    def getHand(self, name):
        '''Show a player his or her hand.'''
        playerObj = None
        for player in self.players:
            if player == name:
                playerObj = player
                break
        if not playerObj: #player not found
            self.say('You are not in this game!', name)
            return
        i = 1
        for card in playerObj.hand:
            self.say('(#' + str(i) + ') ' + card, name)
            i += 1
        if playerObj.playedcard:
            self.say('(Played card) ' + playerObj.playedcard, name)

    def startGame(self, rounds):
        '''Begin a game (move from phase 0 to 1).'''
        if self.phase == 0:
            if not self.questions:
                self.loadQuestionDecks()
            if not self.answers:
                self.loadAnswerDecks()
            self.say('A new game of Cards Against Humanity is starting! Enter !joingame to join.')
            if rounds.isdigit():
                rounds = int(rounds)
                if rounds < 1:
                    rounds = 5
            else:
                rounds = 5
            self.roundsleft = rounds
            self.phase = 1
        else:
            self.say('A game is already in progress!', self.m['target'])

    def getRoundsLeft(self, to):
        self.say('Rounds remaining in this game: ' + str(self.roundsleft), to)

    def startAnsweringRound(self):
        '''Start an answering round (move from phase 1 or 3 to 2).'''
        if self.phase != 1 and self.phase != 3:
            self.say('This is not an appropriate time to start a round!', self.m['target'])
            return
        #clear any votes left over from any previous rounds
        for player in self.players:
            player.vote = ''
        self.phase = 2
        self.roundsleft -= 1
        self.currentquestion = random.choice(self.questions)
        self.say('A new round is starting! Use !play [card] to play the card that you think best answers or completes this sentence:')
        self.say(self.currentquestion)

    def playCard(self, name, card):
        '''Play a card (phase 2 only).'''
        playerObj = None
        for player in self.players:
            if player == name:
                playerObj = player
                break
        if not playerObj: #player not found
            self.say('You are not in this game!', name)
            return
        if self.phase != 2:
            self.say('Now is not an appropriate time to play a card!', name)
            return
        if card.isdigit(): #play by number
            card = int(card)
            if card < 1 or card > 5:
                self.say('Please enter a number between 1 and 5.', name)
                return
            card -= 1 #the price of non-programmer-friendliness
            if playerObj.playedcard: #player has already played a card
                playerObj.hand.append(playerObj.playedcard)
                self.say('Unplayed card "' + playerObj.playedcard + '" now at (#5)', name)
            player.playedcardnum = card
            playerObj.playedcard = playerObj.hand[card]
            playerObj.hand.remove(playerObj.playedcard)
            self.say('Played card "' + playerObj.playedcard + '"', name)
            self.checkAnswers()
        else: #play by name
            if playerObj.playedcard: #player has already played a card
                playerObj.hand.append(playerObj.playedcard)
                self.say('Unplayed card "' + playerObj.playedcard + '"', name)
                playerObj.playedcard = ''
            for cards in playerObj.hand:
                if card.lower() == cards.lower():
                    playerObj.playedcard = cards
                    break
            if not playerObj.playedcard:
                self.say('Could not find card "' + card + '"', name)
                return
            playerObj.hand.remove(playerObj.playedcard)
            self.say('Played card "' + playerObj.playedcard + '"', name)
            self.checkAnswers()

    def checkAnswers(self):
        '''Check if all players have played a card.'''
        for player in self.players:
            if not player.playedcard:
                return
        self.startVotingRound()

    def startVotingRound(self):
        '''End an answering round and begin voting on best answers (move from phase to 3).'''
        if self.phase != 2:
            self.say('This is not the appropriate time to start voting!', self.m['target'])
            return
        self.say('Use !vote [name] to vote for the answer you think best answers or completes this question!:')
        self.say(self.currentquestion)
        #map player names to numbers (and back also) so that players don't know who they're voting for
        i = 1
        for player in self.players:
            self.votingdict[player.name] = i
            self.reversedict[i] = player.name
            i += 1
        #list choices
        for player in self.players:
            if player.playedcard:
                self.say('(#' + str(self.votingdict[player.name]) + ') ' + player.playedcard)
                self.dealCard(player.name, 1, player.playedcardnum)
        self.phase = 3

    def vote(self, voter, ballot):
        '''Register a player's vote.'''
        if self.phase != 3:
            self.say('This is not the appropriate time to vote on answers!', voter)
            return
        if not ballot.isdigit():
            self.say('Please enter a number.', voter)
            return
        ballot = int(ballot)
        #check that this ballot is valid
        if not ballot in self.reversedict.keys():
            self.say('There is no answer for #' + str(ballot) + '.', voter)
            return
        #find the voter's and selected player's (ballot's) player objects
        voterObj = None
        ballotObj = None
        for player in self.players:
            if player == voter:
                voterObj = player
            if player == self.reversedict[ballot]:
                if self.reversedict[ballot] == voter and len(self.players) > 2:
                    self.say(voter + ', don\'t vote for yourself, you killjoy!')
                    return
                ballotObj = player
        if not voterObj:
            self.say('You are not in this game!', voter)
            return
        if not ballotObj:
            self.say('Could not find a player with the number #' + str(ballot) + '.', voter)
            return
        #undo a vote if one has been cast (don't need to worry about not finding a player: if that happens, the player has left the game)
        if voterObj.vote:
            for player in self.players:
                if player == voterObj.vote:
                    player.votes -= 1
                    self.say('Unregistered vote for #' + str(self.votingdict[voterObj.vote]) + '.', voter)
        #register the vote
        voterObj.vote = self.reversedict[ballot]
        ballotObj.votes += 1
        self.say('Registered vote for #' + str(ballot) + ': ' + ballotObj.playedcard, voter)
        self.checkVotes()

    def checkVotes(self):
        '''Check if all players have voted.'''
        for player in self.players:
            if not player.vote:
                return
        self.endVoting()

    def endVoting(self):
        '''Display the answers that received the most votes during this round, and allocate points to the winner(s).'''
        if self.phase != 3:
            self.say('This is not the appropriate time to end voting!', self.m['target'])
            return
        scorelist = []
        playerlist = []
        #copy the player list
        for player in self.players:
            playerlist.append(player)
        #sort the list and assemble output
        i = 1
        while len(playerlist) > 0:
            highscore = 0
            highscorers = []
            removed = []
            for player in playerlist:
                if player.votes > highscore: #new highscore
                    highscore = player.votes
                    highscorers = []
                    removed = []
                    highscorers.append(str(i) + '. ' + player.name + ' (' + str(player.votes) + ' votes): ' + player.playedcard)
                    removed.append(player)
                elif player.votes == highscore: #tie
                    highscorers.append(str(i) + '. ' + player.name + ' (' + str(player.votes) + ' votes): ' + player.playedcard)
                    removed.append(player)
            for playerObj in removed:
                playerlist.remove(playerObj)
                if i == 1: #high scorer(s) of this round
                    playerObj.points += 1
            scorelist.extend(highscorers)
            i += len(removed)
        #display
        self.say('Round scores:')
        for line in scorelist:
            self.say(line)
        #clear answers and votes and replenish hands
        self.votingdict = {}
        self.reversedict = {}
        for player in self.players:
            player.playedcard = ''
            player.vote = ''
            player.votes = 0
        #move on
        if self.roundsleft > 0:
            self.startAnsweringRound()
        else:
            self.endGame()

    def displayScores(self):
        '''Display the cumulative scores of all players from this game.'''
        scorelist = []
        playerlist = []
        #copy the player list
        for player in self.players:
            playerlist.append(player)
        #sort the list and assemble output
        i = 1
        while len(playerlist) > 0:
            highscore = 0
            highscorers = []
            removed = []
            for player in playerlist:
                if player.points > highscore:
                    highscore = player.points
                    highscorers = []
                    removed = []
                    highscorers.append(str(i) + '. ' + player.name + ' (' + str(player.points) + ' pts)')
                    removed.append(player)
                elif player.points == highscore:
                    removed.append(player)
                    highscorers.append(str(i) + '. ' + player.name + ' (' + str(player.points) + ' pts)')
            for playerObj in removed:
                playerlist.remove(playerObj)
            scorelist.extend(highscorers)
            i += len(removed)
        #display
        for line in scorelist:
            self.say(line)

    def endGame(self):
        '''End a game.'''
        #if self.phase != 3:
            #self.say('Now is not an appropriate time to end the game!', self.m['target'])
        self.phase = 0
        self.say('Game over! Final scores:')
        self.displayScores()
        #dump data
        for player in self.players:
            for card in player.hand:
                self.answers.append(card)
        self.players = []

if __name__ == "__main__":
    CahBot('CahBot').loop()
