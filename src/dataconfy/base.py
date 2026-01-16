"""Base class for dataclass persistence managers."""

import json
from abc import ABC, abstractmethod
from dataclasses import fields, is_dataclass
from pathlib import Path
from typing import Any, Dict, Literal, Optional, Type, TypeVar, Union, get_args, get_origin

import yaml

from dataconfy import env_vars
from dataconfy.serializers import Serializer

T = TypeVar("T")


class DataConfyError(Exception):
    """Base exception for dataconfy errors."""

    pass


class BaseFileManager(ABC):
    """
    Abstract base class for managing dataclass file persistence.

    This class provides common functionality for saving and loading dataclass
    instances to/from files, with automatic directory management.

    Args:
        app_name: Name of the application (used for directory creation)
        base_dir: Optional custom base directory (overrides platform defaults)
        use_env_vars: Whether to load values from environment variables (default: False)
    """

    def __init__(
        self,
        app_name: str,
        base_dir: Optional[Union[str, Path]] = None,
        use_env_vars: bool = False,
    ):
        """
        Initialize the persistence manager.

        Args:
            app_name: Name of the application
            base_dir: Optional custom base directory path
            use_env_vars: Whether to load values from environment variables (default: False)
        """
        self.app_name = app_name
        self._base_dir = Path(base_dir) if base_dir else self._default_dir
        self._serializer = Serializer()
        self.use_env_vars = use_env_vars

    @property
    @abstractmethod
    def _default_dir(self) -> Path:
        """
        Get the default directory for this manager type.

        Must be implemented by subclasses to provide platform-specific defaults.

        Returns:
            Path to the default directory
        """
        pass

    @property
    @abstractmethod
    def _default_filename(self) -> str:
        """
        Get the default filename for this manager type.

        Must be implemented by subclasses to provide type-specific defaults.

        Returns:
            Default filename string
        """
        pass

    @property
    def base_dir(self) -> Path:
        """Get the base directory path."""
        return self._base_dir

    def _ensure_dir(self, directory: Path) -> None:
        """
        Ensure a directory exists, creating it if necessary.

        Args:
            directory: Directory path to ensure exists
        """
        directory.mkdir(parents=True, exist_ok=True)

    def save(
        self,
        obj: Any,
        filename: Optional[str] = None,
        format: Optional[Literal["yaml", "json"]] = None,
    ) -> Path:
        """
        Save a dataclass instance to a file.

        Args:
            obj: Dataclass instance to save
            filename: Name of the file (defaults to manager-specific default)
            format: Optional format override ('yaml' or 'json')

        Returns:
            Path to the saved file

        Raises:
            InvalidDataclassError: If obj is not a dataclass instance
            UnsupportedFormatError: If format is not supported
        """
        if filename is None:
            filename = self._default_filename
        file_format = format or self._serializer.get_format_from_filename(filename)
        self._ensure_dir(self.base_dir)

        filepath = self.base_dir / filename
        content = self._serializer.serialize(obj, file_format)

        filepath.write_text(content, encoding="utf-8")
        return filepath

    def load(
        self,
        cls: Type[T],
        filename: Optional[str] = None,
        format: Optional[Literal["yaml", "json"]] = None,
    ) -> T:
        """
        Load a dataclass instance from a file.

        Args:
            cls: Dataclass type to instantiate
            filename: Name of the file to load (defaults to manager-specific default)
            format: Optional format override ('yaml' or 'json')

        Returns:
            Instance of the dataclass with loaded data

        Raises:
            InvalidDataclassError: If cls is not a dataclass
            FileNotFoundError: If the file doesn't exist
            UnsupportedFormatError: If format is not supported
            EnvVarError: If environment variable parsing fails (when use_env_vars=True)
        """
        # Validate that cls is a dataclass
        if not is_dataclass(cls):
            from dataconfy.serializers import InvalidDataclassError

            raise InvalidDataclassError(f"Target class must be a dataclass, got {cls}")

        if filename is None:
            filename = self._default_filename
        file_format = format or self._serializer.get_format_from_filename(filename)
        filepath = self.base_dir / filename

        # Load from file if it exists, otherwise start with empty dict
        if filepath.exists():
            content = filepath.read_text(encoding="utf-8")
            # Parse content to dict
            if file_format == "yaml":
                data = yaml.safe_load(content)
            elif file_format == "json":
                data = json.loads(content)
            else:
                from dataconfy.serializers import UnsupportedFormatError

                raise UnsupportedFormatError(f"Unsupported format: {file_format}")

            # Handle None case (empty file)
            if data is None:
                data = {}
        else:
            # If file doesn't exist and env vars are disabled, raise error
            if not self.use_env_vars:
                raise FileNotFoundError(f"File not found: {filepath}")
            data = {}

        # Load and merge environment variables if enabled
        if self.use_env_vars:
            env_prefix = env_vars.generate_env_prefix(self.app_name)
            env_data = env_vars.load_from_env(cls, env_prefix)

            # Merge with priority: env vars > file values
            data = self._merge_dicts(data, env_data)

        # Instantiate nested dataclasses from dict data
        data = self._instantiate_nested_dataclasses(cls, data)

        # Instantiate dataclass with merged data
        return cls(**data)

    def _merge_dicts(self, base: Dict[str, Any], override: Dict[str, Any]) -> Dict[str, Any]:
        """
        Recursively merge two dictionaries, with override taking precedence.

        Args:
            base: Base dictionary
            override: Dictionary with values to override

        Returns:
            Merged dictionary
        """
        result = base.copy()
        for key, value in override.items():
            if key in result and isinstance(result[key], dict) and isinstance(value, dict):
                # Recursively merge nested dicts
                result[key] = self._merge_dicts(result[key], value)
            else:
                # Override value
                result[key] = value
        return result

    def _instantiate_nested_dataclasses(
        self, cls: Type[T], data: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Recursively instantiate nested dataclasses from dictionary data.

        Args:
            cls: The dataclass type to instantiate
            data: Dictionary of field values

        Returns:
            Dictionary with nested dataclasses instantiated
        """
        if not is_dataclass(cls):
            return data

        result = {}
        dataclass_fields = {f.name: f for f in fields(cls)}

        for key, value in data.items():
            if key not in dataclass_fields:
                result[key] = value
                continue

            field = dataclass_fields[key]
            field_type = field.type

            # Unwrap Optional if needed
            origin = get_origin(field_type)
            if origin is Union:
                args = get_args(field_type)
                if type(None) in args:
                    # It's Optional, get the actual type
                    field_type = next(arg for arg in args if arg is not type(None))

            # If the field type is a dataclass and value is a dict, instantiate it
            if is_dataclass(field_type) and isinstance(value, dict):
                # Recursively instantiate nested dataclass
                from typing import cast

                nested_data = self._instantiate_nested_dataclasses(cast(Type, field_type), value)
                result[key] = field_type(**nested_data)  # type: ignore[misc]
            else:
                result[key] = value

        return result

    def exists(self, filename: Optional[str] = None) -> bool:
        """
        Check if a file exists.

        Args:
            filename: Name of the file to check (defaults to manager-specific default)

        Returns:
            True if the file exists, False otherwise
        """
        if filename is None:
            filename = self._default_filename
        return (self.base_dir / filename).exists()

    def get_path(self, filename: Optional[str] = None) -> Path:
        """
        Get the full path for a filename.

        Args:
            filename: Name of the file (defaults to manager-specific default)

        Returns:
            Full path to the file
        """
        if filename is None:
            filename = self._default_filename
        return self.base_dir / filename
