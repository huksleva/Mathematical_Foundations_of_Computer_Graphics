from math import cos, pi, sin
from unittest import TestCase

import numpy as np
from numpy.testing import assert_allclose, assert_array_equal

from squares.exercises import L_6, L_7, make_scene, parse_points, square_frames
from squares.graphics import Origin, ReferenceFrame, Unit, get_length, get_x, get_y
from squares.transform import cartesian


class ExerciseTests(TestCase):
    def test_point_and_segment_transformations(self):
        point = parse_points("-3,5 2", 1)
        assert_allclose(make_scene(1, point).figures[1].points, [[4.5, -8.5]])
        assert_allclose(make_scene(3).figures[1].points, [[5, 4], [12, 14]])

    def test_coordinate_input_rejects_invalid_values(self):
        for text in ("", "3", "n/a 2", "nan 0", "inf 3", "1000001 0"):
            with self.subTest(text=text), self.assertRaises(ValueError):
                parse_points(text, 1)

    def test_graphic_primitives_fit_including_the_circle(self):
        scene = make_scene(2)
        self.assertEqual(scene.circle.center, (2, 2))
        self.assertEqual(scene.circle.radius, 1)
        assert_allclose(scene.bounds_points().min(axis=0), [1, 0.5])
        assert_allclose(scene.bounds_points().max(axis=0), [7, 3])

    def test_midpoints(self):
        scene = make_scene(4)
        assert_allclose(scene.figures[-3].points, [[100, 200], [700, 400]])
        assert_allclose(scene.figures[-2].points, [[100, 200]])
        assert_allclose(scene.figures[-1].points, [[700, 400]])

    def test_parallel_segments(self):
        scene = make_scene(5)
        for segment, expected_slope in zip(scene.figures, (0.5, 0.5, 1, 1)):
            start, end = segment.points
            dx, dy = end - start
            self.assertAlmostEqual(dy / dx, expected_slope)

    def test_intersection_and_rotation_keep_original_matrices(self):
        intersection = make_scene(6)
        assert_allclose(intersection.figures[-2].points, [[80, 20]])
        assert_allclose(intersection.figures[-1].points, [[100, 100]])
        assert_allclose(L_6, [[-1/2, 3/2], [3, -2], [-1, -1], [3, 5/3]])

        rotation = make_scene(7)
        assert_array_equal(rotation.figures[1].points, [[100, 300], [-100, 400], [-100, 200]])
        assert_array_equal(L_7, [[3, -1], [4, 1], [2, 1]])

    def test_reflection_and_scaling(self):
        assert_array_equal(make_scene(8).figures[1].points, [[1, 8], [3, 7], [2, 6]])
        assert_array_equal(make_scene(9).figures[1].points, [[10, 2], [10, 4], [6, 4]])

    def test_pascal_curve_closes_and_has_an_inner_loop(self):
        curve = make_scene(10).figures[0].points
        assert_allclose(curve[0], [3.2, 0])
        assert_allclose(curve[len(curve) // 2], [0.8, 0], atol=1e-10)
        assert_allclose(curve[0], curve[-1], atol=1e-10)
        self.assertLess(np.linalg.norm(curve, axis=1).min(), 0.01)

    def test_square_iterations_against_direct_rotation(self):
        cases = (
            (False, 20, (0, 0), 400, 0.9, pi / 32),
            (True, 50, (5, 3.5), 6, 0.95, pi / 64),
        )
        for homogeneous, count, center, length, factor, angle in cases:
            with self.subTest(homogeneous=homogeneous):
                frames = square_frames(homogeneous)
                self.assertEqual(len(frames), count + 1)
                x, y = (cartesian(frames[0]) - center).T
                for k, frame in enumerate(frames):
                    xy = cartesian(frame)
                    c, s = cos(k * angle), sin(k * angle)
                    expected = np.column_stack((x * c - y * s, x * s + y * c))
                    expected = expected * factor**k + center
                    assert_allclose(xy, expected, atol=1e-10)
                    assert_allclose(xy.mean(axis=0), center, atol=1e-10)
                    edges = np.roll(xy, -1, axis=0) - xy
                    assert_allclose(np.linalg.norm(edges, axis=1), length * factor**k)
                    if homogeneous:
                        assert_array_equal(frame[:, 2], np.ones(4))

    def test_homogeneous_and_pixel_coordinates(self):
        assert_allclose(cartesian(np.array([[6.0, -9.0, 3.0]])), [[2, -3]])
        with self.assertRaises(ValueError):
            cartesian(np.array([[1.0, 2.0, 0.0]]))
        frame = ReferenceFrame(Origin(120, 300), Unit(40), Unit(50))
        self.assertEqual(get_x(frame, 2.5), 220)
        self.assertEqual(get_y(frame, 2.5), 175)
        self.assertEqual(get_length(frame.uy, 3), 150)
