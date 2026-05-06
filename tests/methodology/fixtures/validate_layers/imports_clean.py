"""Fixture: only stdlib + declared deps."""
import json
import re
from pathlib import Path

import anthropic
from requests import Session


def fetch():
    return Session().get("https://example.com")
