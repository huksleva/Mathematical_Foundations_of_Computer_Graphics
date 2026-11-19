"""Данные упражнений и расчёт фигур для окна визуализации."""

from collections.abc import Iterable
from dataclasses import dataclass
from math import pi

import numpy as np

from .transform import Matrix, about_center, rotate, scale, successive

TITLES = (
    "Преобразование точки",
    "Графические примитивы",
    "Преобразование отрезка",
    "Середины отрезков",
    "Параллельные отрезки",
    "Пересечение отрезков",
    "Поворот треугольника",
    "Отражение треугольника",
    "Масштабирование",
    "Улитка Паскаля",
    "Вращение квадрата",
)

BLUE = (36, 92, 177)
ORANGE = (184, 62, 29)
TEAL = (2, 114, 100)
T_13 = np.array([[1, 3], [4, 1]], dtype=float)
T_45 = np.array([[1, 2], [3, 1]], dtype=float)
T_6 = np.array([[1, 2], [1, -3]], dtype=float)
T_7 = np.array([[0, 1], [-1, 0]], dtype=float)
T_8 = np.array([[0, 1], [1, 0]], dtype=float)
T_9 = 2.0 * np.eye(2)
L_6 = np.array([[-1/2, 3/2], [3, -2], [-1, -1], [3, 5/3]], dtype=float)
L_7 = np.array([[3, -1], [4, 1], [2, 1]], dtype=float)
L_8 = np.array([[8, 1], [7, 3], [6, 2]], dtype=float)

DEFAULT_POINT = np.array([[3, 2]], dtype=float)
DEFAULT_SEGMENT = np.array([[1, 1], [4, 2]], dtype=float)
SQUARE_LINEAR = 100 * np.array([[2, -2], [-2, -2], [-2, 2], [2, 2]], dtype=float)
SQUARE_HOMOGENEOUS = np.array(
    [[2, 0.5, 1], [8, 0.5, 1], [8, 6.5, 1], [2, 6.5, 1]], dtype=float
)

Color = tuple[int, int, int]


@dataclass(frozen=True)
class Figure:
    points: Matrix
    color: Color
    closed: bool = False


@dataclass(frozen=True)
class Circle:
    center: tuple[float, float]
    radius: float
    color: Color

    def bounds(self) -> Matrix:
        x, y = self.center
        r = self.radius
        return np.array([[x - r, y - r], [x + r, y + r]])


@dataclass(frozen=True)
class Scene:
    figures: list[Figure]
    description: tuple[str, str]
    legend: tuple[tuple[Color, str], ...]
    circle: Circle | None = None

    def bounds_points(self) -> Matrix:
        points = [figure.points for figure in self.figures]
        if self.circle is not None:
            points.append(self.circle.bounds())
        return np.vstack(points)


def point_label(point: Iterable[float]) -> str:
    return "(" + "; ".join(f"{value:.6g}" for value in point) + ")"


def matrix_label(matrix: Matrix) -> str:
    rows = [", ".join(f"{value:g}".replace("-", "−") for value in row) for row in matrix]
    return "T = [" + ", ".join(f"[{row}]" for row in rows) + "]"


def parse_points(text: str, rows: int) -> Matrix:
    fields = text.replace(",", ".").split()
    if len(fields) != 2 * rows:
        raise ValueError(f"Нужно ввести {2 * rows} числа через пробел.")
    try:
        values = [float(value) for value in fields]
    except ValueError as exc:
        raise ValueError("Введите числа. Дробную часть отделите точкой или запятой.") from exc
    points = np.array(values, dtype=float).reshape(rows, 2)
    if not np.all(np.isfinite(points)) or np.any(np.abs(points) > 1_000_000):
        raise ValueError("Координаты должны быть числами от −1 000 000 до 1 000 000.")
    return points


def slopes(points: Matrix) -> Matrix:
    vectors = points[1::2] - points[::2]
    return vectors[:, 1] / vectors[:, 0]


def intersection(points: Matrix) -> Matrix:
    a, b, c, d = points
    direction = b - a
    t, _ = np.linalg.solve(np.column_stack((direction, c - d)), c - a)
    return a + t * direction


def pascal_curve() -> Matrix:
    theta = np.linspace(0, 2 * pi, 721)
    r = 1.2 + 2 * np.cos(theta)
    return np.column_stack((r * np.cos(theta), r * np.sin(theta)))


def square_frames(homogeneous: bool) -> list[Matrix]:
    if homogeneous:
        center = SQUARE_HOMOGENEOUS[:, :2].mean(axis=0)
        matrix = about_center(center, 0.95, pi / 64)
        return successive(SQUARE_HOMOGENEOUS, matrix, 50)
    matrix = (scale(0.9, 0.9) @ rotate(pi / 32))[:2, :2]
    return successive(SQUARE_LINEAR, matrix, 20)


def paired(points: Matrix, matrix: Matrix, size: int, description: tuple[str, str]) -> Scene:
    transformed = points @ matrix
    figures = []
    for source, color in ((points, BLUE), (transformed, ORANGE)):
        for start in range(0, len(source), size):
            figures.append(Figure(source[start:start + size], color, closed=size == 3))
    return Scene(figures, description, ((BLUE, "Исходные"), (ORANGE, "Преобразованные")))


def make_scene(task: int, user_points: Matrix | None = None) -> Scene:
    if task == 1:
        points = DEFAULT_POINT if user_points is None else user_points
        return paired(points, T_13, 1, (
            matrix_label(T_13),
            f"A {point_label(points[0])}  →  A′ {point_label((points @ T_13)[0])}",
        ))
    if task == 2:
        circle = Circle((2.0, 2.0), 1.0, BLUE)
        figures = [
            Figure(np.array([[4, 1], [7, 3]], dtype=float), ORANGE),
            Figure(np.array([[4, 1], [7, 0.5]], dtype=float), TEAL),
        ]
        return Scene(figures, (
            "Окружность, два отрезка и текст",
            f"Центр окружности {point_label(circle.center)}, радиус {circle.radius:g}.",
        ), (), circle)
    if task == 3:
        points = DEFAULT_SEGMENT if user_points is None else user_points
        a, b = points
        ap, bp = points @ T_13
        return paired(points, T_13, 2, (
            f"A {point_label(a)}  →  A′ {point_label(ap)}",
            f"B {point_label(b)}  →  B′ {point_label(bp)}",
        ))
    if task == 4:
        points = np.array([[0, 100], [200, 300]], dtype=float)
        mid = points.mean(axis=0, keepdims=True)
        mid_transformed = (points @ T_45).mean(axis=0, keepdims=True)
        scene = paired(points, T_45, 2, (
            matrix_label(T_45),
            f"M {point_label(mid[0])}  →  M′ {point_label(mid_transformed[0])}",
        ))
        figures = scene.figures + [
            Figure(np.vstack((mid, mid_transformed)), TEAL),
            Figure(mid, TEAL),
            Figure(mid_transformed, TEAL),
        ]
        return Scene(figures, scene.description, (*scene.legend, (TEAL, "Середины")))
    if task == 5:
        points = np.array([[50, 100], [250, 200], [50, 200], [250, 300]], dtype=float)
        k1, k2 = slopes(points)
        kp1, kp2 = slopes(points @ T_45)
        return paired(points, T_45, 2, (
            f"До преобразования: k₁ = {k1:g}, k₂ = {k2:g}",
            f"После преобразования: k′₁ = {kp1:g}, k′₂ = {kp2:g}",
        ))
    if task == 6:
        points = L_6 * 100
        cross = intersection(points)
        cross_transformed = intersection(points @ T_6)
        scene = paired(points, T_6, 2, (
            f"{matrix_label(T_6)}, масштаб исходных координат ×100",
            f"P {point_label(cross)}  →  P′ {point_label(cross_transformed)}",
        ))
        figures = scene.figures + [
            Figure(cross[None, :], BLUE),
            Figure(cross_transformed[None, :], ORANGE),
        ]
        return Scene(figures, scene.description, scene.legend)
    if task == 7:
        return paired(100 * L_7, T_7, 3, (
            f"{matrix_label(T_7)}, поворот на 90° против часовой стрелки",
            "Координаты умножены на 100. Экранный сдвиг одинаков для обеих фигур.",
        ))
    if task == 8:
        return paired(L_8, T_8, 3, (
            f"{matrix_label(T_8)}, отражение относительно y = x",
            "Координаты x и y меняются местами.",
        ))
    if task == 9:
        return paired(np.array([[5, 1], [5, 2], [3, 2]], dtype=float), T_9, 3, (
            matrix_label(T_9),
            "Расстояния от начала координат увеличиваются в 2 раза.",
        ))
    if task == 10:
        return Scene([Figure(pascal_curve(), TEAL, closed=True)], (
            "r = b + 2a cos θ,  x = r cos θ,  y = r sin θ",
            "a = 1, b = 1,2. При b < 2a у кривой появляется внутренняя петля.",
        ), ((TEAL, "Улитка Паскаля"),))
    raise ValueError(f"Неизвестное упражнение: {task}")
