"""Sanity check that the app package is importable.

Exists so the CI pipeline has something to collect before feature
tests arrive. Safe to remove once real suites are in place.
"""

import app


def test_app_package_importable():
    assert app is not None