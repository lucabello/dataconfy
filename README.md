# dataconfy

Persist dataclass-based app config/data to disk (YAML/JSON) following XDG conventions, with simple load/save API.

## Overview

`dataconfy` is a lightweight Python library that simplifies configuration and data management for Python applications. It allows you to:

- ✅ Save and load Python dataclasses to/from YAML or JSON files
- ✅ Automatically manage config and data directories using XDG conventions (via `platformdirs`)
- ✅ Support both configuration files and data files with separate directory management
- ✅ Simple, intuitive API with minimal boilerplate

## Installation

```bash
pip install dataconfy
```

## Quick Start

```python
from dataclasses import dataclass
from dataconfy import Config

# Define your configuration using a dataclass
@dataclass
class AppConfig:
    theme: str = "dark"
    font_size: int = 12
    auto_save: bool = True

# Create a config manager
config = Config(app_name="myapp")

# Save configuration to YAML
my_config = AppConfig(theme="light", font_size=14)
config.save_config(my_config, "settings.yaml")

# Load configuration from YAML
loaded_config = config.load_config(AppConfig, "settings.yaml")
print(loaded_config.theme)  # Output: light
```

## Features

### Automatic Directory Management

`dataconfy` uses `platformdirs` to automatically determine the correct directories for configuration and data files based on your operating system:

- **Linux**: `~/.config/appname` (config), `~/.local/share/appname` (data)
- **macOS**: `~/Library/Application Support/appname` (config), `~/Library/Application Support/appname` (data)
- **Windows**: `C:\Users\Username\AppData\Local\appname` (config and data)

```python
config = Config(app_name="myapp")
print(config.config_dir)  # Platform-specific config directory
print(config.data_dir)    # Platform-specific data directory
```

### Custom Directories

You can override the default directories if needed:

```python
config = Config(
    app_name="myapp",
    config_dir="/custom/config/path",
    data_dir="/custom/data/path"
)
```

### Multiple File Formats

Support for both YAML and JSON formats, automatically detected from file extension:

```python
# YAML format
config.save_config(my_config, "settings.yaml")
config.save_config(my_config, "settings.yml")

# JSON format
config.save_config(my_config, "settings.json")

# Force a specific format
config.save_config(my_config, "config.txt", format="yaml")
```

### Separate Config and Data

Distinguish between configuration files and data files:

```python
# Save to config directory
config.save_config(app_settings, "settings.yaml")

# Save to data directory
config.save_data(user_data, "userdata.json")
```

### File Existence Checks

Check if a file exists before loading:

```python
if config.config_file_exists("settings.yaml"):
    my_config = config.load_config(AppConfig, "settings.yaml")
else:
    my_config = AppConfig()  # Use defaults
```

## Complete Example

```python
from dataclasses import dataclass
from dataconfy import Config

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432
    database: str = "mydb"
    ssl_enabled: bool = True

@dataclass
class UserPreferences:
    theme: str = "dark"
    language: str = "en"
    notifications: bool = True

# Initialize config manager
config = Config(app_name="myapp")

# Save database config to YAML
db_config = DatabaseConfig(host="db.example.com", port=3306)
config.save_config(db_config, "database.yaml")

# Save user preferences to JSON
user_prefs = UserPreferences(theme="light", language="fr")
config.save_data(user_prefs, "preferences.json")

# Load them back
loaded_db = config.load_config(DatabaseConfig, "database.yaml")
loaded_prefs = config.load_data(UserPreferences, "preferences.json")

print(f"Database: {loaded_db.host}:{loaded_db.port}")
print(f"Theme: {loaded_prefs.theme}, Language: {loaded_prefs.language}")
```

## API Reference

### `Config` Class

**Constructor:**
```python
Config(app_name: str, config_dir: Optional[Path] = None, data_dir: Optional[Path] = None)
```

**Methods:**

- `save_config(obj, filename, format=None)` - Save a dataclass to a config file
- `load_config(cls, filename, format=None)` - Load a dataclass from a config file
- `save_data(obj, filename, format=None)` - Save a dataclass to a data file
- `load_data(cls, filename, format=None)` - Load a dataclass from a data file
- `config_file_exists(filename)` - Check if a config file exists
- `data_file_exists(filename)` - Check if a data file exists

**Properties:**

- `config_dir` - Path to the configuration directory
- `data_dir` - Path to the data directory

### Exceptions

- `DataConfyError` - Base exception for all dataconfy errors
- `InvalidDataclassError` - Raised when a non-dataclass is provided
- `UnsupportedFormatError` - Raised when an unsupported file format is used

## Requirements

- Python 3.10+
- `platformdirs` >= 4.5.0
- `PyYAML` >= 6.0.3

## Development

If you want to contribute to the project, please start by opening an [issue](https://github.com/lucabello/dataconfy/issues).

You can interact with the project via `uv` and the `justfile` (from [casey/just](https://github.com/casey/just)) at the root of the repository. Simply run `just` to show the available recipes.

```bash
# Create a virtual environment for the project
uv sync

# Linting, formatting, and testing
just          # show the list of all commands
just check    # run all quality checks (format, lint, test)
just format   # format the code
just lint     # lint the code
just test     # run tests
just build    # build the project
```

## License

MIT License - see LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.
