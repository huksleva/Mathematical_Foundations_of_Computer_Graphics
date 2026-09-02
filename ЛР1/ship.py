from pathlib import Path

import pygame


class Ship:
    """Класс корабля игрока."""

    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        self.screen = game.screen

        # Загружаем изображение корабля.
        image_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "ship.png"
        )

        self.image = pygame.image.load(
            image_path
        ).convert_alpha()

        # Уменьшаем исходное изображение
        # до подходящего размера в игре.
        self.image = pygame.transform.smoothscale(
            self.image,
            (70, 50),
        )

        self.rect = self.image.get_rect()

        # Корабль находится внизу по центру.
        self.rect.midbottom = self.screen.get_rect().midbottom

        # Храним координату X как float для плавного движения.
        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Обновляет положение корабля."""
        if (
            self.moving_right
            and self.rect.right < self.screen.get_width()
        ):
            self.x += self.settings.ship_speed

        if (
            self.moving_left
            and self.rect.left > 0
        ):
            self.x -= self.settings.ship_speed

        self.rect.x = int(self.x)

    def center_ship(self):
        """Возвращает корабль в центр нижней части экрана."""
        self.rect.midbottom = self.screen.get_rect().midbottom
        self.x = float(self.rect.x)

    def draw(self):
        """Рисует корабль."""
        self.screen.blit(self.image, self.rect)