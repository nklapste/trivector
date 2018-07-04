#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Convert an image into vector image by converting sub sections of the image
into simple shapes"""

import io
from logging import getLogger
from enum import Enum
from typing import Generator, Tuple

import cv2
import numpy
import progressbar
from numpy import ndarray
import svgwrite
from svgwrite.shapes import Rect, Circle


__log__ = getLogger(__name__)


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


class Sector:
    def __init__(self, image: ndarray, x_pos: int, y_pos: int):
        self.image = image
        self.x_pos = x_pos
        self.y_pos = y_pos

    @property
    def position(self):
        return self.x_pos, self.y_pos


class Vectorizer:
    def __init__(self, image_path: str, cut_size: int,
                 output_path: str = "unnamed.svg",
                 style: Style = Style.tri_alternating,
                 stroke_color: Tuple[int, int, int] = None,
                 stroke_width: int = 0):
        """Initialize the Vectorizer

        Read the image given at ``image_path`` and setup image data needed
        to run the Vectorizer.

        .. note::
            Avoid making ``cut_size`` be small (eg: 2) for very large images.
            As run times can quickly increase.

        :param image_path: path to the image to read
        :param cut_size: size in pixels for each sector
        :param output_path: path to output the vector image. Can be overridden
            by the usage  of the ``output_path`` parameter in
            :meth:`Vectorizer.save`.
        :param style: styling option for composing vectorized sectors
        :param stroke_width:
        :param stroke_color:
        """
        self.image = cv2.imread(image_path)  # pylint: disable=no-member
        self.output_path = output_path
        self.cut_size = cut_size
        self.style = style

        self.stroke_width = stroke_width
        if stroke_color:
            self.stroke_color = svgwrite.rgb(*stroke_color)
        else:
            self.stroke_color = None

        height, width, _ = self.image.shape
        self.width_slices = list(range(0, width, self.cut_size))
        self.height_slices = list(range(0, height, self.cut_size))
        self.drawing = svgwrite.Drawing(self.output_path, profile="full")
        self.drawing.viewbox(
            width=len(self.width_slices) * self.cut_size,
            height=len(self.height_slices) * self.cut_size
        )

    def sectors(self) -> Generator[Sector, None, None]:
        """Return a generator of all the images sectors going from
        the images top to bottom, left to right order"""
        for y in self.height_slices:
            for x in self.width_slices:
                yield Sector(
                    image=self.image[y:y + self.cut_size, x:x + self.cut_size],
                    x_pos=x,
                    y_pos=y
                )

    def vectorize(self):
        """Run the Vectorizer"""
        bar = progressbar.ProgressBar(
            max_value=len(self.width_slices) * len(self.height_slices))
        counter_2 = 0
        sector_num = 0
        for y in self.height_slices:
            counter_1 = counter_2
            counter_2 += 1
            for x in self.width_slices:
                sector = Sector(
                    image=self.image[y:y + self.cut_size, x:x + self.cut_size],
                    x_pos=x,
                    y_pos=y
                )
                if self.style == Style.square:
                    self.square_vectorize_sector(sector)
                elif self.style == Style.circle:
                    self.circle_vectorize_sector(sector)
                elif (self.style == Style.tri_right) or \
                        (self.style == Style.tri_alternating and counter_1 % 2):
                    self.tri_right_vectorize_sector(sector)
                elif (self.style == Style.tri_left) or \
                        (self.style == Style.tri_alternating and counter_1 % 2 == 0):
                    self.tri_left_vectorize_sector(sector)
                sector_num += 1
                counter_1 += 1
                bar.update(sector_num)

    def tri_left_vectorize_sector(self, sector: Sector):
        x, y = sector.position
        b, g, r = upper_tri_sum(sector.image)
        self.drawing.add(
            self.drawing.polygon(
                [
                    (x, y),
                    (x + self.cut_size, y),
                    (x + self.cut_size, y + self.cut_size)
                ],
                stroke=self.stroke_color or svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

        b, g, r = lower_tri_sum(sector.image)
        self.drawing.add(
            self.drawing.polygon(
                [
                    (x, y),
                    (x, y + self.cut_size),
                    (x + self.cut_size, y + self.cut_size)
                ],
                stroke=self.stroke_color or svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def tri_right_vectorize_sector(self, sector: Sector):
        x, y = sector.position
        b, g, r = upper_tri_sum(numpy.rot90(sector.image, axes=(0, 1)))
        self.drawing.add(
            self.drawing.polygon(
                [
                    (x, y + self.cut_size),
                    (x + self.cut_size, y + self.cut_size),
                    (x + self.cut_size, y)
                ],
                stroke=self.stroke_color or svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

        b, g, r = lower_tri_sum(sector.image)
        self.drawing.add(
            self.drawing.polygon(
                [
                    (x, y + self.cut_size),
                    (x, y),
                    (x + self.cut_size, y)
                ],
                stroke=self.stroke_color or svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def circle_vectorize_sector(self, sector: Sector):
        b, g, r = numpy.average(sector.image, (0, 1))
        x, y = sector.position
        self.drawing.add(
            Circle(
                center=(x + (self.cut_size / 2), y + (self.cut_size / 2)),
                r=self.cut_size / 1.3,
                stroke=self.stroke_color or svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def square_vectorize_sector(self, sector: Sector):
        b, g, r = numpy.average(sector.image, (0, 1))
        x, y = sector.position
        self.drawing.add(
            Rect(
                insert=(x, y),
                size=(self.cut_size, self.cut_size),
                stroke=self.stroke_color or svgwrite.rgb(r, g, b, "RGB"),
                stroke_width=self.stroke_width,
                fill=svgwrite.rgb(r, g, b, "RGB")
            )
        )

    def save(self, output_path: str = None, **kwargs):
        """Save the vectorized image

        :param output_path: save the image at the path specified.

        .. note::
            If no ``output_path`` is given :obj:Vectorizer.output_path`
            will be used by default.
        """
        if output_path is None:
            output_path = self.output_path
        fileobj = io.open(output_path, mode='w', encoding='utf-8')
        self.drawing.write(fileobj, **kwargs)
        fileobj.close()

