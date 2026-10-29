import pygame
from pygame.sprite import Sprite


class Bullet(Sprite):
    # Класс для управления снарядом

    def __init__(self, ai_game):
        # Создает объект снарядов в текущей позиции
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.color = self.settings.bullet_color

        # Создания снаряда на позиции (0, 0)

        self.rect = pygame.Rect(0, 0, self.settings.bullet_width,
                                self.settings.bullet_height)
        self.rect.midtop = ai_game.ship.rect.midtop

        # Позиция снаряда храниться в вещественном формате
        self.y = float(self.rect.y)
        self.history = []

    def update(self):
        # Перемещение снаряда вверх
        # Обновление точной позиции снаряда
        self.y -= self.settings.bullet_speed

        # Обновление позиции прямоугольника
        self.rect.y = self.y

        self.history.append((self.rect.x, self.y))
        if len(self.history) > 5:  # 5 кадров - длина хвоста
            self.history.pop(0)

    def draw_bullet(self):
        # Вывод снаряда на экран
        for i, (hx, hy) in enumerate(self.history):
            # Вычисляем затухание: чем старше позиция, тем темнее цвет
            shade = int(255 * (i / 5))
            trail_color = (0, shade, int(shade / 2))
            trail_rect = pygame.Rect(
                hx, hy, self.settings.bullet_width, self.settings.bullet_height)
            pygame.draw.rect(self.screen, trail_color, trail_rect)

        pygame.draw.rect(self.screen, self.color, self.rect)


class AlienBullet(Sprite):
    # Добавляем параметр damage (по умолчанию 1)
    def __init__(self, ai_game, x, y, speed_x=0, speed_y=5, size_w=6, size_h=15, color=(255, 50, 50), damage=1):
        super().__init__()
        self.screen = ai_game.screen
        self.color = color
        self.damage = damage  # Сохраняем урон снаряда

        self.rect = pygame.Rect(0, 0, size_w, size_h)
        self.rect.centerx = x
        self.rect.bottom = y
        self.x = float(self.rect.x)
        self.y = float(self.rect.y)
        self.speed_x = speed_x
        self.speed_y = speed_y

    def update(self):
        self.x += self.speed_x
        self.y += self.speed_y
        self.rect.x = self.x
        self.rect.y = self.y

    def draw_bullet(self):
        pygame.draw.rect(self.screen, self.color, self.rect)
