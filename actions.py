from scipy import interpolate
from bot import VexBot
import math
from abc import ABC, abstractmethod

class Action(ABC):
    
    @abstractmethod
    def set_up(self, bot: VexBot):
        pass
    
    @abstractmethod
    def update(self, bot: VexBot) -> tuple[float, float]:
        pass

    @abstractmethod
    def stop(self, bot: VexBot) -> bool:
        pass

class MoveToPointInLine(Action):

    def __init__(self, xpos, ypos, reverse=False):
        self.g_xpos = xpos
        self.g_ypos = ypos
        self.reverse = reverse

        kP = 0.01
        kI = 0.0
        kD = 0.2
        self.turnPID = PID(kP, kI, kD)

        kP = 0.01
        kI = 0.0
        kD = 0.0
        self.PID = PID(kP, kI, kD)

    def set_up(self, bot: VexBot):
        self.s_xpos = bot.xpos
        self.s_ypos = bot.ypos

        self.xVec = self.g_xpos - self.s_xpos
        self.yVec = self.g_ypos - self.s_ypos

        cte = self.get_cte(bot)
        self.turnPID.set_up(cte, 0)

        dist = self.get_dist(bot)
        self.PID.set_up(dist, 0)

    def update(self, bot: VexBot):
        cte = self.get_cte(bot)
        output = self.turnPID.update(cte)

        dist = self.get_dist(bot)
        baseOutput = min(1, -self.PID.update(dist))
        leftInput = baseOutput
        rightInput = baseOutput

        if self.reverse:
            return -leftInput + max(output, 0), -rightInput - min(output, 0)
        return leftInput + min(output, 0), rightInput - max(output, 0)

    def stop(self, bot: VexBot):
        xdif = self.g_xpos - bot.xpos
        ydif = self.g_ypos - bot.ypos
        dist = (xdif**2 + ydif**2)**0.5
        dot = xdif*self.xVec + ydif*self.yVec

        if dist < 3 or dot < 0:
            return True
        return False

    def get_dist(self, bot: VexBot):
        return ((bot.xpos - self.g_xpos) ** 2 + (bot.ypos - self.g_ypos) ** 2) ** 0.5

    # cross track error
    def get_cte(self, bot: VexBot):
        x1 = self.s_xpos
        y1 = self.s_ypos
        x2 = self.g_xpos
        y2 = self.g_ypos
        x0 = bot.xpos
        y0 = bot.ypos
        num = (x2 - x1) * (y1 - y0) - (y2 - y1) * (x1 - x0)
        deno = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5
        return num/deno


class MoveHermiteSpline(Action):

    def __init__(self, *data, reverse: bool = False):
        self.data_list = data
        n = 600
        self.range = (len(self.data_list)-1) * n

        t_list = []
        x_list = []
        y_list = []
        x_der_list = []
        y_der_list = []
        for i in range(len(self.data_list)):
            t_list.append(i * n)

            data = self.data_list[i]
            x_list.append(data[0])
            y_list.append(data[1])

            radians = math.radians(data[2])
            x_der_list.append(math.cos(radians))
            y_der_list.append(math.sin(radians))

        self.spline_x = interpolate.CubicHermiteSpline(t_list, x_list, x_der_list)
        self.spline_y = interpolate.CubicHermiteSpline(t_list, y_list, y_der_list)

        self.reverse = reverse

        kP = 0.05
        kI = 0.0
        kD = 0.4
        self.turn_pid = PID(kP, kI, kD)

    def set_up(self, bot: VexBot):
        self.t = 0

        cte = self.get_cte(bot)
        self.turn_pid.set_up(cte, 0)

    def update(self, bot: VexBot):
        cte = self.get_cte(bot)
        output = self.turn_pid.update(cte)

        leftInput = 1
        rightInput = 1

        if self.reverse:
            return -leftInput + max(output, 0), -rightInput - min(output, 0)
        return leftInput + min(output, 0), rightInput - max(output, 0)

    def stop(self, bot: VexBot):
        return self.t >= self.range

    def get_cte(self, bot: VexBot):
        rate = 0.1
        while True:
            x = self.spline_x(self.t, extrapolate=True)
            y = self.spline_y(self.t, extrapolate=True)
            dx = self.spline_x(self.t, 1, extrapolate=True)
            dy = self.spline_y(self.t, 1, extrapolate=True)
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

    def set_up(self, currentValue, desiredValue):
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

        outputPower = (
            self.error * self.kP + 
            self.derivative * self.kD + 
            self.totalError * self.kI
        )

        return outputPower