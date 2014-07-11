#by sockman, cheem, and wizzeh :)
#(in no particular order of coolness)

import socket
import random
import ast

class IrcBot():
    def __init__(self, name="cmenbot", channels=['#notahashtag']):
        self.loopfuncs = []
        self.socket = socket.socket()
        self.name = name
        self.password = "noxalia"
        self.server = ("irc.freenode.net", 6667)
        self.channels = channels
        self.socket.connect(self.server)
        self.send("NICK " + self.name)
        self.send("USER %(n)s %(n)s %(n)s : %(n)s" % {'n':self.name})
        #self.send(

    def loop(self):
        while True:
            buf = self.socket.recv(4096)
            lines = buf.decode('UTF-8').split("\n")
            for data in lines:
                data = str(data).strip()
                print("<--", data)
                if not data:
                    continue
                if 'PING' in data:
                    n = data.split(':')[1]
                    self.send('PONG :' + n)
                args = data.split(None, 3)
                if len(args) != 4:
                    continue
                m = {}
                m['sender'] = args[0][1:]
                m['type']   = args[1]
                m['target'] = args[2]
                m['msg']    = args[3][1:]

                if m['target'] == self.name:
                    m['target'] == m['sender']
                
                self.m = m
                
                for func in self.loopfuncs:
                    func()

    def send(self, msg):
        #appropriate place to encode
        print("-->", msg)
        self.socket.send(("%s \r\n" % msg).encode('UTF-8'))
        
    def say(self, msg, *to):
        if not to:
            to = self.channels
        for channel in to:
            self.send("PRIVMSG " + channel + " :" + msg)
        
    def connect(self):
        self.send("MODE " + self.name + "+x")
        for c in self.channels:
            self.send("JOIN " + c)
   
        #self.socket.recv(4096)
        
class HelpBot(IrcBot):
    ''' Not actually helpful. The hello world of botting.'''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs.extend([self.help])
        #there probably exists a more implicit way to do this
        
    def help(self):
        if "!help" in self.m['msg']:
            print("triggered help")
            self.say("Help yourself, asshole.", self.m['target'])

class EvalBot(IrcBot):
    ''' Error handling and mischief for bots. '''
    import ast
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs.extend([self.eval_msg])
        self.errormsg = "\u0001ACTION softly poots\u0001"

    def bot_eval(msg):
        try:
            return str(eval(msg))
        except:
            return self.errormsg

    def bot_literal_eval(self, msg):
        try:
            return str(self.ast.literal_eval(msg))
        except:
            return self.errormsg
        
    def eval_msg(self):
        msg = self.m['msg']
        if msg[0] == '@':
            self.say(self.bot_eval(msg), self.m['target'])
        
class DiceBot(IrcBot):
    ''' an 18! what are the odds? '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs.extend([self.dice])
        
    def dice(self):
        msg = self.m['msg']
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
                self.say("\u0001ACTION softly poots\u0001", self.m['target'])
            self.say("rolled: "+msg+" = "+output, self.m['target'])
            
class ChatterBot(HelpBot):
    ''' A general purpose chattering bot. Inheirits from HelpBot '''
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs.extend([self.didsomebodysay, self.botsay, self.wearing])
        self.clothes = "nothing at all"
            
    def didsomebodysay(self):
        msg = self.m['msg']
        if self.m['target'] != self.name: 
            for w in msg.split():
               if w[-3:] == 'ing' and random.randrange(100) < len(w)-5:
                    self.say('DID SOMEBODY SAY "'+w.upper()+'"??????', self.m['target'])
                    clothing = random.choice(['robe', 'boots', 'pants', 'gloves',
                                              'hat', 'shirt', 'codpiece'])
                    w = w.lower()
                    self.clothes = "my %s %s" % (w, clothing)
                    self.say("\u0001ACTION puts on his "+w+" "
                             +clothing+"\u0001", self.m['target'])

    def wearing(self):
        '''what are you wearing?'''
        if "wearing" in self.m['msg'].lower() and self.name in self.m['msg'].lower():
            self.say("I'm wearing " + self.clothes + "!", self.m['target'])

    def botsay(self):
        ''' #! to msg all channels. #target to message that target. '''
        msg = self.m['msg']
        if self.m['target'] == self.name:
            if msg[0] == "#":
                target = msg[1:].split()[0]
                print(target)
                if target == '!':
                    print("WWW")
                    self.say(msg[len(target)+2:])
                else:
                    self.say(msg[len(target)+2:], target)


if __name__ == "__main__":
    class CmenBot(ChatterBot, DiceBot):
        ''' Our beloved cmenbot <3 '''
        pass
    
    CmenBot().loop()
