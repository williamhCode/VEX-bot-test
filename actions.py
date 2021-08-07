from bot import VexBot
import math

def distance(x, y, xx, yy):
    return ((xx-x)**2 + (yy-y)**2)**0.5

class MoveToPointInLine:

    def __init__(self, xpos, ypos, reverse:bool=False):
        self.gXpos = xpos
        self.gYpos = ypos
        self.reverse = reverse

        kP = 0.015
        kI = 0.0
        kD = 0.3
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

        dist = distance(bot.xpos, bot.ypos, self.gXpos, self.gYpos)
        self.PID.setUp(dist, 0)

    def update(self, bot:VexBot):
        cte = self.getCTE(bot)
        output = self.turnPID.update(cte)
        
        dist = distance(bot.xpos, bot.ypos, self.gXpos, self.gYpos)
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

    # cross track error
    def getCTE(self, bot:VexBot):
        x1 = self.sXpos
        y1 = self.sYpos
        x2 = self.gXpos
        y2 = self.gYpos
        x0 = bot.xpos
        y0 = bot.ypos
        num = (x2 - x1)*(y1 - y0) - (x1 - x0)*(y2 - y1)
        deno = ((x2 - x1)**2 + (y2 - y1)**2)**0.5
        return num/deno


from scipy import interpolate

class MoveHermiteSpline:

    def __init__(self, *dataList, reverse:bool=False):
        self.reverse = reverse
        n = 600
        self.range = (len(dataList)-1)*n

        tList = []
        xList = []
        yList = []
        xDerList = []
        yDerList = []
        for i in range(len(dataList)):
            tList.append(i*n)

            data = dataList[i]
            xList.append(data[0])
            yList.append(data[1])

            radians = math.radians(data[2])
            xDerList.append(math.cos(radians))
            yDerList.append(math.sin(radians))
        
        self.splineX = interpolate.CubicHermiteSpline(tList, xList, xDerList)
        self.splineY = interpolate.CubicHermiteSpline(tList, yList, yDerList)
    

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