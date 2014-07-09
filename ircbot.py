#by sockman, cheem, and wizzeh :)
#(in ascending order of cool)

import socket
import random
import ast

class IrcBot():
    def __init__(self):
        self.loopfuncs = []
        self.socket = socket.socket()
        self.name = "cmendiceman"
        self.password = "noxalia"
        self.server = ("irc.freenode.net", 6667)
        self.channels = ['#notahashtag']
        self.socket.connect(self.server)
        self.send("NICK " + self.name)
        self.send("USER %(n)s %(n)s %(n)s : %(n)s" % {'n':self.name})
        self.connected = False
        #self.send(
        while True:
            buf = self.socket.recv(4096)
            lines = buf.decode('UTF-8').split("\n")
            for data in lines:
                data = str(data).strip()
                print("<--", data)
                if not data:
                    continue
                if data.find('PING') != -1:
                    n = data.split(':')[1]
                    self.send('PONG :' + n)
                    if self.connected == False:
                        self.connect()
                        self.connected = True
                args = data.split(None, 3)
                if len(args) != 4:
                    continue
                m = {}
                m['sender'] = args[0][1:]
                m['type']   = args[1]
                m['target'] = args[2]
                m['msg']    = args[3][1:]
                
                for func in self.loopfuncs:
                    output = func(m)
                    if output:
                        self.say(*output)

    def send(self, msg):
        #appropriate place to encode
        print("-->", msg)
        self.socket.send(("%s \r\n" % msg).encode('UTF-8'))
        
    def say(self, msg, *to):
        if not to:
            to = self.channels[0]
        for channel in to:
            self.send("PRIVMSG " + channel + " :" + msg)
        
    def connect(self):
        self.send("MODE " + self.name + "+x")
        for c in self.channels:
            self.send("JOIN " + c)
   
        #self.socket.recv(4096)
        
class HelpBot(IrcBot):
    ''' Not actually helpful. '''
    def __init__(self):
        super().__init__(*args, **kwargs)
        self.loopfuncs.append(self.help) #there probably exists a more implicit way to do this
        
    def help(self, m):
        if "!help" in m['msg']:
            print("triggered help")
            return "Help yourself, asshole.", m['target']
      
class DiceBot(IrcBot):
    ''' an 18! what are the odds? '''
    def __init__(self):
        super().__init__(*args, **kwargs)
        self.loopfuncs.append(self.dice)
        
    def dice(self, m):
        msg = m['msg']
        nums = '0123456789'
        if msg[0:5] == "roll ":
            msg = msg[5:]
            start = 0
            while 'd' in msg[start:]:
                i = msg.find('d',start)
                end = i+1
                while end < len(msg) and msg[end] in nums:
                    end += 1
                    
                die = msg[i+1:end]
                start = end
                if die and die[0] != '0':
                    msg = msg[:i]+'('+str(random.randrange(int(die))+1)+')'+msg[end:]
                    start += 1
            try:
                output = str(ast.literal_eval(msg))
            except:
                return chr(1) + "ACTION softly poots", m['target']
            return "rolled: "+msg+" = "+output, m['target']
            
def ChatterBot(HelpBot):
    ''' A general purpose chattering bot. Inheirits from HelpBot '''
    def __init__(self):
        super().__init__(*args, **kwargs)
        self.loopfuncs.append(self.didsomebodysay)
            
    def didsomebodysay(self, m):
        msg = m['msg']
        for w in msg.split():
            if random.randrange(1000) < len(w)-6:
                return 'DID SOMEBODY SAY "'+w.upper()+'"??????', m['target']
        
def CmenBot(ChatterBot, DiceBot):
    ''' Our beloved cmenbot <3 '''
    pass
