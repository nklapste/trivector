#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Image conversion functionality for trivector"""

from enum import Enum
from typing import List, Generator, Tuple

import numpy as np
import svgwrite

import cv2
from svgwrite.shapes import Rect, Circle


def bgr_value_average(bgr_values: List[np.ndarray]) -> np.ndarray:
    """Compute the average BGR value from an list of BGR arrays

    :param bgr_values: list of BGR arrays

    :return: a single BGR array noting the average BGR values contained within
        ``bgr_array``
    """
    return np.sum(bgr_values, axis=0) // len(bgr_values)


def upper_tri_sum(d3array: np.ndarray) -> np.ndarray:
    """Get a 3D image array's upper diagonal's pixel color average

    :param d3array: 3D image array derived from :func:`cv2.imread`

    Treat the 3D array as 2d array. Having the innermost array (pixel BGR
    values) be considered base values to be averaged.

    :return: BGR array of the average color of the upper diagonal of the
        3D image array
    """
    x, y, _ = d3array.shape
    tri_elem = []
    for i in range(x):
        if i > y:
            break
        for j in range(y - i):
            tri_elem.append(d3array[i][i + j])
    return bgr_value_average(tri_elem)


def lower_tri_sum(d3array: np.ndarray) -> np.ndarray:
    """Get a 3D image array's lower diagonal's pixel color average

    :param d3array: 3D image array derived from :func:`cv2.imread`

    Treat the 3D array as 2d array. Having the innermost array (pixel BGR
    values) be considered base values to be averaged.

    .. note::

        If the lower diagonal cannot be computed (eg: flat/malformed 3D array)
        use the 3D image array's upper diagonal's pixel color average instead.

    :return: BGR array of the average color of the lower diagonal of the
        3D image array
    """
    x, y, _ = d3array.shape
    tri_elem = []
    for i in range(x):
        if i > y:
            break
        for j in range(i):
            tri_elem.append(d3array[i][j])

    # if bottom tri is empty use the upper tri's sum
    if not tri_elem:
        return upper_tri_sum(d3array)
    return bgr_value_average(tri_elem)


def vectorize_sector_left(sub_img: np.ndarray,
                          svg_drawing: svgwrite.Drawing,
                          x: int, y: int, sector_size: int):
    """Add two triangles to ``svg_drawing`` whose colors are derived from
    the color averages from the top and bottom diagonals of the 3D BGR image
    array of the sub image"""
    b, g, r = upper_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y), (x + sector_size, y), (x + sector_size, y + sector_size)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )
    b, g, r = lower_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y), (x, y + sector_size), (x + sector_size, y + sector_size)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


def vectorize_sector_right(sub_img: np.ndarray,
                           svg_drawing: svgwrite.Drawing,
                           x: int, y: int, sector_size: int):
    """Add two triangles to ``svg_drawing`` whose colors are derived from
    the color averages from the top and bottom diagonals of the 3D BGR image
    array of the sub image"""
    sub_img = np.rot90(sub_img, axes=(0, 1))
    b, g, r = upper_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y + sector_size), (x + sector_size, y + sector_size), (x + sector_size, y)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )
    b, g, r = lower_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y + sector_size), (x, y), (x + sector_size, y)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


class DiagonalStyle(Enum):
    """Styling options noting the diagonal arrangement of the
    triangle sectors"""
    right = "right"
    left = "left"
    left_alternating = "left_alternating"
    right_alternating = "right_alternating"

    def __str__(self):
        return self.value


class Vectorizer:
    def __init__(self, image_path: str, sector_size: int, **kwargs):
        self.image = cv2.imread(image_path)  # pylint: disable=no-member
        self.sector_size = sector_size

        height, width, _ = self.image.shape
        self.width_slices = list(range(0, width, self.sector_size))
        self.height_slices = list(range(0, height, self.sector_size))
        self.svg_drawing = svgwrite.Drawing(
            profile="full",
            size=(len(self.width_slices)*self.sector_size,
                  len(self.height_slices)*self.sector_size)
        )

    def vectorize(self) -> svgwrite.Drawing:
        pass

    def get_sector(self, x: int, y: int) -> np.ndarray:
        return self.image[y:y + self.sector_size, x:x + self.sector_size]

    @property
    def sectors(self) -> Generator[Tuple[int, int, np.ndarray], None, None]:
        for y in self.height_slices:
            for x in self.width_slices:
                yield x, y, self.get_sector(x, y)


class TriVectorizer(Vectorizer):
    def __init__(self, diagonal_style: DiagonalStyle = DiagonalStyle.left_alternating, **kwargs):
        self.diagonal_style = diagonal_style
        super().__init__(**kwargs)

    def vectorize(self) -> svgwrite.Drawing:
        for x, y, sector_image in self.sectors:
            x_idx = x // self.sector_size
            y_idx = y // self.sector_size
               # (self.diagonal_style == DiagonalStyle.left_alternating and (x/self.sector_size == 1 and not (y_idx) % 2) or (x/self.sector_size) % 2) or \ # wave
            if self.diagonal_style == DiagonalStyle.right:
                vectorize_sector_right(sector_image, self.svg_drawing, x, y,
                                       self.sector_size)
            elif (self.diagonal_style == DiagonalStyle.left) or \
                 (self.diagonal_style == DiagonalStyle.right_alternating and
                    ((x_idx % 2 and not y_idx % 2) or
                     (not x_idx % 2 and y_idx % 2))) or \
                 (self.diagonal_style == DiagonalStyle.left_alternating and
                    not ((x_idx % 2 and not y_idx % 2) or
                         (not x_idx % 2 and y_idx % 2))):
                vectorize_sector_left(sector_image, self.svg_drawing, x, y,
                                      self.sector_size)
            else:
                vectorize_sector_right(sector_image, self.svg_drawing, x, y,
                                       self.sector_size)
        return self.svg_drawing


def square_vectorize_sector(sector_image: np.ndarray,
                            svg_drawing: svgwrite.Drawing,
                            x: int, y: int, sector_size: int):
    b, g, r = np.average(sector_image, (0, 1))
    svg_drawing.add(
        Rect(
            insert=(x, y),
            size=(sector_size, sector_size),
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


class SquareVectorizer(Vectorizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def vectorize(self) -> svgwrite.Drawing:
        for x, y, sector_image in self.sectors:
            square_vectorize_sector(
                sector_image, self.svg_drawing, x, y, self.sector_size)
        return self.svg_drawing


def circle_vectorize_sector(sector_image: np.ndarray,
                            svg_drawing: svgwrite.Drawing,
                            x: int, y: int, sector_size: int):
    b, g, r = np.average(sector_image, (0, 1))
    svg_drawing.add(
        Circle(
            center=(x + (sector_size / 2), y + (sector_size / 2)),
            r=sector_size / 1.3,
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


class CircleVectorizer(Vectorizer):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def vectorize(self) -> svgwrite.Drawing:
        for x, y, sector_image in self.sectors:
            circle_vectorize_sector(
                sector_image, self.svg_drawing, x, y, self.sector_size)
        return self.svg_drawing
