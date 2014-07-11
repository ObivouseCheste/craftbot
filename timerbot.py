from ircbot import IrcBot
import time
import datetime as dt

class TimerBot(IrcBot):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.loopfuncs += [self.say_timer, self.timercheck]
        self.timers = set()

    def say_timer(self):
        msg = self.m['msg']
        if msg[:7] == "!timer ":
            spl = msg.split()
            t = spl[1].split(':')
            try:
                t = list(map(int, t))
            except ValueError:
                self.say("invalid time.")
                return
            if len(t) > 4:
                self.say("cannot parse more than day, hour, minute, and second")
                return
            t = [0]*(4-len(t)) + t
            self.new_timer(self.say, tuple([' '.join(spl[2:])]), *t)

    def timercheck(self):
        now = dt.datetime.now()
        complete = set()
        for timer in self.timers:
            if now > timer[0]:
                complete.add(timer)
                eval(str(timer[1](*timer[2])), locals())
        self.timers -= complete

    def new_timer(self, func, args, d=0, h=0, m=0, s=0, ):
        td = dt.timedelta(days=d, hours=h, minutes=m, seconds=s)
        now = dt.datetime.now()
        activate = now + td

        self.timers.add((activate, func, args))

if __name__ == "__main__":
    timebot = TimerBot(name="lord_of_time7")
    timebot.loop()
                
                
