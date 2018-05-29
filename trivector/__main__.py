#!/usr/bin/python
# -*- coding: utf-8 -*-

"""argparse script for trivector"""

import os
import argparse
import sys

from trivector import trivector


def main():
    """argparse function for trivector"""
    parser = argparse.ArgumentParser()
    parser.add_argument("image", required=True, help="Path to the image to trivector")
    parser.add_argument("-o", "--output", default=os.path.join(os.getcwd(), "<image_name>_tri_<cut_size>.<svg & png>"),
                        help="Path to output the trivectored image (default: %(default)s)")

    group = parser.add_argument_group("Image Generation Options")
    group.add_argument("-c", "--cut-size", dest="cut_size", type=int, required=True,
                       help="Size in pixels for each triangle sector (smaller==more triangles)")

    group = parser.add_argument_group("Image Diagonal Options")
    group = group.add_mutually_exclusive_group()
    group.add_argument("--right-diagonal", dest="right_diagonal", action="store_true",
                       help="Triangle sectors will be only orientated to the right `/`")
    group.add_argument("--left-diagonal", dest="left_diagonal", action="store_true",
                       help="Triangle sectors will be only orientated to the left `\\`")

    args = parser.parse_args()

    trivector(
        image_path=args.image,
        cut_size=args.cut_size,
        right_diagonal=args.right_diagonal,
        left_diagonal=args.left_diagonal,
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
