"""Serialization and deserialization utilities for dataclasses."""

import json
from dataclasses import asdict, is_dataclass
from typing import Any, Type, TypeVar

import yaml

T = TypeVar("T")


class InvalidDataclassError(Exception):
    """Raised when the provided class is not a dataclass."""

    pass


class UnsupportedFormatError(Exception):
    """Raised when an unsupported file format is specified."""

    pass


class Serializer:
    """Handles serialization and deserialization of dataclass instances."""

    @staticmethod
    def get_format_from_filename(filename: str) -> str:
        """
        Determine file format from filename extension.

        Args:
            filename: The filename to check

        Returns:
            Format string ('yaml' or 'json')

        Raises:
            UnsupportedFormatError: If the extension is not supported
        """
        from pathlib import Path

        ext = Path(filename).suffix.lower()
        if ext in [".yaml", ".yml"]:
            return "yaml"
        elif ext == ".json":
            return "json"
        else:
            raise UnsupportedFormatError(
                f"Unsupported file extension: {ext}. Use .yaml, .yml, or .json"
            )

    @staticmethod
    def serialize(obj: Any, format: str) -> str:
        """
        Serialize a dataclass instance to string.

        Args:
            obj: Dataclass instance to serialize
            format: Format to serialize to ('yaml' or 'json')

        Returns:
            Serialized string

        Raises:
            InvalidDataclassError: If obj is not a dataclass instance
            UnsupportedFormatError: If format is not supported
        """
        if not is_dataclass(obj) or isinstance(obj, type):
            raise InvalidDataclassError(f"Object must be a dataclass instance, got {type(obj)}")

        data = asdict(obj)

        if format == "yaml":
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        elif format == "json":
            return json.dumps(data, indent=2)
        else:
            raise UnsupportedFormatError(f"Unsupported format: {format}")

    @staticmethod
    def deserialize(content: str, cls: Type[T], format: str) -> T:
        """
        Deserialize string content to a dataclass instance.

        Args:
            content: String content to deserialize
            cls: Dataclass type to instantiate
            format: Format of the content ('yaml' or 'json')

        Returns:
            Instance of the dataclass

        Raises:
            InvalidDataclassError: If cls is not a dataclass
            UnsupportedFormatError: If format is not supported
        """
        if not is_dataclass(cls):
            raise InvalidDataclassError(f"Target class must be a dataclass, got {cls}")

        if format == "yaml":
            data = yaml.safe_load(content)
        elif format == "json":
            data = json.loads(content)
        else:
            raise UnsupportedFormatError(f"Unsupported format: {format}")

        # Handle None case (empty file)
        if data is None:
            data = {}

        return cls(**data)
