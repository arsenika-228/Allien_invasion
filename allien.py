import pygame
import random
from pygame.sprite import Sprite


class Allien(Sprite):
    # Класс 1 пришельца

    def __init__(self, ai_game, alien_type="normal"):
        super().__init__()
        self.screen = ai_game.screen
        self.settings = ai_game.settings
        self.alien_type = alien_type

        # Загружаем базовое изображение
        original_image = pygame.image.load("images/alien.bmp").convert()
        original_image.set_colorkey((0, 0, 0))

        # Пасхалка: шанс 2% на появление переливающегося пришельца
        self.is_rainbow = random.random() < 0.001

        # --- Настройка характеристик по типу ---
        if self.alien_type == "boss":
            width, height = original_image.get_size()
            original_image = pygame.transform.scale(
                original_image, (width * 3, height * 3))
            self.hp = 150
            self.points = 500
            self.speed_factor = 0.6
        elif self.alien_type == "armor":
            self.hp = 3
            self.points = 100
            self.speed_factor = 1.0
        else:
            self.hp = 1
            self.points = self.settings.alien_points
            self.speed_factor = 1.0

        # СОЗДАЕМ МАСКУ: берем только чистый силуэт пришельца, игнорируя его старый цвет
        self.mask = pygame.mask.from_surface(original_image)

        # Выбираем цвет для силуэта
        if self.alien_type == "armor":
            # Бронированного оставляем красным, чтобы отличать в бою
            self.color = (255, 100, 100)
        elif not self.is_rainbow:
            # Генерируем любой яркий случайный цвет
            hue = random.randint(0, 360)
            c = pygame.Color(0)
            c.hsva = (hue, 100, 100, 100)
            self.color = (c.r, c.g, c.b)
        else:
            # Радужный пока белый, цвет начнет меняться в update()
            self.color = (255, 255, 255)

        # ГЕНЕРИРУЕМ КАРТИНКУ ИЗ МАСКИ: заливаем силуэт выбранным цветом, а фон делаем черным
        self.image = self.mask.to_surface(
            setcolor=self.color, unsetcolor=(0, 0, 0))
        # Сразу делаем черный фон прозрачным
        self.image.set_colorkey((0, 0, 0))

        self.rect = self.image.get_rect()
        self.rect.x = self.rect.width
        self.rect.y = self.rect.height
        self.x = float(self.rect.x)

    def update(self):
        # Перемещение с учетом скорости типа
        self.x += (self.settings.alien_speed *
                   self.settings.fleet_direction * self.speed_factor)
        self.rect.x = self.x

        # Анимация плавной смены цвета для радужной пасхалки
        if self.is_rainbow:
            color = pygame.Color(0)
            color.hsva = ((pygame.time.get_ticks() // 10) % 360, 100, 100, 100)

            # Каждый кадр перерисовываем силуэт с новым цветом
            self.image = self.mask.to_surface(
                setcolor=(color.r, color.g, color.b), unsetcolor=(0, 0, 0))
            self.image.set_colorkey((0, 0, 0))

    def check_edges(self):
        screen_rect = self.screen.get_rect()
        return (self.rect.right >= screen_rect.right) or (self.rect.left <= 0)
