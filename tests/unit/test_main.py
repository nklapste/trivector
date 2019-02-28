#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""pytests for __main__.py"""

import argparse
import os

import pytest
from svglib.svglib import svg2rlg
import numpy as np
import cv2

from trivector.__main__ import get_parser, main


def test_get_parser():
    parser = get_parser()
    assert isinstance(parser, argparse.ArgumentParser)


def gen_test_image(image_path: str):
    """Create a random image at the path specified"""
    cv2.imwrite(image_path, np.random.randint(255, size=(400, 400)))


@pytest.fixture(scope="session")
def image_file(tmpdir_factory):
    image_path = str(tmpdir_factory.mktemp("data").join("test_image.png"))
    gen_test_image(image_path)
    return image_path


@pytest.fixture(scope="function")
def output_path(tmpdir_factory):
    output_path = str(tmpdir_factory.mktemp("data").join("output_image.svg"))
    return output_path


def test_main(image_file, output_path):
    exit_code = main([image_file, output_path, "15"])
    assert exit_code == 0
    assert os.path.isfile(output_path)
    drawing = svg2rlg(output_path)
    assert drawing
    assert drawing.contents
