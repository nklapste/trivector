#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""

import os
import numpy
from numpy import ndarray
import svgwrite
import cv2


def upper_tri_sum(d3array: ndarray) -> numpy.array:
    """"""
    x, y, z = d3array.shape

    tri = []
    for i in range(x):
        if i > y:
            break
        for j in range(y - i):
            tri.append(d3array[i][i + j])
    return numpy.sum(tri, axis=0) // len(tri)


def lower_tri_sum(d3array: ndarray) -> numpy.array:
    """"""
    x, y, z = d3array.shape
    tri = []
    for i in range(x):
        if i > y:
            break
        for j in range(i):
            tri.append(d3array[i][j])

    # if bottom tri is empty fill it with the top tri's data
    if not tri:
        return upper_tri_sum(d3array)
    return numpy.sum(tri, axis=0) // len(tri)


def trivector(image_path: str, cut_size: int, right_diagonal: bool, left_diagonal: bool):
    """"""
    img = cv2.imread(image_path)
    image_name = os.path.basename(image_path)
    image_name, ext = os.path.splitext(image_name)

    dwg = svgwrite.Drawing("{}_tri_{}.svg".format(image_name, cut_size), profile="tiny")

    height, width, channels = img.shape
    diff = width // cut_size
    adjusted_width = (diff+1)*cut_size
    diff = height // cut_size
    adjusted_height = (diff+1)*cut_size
    dwg.viewbox(width=adjusted_width, height=adjusted_height)

    counter2 = 0
    for y in range(0, height, cut_size):
        counter = counter2
        for x in range(0, width, cut_size):
            sub_img = img[y:y + cut_size, x:x + cut_size]
            if left_diagonal or (not right_diagonal and counter % 2):
                tri_color = upper_tri_sum(sub_img)
                b, g, r = tri_color
                dwg.add(
                    dwg.polygon(
                        [(x, y), (x + cut_size, y), (x + cut_size, y + cut_size)],
                        stroke=svgwrite.rgb(r, g, b, 'RGB'),
                        fill=svgwrite.rgb(r, g, b, 'RGB')
                    )
                )

                tri_color = lower_tri_sum(sub_img)
                b, g, r = tri_color
                dwg.add(
                    dwg.polygon(
                        [(x, y), (x, y + cut_size), (x + cut_size, y + cut_size)],
                        stroke=svgwrite.rgb(r, g, b, 'RGB'),
                        fill=svgwrite.rgb(r, g, b, 'RGB')
                    )
                )
            else:
                # inverting orientation of tris
                sub_img = numpy.rot90(sub_img, axes=(0, 1))
                tri_color = upper_tri_sum(sub_img)
                b, g, r = tri_color
                dwg.add(
                    dwg.polygon(
                        [(x, y+cut_size), (x + cut_size, y), (x + cut_size, y + cut_size)],
                        stroke=svgwrite.rgb(r, g, b, 'RGB'),
                        fill=svgwrite.rgb(r, g, b, 'RGB')
                    )
                )

                tri_color = lower_tri_sum(sub_img)
                b, g, r = tri_color
                dwg.add(
                    dwg.polygon(
                        [(x, y), (x, y + cut_size), (x+ cut_size, y)],
                        stroke=svgwrite.rgb(r, g, b, 'RGB'),
                        fill=svgwrite.rgb(r, g, b, 'RGB')
                    )
                )
            counter += 1
        counter2 += 1
    dwg.save()
