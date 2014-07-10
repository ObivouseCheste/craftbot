from ircbot import IrcBot
import time

    class TimerBot(IrcBot):
        def __init__(self, **kwargs):
            super().__init__(**kwargs)
            self.loopfuncs += [self.timestart]

        def timestart(self):
            msg = self.m['msg']:
                if msg[
