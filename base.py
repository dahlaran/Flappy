import pygame
import os

VEL = 5

GROUND_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("imgs", "base.png")))
WIDTH = GROUND_IMG.get_width()


class Base:
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = WIDTH

    def move(self):
        self.x1 -= VEL
        self.x2 -= VEL

        if self.x1 + WIDTH < 0:
            self.x1 = self.x2 + WIDTH

        if self.x2 + WIDTH < 0:
            self.x2 = self.x1 + WIDTH

    def draw(self, window):
        window.blit(GROUND_IMG, (self.x1, self.y))
        window.blit(GROUND_IMG, (self.x2, self.y))
