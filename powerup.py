import pygame
from pygame.sprite import Sprite
import random


class PowerUp(Sprite):
    def __init__(self, ai_game, x, y):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings

        # Случайно выбираем тип баффа
        self.type = random.choice(['heal', 'gun'])

        # Задаем размер (квадрат, в который мы впишем круг)
        self.rect = pygame.Rect(0, 0, 16, 16)
        self.rect.centerx = x
        self.rect.centery = y
        self.y = float(self.rect.y)

        # Настраиваем цвет в зависимости от типа
        if self.type == 'heal':
            self.color = (50, 255, 50)  # Зеленый
        elif self.type == 'gun':
            self.color = (50, 200, 255)  # Голубой

    def update(self):
        # Бафф медленно падает вниз
        self.y += 1.5
        self.rect.y = self.y

    def draw_powerup(self):
        # Рисуем цветной круг и белую обводку для красоты
        pygame.draw.circle(self.screen, self.color, self.rect.center, 8)
        pygame.draw.circle(self.screen, (255, 255, 255),
                           self.rect.center, 8, 2)
