#!/usr/bin/python
# -*- coding: utf-8 -*-

""""""

import os
import numpy
from numpy import ndarray
import svgwrite
import cv2
import progressbar
from cairosvg import svg2png


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


def trivector(image_path: str, cut_size: int, right_diagonal: bool = False, left_diagonal: bool = False, output_path: str = None):
    """"""
    img = cv2.imread(image_path)
    image_name = os.path.basename(image_path)
    image_name, ext = os.path.splitext(image_name)

    if not output_path:
        output_path = os.path.join(os.getcwd(), "{}_tri_{}.svg".format(image_name, cut_size))
    dwg = svgwrite.Drawing(output_path, profile="full")

    height, width, channels = img.shape

    width_slices = range(0, width, cut_size)
    height_slices = range(0, height, cut_size)
    dwg.viewbox(width=len(width_slices)*cut_size, height=len(height_slices)*cut_size)
    bar = progressbar.ProgressBar(max_value=len(width_slices)*len(height_slices))
    counter2 = 0
    sector_num = 0


    for y in height_slices:
        counter = counter2
        for x in width_slices:

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
                        [(x, y), (x, y + cut_size), (x + cut_size, y)],
                        stroke=svgwrite.rgb(r, g, b, 'RGB'),
                        fill=svgwrite.rgb(r, g, b, 'RGB')
                    )
                )
            sector_num += 1
            bar.update(sector_num)
            counter += 1
        counter2 += 1
    dwg.save()
    filename, file_extension = os.path.splitext(output_path)
    svg2png(open(output_path, 'rb').read(), write_to=open(filename+os.extsep+"png", 'wb'))


if __name__ == "__main__":
    trivector("../images/me2.png", 45)
