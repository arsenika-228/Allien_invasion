from pathlib import Path


class GameStats:
    # -- Статистика игры --

    def __init__(self, ai_game):
        self.settings = ai_game.settings
        self.path = Path('high_score.txt')
        self.high_score = self.load_high_score()
        self.reset_stats()

    def reset_stats(self):
        # Инициализация статистики
        self.ships_left = self.settings.ship_limit
        self.score = 0
        self.level = 1

    def load_high_score(self):
        if self.path.exists():
            try:
                return int(self.path.read_text())
            except ValueError:
                return 0
        return 0

    def save_high_score(self):
        self.path.write_text(str(self.high_score))
