import sys
import pygame

from settings import Settings
from ship import Ship
from bullet import Bullet
from alien import Alien
from game_stats import GameStats
from scoreboard import Scoreboard


class AlienInvasion:
    """Основной класс игры."""

    def __init__(self):
        pygame.init()

        self.settings = Settings()

        self.screen = pygame.display.set_mode(
            (
                self.settings.screen_width,
                self.settings.screen_height,
            )
        )

        pygame.display.set_caption("Инопланетное вторжение")

        self.clock = pygame.time.Clock()

        self.stats = GameStats(self)
        self.scoreboard = Scoreboard(self)

        self.ship = Ship(self)

        self.bullets = pygame.sprite.Group()
        self.aliens = pygame.sprite.Group()

        self._create_fleet()

    def run_game(self):
        """Главный игровой цикл."""
        while True:
            self._check_events()

            if self.stats.game_active:
                self.ship.update()
                self._update_bullets()
                self._update_aliens()

            self._update_screen()

            self.clock.tick(60)

    def _check_events(self):
        """Обрабатывает события."""
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self._quit_game()

            elif event.type == pygame.KEYDOWN:
                self._check_keydown_events(event)

            elif event.type == pygame.KEYUP:
                self._check_keyup_events(event)

        keys = pygame.key.get_pressed()

        if keys[pygame.K_SPACE] and self.stats.game_active:
            self._fire_bullet()

    def _check_keydown_events(self, event):
        """Обрабатывает нажатия клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = True

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = True

        elif event.key == pygame.K_ESCAPE:
            self._quit_game()

        elif event.key == pygame.K_RETURN:
            if not self.stats.game_active:
                self._start_game()

    def _check_keyup_events(self, event):
        """Обрабатывает отпускание клавиш."""
        if event.key == pygame.K_RIGHT:
            self.ship.moving_right = False

        elif event.key == pygame.K_LEFT:
            self.ship.moving_left = False

    def _fire_bullet(self):
        """Создаёт новый снаряд."""
        if len(self.bullets) < self.settings.bullets_allowed:
            bullet = Bullet(self)
            self.bullets.add(bullet)

    def _update_bullets(self):
        """Обновляет снаряды."""
        self.bullets.update()

        for bullet in self.bullets.copy():
            if bullet.rect.bottom <= 0:
                self.bullets.remove(bullet)

        self._check_bullet_alien_collisions()

    def _check_bullet_alien_collisions(self):
        """Проверяет столкновения снарядов и пришельцев."""
        collisions = pygame.sprite.groupcollide(
            self.bullets,
            self.aliens,
            True,
            True,
        )

        if collisions:
            for aliens in collisions.values():
                self.stats.score += (
                    self.settings.alien_points * len(aliens)
                )

            if self.stats.score > self.stats.high_score:
                self.stats.high_score = self.stats.score

        if not self.aliens:
            self._start_new_level()

    def _create_fleet(self):
        """Создаёт флот пришельцев."""
        self.aliens.empty()

        alien_width = self.settings.alien_width
        alien_height = self.settings.alien_height

        available_x = (
            self.settings.screen_width
            - 2 * alien_width
        )

        columns = available_x // (2 * alien_width)

        available_y = (
            self.settings.screen_height
            // 3
        )

        rows = max(
            2,
            available_y // (2 * alien_height),
        )

        for row_number in range(rows):
            for column_number in range(columns):
                alien = Alien(self)

                alien.x = (
                    alien_width
                    + 2 * alien_width * column_number
                )

                alien.rect.x = int(alien.x)

                alien.rect.y = (
                    alien_height
                    + 2 * alien_height * row_number
                )

                self.aliens.add(alien)

    def _update_aliens(self):
        """Обновляет флот."""
        self._check_fleet_edges()

        self.aliens.update()

        if pygame.sprite.spritecollideany(
            self.ship,
            self.aliens,
        ):
            self._ship_hit()

        self._check_aliens_bottom()

    def _check_fleet_edges(self):
        """Проверяет достижение флотом края экрана."""
        for alien in self.aliens.sprites():
            if (
                alien.rect.right
                >= self.settings.screen_width
                and self.settings.fleet_direction == 1
            ):
                self._change_fleet_direction()
                break

            if (
                alien.rect.left <= 0
                and self.settings.fleet_direction == -1
            ):
                self._change_fleet_direction()
                break

    def _change_fleet_direction(self):
        """Меняет направление и опускает флот."""
        self.settings.fleet_direction *= -1

        for alien in self.aliens.sprites():
            alien.rect.y += self.settings.alien_drop_speed

    def _check_aliens_bottom(self):
        """Проверяет достижение нижней границы."""
        screen_rect = self.screen.get_rect()

        for alien in self.aliens.sprites():
            if alien.rect.bottom >= screen_rect.bottom:
                self._ship_hit()
                break

    def _ship_hit(self):
        """Обрабатывает потерю корабля."""
        if self.stats.ships_left > 1:
            self.stats.ships_left -= 1

            self.bullets.empty()
            self.aliens.empty()

            self.ship.center_ship()
            self._create_fleet()

            pygame.time.delay(700)
        else:
            self.stats.ships_left = 0
            self.stats.game_active = False

    def _start_game(self):
        """Начинает новую игру."""
        self.stats.reset_stats()
        self.stats.game_active = True

        self.settings.initialize_dynamic_settings()

        self.bullets.empty()
        self._create_fleet()

        self.ship.center_ship()

    def _start_new_level(self):
        """Переходит на новый уровень."""
        self.stats.level += 1
        self.settings.increase_speed()

        self.bullets.empty()
        self._create_fleet()

    def _update_screen(self):
        """Перерисовывает экран."""
        self.screen.fill(self.settings.bg_color)

        for bullet in self.bullets.sprites():
            bullet.draw_bullet()

        for alien in self.aliens.sprites():
            alien.draw()

        self.ship.draw()

        self.scoreboard.draw()

        if not self.stats.game_active:
            if self.stats.level == 1 and self.stats.score == 0:
                self.scoreboard.draw_center_message(
                    "ENTER — начать игру"
                )
            else:
                self.scoreboard.draw_center_message(
                    "GAME OVER"
                )

        pygame.display.flip()

    @staticmethod
    def _quit_game():
        """Завершает игру."""
        pygame.quit()
        sys.exit()


def main():
    """Точка входа."""
    game = AlienInvasion()
    game.run_game()


if __name__ == "__main__":
    main()