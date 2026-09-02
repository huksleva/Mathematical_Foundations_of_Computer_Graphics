from pathlib import Path

import pygame


class Alien(pygame.sprite.Sprite):
    """Класс одного пришельца."""

    def __init__(self, game):
        super().__init__()

        self.game = game
        self.settings = game.settings
        self.screen = game.screen

        # Загружаем изображение пришельца.
        image_path = (
            Path(__file__).resolve().parent
            / "assets"
            / "alien.png"
        )

        self.image = pygame.image.load(
            image_path
        ).convert_alpha()

        # Масштабируем изображение.
        self.image = pygame.transform.smoothscale(
            self.image,
            (50, 50),
        )

        self.rect = self.image.get_rect()

        # Координата X хранится как float.
        self.x = float(self.rect.x)

    def update(self):
        """Перемещает пришельца по горизонтали."""
        self.x += (
            self.settings.alien_speed
            * self.settings.fleet_direction
        )

        self.rect.x = int(self.x)

    def draw(self):
        """Рисует пришельца."""
        self.screen.blit(
            self.image,
            self.rect,
        )