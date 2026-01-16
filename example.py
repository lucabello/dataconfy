#!/usr/bin/env python
"""
Example usage of dataconfy library.

This script demonstrates how to use dataconfy to save and load
configuration data using dataclasses.
"""

from dataclasses import dataclass
from typing import Dict, Any, Optional
import dataconfy


@dataclass
class AppConfig:
    """Example application configuration."""

    theme: str = "dark"
    font_size: int = 12
    auto_save: bool = True
    max_recent_files: int = 10


@dataclass
class UserData:
    """Example user data."""

    username: str = "user"
    email: str = "user@example.com"
    preferences: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.preferences is None:
            self.preferences = {}


def main():
    """Demonstrate dataconfy usage."""
    print("=" * 60)
    print("dataconfy Example - Configuration & Data Management")
    print("=" * 60)
    print()

    # Initialize config manager
    config = dataconfy.Config(app_name="example_app")

    print(f"Config directory: {config.config_dir}")
    print(f"Data directory:   {config.data_dir}")
    print()

    # Example 1: Save and load YAML config
    print("1. Working with YAML configuration:")
    print("-" * 60)

    app_config = AppConfig(theme="light", font_size=14, auto_save=False)
    print(f"Created config: {app_config}")

    # Save to YAML
    config_path = config.save_config(app_config, "settings.yaml")
    print(f"Saved to: {config_path}")

    # Load from YAML
    loaded_config = config.load_config(AppConfig, "settings.yaml")
    print(f"Loaded config: {loaded_config}")
    print()

    # Example 2: Save and load JSON data
    print("2. Working with JSON data:")
    print("-" * 60)

    user_data = UserData(
        username="john_doe",
        email="john@example.com",
        preferences={"notifications": True, "language": "en"},
    )
    print(f"Created data: {user_data}")

    # Save to JSON
    data_path = config.save_data(user_data, "user.json")
    print(f"Saved to: {data_path}")

    # Load from JSON
    loaded_data = config.load_data(UserData, "user.json")
    print(f"Loaded data: {loaded_data}")
    print()

    # Example 3: Check file existence
    print("3. Checking file existence:")
    print("-" * 60)
    print(f"settings.yaml exists: {config.config_file_exists('settings.yaml')}")
    print(f"user.json exists: {config.data_file_exists('user.json')}")
    print(f"missing.yaml exists: {config.config_file_exists('missing.yaml')}")
    print()

    # Example 4: Show file contents
    print("4. File contents:")
    print("-" * 60)

    print("YAML content:")
    print(config_path.read_text())

    print("JSON content:")
    print(data_path.read_text())

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
