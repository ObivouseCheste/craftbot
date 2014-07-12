#wizzeh wuz here

from ircbot import IrcBot

class MasterBot(IrcBot):
    def __init__(self,**kwargs):
        super().__init__(**kwargs)
        self.loopfuncs += [self.masterbot]
        self.ownedbots = []
        self.roamingbots = []

    def masterbot(self):
        if (self.m['sender'] == self.m['target']) and m['type']=="PRIVMSG": #if this is a pm
            marr = self.m['msg'].split()
            target = self.m['target'][0:self.m['target'].find("!~")]
            if(marr[0] == "!bot"):
                if(marr[1] == "create"):
                    

if __name__ == "__main__":
	MasterBot(name="masterbotter").loop()
