#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Sun Jan 31 18:22:36 2021

@author: williamhou
"""

import pygame
from bot import VexBot
from loader import ActionsLoader
from actions import *

import time as t

def rotate(surface, angle, pivot, offset):
    rotated_image = pygame.transform.rotozoom(surface, angle, 1)
    rotated_offset = offset.rotate(-angle)
    rect = rotated_image.get_rect(center= pivot+rotated_offset)
    return rotated_image, rect
        
def showPositions(screen, vehicle: VexBot):
    wheelL_xpos, wheelL_ypos, wheelR_xpos, wheelR_ypos = vehicle.getWheelPositions()
    pygame.draw.circle(screen, (0,0,225), (wheelL_xpos, wheelL_ypos),5)
    pygame.draw.circle(screen, (0,0,225), (wheelR_xpos, wheelR_ypos),5)
    pygame.draw.circle(screen, (225,225,225), (vehicle.xpos, vehicle.ypos),5)
            
def main():
    botImg = pygame.image.load('pic/vex_bot.png')
    botImg = pygame.transform.smoothscale(botImg, (120,130))
    bot_1 = VexBot(300,200,-90, botImg.get_height(), botImg.get_width(), 350)
    actions = [MoveInLine(1000,200), MoveInLine(1000,800), MoveInLine(300,800), MoveInLine(300,200)]
    loader = ActionsLoader(actions)

    # positions = []
    # saved = False
    
    #SetupWindow
    screen = pygame.display.set_mode((1200,900),pygame.RESIZABLE)
    pygame.display.set_caption('VEX-bot-test')
    
    font = pygame.font.SysFont('Comic Sans MS', 18)
    
    #Game Loop
    key_w = False
    key_s = False
    key_up = False
    key_down = False
    mode = 'manual'

    frame_cap = 1.0/60
    time = t.time()
    unprocessed = 0

    clock = pygame.time.Clock()

    while True:
        can_render = False
        time_2 = t.time()
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
                if event.key == pygame.K_w:
                    key_w = True
                if event.key == pygame.K_s:
                    key_s = True
                if event.key == pygame.K_UP:
                    key_up = True
                if event.key == pygame.K_DOWN:
                    key_down = True
                
                if event.key == pygame.K_m:
                    if mode == 'manual':
                        mode = 'auton'
                        loader.setUp(bot_1)
                    elif mode == 'auton':
                        mode = 'manual'

            if event.type == pygame.KEYUP:
                if event.key == pygame.K_w:
                    key_w = False
                if event.key == pygame.K_s:
                    key_s = False
                if event.key == pygame.K_UP:
                    key_up = False
                if event.key == pygame.K_DOWN:
                    key_down = False

        if can_render:
            dt = clock.tick()/1000
            screen.fill((255,255,255))

            if mode == 'manual':
                left_input = 0
                right_input = 0
                if key_w:
                    left_input += 1
                if key_s:
                    left_input -= 1
                if key_up:
                    right_input += 1
                if key_down:
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


            botImg_copy, botImg_copy_rect = rotate(botImg, bot_1.angle, [bot_1.xpos,bot_1.ypos], pygame.math.Vector2(0,0))
            screen.blit(botImg_copy, botImg_copy_rect)
            showPositions(screen, bot_1)

            position = font.render(f'Mode: {mode}, Coords: {bot_1.xpos:.2f}, {bot_1.ypos:.2f}', False, (0,0,0))
            screen.blit(position, (25, 25))

            pygame.draw.circle(screen, (0,0,0), (1000,200),5)
            pygame.draw.circle(screen, (0,0,0), (1000,800),5)
            pygame.draw.circle(screen, (0,0,0), (300,800),5)
            pygame.draw.circle(screen, (0,0,0), (300,200),5)
                
            pygame.display.update()
        
    
if __name__ == '__main__':
    pygame.init()
    pygame.font.init()
    main()
    pygame.quit()
    