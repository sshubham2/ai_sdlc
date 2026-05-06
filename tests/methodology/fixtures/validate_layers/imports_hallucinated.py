"""Fixture: imports an undeclared package — should be flagged."""
import json
import nonexistent_pkg
from another_phantom import Helper

from anthropic import Anthropic  # this one is declared
