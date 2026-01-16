"""Configuration and data persistence managers for application files."""

from pathlib import Path
from typing import Literal, Optional, Union

from platformdirs import user_config_dir, user_data_dir

from dataconfy.base import BaseFileManager


class ConfigManager(BaseFileManager):
    """
    Configuration manager for dataclass-based configs.

    This class handles saving and loading dataclass instances to/from config files,
    with automatic directory management based on XDG config conventions.

    Args:
        app_name: Name of the application (used for directory creation)
        config_dir: Optional custom config directory (overrides platformdirs)
        use_env_vars: Whether to load values from environment variables (default: False)

    Example:
        >>> from dataclasses import dataclass
        >>>
        >>> @dataclass
        >>> class AppConfig:
        ...     theme: str = "dark"
        ...     font_size: int = 12
        >>>
        >>> config = ConfigManager(app_name="myapp")
        >>> my_config = AppConfig()
        >>>
        >>> # Save to YAML
        >>> config.save(my_config, "settings.yaml")
        >>>
        >>> # Load from YAML
        >>> loaded = config.load(AppConfig, "settings.yaml")
    """

    def __init__(
        self,
        app_name: str,
        config_dir: Optional[Union[str, Path]] = None,
        use_env_vars: bool = False,
    ):
        """
        Initialize the Config manager.

        Args:
            app_name: Name of the application
            config_dir: Optional custom config directory path
            use_env_vars: Whether to load values from environment variables (default: False)
        """
        super().__init__(app_name, config_dir, use_env_vars)

    @property
    def _default_dir(self) -> Path:
        """
        Get the default config directory using platformdirs.

        Returns:
            Path to the user config directory
        """
        return Path(user_config_dir(self.app_name))

    @property
    def _default_filename(self) -> str:
        """
        Get the default filename for config files.

        Returns:
            Default filename 'config.yaml'
        """
        return "config.yaml"

    @property
    def config_dir(self) -> Path:
        """Get the config directory path (alias for base_dir)."""
        return self.base_dir

    def save(
        self,
        obj: object,
        filename: Optional[str] = "config.yaml",
        format: Optional[Literal["yaml", "json"]] = None,
    ) -> Path:
        """Save a dataclass instance to a config file.

        Args:
            obj: Dataclass instance to save
            filename: Name of the file (defaults to 'config.yaml')
            format: Optional format override ('yaml' or 'json')

        Returns:
            Path to the saved file
        """
        return super().save(obj, filename, format)

    def load(
        self,
        cls: type,
        filename: Optional[str] = "config.yaml",
        format: Optional[Literal["yaml", "json"]] = None,
    ):
        """Load a dataclass instance from a config file.

        Args:
            cls: Dataclass type to instantiate
            filename: Name of the file to load (defaults to 'config.yaml')
            format: Optional format override ('yaml' or 'json')

        Returns:
            Instance of the dataclass with loaded data
        """
        return super().load(cls, filename, format)


class DataManager(BaseFileManager):
    """
    Data manager for dataclass-based application data.

    This class handles saving and loading dataclass instances to/from data files,
    with automatic directory management based on XDG data conventions.

    Args:
        app_name: Name of the application (used for directory creation)
        data_dir: Optional custom data directory (overrides platformdirs)
        use_env_vars: Whether to load values from environment variables (default: False)

    Example:
        >>> from dataclasses import dataclass
        >>>
        >>> @dataclass
        >>> class UserData:
        ...     username: str
        ...     score: int = 0
        >>>
        >>> data_manager = DataManager(app_name="myapp")
        >>> user_data = UserData(username="alice", score=100)
        >>>
        >>> # Save to YAML
        >>> data_manager.save(user_data, "user.yaml")
        >>>
        >>> # Load from YAML
        >>> loaded = data_manager.load(UserData, "user.yaml")
    """

    def __init__(
        self,
        app_name: str,
        data_dir: Optional[Union[str, Path]] = None,
        use_env_vars: bool = False,
    ):
        """
        Initialize the Data manager.

        Args:
            app_name: Name of the application
            data_dir: Optional custom data directory path
            use_env_vars: Whether to load values from environment variables (default: False)
        """
        super().__init__(app_name, data_dir, use_env_vars)

    @property
    def _default_dir(self) -> Path:
        """
        Get the default data directory using platformdirs.

        Returns:
            Path to the user data directory
        """
        return Path(user_data_dir(self.app_name))

    @property
    def _default_filename(self) -> str:
        """
        Get the default filename for data files.

        Returns:
            Default filename 'data.yaml'
        """
        return "data.yaml"

    @property
    def data_dir(self) -> Path:
        """Get the data directory path (alias for base_dir)."""
        return self.base_dir

    def save(
        self,
        obj: object,
        filename: Optional[str] = "data.yaml",
        format: Optional[Literal["yaml", "json"]] = None,
    ) -> Path:
        """Save a dataclass instance to a data file.

        Args:
            obj: Dataclass instance to save
            filename: Name of the file (defaults to 'data.yaml')
            format: Optional format override ('yaml' or 'json')

        Returns:
            Path to the saved file
        """
        return super().save(obj, filename, format)

    def load(
        self,
        cls: type,
        filename: Optional[str] = "data.yaml",
        format: Optional[Literal["yaml", "json"]] = None,
    ):
        """Load a dataclass instance from a data file.

        Args:
            cls: Dataclass type to instantiate
            filename: Name of the file to load (defaults to 'data.yaml')
            format: Optional format override ('yaml' or 'json')

        Returns:
            Instance of the dataclass with loaded data
        """
        return super().load(cls, filename, format)
