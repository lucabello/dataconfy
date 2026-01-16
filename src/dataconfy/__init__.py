"""
dataconfy - Configuration and data persistence for Python dataclasses.

A simple library for persisting dataclass-based application configuration and data
to disk in YAML or JSON format, following XDG conventions for file placement.
"""

from importlib.metadata import version

from dataconfy.base import DataConfyError
from dataconfy.env_vars import EnvVarError
from dataconfy.managers import ConfigManager, DataManager
from dataconfy.serializers import InvalidDataclassError, UnsupportedFormatError

__version__ = version("dataconfy")

__all__ = [
    "__version__",
    "ConfigManager",
    "DataManager",
    "DataConfyError",
    "EnvVarError",
    "InvalidDataclassError",
    "UnsupportedFormatError",
]
