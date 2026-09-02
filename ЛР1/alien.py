import pygame


class Alien(pygame.sprite.Sprite):
    """Класс одного пришельца."""

    def __init__(self, game):
        super().__init__()

        self.game = game
        self.settings = game.settings
        self.screen = game.screen

        self.width = self.settings.alien_width
        self.height = self.settings.alien_height

        self.rect = pygame.Rect(
            0,
            0,
            self.width,
            self.height,
        )

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
        pygame.draw.ellipse(
            self.screen,
            self.settings.alien_color,
            self.rect,
        )

        eye_size = 6

        pygame.draw.circle(
            self.screen,
            (20, 20, 20),
            (
                self.rect.centerx - 10,
                self.rect.centery - 3,
            ),
            eye_size,
        )

        pygame.draw.circle(
            self.screen,
            (20, 20, 20),
            (
                self.rect.centerx + 10,
                self.rect.centery - 3,
            ),
            eye_size,
        )