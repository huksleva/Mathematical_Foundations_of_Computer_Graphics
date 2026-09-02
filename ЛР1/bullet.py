import pygame


class Bullet(pygame.sprite.Sprite):
    """Класс снаряда."""

    def __init__(self, game):
        super().__init__()

        self.settings = game.settings
        self.screen = game.screen

        self.rect = pygame.Rect(
            0,
            0,
            self.settings.bullet_width,
            self.settings.bullet_height,
        )

        self.rect.midtop = game.ship.rect.midtop

        self.y = float(self.rect.y)

    def update(self):
        """Перемещает снаряд вверх."""
        self.y -= self.settings.bullet_speed
        self.rect.y = int(self.y)

    def draw_bullet(self):
        """Рисует снаряд."""
        pygame.draw.rect(
            self.screen,
            self.settings.bullet_color,
            self.rect,
        )