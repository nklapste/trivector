#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse script for trivector"""

import argparse
import sys

from trivector.vectorizer import Vectorizer, Style


def rgb(s):
    try:
        r, g, b = map(int, tuple(s))
        return r, g, b
    except:
        raise argparse.ArgumentTypeError("RGB values must be r,g,b")


def get_parser() -> argparse.ArgumentParser:
    """Create and return the argparser for trivector"""
    parser = argparse.ArgumentParser(
        description="Convert an image into a ``.svg`` vector image composed "
                    "of triangles"
    )
    parser.add_argument("image", help="Path to the image to trivector")

    group = parser.add_argument_group("Image Generation Options")
    group.add_argument("-o", "--output-path", dest="output_path",
                       default="unnamed.svg",
                       help="Path to output the vectorized image "
                            "(default: %(default)s)")
    group.add_argument("-c", "--cut-size", dest="cut_size", type=int,
                       required=True,
                       help="Size in pixels for each vectorized sector "
                            "(smaller==more sectors)")
    group.add_argument("-s", "--style", dest="style",
                       type=Style, choices=list(Style),
                       default=Style.tri_alternating.value,
                       help="Styling to use to compose the vectorized "
                            "sectors (default: %(default)s)")
    group.add_argument("--stroke-color", dest="stroke_color",
                       default=None, type=rgb,
                       help="Tuple representing the R,G,B color for "
                            "the border stroke for each vectorized sector "
                            "(default: %(default)s)")
    group.add_argument("-stroke-width", dest="stroke_width",
                       type=float, default=0.0,
                       help="Width of the border stroke for each vectorized "
                            "sector (default: %(default)s)")
    return parser


def main(argv=sys.argv[1:]):
    """argparse function for trivector"""
    parser = get_parser()
    args = parser.parse_args(argv)

    # create run and save with the Vectorizer
    vectorizer = Vectorizer(
        image_path=args.image,
        cut_size=args.cut_size,
        output_path=args.output_path,
        style=args.style,
        stroke_width=args.stroke_width
    )
    vectorizer.run()
    vectorizer.save()

    return 0


if __name__ == "__main__":
    sys.exit(main())
