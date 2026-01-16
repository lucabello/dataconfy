"""
dataconfy - Configuration and data persistence for Python dataclasses.

A simple library for persisting dataclass-based application configuration and data
to disk in YAML or JSON format, following XDG conventions for file placement.
"""

from dataconfy.__version__ import __version__
from dataconfy.config import (
    Config,
    DataConfyError,
    InvalidDataclassError,
    UnsupportedFormatError,
)

__all__ = [
    "__version__",
    "Config",
    "DataConfyError",
    "InvalidDataclassError",
    "UnsupportedFormatError",
]
