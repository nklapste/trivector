*********
trivector
*********

.. image:: https://travis-ci.com/nklapste/trivector.svg?branch=master
    :target: https://travis-ci.com/nklapste/trivector
    :alt: Build Status

.. image:: https://readthedocs.org/projects/trivector/badge/?version=latest
    :target: https://trivector.readthedocs.io/en/latest/?badge=latest
    :alt: Documentation Status

Description
===========

Convert an image into a SVG vector image composed of triangular sectors.

Installation
============

You can install trivector from pypi with the following command:

.. code-block:: shell

    pip install trivector

Usage
=====

To get help on using trivector type the following command:

.. code-block:: shell

    trivector --help

Example
-------

Below is a simple PNG raster image to trivectorize!

.. image:: https://raw.githubusercontent.com/nklapste/trivector/master/examples/meface_before.png
    :width: 250

Running ``trivector meface_before.png meface_after.svg 20`` yields the
following trivectorized SVG image at ``meface_after.svg``:

.. image:: https://raw.githubusercontent.com/nklapste/trivector/master/examples/meface_after.svg?sanitize=true
    :width: 250
