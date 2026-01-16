# dataconfy

**Effortless configuration and data persistence for Python applications.**

`dataconfy` is a lightweight Python library that transforms your dataclasses into persistent configuration and data stores. It seamlessly handles file serialization (YAML/JSON), follows XDG directory conventions for cross-platform compatibility, and supports environment variable overrides for cloud-native deployments—all with a simple, intuitive API.

**Key Features:**
- 🎯 **Type-safe**: Uses Python dataclasses for structured, validated configuration
- 💾 **Multiple formats**: YAML and JSON support with automatic format detection
- 📁 **XDG compliant**: Platform-specific directories (Linux, macOS, Windows)
- 🌍 **Environment variables**: Override config values with env vars (perfect for containers and CI/CD)
- 🔄 **Nested structures**: Full support for nested dataclasses with automatic flattening
- 🚀 **Zero config**: Sensible defaults with extensive customization options

## Installation

Install from PyPI:

```bash
pip install dataconfy
```

## Usage

Define your configuration or data structure using Python dataclasses, then use `ConfigManager` or `DataManager` to persist them to disk:

```python
from dataclasses import dataclass
from dataconfy import ConfigManager

@dataclass
class AppConfig:
    theme: str = "dark"
    font_size: int = 12
    auto_save: bool = True

# Create a config manager
config = ConfigManager(app_name="myapp")

# Save configuration to YAML
my_config = AppConfig(theme="light", font_size=14)
config.save(my_config)  # Saved to ~/.config/myapp/config.yaml
config.save(my_config, "settings.yaml")  # Saved to ~/.config/myapp/settings.yaml

# Load configuration from YAML
loaded_config = config.load(AppConfig)
print(loaded_config.theme)  # Output: light
```

### Platform-Specific Directories

`dataconfy` automatically uses the appropriate directories for your operating system:

- **Linux**: `~/.config/appname` (config), `~/.local/share/appname` (data)
- **macOS**: `~/Library/Application Support/appname` (config and data)
- **Windows**: `%LOCALAPPDATA%\appname` (config and data)

```python
from dataconfy import ConfigManager, DataManager

config = ConfigManager(app_name="myapp")
data = DataManager(app_name="myapp")

print(config.config_dir)  # Platform-specific config directory
print(data.data_dir)      # Platform-specific data directory
```

### File Formats

Both YAML and JSON formats are supported, automatically detected from the file extension:

```python
# YAML format
config.save(my_config, "settings.yaml")

# JSON format
config.save(my_config, "settings.json")

# Force a specific format
config.save(my_config, "config.txt", format="yaml")
```

### Checking File Existence

```python
if config.exists("settings.yaml"):
    my_config = config.load(AppConfig, "settings.yaml")
else:
    my_config = AppConfig()  # Use defaults
```

### Complete Example

```python
from dataclasses import dataclass
from dataconfy import ConfigManager, DataManager

@dataclass
class AppConfig:
    theme: str = "dark"
    font_size: int = 12
    auto_save: bool = True

@dataclass
class UserPreferences:
    language: str = "en"

# Initialize managers
config = ConfigManager(app_name="myapp")
data = DataManager(app_name="myapp")

# Save database config to config directory
app_config = AppConfig(theme="light")
config.save(app_config)

# Save user preferences to data directory
user_prefs = UserPreferences(language="fr")
data.save(user_prefs, "preferences.json")

# Load them back
loaded_config = config.load(AppConfig)
loaded_prefs = data.load(UserPreferences, "preferences.json")
```

### Environment Variable Support

`dataconfy` can load configuration values from environment variables, allowing you to override file-based settings with environment-specific values. This is especially useful for containerized applications, CI/CD pipelines, and cloud deployments.

#### Basic Usage

Enable environment variable support by setting `use_env_vars=True`:

```python
from dataclasses import dataclass
from dataconfy import ConfigManager

@dataclass
class AppConfig:
    host: str = "localhost"
    port: int = 8000
    debug: bool = False

# Enable environment variable support
config = ConfigManager(app_name="myapp", use_env_vars=True)

# Environment variables like MYAPP_HOST, MYAPP_PORT, MYAPP_DEBUG
# will override values from the config file
app_config = config.load(AppConfig, "config.yaml")
```

#### Environment Variable Naming

Environment variables are automatically mapped from dataclass field names:

- App name is converted to uppercase with underscores: `my-app` → `MY_APP_`
- Field names are converted to uppercase: `port` → `PORT`
- Combined: `MYAPP_PORT`

**Examples:**

| App Name | Field Name | Environment Variable |
|----------|------------|---------------------|
| `myapp` | `debug` | `MYAPP_DEBUG` |
| `docker-captain` | `projects_folder` | `DOCKER_CAPTAIN_PROJECTS_FOLDER` |
| `hledger-tui` | `ledger_file` | `HLEDGER_TUI_LEDGER_FILE` |

#### Nested Dataclasses

Nested dataclasses are flattened using underscore notation:

```python
from dataclasses import dataclass

@dataclass
class DatabaseConfig:
    host: str = "localhost"
    port: int = 5432

@dataclass
class AppConfig:
    database: DatabaseConfig
    debug: bool = False

config = ConfigManager(app_name="myapp", use_env_vars=True)

# Set environment variables:
# MYAPP_DATABASE_HOST=prod.example.com
# MYAPP_DATABASE_PORT=3306
# MYAPP_DEBUG=true

app_config = config.load(AppConfig, "config.yaml")
# database.host will be "prod.example.com" (from env)
# database.port will be 3306 (from env)
```

#### Custom Environment Variable Names

You can specify custom environment variable names using field metadata:

```python
from dataclasses import dataclass, field

@dataclass
class AppConfig:
    # Use custom env var name instead of MYAPP_API_KEY
    api_key: str = field(default="", metadata={"env": "SECRET_API_KEY"})
    timeout: int = 30

config = ConfigManager(app_name="myapp", use_env_vars=True)

# Set: MYAPP_SECRET_API_KEY=abc123
# Set: MYAPP_TIMEOUT=60
```

#### Type Conversion

Environment variables are automatically converted to the appropriate types:

- **Strings**: Used as-is
- **Integers & Floats**: Parsed from numeric strings
- **Booleans**: Flexible parsing supports `true/false`, `yes/no`, `on/off`, `1/0` (case-insensitive)
- **Lists & Dicts**: Parsed from JSON strings

```python
# Boolean examples:
# MYAPP_DEBUG=true    → True
# MYAPP_DEBUG=1       → True
# MYAPP_DEBUG=yes     → True
# MYAPP_DEBUG=false   → False

# List example:
# MYAPP_TAGS='["tag1", "tag2", "tag3"]'  → ["tag1", "tag2", "tag3"]

# Dict example:
# MYAPP_METADATA='{"key": "value"}'      → {"key": "value"}
```

#### Priority Order

When loading configuration, values are merged in this priority order (highest to lowest):

1. **Environment variables** (highest priority)
2. **File values**
3. **Dataclass defaults** (lowest priority)

```python
# config.yaml:
# debug: false
# port: 8000

# Environment:
# MYAPP_DEBUG=true

config = ConfigManager(app_name="myapp", use_env_vars=True)
app_config = config.load(AppConfig, "config.yaml")

# Result:
# debug: True   (from environment variable)
# port: 8000    (from file)
```

#### Loading Without Files

When `use_env_vars=True`, you can load configuration entirely from environment variables without a config file:

```python
config = ConfigManager(app_name="myapp", use_env_vars=True)

# This works even if config.yaml doesn't exist
app_config = config.load(AppConfig, "config.yaml")
```

#### Limitations

- **Name collisions**: Fields like `database_host` and a nested `database.host` both map to `DATABASE_HOST`. The library will detect and raise an error for such collisions.
- **Complex nested structures**: Only dataclass nesting is supported. Lists of dataclasses or deeply nested custom types may not work as expected.

## Development

If you want to contribute to the project, please start by opening an [issue](https://github.com/lucabello/dataconfy/issues).

The project uses `uv` for dependency management and `just` for task automation. Run `just` to see all available commands.

## License

Apache 2.0 License - see [LICENSE](LICENSE) file for details.
