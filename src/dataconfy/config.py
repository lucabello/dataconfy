"""
dataconfy - Configuration and data persistence for Python dataclasses.

This module provides utilities to save and load dataclass instances to/from
YAML or JSON files, with automatic path management using XDG conventions via platformdirs.
"""

import json
import os
from dataclasses import asdict, is_dataclass
from pathlib import Path
from typing import Any, Type, TypeVar, Optional, Union

import yaml
from platformdirs import user_config_dir, user_data_dir

T = TypeVar('T')


class DataConfyError(Exception):
    """Base exception for dataconfy errors."""
    pass


class InvalidDataclassError(DataConfyError):
    """Raised when the provided class is not a dataclass."""
    pass


class UnsupportedFormatError(DataConfyError):
    """Raised when an unsupported file format is specified."""
    pass


class Config:
    """
    Configuration manager for dataclass-based configs and data.
    
    This class handles saving and loading dataclass instances to/from files,
    with automatic directory management based on XDG conventions.
    
    Args:
        app_name: Name of the application (used for directory creation)
        config_dir: Optional custom config directory (overrides platformdirs)
        data_dir: Optional custom data directory (overrides platformdirs)
    
    Example:
        >>> from dataclasses import dataclass
        >>> 
        >>> @dataclass
        >>> class AppConfig:
        ...     theme: str = "dark"
        ...     font_size: int = 12
        >>> 
        >>> config = Config(app_name="myapp")
        >>> my_config = AppConfig()
        >>> 
        >>> # Save to YAML
        >>> config.save_config(my_config, "settings.yaml")
        >>> 
        >>> # Load from YAML
        >>> loaded = config.load_config(AppConfig, "settings.yaml")
    """
    
    def __init__(
        self,
        app_name: str,
        config_dir: Optional[Union[str, Path]] = None,
        data_dir: Optional[Union[str, Path]] = None,
    ):
        """
        Initialize the Config manager.
        
        Args:
            app_name: Name of the application
            config_dir: Optional custom config directory path
            data_dir: Optional custom data directory path
        """
        self.app_name = app_name
        self._config_dir = Path(config_dir) if config_dir else Path(user_config_dir(app_name))
        self._data_dir = Path(data_dir) if data_dir else Path(user_data_dir(app_name))
    
    @property
    def config_dir(self) -> Path:
        """Get the configuration directory path."""
        return self._config_dir
    
    @property
    def data_dir(self) -> Path:
        """Get the data directory path."""
        return self._data_dir
    
    def _ensure_dir(self, directory: Path) -> None:
        """Ensure a directory exists, creating it if necessary."""
        directory.mkdir(parents=True, exist_ok=True)
    
    def _get_format(self, filename: str) -> str:
        """Determine file format from filename extension."""
        ext = Path(filename).suffix.lower()
        if ext in ['.yaml', '.yml']:
            return 'yaml'
        elif ext == '.json':
            return 'json'
        else:
            raise UnsupportedFormatError(
                f"Unsupported file extension: {ext}. Use .yaml, .yml, or .json"
            )
    
    def _serialize(self, obj: Any, format: str) -> str:
        """Serialize a dataclass instance to string."""
        if not is_dataclass(obj):
            raise InvalidDataclassError(
                f"Object must be a dataclass instance, got {type(obj)}"
            )
        
        data = asdict(obj)
        
        if format == 'yaml':
            return yaml.dump(data, default_flow_style=False, sort_keys=False)
        elif format == 'json':
            return json.dumps(data, indent=2)
        else:
            raise UnsupportedFormatError(f"Unsupported format: {format}")
    
    def _deserialize(self, content: str, cls: Type[T], format: str) -> T:
        """Deserialize string content to a dataclass instance."""
        if not is_dataclass(cls):
            raise InvalidDataclassError(
                f"Target class must be a dataclass, got {cls}"
            )
        
        if format == 'yaml':
            data = yaml.safe_load(content)
        elif format == 'json':
            data = json.loads(content)
        else:
            raise UnsupportedFormatError(f"Unsupported format: {format}")
        
        # Handle None case (empty file)
        if data is None:
            data = {}
        
        return cls(**data)
    
    def save_config(
        self,
        obj: Any,
        filename: str,
        format: Optional[str] = None,
    ) -> Path:
        """
        Save a dataclass instance to a config file.
        
        Args:
            obj: Dataclass instance to save
            filename: Name of the file (extension determines format if not specified)
            format: Optional format override ('yaml' or 'json')
        
        Returns:
            Path to the saved file
        
        Raises:
            InvalidDataclassError: If obj is not a dataclass instance
            UnsupportedFormatError: If format is not supported
        """
        file_format = format or self._get_format(filename)
        self._ensure_dir(self.config_dir)
        
        filepath = self.config_dir / filename
        content = self._serialize(obj, file_format)
        
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def load_config(
        self,
        cls: Type[T],
        filename: str,
        format: Optional[str] = None,
    ) -> T:
        """
        Load a dataclass instance from a config file.
        
        Args:
            cls: Dataclass type to instantiate
            filename: Name of the file to load
            format: Optional format override ('yaml' or 'json')
        
        Returns:
            Instance of the dataclass with loaded data
        
        Raises:
            InvalidDataclassError: If cls is not a dataclass
            FileNotFoundError: If the file doesn't exist
            UnsupportedFormatError: If format is not supported
        """
        file_format = format or self._get_format(filename)
        filepath = self.config_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Config file not found: {filepath}")
        
        content = filepath.read_text(encoding='utf-8')
        return self._deserialize(content, cls, file_format)
    
    def save_data(
        self,
        obj: Any,
        filename: str,
        format: Optional[str] = None,
    ) -> Path:
        """
        Save a dataclass instance to a data file.
        
        Args:
            obj: Dataclass instance to save
            filename: Name of the file (extension determines format if not specified)
            format: Optional format override ('yaml' or 'json')
        
        Returns:
            Path to the saved file
        
        Raises:
            InvalidDataclassError: If obj is not a dataclass instance
            UnsupportedFormatError: If format is not supported
        """
        file_format = format or self._get_format(filename)
        self._ensure_dir(self.data_dir)
        
        filepath = self.data_dir / filename
        content = self._serialize(obj, file_format)
        
        filepath.write_text(content, encoding='utf-8')
        return filepath
    
    def load_data(
        self,
        cls: Type[T],
        filename: str,
        format: Optional[str] = None,
    ) -> T:
        """
        Load a dataclass instance from a data file.
        
        Args:
            cls: Dataclass type to instantiate
            filename: Name of the file to load
            format: Optional format override ('yaml' or 'json')
        
        Returns:
            Instance of the dataclass with loaded data
        
        Raises:
            InvalidDataclassError: If cls is not a dataclass
            FileNotFoundError: If the file doesn't exist
            UnsupportedFormatError: If format is not supported
        """
        file_format = format or self._get_format(filename)
        filepath = self.data_dir / filename
        
        if not filepath.exists():
            raise FileNotFoundError(f"Data file not found: {filepath}")
        
        content = filepath.read_text(encoding='utf-8')
        return self._deserialize(content, cls, file_format)
    
    def config_file_exists(self, filename: str) -> bool:
        """Check if a config file exists."""
        return (self.config_dir / filename).exists()
    
    def data_file_exists(self, filename: str) -> bool:
        """Check if a data file exists."""
        return (self.data_dir / filename).exists()
