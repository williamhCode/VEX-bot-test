from bot import VexBot
import math

class MoveToPointInLine:

    def __init__(self, xpos, ypos, reverse:bool=False):
        self.gXpos = xpos
        self.gYpos = ypos
        self.reverse = reverse

        kP = 0.015
        kI = 0.0
        kD = 0.1
        self.turnPID = PID(kP, kI, kD)

        kP = 0.01
        kI = 0.0
        kD = 0.0
        self.PID = PID(kP, kI, kD)

    def setUp(self, bot:VexBot):
        self.sXpos = bot.xpos
        self.sYpos = bot.ypos

        self.xVec = self.gXpos - self.sXpos
        self.yVec = self.gYpos - self.sYpos

        cte = self.getCTE(bot)
        self.turnPID.setUp(cte, 0)

        dist = self.getDist(bot)
        self.PID.setUp(dist, 0)

    def update(self, bot:VexBot):
        cte = self.getCTE(bot)
        output = self.turnPID.update(cte)
        
        dist = self.getDist(bot)
        baseOutput = min(1, -self.PID.update(dist))
        leftInput = baseOutput
        rightInput = baseOutput

        if self.reverse:
            return -leftInput + max(output, 0), -rightInput - min(output, 0)
        return leftInput + min(output, 0), rightInput - max(output, 0)

    def stop(self, bot:VexBot):
        xdif = self.gXpos - bot.xpos
        ydif = self.gYpos - bot.ypos
        dist = (xdif**2 + ydif**2)**0.5
        dot = xdif*self.xVec + ydif*self.yVec

        if dist < 3 or dot < 0:
            return True
        return False

    def getDist(self, bot:VexBot):
        return ((bot.xpos - self.gXpos) ** 2 + (bot.ypos - self.gYpos) ** 2) ** 0.5

    # cross track error
    def getCTE(self, bot:VexBot):
        x1 = self.sXpos
        y1 = self.sYpos
        x2 = self.gXpos
        y2 = self.gYpos
        x0 = bot.xpos
        y0 = bot.ypos
        num = (x2 - x1) * (y1 - y0) - (y2 - y1) * (x1 - x0) 
        deno = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return num/deno


from scipy import interpolate

class MoveHermiteSpline:

    def __init__(self, *data, reverse:bool=False):
        self.dataList = data
        n = 600
        self.range = (len(self.dataList)-1)*n

        tList = []
        xList = []
        yList = []
        xDerList = []
        yDerList = []
        for i in range(len(self.dataList)):
            tList.append(i*n)

            data = self.dataList[i]
            xList.append(data[0])
            yList.append(data[1])

            radians = math.radians(data[2])
            xDerList.append(math.cos(radians))
            yDerList.append(math.sin(radians))
        
        self.splineX = interpolate.CubicHermiteSpline(tList, xList, xDerList)
        self.splineY = interpolate.CubicHermiteSpline(tList, yList, yDerList)

        self.reverse = reverse

        kP = 0.05
        kI = 0.0
        kD = 0.4
        self.turnPID = PID(kP, kI, kD)

        kP = 0.01
        kI = 0.0
        kD = 0.0
        self.PID = PID(kP, kI, kD)

    def setUp(self, bot:VexBot):
        self.t = 0

        cte = self.getCTE(bot)
        self.turnPID.setUp(cte, 0)

        # dist = self.getDist(bot)
        # self.PID.setUp(dist, 0)        
    
    def update(self, bot:VexBot):
        cte = self.getCTE(bot)
        output = self.turnPID.update(cte)
        
        # dist = self.getDist(bot)
        # baseOutput = min(1, -self.PID.update(dist))
        # leftInput = baseOutput
        # rightInput = baseOutput
        leftInput = 1
        rightInput = 1

        if self.reverse:
            return -leftInput + max(output, 0), -rightInput - min(output, 0)
        return leftInput + min(output, 0), rightInput - max(output, 0)

    def stop(self, bot:VexBot):
        return False

    def getDist(self, bot:VexBot):
        pass

    def getCTE(self, bot:VexBot):
        rate = 0.1
        while True:
            x = self.splineX(self.t, extrapolate=True)
            y = self.splineY(self.t, extrapolate=True)
            dx = self.splineX(self.t, 1, extrapolate=True)
            dy = self.splineY(self.t, 1, extrapolate=True)
            slope = 2 * (x - bot.xpos) * dx + 2 * (y - bot.ypos) * dy
            if abs(slope) < 0.1:
                break
            self.t += -slope * rate
        dot = dy * (bot.xpos - x) + -dx * (bot.ypos - y)
        cte = ((x - bot.xpos) ** 2 + (y - bot.ypos) ** 2) ** 0.5 * 1

        return math.copysign(cte, dot)


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