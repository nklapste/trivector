#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""Image conversion functionality for trivector"""

from enum import Enum

import numpy as np
import svgwrite

import cv2
import progressbar


def upper_tri_sum(d3array: np.ndarray) -> np.ndarray:
    """Get a 3D image array's upper diagonal's pixel color average

    :param d3array: 3D image array derived from :func:`cv2.imread`

    Treat the 3D array as 2d array. Having the innermost array (pixel BGR
    values) be considered base values to be averaged.

    :return: BGR array of the average color of the upper diagonal of the
        3D image array
    """
    x, y, _ = d3array.shape
    tri = []
    for i in range(x):
        if i > y:
            break
        for j in range(y - i):
            tri.append(d3array[i][i + j])
    return np.sum(tri, axis=0) // len(tri)


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
    tri = []
    for i in range(x):
        if i > y:
            break
        for j in range(i):
            tri.append(d3array[i][j])

    # if bottom tri is empty use the upper tri's sum
    if not tri:
        return upper_tri_sum(d3array)
    return np.sum(tri, axis=0) // len(tri)


def vectorize_sector_left(sub_img: np.ndarray, svg_drawing: svgwrite.Drawing,
                          x: int, y: int, cut_size: int):
    """Add two triangles to ``svg_drawing`` whose colors are derived from
    the color averages from the top and bottom diagonals of the 3D BGR image
    array of the sub image"""
    b, g, r = upper_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y), (x + cut_size, y), (x + cut_size, y + cut_size)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )
    b, g, r = lower_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y), (x, y + cut_size), (x + cut_size, y + cut_size)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


def vectorize_sector_right(sub_img: np.ndarray, svg_drawing: svgwrite.Drawing,
                           x: int, y: int, cut_size: int):
    """Add two triangles to ``svg_drawing`` whose colors are derived from
    the color averages from the top and bottom diagonals of the 3D BGR image
    array of the sub image"""
    b, g, r = upper_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y + cut_size), (x + cut_size, y + cut_size), (x + cut_size, y)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )
    b, g, r = lower_tri_sum(sub_img)
    svg_drawing.add(
        svg_drawing.polygon(
            [(x, y + cut_size), (x, y), (x + cut_size, y)],
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


class DiagonalStyle(Enum):
    """Styling options noting the diagonal arrangement of the
    triangle sectors"""
    right = "right"
    left = "left"
    alternating = "alternating"

    def __str__(self):
        return self.value


def trivector(image_path: str, cut_size: int, output_path: str,
              diagonal_style: DiagonalStyle = DiagonalStyle.alternating):
    """Convert an image into a SVG vector image composed of triangular sectors

    :param image_path: path to the image to trivector
    :param cut_size: size in pixels for each triangle sector
    :param diagonal_style: diagonal arrangement of the triangle sectors
    :param output_path: path to write the trivectored image
    """
    image = cv2.imread(image_path)  # pylint:disable=no-member

    height, width, _ = image.shape

    width_slices = range(0, width, cut_size)
    height_slices = range(0, height, cut_size)
    svg_drawing = svgwrite.Drawing(
        output_path,
        profile="full",
        size=(len(width_slices)*cut_size, len(height_slices)*cut_size)
    )

    # start up the progress bar
    # each image sector is one tick one the progress bar
    bar = progressbar.ProgressBar(max_value=len(width_slices)*len(height_slices))
    counter_2 = 0
    sector_num = 0
    for y in height_slices:
        counter_1 = counter_2
        counter_2 += 1
        for x in width_slices:
            sub_img = image[y:y + cut_size, x:x + cut_size]
            if (diagonal_style == DiagonalStyle.left) or \
                    (diagonal_style == DiagonalStyle.alternating and counter_1 % 2):
                vectorize_sector_left(sub_img, svg_drawing, x, y, cut_size)
            else:
                sub_img = np.rot90(sub_img, axes=(0, 1))
                vectorize_sector_right(sub_img, svg_drawing, x, y, cut_size)
            sector_num += 1
            counter_1 += 1
            bar.update(sector_num)

    svg_drawing.save()
