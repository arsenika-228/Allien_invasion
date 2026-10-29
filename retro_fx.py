import random
import pygame
import numpy as np


class RetroEffects:
    def __init__(self, screen_w, screen_h):
        self.screen_w = screen_w
        self.screen_h = screen_h

        # 1. Полосы сканирования CRT-монитора (Scanlines)
        self.scanlines_surf = pygame.Surface(
            (screen_w, screen_h), pygame.SRCALPHA)
        for y in range(0, screen_h, 4):
            pygame.draw.line(self.scanlines_surf, (0, 0, 0, 85),
                             (0, y), (screen_w, y), 1)

        # 2. Звездное поле (параллакс-звезды)
        self.stars = []
        for _ in range(60):
            x = random.randint(0, screen_w)
            y = random.randint(0, screen_h)
            speed = random.choice([0.5, 1.0, 1.8])
            color = (180, 180, 255) if speed > 1 else (100, 100, 150)
            self.stars.append([x, y, speed, color])

        # 3. Инициализация 8-битного звукового синтезатора
        self._init_sounds()

    def update_stars(self):
        for star in self.stars:
            star[1] += star[2]
            if star[1] > self.screen_h:
                star[1] = 0
                star[0] = random.randint(0, self.screen_w)

    def draw_stars(self, surface):
        for star in self.stars:
            pygame.draw.rect(surface, star[3],
                             (int(star[0]), int(star[1]), 2, 2))

    def draw_crt_overlay(self, surface):
        surface.blit(self.scanlines_surf, (0, 0))

    def _init_sounds(self):
        try:
            # Явно инициализируем микшер с нужными параметрами
            pygame.mixer.init(frequency=44100, size=-
                              16, channels=1, buffer=512)
            import numpy as np

            self.laser_snd = self._make_laser_sound()
            self.explosion_snd = self._make_explosion_sound()
            print("Аудио: Ретро-звуки успешно синтезированы и готовы!")

        except ImportError:
            print(
                "Аудио ОШИБКА: Библиотека numpy не найдена. Напиши в консоли: pip install numpy")
            self.laser_snd = None
            self.explosion_snd = None
        except Exception as e:
            print(f"Аудио ОШИБКА: Проблема с микшером Pygame — {e}")
            self.laser_snd = None
            self.explosion_snd = None

    def play_laser(self):
        if self.laser_snd:
            self.laser_snd.play()

    def play_explosion(self):
        if self.explosion_snd:
            self.explosion_snd.play()

    def _make_laser_sound(self):
        import numpy as np
        sample_rate = 44100
        # Сделали звук чуть длиннее (0.2 вместо 0.12)
        duration = 0.20
        n_samples = int(sample_rate * duration)
        freqs = np.linspace(880, 220, n_samples)
        phases = 2 * np.pi * np.cumsum(freqs) / sample_rate
        wave = np.where(np.sin(phases) > 0, 1.0, -1.0)
        envelope = np.linspace(1.0, 0.0, n_samples)

        # Увеличили громкость с 0.25 до 0.4
        audio = (wave * envelope * 0.4 * 32767).astype(np.int16)

        stereo_audio = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo_audio)

    def _make_explosion_sound(self):
        import numpy as np
        sample_rate = 44100
        duration = 0.22
        n_samples = int(sample_rate * duration)
        noise = np.random.uniform(-1.0, 1.0, n_samples)
        envelope = np.linspace(1.0, 0.0, n_samples) ** 2

        # Генерируем аудио
        audio = (noise * envelope * 0.35 * 32767).astype(np.int16)

        # Превращаем моно (1D) в стерео (2D)
        stereo_audio = np.column_stack((audio, audio))
        return pygame.sndarray.make_sound(stereo_audio)
