import math

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
    