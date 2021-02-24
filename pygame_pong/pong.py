#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 19:14:17 2021

@author: Shagadelic

Weather: sunny

Groovyness: 4/10
"""

import pygame 
#from pygame import *
from pygame import mixer
from pygame import font

import sys

from bars import Bar
from ball import Ball

from random import randint

pygame.init()

#screen window setup
black = (0, 0, 0)
white = (255, 255, 255)

size = (800, 600)
game_display = pygame.display.set_mode(size)
pygame.display.set_caption("Pygame pong")

#adds the bars to the screen
bar1 = Bar(white, 10, 100)
bar1.rect.x = 25
bar1.rect.y = 250

bar2 = Bar(white, 10, 100)
bar2.rect.x = 765
bar2.rect.y = 250

ball = Ball(white, 20, 20)
ball.rect.x = 400
ball.rect.y = 200

spriteLi = pygame.sprite.Group()

spriteLi.add(bar1)
spriteLi.add(bar2)
spriteLi.add(ball)

#main loop variables
clock = pygame.time.Clock()
bar_px_move = 7
game_ongoing = True

#background track with a reasonable production value
mixer.music.load("background.wav")

#background track loop
#mixer.music.play(-1)

#sounds for the collisions
boundSo = mixer.Sound("bound.wav")
goalSo = mixer.Sound("score.wav")
barSo = mixer.Sound("bounce.wav")

#score display variables
p1Score = 0
p2Score = 0

font = font.SysFont(None, 100)

#main loop, exit with x
while game_ongoing:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            game_ongoing = False
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_x:
                game_ongoing = False
    
    #gets user input and moves the bars
    
    keys = pygame.key.get_pressed()
    
    
    if keys[pygame.K_w]:
        if keys[pygame.K_q]:
            bar1.bar_up(bar_px_move*2)
        bar1.bar_up(bar_px_move)
    if keys[pygame.K_s]:
        if keys[pygame.K_q]:
            bar1.bar_down(bar_px_move*2)
        bar1.bar_down(bar_px_move)
      
    if keys[pygame.K_o]:
        if keys[pygame.K_p]:
            bar2.bar_up(bar_px_move*2)
        bar2.bar_up(bar_px_move)
    if keys[pygame.K_l]:
        if keys[pygame.K_p]:
            bar2.bar_down(bar_px_move*2)
        bar2.bar_down(bar_px_move)
    
    #checks ball position at screen edges
    #right and left bound
    if ball.rect.x >= 780:   
        p1Score +=1
        goalSo.play()
        ball.rect.x = 400
        ball.rect.y = 200
        ball.velocity = [randint(-8, -4), randint(-8, 8)]
        
    if ball.rect.x <= 2:        
        p2Score +=1
        goalSo.play()
        ball.rect.x = 400
        ball.rect.y = 200
        ball.velocity = [randint(4, 8), randint(-8, 8)]

    #upper and lower bound
    if ball.rect.y > 580:
        boundSo.play()
        ball.velocity[1] = -ball.velocity[1]
    
    if ball.rect.y < 0:
        boundSo.play()
        ball.velocity[1] = -ball.velocity[1]
    
    if pygame.sprite.collide_mask(ball, bar1) or pygame.sprite.collide_mask(ball, bar2):
        barSo.play()
        ball.bounce()

        #some acceleration to keep things interesting
        if ball.velocity[0] < 8:
            ball.velocity[0] *= 1.1
            ball.velocity[1] *= 1.1

    #update sprites
    spriteLi.update()
    
    #draws game components
    #background
    game_display.fill(black)
    
    #middle line
    pygame.draw.line(game_display, white, [400, 0], [400, 600], 5)
    
    #draws sprites
    spriteLi.draw(game_display)
    
    #refresh score
    sc1 = font.render(str(p1Score), 1, white)
    sc2 = font.render(str(p2Score), 1, white)
    game_display.blit(sc1, (320, 10))
    game_display.blit(sc2, (450, 10))
    
    #update screen step
    pygame.display.update()
    
    #60 fps
    clock.tick(60)
    
pygame.quit()