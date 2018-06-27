#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""
from enum import Enum

import cv2
import numpy
import progressbar
from numpy import ndarray
import svgwrite
from svgwrite.shapes import Rect, Circle


def upper_tri_sum(d3array: ndarray) -> ndarray:
    """Get a 3D image array's upper diagonal's pixel color average

    :param d3array: a 3D image array derived from :func:`cv2.imread`

    Treat the 3D array as 2d array. Having the innermost array (pixel BGR
    values) be considered base values to be averaged.

    :return: a BGR array of the average color of the upper diagonal of the
        3D image array
    """
    x, y, _ = d3array.shape
    tri = []
    for i in range(x):
        if i > y:
            break
        for j in range(y - i):
            tri.append(d3array[i][i + j])
    return numpy.sum(tri, axis=0) // len(tri)


def lower_tri_sum(d3array: ndarray) -> ndarray:
    """Get a 3D image array's lower diagonal's pixel color average

    :param d3array: a 3D image array derived from :func:`cv2.imread`

    Treat the 3D array as 2d array. Having the innermost array (pixel BGR
    values) be considered base values to be averaged.

    .. note::

        If the lower diagonal cannot be computed (eg: flat/malformed 3D array)
        use the 3D image array's upper diagonal's pixel color average instead.

    :return: a BGR array of the average color of the lower diagonal of the
        3D image array
    """
    x, y, _ = d3array.shape
    tri = []
    for i in range(x):
        if i > y:
            break
        for j in range(i):
            tri.append(d3array[i][j])

    # if bottom tri is use the upper tri's sum
    if not tri:
        return upper_tri_sum(d3array)
    return numpy.sum(tri, axis=0) // len(tri)


class Style(Enum):
    """Styling options for composing vectorized sectors"""
    tri_right = "tri_right"
    tri_left = "tri_left"
    tri_alternating = "tri_alternating"
    square = "square"
    circle = "circle"

    def __str__(self):
        return self.value


class Vectorizer:
    def __init__(self, image: str, cut_size: int, output_path: str = "unnamed.svg",
                 stroke_width: int = 0, style: Style = Style.tri_alternating):
        """"""
        self.image = cv2.imread(image)  # pylint: disable=no-member
        self.drawing = svgwrite.Drawing(output_path, profile="full")
        self.style = style
        self.stroke_width = stroke_width
        self.cut_size = cut_size

        height, width, _ = self.image.shape

        self.width_slices = list(range(0, width, self.cut_size))
        self.height_slices = list(range(0, height, self.cut_size))
        self.drawing.viewbox(
            width=len(self.width_slices) * self.cut_size,
            height=len(self.height_slices) * self.cut_size
        )

    def vectorize(self):
        """Run the Vectorizer"""
        # start up the progress bar
        # each image sector is one tick one the progress bar
        bar = progressbar.ProgressBar(
            prefix="Vectorizing |",
            max_value=len(self.width_slices) * len(self.height_slices)
        )
        counter_2 = 0
        sector_num = 0

        for y in self.height_slices:
            counter_1 = counter_2
            counter_2 += 1
            for x in self.width_slices:
                sub_img = self.image[y:y + self.cut_size, x:x + self.cut_size]
                if self.style == Style.square:
                    self.square_vectorize_sector(sub_img, x, y)
                if self.style == Style.circle:
                    self.circle_vectorize_sector(sub_img, x, y)
                if (self.style == Style.tri_left) or \
                        (self.style == Style.tri_alternating and counter_1 % 2):
                    self.tri_left_vectorize_sector(sub_img, x, y)
                else:
                    sub_img = numpy.rot90(sub_img, axes=(0, 1))
                    self.tri_right_vectorize_sector(sub_img, x, y)

                sector_num += 1
                counter_1 += 1
                bar.update(sector_num)

        self.drawing.save()

    def tri_left_vectorize_sector(self, sub_img: ndarray,
                                  x: int, y: int):
        """Add two triangles to ``dwg`` whose colors are derived from the color
        averages from the top and bottom diagonals of the 3D BGR image array of
        the sub image"""
        b, g, r = upper_tri_sum(sub_img)
        self.drawing.add(
            self.drawing.polygon(
                [(x, y), (x + self.cut_size, y), (x + self.cut_size, y + self.cut_size)],
                stroke=svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )
        b, g, r = lower_tri_sum(sub_img)
        self.drawing.add(
            self.drawing.polygon(
                [(x, y), (x, y + self.cut_size), (x + self.cut_size, y + self.cut_size)],
                stroke=svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def tri_right_vectorize_sector(self, sub_img: ndarray,
                                   x: int, y: int):
        """Add two triangles to ``dwg`` whose colors are derived from the color
        averages from the top and bottom diagonals of the 3D BGR image array of
        the sub image"""

        b, g, r = upper_tri_sum(sub_img)
        self.drawing.add(
            self.drawing.polygon(
                [(x, y + self.cut_size), (x + self.cut_size, y + self.cut_size),
                 (x + self.cut_size, y)],
                stroke=svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,

                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )
        b, g, r = lower_tri_sum(sub_img)
        self.drawing.add(
            self.drawing.polygon(
                [(x, y + self.cut_size), (x, y), (x + self.cut_size, y)],
                stroke=svgwrite.rgb(r, g, b, "RGB"),

                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def circle_vectorize_sector(self, sub_image: ndarray,
                                x: int, y: int):
        b, g, r = numpy.average(sub_image, (0, 1))
        self.drawing.add(
            Circle(
                center=(x + (self.cut_size / 2), y + (self.cut_size / 2)),
                r=self.cut_size / 1.3,
                stroke=svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def square_vectorize_sector(self, sub_image: ndarray, x: int, y: int):
        b, g, r = numpy.average(sub_image, (0, 1))
        self.drawing.add(
            Rect(
                insert=(x, y),
                size=(self.cut_size, self.cut_size),
                stroke=svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )


v = Vectorizer("shooter.jpg", 15)
v.vectorize()