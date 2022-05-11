import math


class VexBot:
    
    def __init__(self, xpos, ypos, angle, distance, wheel_width, max_speed):
        self.xpos = xpos
        self.ypos = ypos
        self.angle = angle
        self.distance = distance
        self.wheel_width = wheel_width
        self.max_speed = max_speed
        
    # setting the motor speeds
    def set_inputs(self, left_input, right_input):
        self.intensityL = self.max_speed * max(min(1, left_input), -1)
        self.intensityR = self.max_speed * max(min(1, right_input), -1)

    def update(self, dt):
        translateL = self.intensityL * dt
        translateR = self.intensityR * dt
            
        if translateL == translateR:
            dx, dy = rotate_vector(0, translateL, math.radians(self.angle))
            dtheta = 0
        else:
            dx, dy, dtheta = turn_transformation(translateL, translateR, self.wheel_width, self.angle)
            
        self.xpos += dx
        self.ypos += dy
        self.angle += math.degrees(dtheta)

    def get_offset_position(self, offset, angle_diff):
        xpos = self.xpos + offset * math.cos(math.radians(self.angle + angle_diff))
        ypos = self.ypos + offset * math.sin(math.radians(self.angle + angle_diff))

        return xpos, ypos

    def get_wheel_positions(self):
        wheelL_xpos, wheelL_ypos = self.get_offset_position(self.wheel_width / 2, 180)
        wheelR_xpos, wheelR_ypos = self.get_offset_position(self.wheel_width / 2, 0)

        return wheelL_xpos, wheelL_ypos, wheelR_xpos, wheelR_ypos

def turn_transformation(translateL, translateR, wheel_width, angle):
    dtheta = (translateL - translateR) / wheel_width
    radius = translateR / dtheta + wheel_width / 2
    dx = radius - math.cos(dtheta) * radius
    dy = math.sin(dtheta) * radius
    dx, dy = rotate_vector(dx, dy, math.radians(angle))

    return dx, dy, -dtheta

def rotate_vector(x, y, angle):
    xprime = x * math.cos(angle) - y * math.sin(angle)
    yprime = x * math.sin(angle) + y * math.cos(angle)

    return xprime, yprime