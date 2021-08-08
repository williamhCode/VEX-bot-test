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
            
from pygame.locals import DOUBLEBUF
def main():
    #SetupWindow
    flags = DOUBLEBUF
    screen = pygame.display.set_mode((1200,900), flags)
    screen.set_alpha(None)
    pygame.display.set_caption('VEX-bot-test')
    
    font = pygame.font.SysFont('Comic Sans MS', 18)

    botImg = pygame.image.load('pic/bot.png').convert()
    botImg = pygame.transform.smoothscale(botImg, (120,130))

    bot_1 = VexBot(1000,200,0, botImg.get_height(), botImg.get_width(), 350)

    straight = MoveToPointInLine(1000,200,True), MoveToPointInLine(1000,800,True), MoveToPointInLine(300,800,True), MoveToPointInLine(300,200,True)
    spline = MoveHermiteSpline((1000, 200, 90), (1000, 800, 135), (300, 800, 225), (500, 200, 315))
    actions = [spline]
    loader = ActionsLoader(actions)

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
        can_render = False
        time_2 = ti.time()
        passed = time_2 - time
        unprocessed += passed
        time = time_2

        while(unprocessed >= frame_cap):
            unprocessed -= frame_cap
            can_render = True
    
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

        if can_render:
            # dt = clock.tick()
            # print(clock.get_fps())
            dt = 1/60
            screen.fill((255,255,255))

            if mode == 'manual':
                left_input = 0
                right_input = 0

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

                leftInput, rightInput = loader.update(bot_1)
                bot_1.input(leftInput, rightInput)
            bot_1.update(dt)

            pygame.draw.circle(screen, (0,0,0), (1000,revY(200)),5)
            pygame.draw.circle(screen, (0,0,0), (1000,revY(800)),5)
            pygame.draw.circle(screen, (0,0,0), (300,revY(800)),5)
            pygame.draw.circle(screen, (0,0,0), (300,revY(200)),5)

            for i in range(len(t)):
                pygame.draw.circle(screen, (0,0,0), (int(x[i]),revY(int(y[i]))),5)

            botImg_copy, botImg_copy_rect = rotate(botImg, bot_1.angle, [bot_1.xpos, revY(bot_1.ypos)], pygame.math.Vector2(0,0))
            screen.blit(botImg_copy, botImg_copy_rect)
            showPositions(screen, bot_1)

            position = font.render(f'Mode: {mode}, Coords: {bot_1.xpos:.2f}, {bot_1.ypos:.2f}', False, (0,0,0))
            screen.blit(position, (25, 25))
                
            pygame.display.update()
        
    
if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    main()
    pygame.quit()
    