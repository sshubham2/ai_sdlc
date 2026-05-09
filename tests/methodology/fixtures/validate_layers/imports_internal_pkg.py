"""Fixture: stdlib + setuptools-declared internal package."""
import json

from my_internal_pkg.x import y


def use_internal():
    return y(json.dumps({}))
