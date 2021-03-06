#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""argparse and entry point script for trivector"""

import argparse
import sys

from trivector.trivector import trivector, DiagonalStyle


def get_parser():
    """Create and return the argparser for trivector"""
    parser = argparse.ArgumentParser(
        description="Convert an image into a SVG vector image composed "
                    "of triangular sectors",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )
    parser.add_argument("image", help="path to the image to trivector")
    parser.add_argument("output", help="path to output the trivectored image")

    group = parser.add_argument_group("Image Generation Options")
    group.add_argument("sector_size", type=int,
                       help="size in pixels for each triangle sector")
    group.add_argument("-d", "--diagonal-style", dest="diagonal_style",
                       type=DiagonalStyle, choices=list(DiagonalStyle),
                       default=DiagonalStyle.alternating.value,
                       help="diagonal arrangement of the triangle sectors")
    return parser


def main(argv=sys.argv[1:]):
    """main entry point for trivector"""
    parser = get_parser()
    args = parser.parse_args(argv)

    trivector(
        image_path=args.image,
        cut_size=args.sector_size,
        output_path=args.output,
        diagonal_style=args.diagonal_style
    )

    return 0


if __name__ == "__main__":
    sys.exit(main())
