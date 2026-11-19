"""Интерактивное окно с одиннадцатью упражнениями."""

import numpy as np
import pygame

from .exercises import (
    BLUE, ORANGE, TEAL, DEFAULT_POINT, DEFAULT_SEGMENT, TITLES,
    make_scene, parse_points, square_frames,
)
from .graphics import Drawer, Origin, ReferenceFrame, Unit, fit_frame

SIZE = (1120, 760)
PLOT = pygame.Rect(294, 174, 798, 452)
DETAILS = pygame.Rect(294, 642, 798, 89)
BUTTON = pygame.Rect(950, 104, 142, 37)
MODE_LINEAR = pygame.Rect(774, 104, 149, 37)
MODE_HOMOGENEOUS = pygame.Rect(923, 104, 169, 37)
PLAY = pygame.Rect(937, 666, 126, 36)
FIELD = pygame.Rect(303, 354, 514, 45)
SUBMIT = pygame.Rect(682, 428, 135, 38)
CANCEL = pygame.Rect(547, 428, 119, 38)
NAV = [pygame.Rect(21, 133 + i * 44, 234, 39) for i in range(len(TITLES))]

INK = (22, 35, 56)
MUTED = (82, 99, 123)
PANEL = (244, 247, 251)
WHITE = (255, 255, 255)
BORDER = (217, 225, 236)
SELECTED = (222, 235, 252)
ACCENT = (35, 84, 155)
SQUARE_LINE = (213, 89, 59)


class App:
    def __init__(self) -> None:
        unit = Unit(1)
        self.drawer = Drawer(*SIZE, 32, ReferenceFrame(Origin(0, 0), unit, unit))
        self.drawer.initialize("Матричная графика · Практическая работа № 3")
        self.screen = self.drawer.surface
        self.fonts = {
            name: pygame.font.SysFont(("segoeui", "dejavusans", "arial"), size, bold=bold)
            for name, size, bold in (
                ("small", 15, False), ("normal", 17, False), ("medium", 17, True),
                ("title", 32, True), ("brand", 23, True), ("input", 22, False),
            )
        }
        self.points = {1: DEFAULT_POINT.copy(), 3: DEFAULT_SEGMENT.copy()}
        self.homogeneous = True
        self.frames = {mode: square_frames(mode) for mode in (True, False)}
        self.editing = False
        self.edit_text = ""
        self.edit_error = ""
        self.running = True
        self.select(11)

    def select(self, task: int) -> None:
        self.task = task
        if task == 11:
            self.scene = None
            self.drawer.rf = fit_frame(PLOT, self.frames[self.homogeneous][0])
            self.restart()
        else:
            self.scene = make_scene(task, self.points.get(task))
            self.drawer.rf = fit_frame(PLOT, np.vstack([figure.points for figure in self.scene.figures]))

    def restart(self) -> None:
        self.progress = 0
        self.playing = True
        self.elapsed = 0

    def set_mode(self, homogeneous: bool) -> None:
        if self.homogeneous != homogeneous:
            self.homogeneous = homogeneous
            self.select(11)

    def update(self, elapsed: int) -> None:
        if self.task != 11 or not self.playing:
            return
        self.elapsed += elapsed
        steps, self.elapsed = divmod(self.elapsed, 66)
        last = len(self.frames[self.homogeneous]) - 1
        self.progress = min(last, self.progress + steps)
        self.playing = self.progress < last

    def open_editor(self) -> None:
        self.editing = True
        self.edit_error = ""
        self.edit_text = " ".join(f"{value:g}" for value in self.points[self.task].flat)
        pygame.key.start_text_input()

    def close_editor(self) -> None:
        self.editing = False
        pygame.key.stop_text_input()

    def apply_editor(self) -> None:
        try:
            points = parse_points(self.edit_text, 1 if self.task == 1 else 2)
        except ValueError as exc:
            self.edit_error = str(exc) if self.edit_text else "Введите координаты."
            return
        self.points[self.task] = points
        self.close_editor()
        self.select(self.task)

    def toggle_playback(self) -> None:
        if self.progress == len(self.frames[self.homogeneous]) - 1:
            self.restart()
        else:
            self.playing = not self.playing

    def handle(self, event: pygame.event.Event) -> None:
        if event.type == pygame.QUIT:
            self.running = False
            return
        if self.editing:
            if event.type == pygame.TEXTINPUT:
                self.edit_text = (self.edit_text + event.text)[:55]
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.close_editor()
                elif event.key == pygame.K_RETURN:
                    self.apply_editor()
                elif event.key == pygame.K_BACKSPACE:
                    mods = event.mod
                    self.edit_text = "" if mods & pygame.KMOD_CTRL else self.edit_text[:-1]
            elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if SUBMIT.collidepoint(event.pos):
                    self.apply_editor()
                elif CANCEL.collidepoint(event.pos):
                    self.close_editor()
            return
        if event.type == pygame.KEYDOWN:
            if event.key == pygame.K_ESCAPE:
                self.running = False
            elif event.key in (pygame.K_UP, pygame.K_DOWN):
                step = -1 if event.key == pygame.K_UP else 1
                self.select((self.task - 1 + step) % len(TITLES) + 1)
            elif self.task in (1, 3) and event.key == pygame.K_e:
                self.open_editor()
            elif self.task == 11:
                if event.key == pygame.K_TAB:
                    self.set_mode(not self.homogeneous)
                elif event.key == pygame.K_SPACE:
                    self.toggle_playback()
                elif event.key == pygame.K_r:
                    self.restart()
        elif event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for task, rect in enumerate(NAV, 1):
                if rect.collidepoint(event.pos):
                    self.select(task)
                    return
            if self.task in (1, 3) and BUTTON.collidepoint(event.pos):
                self.open_editor()
            elif self.task == 11:
                if MODE_LINEAR.collidepoint(event.pos):
                    self.set_mode(False)
                elif MODE_HOMOGENEOUS.collidepoint(event.pos):
                    self.set_mode(True)
                elif PLAY.collidepoint(event.pos):
                    self.toggle_playback()

    def text(self, text: str, position: tuple[int, int], font: str = "normal", color=INK) -> None:
        self.screen.blit(self.fonts[font].render(text, True, color), position)

    def card(self, rect: pygame.Rect, color=WHITE, *, border=True) -> None:
        pygame.draw.rect(self.screen, color, rect, border_radius=9)
        if border:
            pygame.draw.rect(self.screen, BORDER, rect, width=1, border_radius=9)

    def button(self, label: str, rect: pygame.Rect, selected: bool = False) -> None:
        self.card(rect, SELECTED if selected else WHITE)
        text = self.fonts["small"].render(label, True, ACCENT if selected else INK)
        self.screen.blit(text, text.get_rect(center=rect.center))

    def draw_navigation(self) -> None:
        pygame.draw.rect(self.screen, PANEL, (0, 75, 272, 685))
        pygame.draw.line(self.screen, BORDER, (271, 75), (271, 759))
        self.text("Упражнения", (30, 102), "medium", MUTED)
        for task, (title, rect) in enumerate(zip(TITLES, NAV), 1):
            active = task == self.task
            if active:
                self.card(rect, SELECTED, border=False)
            self.text(f"{task:02d}", (rect.x + 11, rect.y + 9), "small", ACCENT if active else MUTED)
            self.text(title, (rect.x + 41, rect.y + 9), "small", INK)
        pygame.draw.line(self.screen, BORDER, (30, 638), (240, 638))
        self.text("↑ / ↓   Смена упражнения", (30, 658), "small", MUTED)
        self.text("Esc   Выход", (30, 684), "small", MUTED)

    def draw_legend(self, items) -> None:
        x = PLOT.x + 2
        for color, label in items:
            pygame.draw.line(self.screen, color, (x, 153), (x + 18, 153), width=3)
            self.text(label, (x + 28, 142), "small", MUTED)
            x += self.fonts["small"].size(label)[0] + 52

    def draw_scene(self) -> None:
        drawer = self.drawer
        if self.task == 8:
            drawer.color = (136, 152, 174)
            drawer.draw_line(0, 0, 8, 8)
            drawer.draw_text(8, 8, "y = x")
        for figure in self.scene.figures:
            drawer.color = figure.color
            if len(figure.points) == 1:
                drawer.draw_point(*figure.points[0])
            else:
                drawer.draw_polygon(figure.points, 3, closed=figure.closed)
        if self.task == 1:
            labels = ("A", "A′")
        elif self.task == 4:
            labels = ("M", "M′")
        elif self.task == 6:
            labels = ("P", "P′")
        else:
            labels = ()
        if labels:
            points = [figure for figure in self.scene.figures if len(figure.points) == 1]
            for i, (label, figure) in enumerate(zip(labels, points)):
                x, y = drawer.pixel(*figure.points[0])
                self.text(label, (x + 9, y - 27 + 38 * i), "medium", figure.color)
        if self.task == 2:
            drawer.color = TEAL
            drawer.draw_text(3.65, -0.45, "Примитивы Pygame")

    def draw_squares(self) -> None:
        drawer = self.drawer
        frames = self.frames[self.homogeneous]
        for i, frame in enumerate(frames[:self.progress + 1]):
            drawer.color = INK if i == 0 else SQUARE_LINE
            drawer.draw_polygon(frame, 2 if i == 0 else 1)
        center = (5, 3.5) if self.homogeneous else (0, 0)
        drawer.color = ACCENT
        drawer.draw_point(*center)

    def draw_details(self) -> None:
        self.card(DETAILS, PANEL)
        if self.task == 11:
            last = len(self.frames[self.homogeneous]) - 1
            subtitle, params = (
                ("Вращение вокруг центра (5; 3,5)", "Sₓ = Sᵧ = 0,95   ·   α = π/64")
                if self.homogeneous
                else ("Вращение вокруг начала координат", "m = 0,9   ·   α = π/32")
            )
            self.text(subtitle, (315, 654), "medium")
            self.text(params, (315, 689), "normal", MUTED)
            self.text(f"Шаг {self.progress} / {last}", (801, 652), "small", MUTED)
            pygame.draw.rect(self.screen, BORDER, (801, 684, 110, 5), border_radius=2)
            if self.progress:
                pygame.draw.rect(self.screen, ACCENT, (801, 684, int(110 * self.progress / last), 5), border_radius=2)
            label = "Повторить" if self.progress == last else "Пауза" if self.playing else "Продолжить"
            self.button(label, PLAY)
        else:
            first, second = self.scene.description
            self.text(first, (315, 655), "medium")
            self.text(second, (315, 689), "normal", MUTED)

    def draw_editor(self) -> None:
        shade = pygame.Surface(SIZE, pygame.SRCALPHA)
        shade.fill((14, 26, 45, 140))
        self.screen.blit(shade, (0, 0))
        self.card(pygame.Rect(273, 240, 574, 253))
        self.text("Ввод координат", (303, 261), "brand")
        fields = "x y" if self.task == 1 else "x₁ y₁ x₂ y₂"
        self.text(f"Порядок чисел  {fields}   ·   Ctrl+Backspace очищает поле", (303, 307), "small", MUTED)
        self.card(FIELD, SELECTED)
        previous_clip = self.screen.get_clip()
        self.screen.set_clip(FIELD.inflate(-20, -4))
        field_text = self.fonts["input"].render(self.edit_text, True, INK)
        field_x = min(FIELD.x + 11, FIELD.right - 15 - field_text.get_width())
        self.screen.blit(field_text, (field_x, FIELD.y + 6))
        cursor = field_x + field_text.get_width() + 2
        pygame.draw.line(self.screen, ACCENT, (cursor, FIELD.y + 10), (cursor, FIELD.bottom - 10))
        self.screen.set_clip(previous_clip)
        self.text(self.edit_error, (303, 400), "small", ORANGE)
        self.button("Отмена", CANCEL)
        self.button("Применить", SUBMIT, selected=True)

    def draw(self) -> None:
        self.screen.fill(WHITE)
        pygame.draw.line(self.screen, BORDER, (0, 74), (1119, 74))
        self.text("Матричная графика", (30, 19), "brand")
        self.text("Практическая работа № 3", (870, 25), "normal", MUTED)
        self.draw_navigation()
        self.text(TITLES[self.task - 1], (294, 91), "title")
        if self.task == 11:
            self.button("Линейные", MODE_LINEAR, not self.homogeneous)
            self.button("Однородные", MODE_HOMOGENEOUS, self.homogeneous)
            self.draw_legend(((INK, "Исходный квадрат"), (SQUARE_LINE, "Последовательные контуры"), (ACCENT, "Центр")))
        else:
            self.draw_legend(self.scene.legend)
            if self.task in (1, 3):
                self.button("Ввести координаты", BUTTON)
        self.card(PLOT)
        self.drawer.draw_grid(PLOT)
        if self.task == 11:
            self.draw_squares()
        else:
            self.draw_scene()
        self.draw_details()
        if self.editing:
            self.draw_editor()


def main() -> None:
    app = App()
    clock = pygame.time.Clock()
    try:
        while app.running:
            elapsed = clock.tick(30)
            for event in pygame.event.get():
                app.handle(event)
            app.update(elapsed)
            app.draw()
            pygame.display.flip()
    finally:
        pygame.quit()


if __name__ == "__main__":
    main()
