import pygame


class Scoreboard:
    """Выводит игровую статистику."""

    def __init__(self, game):
        self.game = game
        self.screen = game.screen
        self.settings = game.settings
        self.stats = game.stats

        self.text_color = (230, 230, 230)

        self.font = pygame.font.Font(None, 32)
        self.large_font = pygame.font.Font(None, 64)

    def draw(self):
        """Отображает счёт, рекорд, уровень и жизни."""
        score_text = f"Счёт: {self.stats.score}"
        high_score_text = f"Рекорд: {self.stats.high_score}"
        level_text = f"Уровень: {self.stats.level}"
        ships_text = f"Жизни: {self.stats.ships_left}"

        self.screen.blit(
            self.font.render(
                score_text,
                True,
                self.text_color,
            ),
            (20, 15),
        )

        self.screen.blit(
            self.font.render(
                high_score_text,
                True,
                self.text_color,
            ),
            (20, 50),
        )

        self.screen.blit(
            self.font.render(
                level_text,
                True,
                self.text_color,
            ),
            (20, 85),
        )

        self.screen.blit(
            self.font.render(
                ships_text,
                True,
                self.text_color,
            ),
            (
                self.screen.get_width() - 150,
                15,
            ),
        )

    def draw_center_message(self, text):
        """Выводит крупное сообщение по центру."""
        image = self.large_font.render(
            text,
            True,
            self.text_color,
        )

        rect = image.get_rect(
            center=self.screen.get_rect().center
        )

        self.screen.blit(image, rect)