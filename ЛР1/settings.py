class Settings:
    """Хранит настройки игры."""

    def __init__(self):
        # Параметры экрана
        self.screen_width = 1200
        self.screen_height = 700
        self.bg_color = (15, 20, 35)

        # Настройки корабля
        self.ship_speed = 5.0
        self.ship_limit = 3

        # Настройки пули
        self.bullet_width = 4
        self.bullet_height = 15
        self.bullet_color = (240, 240, 240)
        self.bullet_speed = 7.0
        self.bullets_allowed = 3

        # Настройки пришельцев
        self.alien_width = 50
        self.alien_height = 35
        self.alien_color = (80, 220, 120)
        self.alien_speed = 1.0
        self.alien_drop_speed = 20
        self.fleet_direction = 1

        # Система очков
        self.alien_points = 50

        # Уровень сложности
        self.speedup_scale = 1.15
        self.score_scale = 1.5

        self.initialize_dynamic_settings()

    def initialize_dynamic_settings(self):
        """Сбрасывает динамические настройки."""
        self.ship_speed = 5.0
        self.bullet_speed = 7.0
        self.alien_speed = 1.0

        self.alien_points = 50
        self.fleet_direction = 1

    def increase_speed(self):
        """Увеличивает скорость игры при переходе на новый уровень."""
        self.ship_speed *= self.speedup_scale
        self.bullet_speed *= self.speedup_scale
        self.alien_speed *= self.speedup_scale

        self.alien_points = int(self.alien_points * self.score_scale)