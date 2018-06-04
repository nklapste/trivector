#!/usr/bin/python
# -*- coding: utf-8 -*-

"""Convert an image into a ``.svg`` vector image composed of triangles"""

import os
from enum import Enum

import numpy
from numpy import ndarray
import svgwrite
from svgwrite import Drawing

import cv2
import progressbar


def upper_tri_sum(d3array: ndarray) -> ndarray:
    """Get a 3D image array's upper diagonal's pixel color average

    :param d3array: a 3D image array derived from :func:`cv2.imread`

    Treat the 3D array as 2d array. Having the innermost array (pixel BGR
    values) be considered base values to be averaged.

    :return: a BGR array of the average color of the upper diagonal of the
        3D image array
    """
    x, y, z = d3array.shape
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
    x, y, z = d3array.shape
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


def vectorize_sector_left(sub_img: ndarray, dwg: Drawing,
                     x: int, y: int, cut_size: int):
    """Add two triangles to ``dwg`` whose colors are derived from the color
    averages from the top and bottom diagonals of the 3D BGR image array of
    the sub image"""
    b, g, r = upper_tri_sum(sub_img)
    dwg.add(
        dwg.polygon(
            [(x, y), (x + cut_size, y), (x + cut_size, y + cut_size)],
            stroke=svgwrite.rgb(r, g, b, "RGB"),
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )
    b, g, r = lower_tri_sum(sub_img)
    dwg.add(
        dwg.polygon(
            [(x, y), (x, y + cut_size), (x + cut_size, y + cut_size)],
            stroke=svgwrite.rgb(r, g, b, "RGB"),
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


def vectorize_sector_right(sub_img: ndarray, dwg: Drawing,
                           x: int, y: int, cut_size: int):
    """Add two triangles to ``dwg`` whose colors are derived from the color
    averages from the top and bottom diagonals of the 3D BGR image array of
    the sub image"""
    b, g, r = upper_tri_sum(sub_img)
    dwg.add(
        dwg.polygon(
            [(x, y + cut_size), (x + cut_size, y + cut_size), (x + cut_size, y)],
            stroke=svgwrite.rgb(r, g, b, "RGB"),
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )

    b, g, r = lower_tri_sum(sub_img)
    dwg.add(
        dwg.polygon(
            [(x, y + cut_size), (x, y), (x + cut_size, y)],
            stroke=svgwrite.rgb(r, g, b, "RGB"),
            fill=svgwrite.rgb(r, g, b, "RGB")
        )
    )


class DiagonalStyle(Enum):
    """Styling noting on how to arrange the triangle sectors diagonals"""
    right = "right"
    left = "left"
    alternating = "alternating"

    def __str__(self):
        return self.value


def trivector(image_path: str, cut_size: int, output_path: str = None,
              diagonal_style: DiagonalStyle = DiagonalStyle.alternating):
    """Convert an image into a vector image composed of triangles

    Save the vector image as a ``.svg``.

    :param image_path: path to the image to convert to a vector image
    :param cut_size: size in pixels for each triangle sector
        (smaller==more triangles)
    :param diagonal_style: a :class:`DiagonalStyle` styling noting on how to
        arrange the triangle sectors diagonals
    :param output_path: path to write the output images to (note: extension
        not required)
    """
    img = cv2.imread(image_path)
    image_name = os.path.basename(image_path)
    image_name, _ = os.path.splitext(image_name)

    if not output_path:
        output_path = os.path.join(os.getcwd(), "{}_tri_{}".format(image_name, cut_size))
    dwg = svgwrite.Drawing(output_path+".svg", profile="full")

    height, width, channels = img.shape

    width_slices = range(0, width, cut_size)
    height_slices = range(0, height, cut_size)
    dwg.viewbox(width=len(width_slices)*cut_size, height=len(height_slices)*cut_size)

    # start up the progress bar
    # each image sector is one tick one the progress bar
    bar = progressbar.ProgressBar(max_value=len(width_slices)*len(height_slices))
    counter2 = 0
    sector_num = 0
    for y in height_slices:

        counter = counter2
        for x in width_slices:

            sub_img = img[y:y + cut_size, x:x + cut_size]
            if (diagonal_style == DiagonalStyle.left) or \
                    (diagonal_style == DiagonalStyle.alternating and counter % 2):
                vectorize_sector_left(sub_img, dwg, x, y, cut_size)
            elif (diagonal_style == DiagonalStyle.right) or \
                    (diagonal_style == DiagonalStyle.alternating and not counter % 2):
                sub_img = numpy.rot90(sub_img, axes=(0, 1))
                vectorize_sector_right(sub_img, dwg, x, y, cut_size)
            else:
                raise TypeError("diagonal_style is invalid")
            sector_num += 1
            bar.update(sector_num)
            counter += 1
        counter2 += 1

    dwg.save()
