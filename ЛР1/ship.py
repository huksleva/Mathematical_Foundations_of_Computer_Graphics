import pygame


class Ship:
    """Класс корабля игрока."""

    def __init__(self, game):
        self.game = game
        self.settings = game.settings
        self.screen = game.screen

        self.width = 60
        self.height = 30

        self.rect = pygame.Rect(
            0,
            0,
            self.width,
            self.height,
        )

        self.rect.midbottom = self.screen.get_rect().midbottom

        self.x = float(self.rect.x)

        self.moving_right = False
        self.moving_left = False

    def update(self):
        """Обновляет положение корабля."""
        if self.moving_right and self.rect.right < self.screen.get_width():
            self.x += self.settings.ship_speed

        if self.moving_left and self.rect.left > 0:
            self.x -= self.settings.ship_speed

        self.rect.x = int(self.x)

    def center_ship(self):
        """Возвращает корабль в центр нижней части экрана."""
        self.rect.midbottom = self.screen.get_rect().midbottom
        self.x = float(self.rect.x)

    def draw(self):
        """Рисует корабль."""
        pygame.draw.polygon(
            self.screen,
            (80, 160, 255),
            [
                (self.rect.centerx, self.rect.top),
                (self.rect.left, self.rect.bottom),
                (self.rect.right, self.rect.bottom),
            ],
        )

        pygame.draw.rect(
            self.screen,
            (220, 220, 230),
            (
                self.rect.centerx - 5,
                self.rect.top + 5,
                10,
                15,
            ),
        )