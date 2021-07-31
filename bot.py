import math

class VexBot:
    
    def __init__(self, xpos, ypos, angle, distance, wheel_width, motor_speed):
        # true states
        self.xpos = xpos
        self.ypos = ypos
        self.angle = angle
        self.distance = distance
        self.wheel_width = wheel_width
        self.motor_speed = motor_speed
        
    def input(self, leftInput, rightInput):
        self.intensityL = self.motor_speed * max(min(1, leftInput), -1)
        self.intensityR = self.motor_speed * max(min(1, rightInput), -1)

    def update(self, dt):
        translateL = self.intensityL * dt
        translateR = self.intensityR * dt
            
        if translateL == translateR:
            dx, dy = self.rotateVector(0, translateL, math.radians(self.angle))
            dtheta = 0
        else:
            dx, dy, dtheta = self.turnRightTransformation(translateL, translateR)
            
        self.xpos += dx
        self.ypos += dy
        self.angle += math.degrees(dtheta)
        
    def turnRightTransformation(self, translateL, translateR):
        dtheta = (translateL - translateR)/self.wheel_width
        radius = translateR/dtheta + self.wheel_width/2
        dx = radius - math.cos(dtheta) * radius
        dy = math.sin(dtheta) * radius
        dx, dy = self.rotateVector(dx, dy, math.radians(self.angle))

        return dx, dy, -dtheta
    
    def turnLeftTransformation(self, translateL, translateR):
        dtheta = (translateR - translateL)/self.wheel_width
        radius = translateL/dtheta + self.wheel_width/2
        dx = math.cos(dtheta) * radius - radius
        dy = math.sin(dtheta) * radius
        dx, dy = self.rotateVector(dx, dy, math.radians(self.angle))

        return dx, dy, dtheta
        
    def rotateVector(self, x, y, angle):
        xprime = x * math.cos(angle) - y * math.sin(angle)
        yprime = x * math.sin(angle) + y * math.cos(angle)

        return xprime, yprime

    def getOffsetPosition(self, offset, angle_diff):
        xpos = self.xpos + offset * math.cos(math.radians(self.angle + angle_diff))
        ypos = self.ypos + offset * math.sin(math.radians(self.angle + angle_diff))

        return xpos, ypos

    def getWheelPositions(self):
        wheelL_xpos, wheelL_ypos = self.getOffsetPosition(self.wheel_width/2, 180)
        wheelR_xpos, wheelR_ypos = self.getOffsetPosition(self.wheel_width/2, 0)

        return wheelL_xpos, wheelL_ypos, wheelR_xpos, wheelR_ypos
    