#!/usr/bin/env python
"""
Example usage of dataconfy library.

This script demonstrates how to use dataconfy to save and load
configuration data using dataclasses, including environment variable support.
"""

import os
from dataclasses import dataclass, field
from typing import Any, Dict, Optional

import dataconfy


@dataclass
class AppConfig:
    """Example application configuration."""

    theme: str = "dark"
    font_size: int = 12
    auto_save: bool = True
    max_recent_files: int = 10


@dataclass
class DatabaseConfig:
    """Example database configuration with nested structure."""

    host: str = "localhost"
    port: int = 5432
    database: str = "myapp"
    username: str = "user"


@dataclass
class AppConfigWithDatabase:
    """Application config with nested database configuration."""

    app_name: str = "MyApp"
    debug: bool = False
    database: DatabaseConfig = field(default_factory=DatabaseConfig)
    # Custom env var name example
    api_key: str = field(default="", metadata={"env": "SECRET_API_KEY"})


@dataclass
class UserData:
    """Example user data."""

    username: str = "user"
    email: str = "user@example.com"
    preferences: Optional[Dict[str, Any]] = None


def main():
    """Demonstrate dataconfy usage."""
    print("=" * 60)
    print("dataconfy Example - Configuration & Data Management")
    print("=" * 60)
    print()

    # Initialize managers
    config_manager = dataconfy.ConfigManager(app_name="example_app")
    data_manager = dataconfy.DataManager(app_name="example_app")

    print(f"Config directory: {config_manager.config_dir}")
    print(f"Data directory:   {data_manager.data_dir}")
    print()

    # Example 1: Save and load YAML config
    print("1. Working with YAML configuration:")
    print("-" * 60)

    app_config = AppConfig(theme="light", font_size=14, auto_save=False)
    print(f"Created config: {app_config}")

    # Save to YAML
    config_path = config_manager.save(app_config, "settings.yaml")
    print(f"Saved to: {config_path}")

    # Load from YAML
    loaded_config = config_manager.load(AppConfig, "settings.yaml")
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
    data_path = data_manager.save(user_data, "user.json")
    print(f"Saved to: {data_path}")

    # Load from JSON
    loaded_data = data_manager.load(UserData, "user.json")
    print(f"Loaded data: {loaded_data}")
    print()

    # Example 3: Check file existence
    print("3. Checking file existence:")
    print("-" * 60)
    print(f"settings.yaml exists: {config_manager.exists('settings.yaml')}")
    print(f"user.json exists: {data_manager.exists('user.json')}")
    print(f"missing.yaml exists: {config_manager.exists('missing.yaml')}")
    print()

    # Example 4: Show file contents
    print("4. File contents:")
    print("-" * 60)

    print("YAML content:")
    print(config_path.read_text())

    print("JSON content:")
    print(data_path.read_text())

    # Example 5: Environment variables support
    print("\n5. Environment variables support:")
    print("-" * 60)

    # Set some environment variables
    os.environ["MYAPP_DATABASE_HOST"] = "prod.example.com"
    os.environ["MYAPP_DATABASE_PORT"] = "3306"
    os.environ["MYAPP_DEBUG"] = "true"
    os.environ["MYAPP_SECRET_API_KEY"] = "secret-key-from-env"

    # Create config manager with env vars enabled
    config_with_env = dataconfy.ConfigManager(
        app_name="myapp",
        use_env_vars=True,
    )

    # Save a config file with default values
    default_config = AppConfigWithDatabase(
        app_name="MyApp",
        debug=False,
        database=DatabaseConfig(host="localhost", port=5432),
        api_key="default-key",
    )
    env_config_path = config_with_env.save(default_config, "app_config.yaml")
    print(f"Saved config to: {env_config_path}")
    print(f"File content:\n{env_config_path.read_text()}")

    # Load will merge env vars with file values (env vars take priority)
    loaded_with_env = config_with_env.load(AppConfigWithDatabase, "app_config.yaml")
    print("\nLoaded config (with env var overrides):")
    print(f"  app_name: {loaded_with_env.app_name} (from file)")
    print(f"  debug: {loaded_with_env.debug} (from env: MYAPP_DEBUG)")
    print(f"  database.host: {loaded_with_env.database.host} (from env: MYAPP_DATABASE_HOST)")
    print(f"  database.port: {loaded_with_env.database.port} (from env: MYAPP_DATABASE_PORT)")
    print(f"  database.database: {loaded_with_env.database.database} (from file)")
    print(f"  api_key: {loaded_with_env.api_key} (from env: MYAPP_SECRET_API_KEY)")

    # Clean up environment variables
    del os.environ["MYAPP_DATABASE_HOST"]
    del os.environ["MYAPP_DATABASE_PORT"]
    del os.environ["MYAPP_DEBUG"]
    del os.environ["MYAPP_SECRET_API_KEY"]
    print()

    print("=" * 60)
    print("Example completed successfully!")
    print("=" * 60)


if __name__ == "__main__":
    main()
