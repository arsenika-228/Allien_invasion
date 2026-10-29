class settings:
    # Хранение настроек для Allien_invasion.py
    def __init__(self):
        # -- Инициализайия настроек --

        # Параметры экрана
        self.screen_width = 1200
        self.screen_height = 800
        self.bg_color = (10, 10, 20)

        self.screen_height = 800
        self.bg_color = (10, 10, 20)

        # --- НОВОЕ: Список цветов космоса для разных уровней ---
        self.level_bg_colors = [
            (10, 10, 20),  # Уровень 1: Темно-синий
            (20, 10, 10),  # Уровень 2: Темно-красный
            (10, 20, 10),  # Уровень 3: Темно-зеленый
            (20, 20, 10),  # Уровень 4: Грязно-желтый
            (20, 10, 20)   # Уровень 5: Темно-фиолетовый
        ]

        # Темп роста стоймости пришельцев
        self.score_scale = 1.5

        # Параметры снаряда
        self.bullet_width = 100
        self.bullet_height = 180
        self.bullet_color = (0, 255, 128)
        self.bullets_allowed = 3

        # Настройки пришельцев
        self.fleet_drop_speed = 10
        self.fleet_direction = 1

        # Темп ускорения игры
        self.speedup_scale = 1.1

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        # Инициализация настроек, изменяющеюся в ходе игры
        self.bullet_speed = 2.5
        self.ship_speed = 1.5
        self.alien_speed = 1.0
        self.ship_limit = 3

        self.fleet_direction = 1

        # Подсчет очков
        self.alien_points = 50

    def increase_speed(self):
        # Увеличивает настройки скорости
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)
