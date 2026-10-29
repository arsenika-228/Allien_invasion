from retro_fx import RetroEffects
from scoreboard import Scoreboard
from button import Button
from allien import Allien
from bullet import Bullet, AlienBullet
from Ship import Ship
from Settings import settings
from game_stats import GameStats
from powerup import PowerUp
from time import sleep
import pygame
import sys
import random


# Класс для управления ресурсами и поведения


class AllienInvasion:
    def __init__(self):
        # Инициализация игры и создание игровых  ресурсов
        pygame.init()
        self.clock = pygame.time.Clock()
        self.settings = settings()

        self.screen = pygame.display.set_mode((
            self.settings.screen_width, self.settings.screen_height))

        pygame.display.set_caption("Allien Invasion")

        # Подключаем ретро-эффекты и звуки
        self.fx = RetroEffects(self.settings.screen_width,
                               self.settings.screen_height)

        self.powerups = pygame.sprite.Group()

        self.explosions = []
        self.engine_particles = []  # <-- Список для частиц двигателя

        self.stats = GameStats(self)  # [cite: 2]
        self.sb = Scoreboard(self)  # [cite: 2]
        self.ship = Ship(self)  # [cite: 2]
        self.bullets = pygame.sprite.Group()  # [cite: 2]
        self.alien_bullets = pygame.sprite.Group()  # <-- Снаряды врагов
        self.alliens = pygame.sprite.Group()  # [cite: 2]
        self._create_fleet()  # [cite: 2]
        self.game_active = False  # [cite: 2]
        self.play_button = Button(self, "Play")  # [cite: 2]

        self.shake_intensity = 0
        self.glitch_frames = 0

        self.explosions = []

    def run_game(self):
        # Запускает цикл игры
        while True:
            self._check_events()

            if self.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_alien_bullets()
                self._update_powerups()
                self._update_aliens()

            self._update_screen()
            self.clock.tick(60)

    def _fire_bullet(self):
        # Создает новый заряд и добавляет в группу bullets
        if len(self.bullets) < self.settings.bullets_allowed:
            new_bullet = Bullet(self)
            self.bullets.add(new_bullet)

            # Включаем звук и выводим текст в консоль для проверки
            self.fx.play_laser()

    def _create_fleet(self):
        # Если уровень делится на 5 без остатка — это уровень БОССА
        if self.stats.level % 5 == 0:
            boss = Allien(self, "boss")
            boss.rect.centerx = self.settings.screen_width // 2
            boss.rect.y = 50
            boss.x = float(boss.rect.x)
            self.alliens.add(boss)
            return  # Выходим из функции, обычный флот не создаем

        # --- Создание обычного флота ---
        alien = Allien(self)
        alien_width, alien_height = alien.rect.size
        number_aliens_x = 10
        number_rows = 3
        spacing_x = 2 * alien_width
        spacing_y = 2 * alien_height
        total_fleet_width = (number_aliens_x - 1) * spacing_x + alien_width
        start_x = (self.settings.screen_width - total_fleet_width) // 2
        start_y = 80

        for row_number in range(number_rows):
            for alien_number in range(number_aliens_x):
                current_x = start_x + alien_number * spacing_x
                current_y = start_y + row_number * spacing_y

                # Верхний ряд (индекс 0) делаем бронированным
                if row_number == 0:
                    self._create_alien(current_x, current_y, "armor")
                else:
                    self._create_alien(current_x, current_y, "normal")

    def _check_events(self):
        # Обработка клавиатуры и мыши
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._close_game()
            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)
            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = pygame.mouse.get_pos()
                self._check_play_button(mouse_pos)

    def _check_play_button(self, mouse_pos):
        # Запускает новую игру при нажатии Play
        button_clicked = self.play_button.rect.collidepoint(mouse_pos)
        if button_clicked and not self.game_active:
            self.start_game()
            self.sb.prep_high_score()
            self.sb.prep_level()
            self.sb.prep_ships()

    def start_game(self):
        # Сброс игровой статистики
        self.powerups.empty()
        self.stats.reset_stats()
        self.game_active = True
        self.sb.prep_score()

        # Cброс игровых настроек
        self.settings.initialize_dynamic_settings()

        # Очистка групп aliens и bullets
        self.bullets.empty()
        self.alliens.empty()

        # Создание флота и размещение его в центре
        self._create_fleet()
        self.ship.center_ship()

        # Указатель мыши скрывается
        pygame.mouse.set_visible(False)

    def _update_screen(self):
        # --- НОВОЕ: Смена фона в зависимости от уровня ---
        # Вычисляем цвет фона (остаток от деления зациклит цвета, если уровней будет больше 5)
        level_index = (self.stats.level -
                       1) % len(self.settings.level_bg_colors)
        current_bg_color = self.settings.level_bg_colors[level_index]
        self.screen.fill(current_bg_color)
        # ------------------------------------------------

        # Обновление и отрисовка ретро-звёзд
        self.fx.update_stars()
        self.fx.draw_stars(self.screen)

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        # --- НОВОЕ: Эффект выхлопа двигателя ---
        # Генерируем частицы только тогда, когда корабль движется
        if self.ship.moving_right or self.ship.moving_left or self.ship.moving_up or self.ship.moving_down:
            self.engine_particles.append({
                'x': self.ship.rect.centerx + random.randint(-5, 5),
                'y': self.ship.rect.bottom - 5,
                'radius': random.randint(3, 6),
                # Огненные цвета
                'color': random.choice([(255, 100, 0), (255, 200, 0), (255, 0, 0)])
            })

        # Отрисовка и обновление частиц двигателя
        for particle in self.engine_particles[:]:
            particle['y'] += 2  # Искры летят вниз от корабля
            particle['radius'] -= 0.2  # Постепенно уменьшаются

            if particle['radius'] <= 0:
                self.engine_particles.remove(particle)
            else:
                pygame.draw.circle(
                    self.screen,
                    particle['color'],
                    (int(particle['x']), int(particle['y'])),
                    int(particle['radius'])
                )
        # ---------------------------------------

        for p in self.powerups.sprites():
            p.draw_powerup()

        self.ship.blitme()
        self.alliens.draw(self.screen)

        for bullet in self.alien_bullets.sprites():
            bullet.draw_bullet()

        # --- Анимация и отрисовка взрывов ---
        for explosion in self.explosions[:]:
            explosion['radius'] += 3  # Скорость расширения круга

            # Внешнее оранжевое кольцо (толщина уменьшается со временем)
            thickness = max(1, 10 - explosion['radius'] // 4)
            pygame.draw.circle(
                self.screen,
                (255, 100, 0),  # Оранжевый цвет
                (explosion['x'], explosion['y']),
                explosion['radius'],
                thickness
            )

            # Внутреннее желтое пятно
            pygame.draw.circle(
                self.screen,
                (255, 255, 0),  # Желтый цвет
                (explosion['x'], explosion['y']),
                explosion['radius'] // 2
            )

            # Удаляем взрыв из списка, когда он достиг максимального размера
            if explosion['radius'] >= explosion['max_radius']:
                self.explosions.remove(explosion)
        # ------------------------------------

        self.sb.show_score()

        if not self.game_active:
            self.play_button.draw_button()

        # --- Эффект глитча (случайные цветные прямоугольники) ---
        if hasattr(self, 'glitch_frames') and self.glitch_frames > 0:
            for _ in range(8):
                gx = random.randint(0, self.settings.screen_width)
                gy = random.randint(0, self.settings.screen_height)
                gw, gh = random.randint(50, 300), random.randint(5, 30)
                color = random.choice([(255, 0, 0), (0, 255, 0), (0, 0, 255)])
                pygame.draw.rect(self.screen, color, (gx, gy, gw, gh))
            self.glitch_frames -= 1

        # --- Тряска экрана (копируем весь экран и сдвигаем) ---
        if hasattr(self, 'shake_intensity') and self.shake_intensity > 0:
            shake_x = random.randint(-self.shake_intensity,
                                     self.shake_intensity)
            shake_y = random.randint(-self.shake_intensity,
                                     self.shake_intensity)
            screen_copy = self.screen.copy()
            self.screen.fill(self.settings.bg_color)
            self.screen.blit(screen_copy, (shake_x, shake_y))
            self.shake_intensity = max(0, self.shake_intensity - 1)

        # Наложение CRT сканлайн-эффекта поверх экрана
        self.fx.draw_crt_overlay(self.screen)

        pygame.display.flip()

    def _update_bullets(self):
        self.bullets.update()

        # Удаление снарядов, вышедших за край экрана
        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._update_bullets_collision()

    def _create_alien(self, x_position, y_position, alien_type="normal"):
        # Теперь передаем тип пришельца
        new_alien = Allien(self, alien_type)
        new_alien.x = x_position
        new_alien.rect.x = x_position
        new_alien.rect.y = y_position
        self.alliens.add(new_alien)

    def _check_keydown_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True
        elif event.key == pygame.K_UP:
            self.ship.moving_up = True
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = True
        elif event.key == pygame.K_q:
            self._close_game()
        elif event.key == pygame.K_SPACE:
            self._fire_bullet()
        elif event.key == pygame.K_p:
            self.start_game()

    def _check_keyup_events(self, event):
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False
        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False
        elif event.key == pygame.K_UP:
            self.ship.moving_up = False
        elif event.key == pygame.K_DOWN:
            self.ship.moving_down = False

    def _update_alien_bullets(self):
        self.alien_bullets.update()
        for bullet in self.alien_bullets.copy():
            if bullet.rect.top >= self.settings.screen_height:
                self.alien_bullets.remove(bullet)

        # Проверяем, какие именно пули попали в корабль
        collisions = pygame.sprite.spritecollide(
            self.ship, self.alien_bullets, True)
        for bullet in collisions:
            self._ship_hit(damage=bullet.damage)

    def _update_bullets_collision(self):
        # ВАЖНО: Четвертый аргумент False! Пришельцы не удаляются автоматически.
        collisions = pygame.sprite.groupcollide(
            self.bullets, self.alliens, True, False
        )

        if collisions:
            for bullets, aliens in collisions.items():
                for alien in aliens:
                    alien.hp -= 1  # Наносим 1 урон

                    if alien.hp <= 0:
                        # Враг уничтожен
                        self.fx.play_explosion()
                        self.stats.score += alien.points
                        self.alliens.remove(alien)

                        # ---  Шанс 4% на выпадение баффа ---
                        if random.random() < 0.08:
                            buff = PowerUp(
                                self, alien.rect.centerx, alien.rect.centery)
                            self.powerups.add(buff)
                        # ------------------------------------------

                        # Взрыв босса делаем гигантским
                        explosion_radius = 150 if alien.alien_type == "boss" else 35
                        self.explosions.append({
                            'x': alien.rect.centerx,
                            'y': alien.rect.centery,
                            'radius': 0,
                            'max_radius': explosion_radius
                        })
                        self.shake_intensity = 15 if alien.alien_type == "boss" else 5
                    else:
                        # Враг получил урон, но жив (рисуем маленький взрывчик от попадания)
                        self.fx.play_explosion()
                        self.explosions.append({
                            'x': alien.rect.centerx,
                            'y': alien.rect.bottom,
                            'radius': 0,
                            'max_radius': 15
                        })

            self.sb.prep_score()
            self.sb.check_high_score()

        # Если все враги уничтожены
        if not self.alliens:
            self.bullets.empty()

            # ВАЖНО: Сначала увеличиваем уровень!
            self.stats.level += 1
            self.sb.prep_level()
            self.settings.increase_speed()

            # Только потом создаем новый флот (с учетом нового уровня)
            self._create_fleet()

    def _update_aliens(self):
        # Обновляет позицию всех пришельцов
        self._check_fleet_edges()
        self.alliens.update()

        # Проверка колизии пришелец - корабль
        if pygame.sprite.spritecollideany(self.ship, self.alliens):
            self._ship_hit()

        # Проверка, сталкиваются ли пришельцы с нижнем края экрана
        self._check_aliens_bottom()

        # --- ИИ БОССА (Выбор 4 атак) ---
        now = pygame.time.get_ticks()
        for alien in self.alliens.sprites():
            if alien.alien_type == "boss":
                if not hasattr(alien, 'last_attack'):
                    alien.last_attack = now

                # Босс делает ход каждые 1.5 секунды (1500 миллисекунд)
                if now - alien.last_attack > 2000:
                    alien.last_attack = now
                    # Случайный выбор атаки
                    attack = random.choice([1, 2, 3, 4])

                    if attack == 1:
                        # 1. Веерный залп (3 красных снаряда)
                        for dx in [-3, 0, 3]:
                            b = AlienBullet(
                                self, alien.rect.centerx, alien.rect.bottom, speed_x=dx)
                            self.alien_bullets.add(b)

                    elif attack == 2:
                        # 2. Плазменный шар (Огромный, медленный, фиолетовый)
                        b = AlienBullet(self, alien.rect.centerx, alien.rect.bottom,
                                        speed_y=3, size_w=25, size_h=25, color=(200, 0, 255), damage=2)
                        self.alien_bullets.add(b)

                    elif attack == 3:
                        # 3. Подкрепление (спавн 2 мелких пришельцев по бокам)
                        self._create_alien(
                            alien.rect.left - 40, alien.rect.top, "normal")
                        self._create_alien(
                            alien.rect.right + 40, alien.rect.top, "normal")

                    elif attack == 4:
                        # 4. Телепортация (уклонение в случайную точку по X)
                        alien.x = random.randint(
                            100, self.settings.screen_width - 100)
                        alien.rect.x = alien.x
                        # Добавляем вспышку на место, куда он переместился
                        self.explosions.append({
                            'x': alien.rect.centerx, 'y': alien.rect.centery,
                            'radius': 0, 'max_radius': 60
                        })

    def _check_fleet_edges(self):
        for alien in self.alliens.sprites():
            if alien.check_edges():
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        for alien in self.alliens.sprites():
            alien.rect.y += self.settings.fleet_drop_speed
        self.settings.fleet_direction *= -1

    def _ship_hit(self, damage=1):
        # Отнимаем переданный урон
        self.stats.ships_left -= damage

        if self.stats.ships_left > 0:
            self.fx.play_explosion()
            self.sb.prep_ships()
            self.alliens.empty()
            self.bullets.empty()
            if hasattr(self, 'alien_bullets'):
                self.alien_bullets.empty()  # Убираем пули босса

            self._create_fleet()
            self.ship.center_ship()
            sleep(0.5)
        else:
            self.fx.play_explosion()
            self.stats.ships_left = 0  # Чтобы на экране не было "-1"
            self.sb.prep_ships()
            self.game_active = False
            pygame.mouse.set_visible(True)
            self.powerups.empty()

    def _check_aliens_bottom(self):
        # Проверяет, добрались ли пришельцы до нижнего края экрана
        for alien in self.alliens.sprites():
            if alien.rect.bottom >= self.settings.screen_height:
                if alien.alien_type == "boss":
                    self.stats.ships_left = 0  # Босс уничтожает базу сразу
                self._ship_hit()
                break

    def _close_game(self):
        # Сохранение перед закрытием
        self.stats.save_high_score()
        sys.exit()

    def _update_powerups(self):
        self.powerups.update()

        # Удаляем баффы, улетевшие за нижний край
        for p in self.powerups.copy():
            if p.rect.top >= self.settings.screen_height:
                self.powerups.remove(p)

        # Проверяем столкновение корабля с баффами
        collisions = pygame.sprite.spritecollide(
            self.ship, self.powerups, True)
        for p in collisions:
            if p.type == 'heal':
                # Лечим, если жизней меньше лимита
                if self.stats.ships_left < self.settings.ship_limit:
                    self.stats.ships_left += 1
                    self.sb.prep_ships()

            elif p.type == 'gun':
                # Увеличиваем лимит пуль на экране
                self.settings.bullets_allowed += 1


if __name__ == '__main__':
    # Создание экземпляра и запуск игры
    ai = AllienInvasion()
    ai.run_game()
