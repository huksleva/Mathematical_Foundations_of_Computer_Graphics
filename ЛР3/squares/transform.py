"""Матрицы для векторов-строк. Преобразования применяются слева направо."""

from math import cos, sin

import numpy as np
from numpy.typing import NDArray

Matrix = NDArray[np.float64]


def translate(dx: float, dy: float) -> Matrix:
    return np.array([[1, 0, 0], [0, 1, 0], [dx, dy, 1]], dtype=float)


def scale(sx: float, sy: float) -> Matrix:
    return np.diag([sx, sy, 1.0])


def rotate(angle: float) -> Matrix:
    c, s = cos(angle), sin(angle)
    return np.array([[c, s, 0], [-s, c, 0], [0, 0, 1]], dtype=float)


def about_center(center: Matrix, factor: float, angle: float) -> Matrix:
    x, y = center
    return translate(-x, -y) @ scale(factor, factor) @ rotate(angle) @ translate(x, y)


def cartesian(points: Matrix) -> Matrix:
    """Нормализует [x, y, w] при w ≠ 0 и пропускает обычные пары [x, y]."""
    if points.shape[1] == 2:
        return points
    weights = points[:, 2:3]
    if np.any(weights == 0):
        raise ValueError("Точка с w = 0 не имеет конечных декартовых координат.")
    return points[:, :2] / weights


def successive(points: Matrix, matrix: Matrix, count: int) -> list[Matrix]:
    frames = [points.copy()]
    for _ in range(count):
        frames.append(frames[-1] @ matrix)
    return frames
