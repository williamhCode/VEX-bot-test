import pygame
import numpy
from bot import VexBot
from loader import ActionsLoader
from actions import *

import time as ti

def rotate(surface, angle, pivot, offset):
    rotated_image = pygame.transform.rotozoom(surface, angle, 1)
    rotated_offset = offset.rotate(-angle)
    rect = rotated_image.get_rect(center= pivot+rotated_offset)
    return rotated_image, rect

def showPositions(screen, vehicle: VexBot):
    wheelL_xpos, wheelL_ypos, wheelR_xpos, wheelR_ypos = vehicle.getWheelPositions()
    pygame.draw.circle(screen, (0,0,225), (wheelL_xpos, revY(wheelL_ypos)),5)
    pygame.draw.circle(screen, (0,0,225), (wheelR_xpos, revY(wheelR_ypos)),5)
    pygame.draw.circle(screen, (225,225,225), (vehicle.xpos, revY(vehicle.ypos)),5)

def revY(ypos):
    return -ypos + 900
            
def main():
    #SetupWindow
    screen = pygame.display.set_mode((1200,900), pygame.SCALED)
    screen.set_alpha(None)
    pygame.display.set_caption('VEX-bot-test')
    
    font = pygame.font.SysFont('Comic Sans MS', 18)

    botImg = pygame.image.load('pic/bot.png').convert_alpha()
    botImg = pygame.transform.smoothscale(botImg, (120,130))

    bot_1 = VexBot(200,200,-45, botImg.get_height(), botImg.get_width(), 350)
    # bot_1 = VexBot(200,200,-90, botImg.get_height(), botImg.get_width(), 350)

    straight_1 = MoveToPointInLine(800,200,False),
    straight_2 = MoveToPointInLine(1000,200,False), MoveToPointInLine(1000,800,True), MoveToPointInLine(300,800,True), MoveToPointInLine(300,200,True), MoveHermiteSpline((200, 200, 0), (600, 100, 90), (800, 500, 90), (300, 700, 180))
    spline_1 = MoveHermiteSpline((200, 200, 90), (1000, 700, 135), (300, 700, 225), (500, 200, 315)),
    spline_2 = MoveHermiteSpline((200, 200, 0), (900, 200, 90), (800, 500, 90), (300, 700, 180)),
    
    # actions = straight_1
    actions = spline_2
    loader = ActionsLoader(actions)
    
    if isinstance(actions[0], MoveHermiteSpline):
        spline = actions
        spline = spline[0]
        x = []
        y = []
        t = numpy.arange(0, spline.range, spline.range/300)
        for i in t:
            x.append(spline.splineX(i))
            y.append(spline.splineY(i))

    # positions = []
    # saved = False

    #Game Loop
    mode = 'manual'

    frame_cap = 1.0/60
    time = ti.time()
    unprocessed = 0

    clock = pygame.time.Clock()

    while True:
        # timer
        dt = clock.tick(60)/1000
        
        # inputs and events ----------------------------- #
        left_input = 0
        right_input = 0
        
        events = pygame.event.get()
        for event in events:

            if event.type == pygame.QUIT:
                return
            
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_r:
                    loader.reset(bot_1)
                
                if event.key == pygame.K_m:
                    if mode == 'manual':
                        mode = 'auton'
                        loader.setUp(bot_1)
                    elif mode == 'auton':
                        mode = 'manual'

        left_input = 0
        right_input = 0
        
        if mode == 'manual':
            keys = pygame.key.get_pressed()

            if keys[pygame.K_w]:
                left_input += 1
            if keys[pygame.K_s]:
                left_input -= 1
            if keys[pygame.K_UP]:
                right_input += 1
            if keys[pygame.K_DOWN]:
                right_input -= 1
                
            bot_1.input(left_input, right_input)
            
        elif mode == 'auton':
            # positions.append(round(bot_1.xpos, 2))
            # if not saved:
            #     if round(bot_1.xpos, 2) == 800:
            #         with open('positions.txt', 'w') as f:
            #             for item in positions:
            #                 f.write("%s\n" % item)
            #         saved = True

            left_input, right_input = loader.update(bot_1)
            bot_1.input(left_input, right_input)
        bot_1.update(dt)

        # rendering --------------------------------------------- #
        screen.fill((255, 255, 255))
        
        for action in actions:
            if isinstance(action, MoveToPointInLine):
                pygame.draw.circle(screen, (0,0,0), (action.gXpos, revY(action.gYpos)), 5)
            elif isinstance(action, MoveHermiteSpline):
                for data in action.dataList:
                    pygame.draw.circle(screen, (0,0,0), (data[0], revY(data[1])), 5)

        if isinstance(actions[0], MoveHermiteSpline):
            for i in range(len(t)):
                pygame.draw.circle(screen, (0,0,0), (int(x[i]),revY(int(y[i]))),5)

        botImg_copy, botImg_copy_rect = rotate(botImg, bot_1.angle, [bot_1.xpos, revY(bot_1.ypos)], pygame.math.Vector2(0,0))
        screen.blit(botImg_copy, botImg_copy_rect)
        showPositions(screen, bot_1)

        position = font.render(f'Mode: {mode}, Coords: {bot_1.xpos:.2f}, {bot_1.ypos:.2f}', False, (0,0,0))
        screen.blit(position, (25, 25))
        motor_speeds = font.render(f'leftVel: {left_input:.2f}, rightVel: {right_input:.2f}', False, (0,0,0))
        screen.blit(motor_speeds, (700, 25))
            
        pygame.display.update()
        
    
if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    main()
    pygame.quit()

