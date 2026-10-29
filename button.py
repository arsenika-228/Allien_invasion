import pygame.font


class Button:
    # -- Класс для создания кнопок для игры --

    def __init__(self, ai_game, msg):
        self.screen = ai_game.screen
        self.screen_rect = self.screen.get_rect()

        # Назначение размеров и свойств кнопки
        self.width, self.height = 220, 60
        self.button_color = (0, 180, 80)
        self.text_color = (10, 10, 20)
        self.font = pygame.font.SysFont('couriernew', 36, bold=True)

        # Создание кнопки и выравнивание по центру
        self.rect = pygame.Rect(0, 0, self.width, self.height)
        self.rect.center = self.screen_rect.center

        # Сообщение кнопки создается 1 раз
        self._prep_msg(msg)

        self.visible = True
        self.last_toggle = pygame.time.get_ticks()

    def _prep_msg(self, msg):
        # Преобразует msg в прямоугольник и выравнивает по центру
        self.msg_image = self.font.render(
            msg, True, self.text_color, self.button_color)
        self.msg_image_rect = self.msg_image.get_rect()
        self.msg_image_rect.center = self.rect.center

    def draw_button(self):
        now = pygame.time.get_ticks()
        if now - self.last_toggle > 500:  # Переключаем каждые 500 миллисекунд
            self.visible = not self.visible
            self.last_toggle = now

        if self.visible:
            self.screen.fill(self.button_color, self.rect)
            self.screen.blit(self.msg_image, self.msg_image_rect)
