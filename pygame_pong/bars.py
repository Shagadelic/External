#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 22 19:52:15 2021

@author: Shagadelic
"""

import pygame

black=(0,0,0)

class Bar(pygame.sprite.Sprite):
    def __init__(self, color, width, height):
        super().__init__()
        
        self.image = pygame.Surface([width, height])
        self.image.fill(black)
        self.image.set_colorkey(black)
        
        pygame.draw.rect(self.image, color, [0, 0, width, height])
        
        self.rect = self.image.get_rect()
        
    def bar_up(self, pixel_num):
        self.rect.y -= pixel_num
        
        if self.rect.y < 0:
            self.rect.y = 0
            
    def bar_down(self, pixel_num):
        self.rect.y += pixel_num
        
        if self.rect.y > 500:
            self.rect.y = 500