"""Преобразование координат и графические примитивы Pygame."""

from dataclasses import dataclass
from math import ceil, floor, log10

import numpy as np
import pygame
from pygame import gfxdraw

from .transform import Matrix, cartesian


@dataclass(frozen=True)
class Origin:
    x0: float
    y0: float


@dataclass(frozen=True)
class Unit:
    pixels: float


@dataclass(frozen=True)
class ReferenceFrame:
    origin: Origin
    ux: Unit
    uy: Unit


def get_x(rf: ReferenceFrame, x: float) -> int:
    return int(rf.origin.x0 + x * rf.ux.pixels)


def get_y(rf: ReferenceFrame, y: float) -> int:
    return int(rf.origin.y0 - y * rf.uy.pixels)


def get_length(unit: Unit, dl: float) -> int:
    return int(unit.pixels * dl)


def fit_frame(rect: pygame.Rect, points: Matrix) -> ReferenceFrame:
    """Вписывает фигуры и начало координат, сохраняя одинаковый масштаб осей."""
    bounds = np.vstack((cartesian(points), (0, 0)))
    low = bounds.min(axis=0)
    high = bounds.max(axis=0)
    span = high - low
    span = np.maximum(span, max(span.max() * 0.1, 1e-7))
    pixels = min((rect.width - 104) / span[0], (rect.height - 104) / span[1])
    x, y = (high + low) / 2
    unit = Unit(float(pixels))
    return ReferenceFrame(Origin(rect.centerx - x * pixels, rect.centery + y * pixels), unit, unit)


def ticks(low: float, high: float, bins: int) -> list[float]:
    raw = (high - low) / bins
    power = 10 ** floor(log10(raw))
    step = next(n * power for n in (1, 2, 5, 10) if n * power >= raw)
    return [i * step for i in range(ceil(low / step), floor(high / step) + 1)]


class Drawer:
    def __init__(self, res_x: int, res_y: int, color_depth: int, rf: ReferenceFrame):
        self.size = (res_x, res_y)
        self.color_depth = color_depth
        self.rf = rf
        self._color = (23, 33, 53)

    def initialize(self, caption: str) -> None:
        pygame.display.init()
        pygame.font.init()
        self.surface = pygame.display.set_mode(self.size, depth=self.color_depth)
        pygame.display.set_caption(caption)
        self.font = pygame.font.SysFont(("segoeui", "dejavusans", "arial"), 15)

    @property
    def color(self) -> tuple[int, int, int]:
        return self._color

    @color.setter
    def color(self, value: tuple[int, int, int]) -> None:
        self._color = value

    def pixel(self, x: float, y: float) -> tuple[int, int]:
        return get_x(self.rf, x), get_y(self.rf, y)

    def draw_text(self, x: float, y: float, text: str) -> None:
        self.surface.blit(self.font.render(text, True, self.color), self.pixel(x, y))

    def draw_line(self, x1: float, y1: float, x2: float, y2: float, width: int = 1) -> None:
        start, end = self.pixel(x1, y1), self.pixel(x2, y2)
        if width == 1:
            pygame.draw.aaline(self.surface, self.color, start, end)
        else:
            pygame.draw.line(self.surface, self.color, start, end, width)

    def draw_polygon(self, points: Matrix, width: int = 1, *, closed: bool = True) -> None:
        pixels = [self.pixel(x, y) for x, y in cartesian(points)]
        if width == 1:
            pygame.draw.aalines(self.surface, self.color, closed, pixels)
        else:
            pygame.draw.lines(self.surface, self.color, closed, pixels, width)

    def draw_circle(self, x: float, y: float, radius: float) -> None:
        pixels = max(1, get_length(self.rf.ux, radius))
        pygame.draw.circle(self.surface, self.color, self.pixel(x, y), pixels, width=2)

    def draw_point(self, x: float, y: float, radius: int = 5) -> None:
        px, py = self.pixel(x, y)
        gfxdraw.filled_circle(self.surface, px, py, radius + 2, (255, 255, 255))
        gfxdraw.filled_circle(self.surface, px, py, radius, self.color)
        gfxdraw.aacircle(self.surface, px, py, radius, self.color)

    def draw_axes(self, x_min: float, x_max: float, y_min: float, y_max: float) -> None:
        self.draw_line(x_min, 0, x_max, 0)
        self.draw_line(0, y_min, 0, y_max)

    def draw_grid(self, rect: pygame.Rect) -> None:
        rf = self.rf
        x_min = (rect.left + 22 - rf.origin.x0) / rf.ux.pixels
        x_max = (rect.right - 22 - rf.origin.x0) / rf.ux.pixels
        y_min = (rf.origin.y0 - rect.bottom + 22) / rf.uy.pixels
        y_max = (rf.origin.y0 - rect.top - 22) / rf.uy.pixels
        grid = (230, 235, 242)
        text = (83, 99, 124)
        for x in ticks(x_min, x_max, 9):
            self.color = grid
            self.draw_line(x, y_min, x, y_max)
            if x:
                px, py = self.pixel(x, y_min)
                label = self.font.render(f"{x:g}", True, text)
                self.surface.blit(label, label.get_rect(midtop=(px, py + 2)))
        for y in ticks(y_min, y_max, 6):
            self.color = grid
            self.draw_line(x_min, y, x_max, y)
            if y:
                self.color = text
                self.draw_text(x_min, y, f"{y:g}")
        self.color = (112, 136, 172)
        self.draw_axes(x_min, x_max, y_min, y_max)
        self.draw_text(x_max, 0, "x")
        self.draw_text(0, y_max, "y")
        self.draw_text(0, 0, "  O")
