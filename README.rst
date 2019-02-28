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

To install trivector from source, first, clone and enter this repository, then
run the following pip command:

.. code-block:: shell

    pip install .

Usage
=====

To get help on using trivector type the following command:

.. code-block:: shell

    trivector --help

Example
-------

Below is a simple PNG raster image to trivectorize!

.. image:: ../examples/meface_before.png
    :width: 250

Running ``trivector meface_before.png meface_after.svg 20`` yields the
following trivectorized SVG image at ``meface_after.svg``:

.. image:: ../examples/meface_after.svg
    :width: 250
