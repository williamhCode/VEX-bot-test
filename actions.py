from bot import VexBot
import math

class MoveInLine:

    def __init__(self, xpos, ypos):
        self.gXpos = xpos
        self.gYpos = ypos

        kP = 0.015
        kI = 0.0
        kD = 0.3
        self.pid = PID(kP, kI, kD)

    def setUp(self, bot:VexBot):
        # self.sXpos = 300
        # self.sYpos = 400

        self.sXpos = bot.xpos
        self.sYpos = bot.ypos

        cte = self.getCTE(bot)

        self.pid.setUp(cte, 0)

    def update(self, bot:VexBot):
        cte = self.getCTE(bot)
        output = self.pid.update(cte)

        leftInput = 1
        rightInput = 1
        
        return max(-1, leftInput + min(output, 0)), max(-1, rightInput - max(output, 0))

    def stop(self, bot:VexBot):
        if abs(self.gXpos - bot.xpos) < 5 and abs(self.gYpos - bot.ypos) < 5:
            return True
        return False

    # cross track error
    def getCTE(self, bot:VexBot):
        x1 = self.gXpos
        y1 = self.gYpos
        x2 = self.sXpos
        y2 = self.sYpos
        x0 = bot.xpos
        y0 = bot.ypos
        num = (x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1)
        deno = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return num/deno

class PID:
    
    def __init__(self, kP, kI, kD):
        self.kP = kP
        self.kI = kI
        self.kD = kD

    def setUp(self, currentValue, desiredValue):
        self.desiredValue = desiredValue

        self.error = math.inf
        self.prevError = self.desiredValue - currentValue
        self.derivative = None
        self.totalError = 0

    def update(self, currentValue):
        self.error = self.desiredValue - currentValue
        self.derivative = self.error - self.prevError
        self.totalError += self.error

        self.prevError = self.error

        outputPower = self.error * self.kP + self.derivative * self.kD + self.totalError * self.kI

        return outputPower