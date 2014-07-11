#a bot that roams in and out of its channels

from ircbot import IrcBot
import random

class RoamBot(IrcBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.current = None
        self.partmsg = "roaming"

    def send(self, msg):
        super().send(msg)
        if "PONG" in msg:
            self.roam()
        
    def roam(self):
        if self.current:
            self.send("PART "+self.current+" "+self.partmsg)
            self.current = None
        else:
            self.current = random.choice(self.channels)
            self.send("JOIN " + self.current)

if __name__ == "__main__":
    RoamBot(name="romeobot").loop()
            
