#!/usr/bin/python
# -*- coding: utf-8 -*-

"""argparse script for trivector"""

import os
import argparse
import sys

from trivector.trivector import trivector, DiagonalStyle


def main():
    """argparse function for trivector"""
    parser = argparse.ArgumentParser()
    parser.add_argument("image", help="Path to the image to trivector")
    parser.add_argument("-o", "--output", default=os.path.join(os.getcwd(), "<image_name>_tri_<cut_size>.<svg & png>"),
                        help="Path to output the trivectored image "
                             "(default: %(default)s)")

    group = parser.add_argument_group("Image Generation Options")
    group.add_argument("-c", "--cut-size", dest="cut_size", type=int, required=True,
                       help="Size in pixels for each triangle sector "
                            "(smaller==more triangles)")
    group.add_argument("-d", "--diagonal-style", dest="diagonal_style",
                       type=DiagonalStyle, choices=list(DiagonalStyle),
                       default=DiagonalStyle.alternating.value,
                       help="Styling on how to arrange the triangle "
                            "sectors diagonals (default: %(default)s)")

    args = parser.parse_args()

    trivector(
        image_path=args.image,
        cut_size=args.cut_size,
        diagonal_style=args.diagonal_style
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
