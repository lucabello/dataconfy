"""Environment variable support for dataclass configuration and data management."""

import json
import os
from dataclasses import Field, fields, is_dataclass
from typing import Any, Dict, Optional, Tuple, Type, Union, get_args, get_origin


class EnvVarError(Exception):
    """Exception raised for environment variable related errors."""

    pass


def generate_env_prefix(app_name: str) -> str:
    """
    Generate environment variable prefix from app name.

    Converts app name to uppercase and replaces hyphens/spaces with underscores,
    then adds trailing underscore.

    Args:
        app_name: The application name

    Returns:
        Environment variable prefix (e.g., "docker-captain" -> "DOCKER_CAPTAIN_")

    Examples:
        >>> generate_env_prefix("docker-captain")
        'DOCKER_CAPTAIN_'
        >>> generate_env_prefix("noctua")
        'NOCTUA_'
        >>> generate_env_prefix("my app")
        'MY_APP_'
    """
    # Replace hyphens and spaces with underscores, convert to uppercase
    normalized = app_name.replace("-", "_").replace(" ", "_")
    return f"{normalized.upper()}_"


def _unwrap_optional(field_type: Type) -> Tuple[Type, bool]:
    """
    Unwrap Optional[T] to get the actual type T.

    Args:
        field_type: The field type to unwrap

    Returns:
        Tuple of (actual_type, is_optional)
    """
    origin = get_origin(field_type)
    if origin is Union:
        args = get_args(field_type)
        # Check if it's Optional (Union with None)
        if type(None) in args:
            # Get the non-None type
            actual_type = next(arg for arg in args if arg is not type(None))
            return actual_type, True
    return field_type, False


def flatten_dataclass_fields(
    dataclass_type: Type,
    prefix: str = "",
    visited: Optional[set] = None,
) -> Dict[str, Tuple[str, Field, Type]]:
    """
    Recursively flatten dataclass fields to environment variable names.

    Args:
        dataclass_type: The dataclass type to flatten
        prefix: Current field path prefix (for nested dataclasses)
        visited: Set of visited types to prevent infinite recursion

    Returns:
        Dictionary mapping env var names to (field_path, Field, actual_type) tuples

    Raises:
        EnvVarError: If name collision is detected or circular reference found

    Examples:
        Given a dataclass:

        @dataclass
        class DatabaseConfig:
            host: str = "localhost"
            port: int = 5432

        @dataclass
        class AppConfig:
            database: DatabaseConfig
            debug: bool = False

        Returns:
        {
            "DATABASE_HOST": ("database.host", Field(...), str),
            "DATABASE_PORT": ("database.port", Field(...), int),
            "DEBUG": ("debug", Field(...), bool),
        }
    """
    if not is_dataclass(dataclass_type):
        raise EnvVarError(f"{dataclass_type} is not a dataclass")

    if visited is None:
        visited = set()

    # Check for circular references
    if dataclass_type in visited:
        raise EnvVarError(
            f"Circular reference detected: {dataclass_type.__name__} references itself"
        )

    visited.add(dataclass_type)
    result: Dict[str, Tuple[str, Field, Type]] = {}

    for field in fields(dataclass_type):
        # Check for custom env var name in metadata
        custom_env_name = field.metadata.get("env") if field.metadata else None

        # Build field path (e.g., "database.host")
        field_path = f"{prefix}.{field.name}" if prefix else field.name

        # Unwrap Optional if needed
        from typing import cast

        field_type, is_optional = _unwrap_optional(cast(Type, field.type))

        # Check if field is a nested dataclass
        if is_dataclass(field_type):
            # Recursively flatten nested dataclass
            nested_prefix = field_path
            nested_fields = flatten_dataclass_fields(
                field_type, prefix=nested_prefix, visited=visited.copy()
            )
            result.update(nested_fields)
        else:
            # Generate env var name
            if custom_env_name:
                env_name = custom_env_name
            else:
                # Convert field path to env var name (e.g., database.host -> DATABASE_HOST)
                env_name = field_path.replace(".", "_").upper()

            # Check for collision
            if env_name in result:
                existing_path = result[env_name][0]
                raise EnvVarError(
                    f"Env var name collision: '{env_name}' maps to both "
                    f"'{existing_path}' and '{field_path}'"
                )

            result[env_name] = (field_path, field, field_type)

    return result


def parse_bool(value: str) -> bool:
    """
    Parse boolean value from string with flexible formats.

    Args:
        value: String value to parse

    Returns:
        Boolean value

    Raises:
        ValueError: If value is not a recognized boolean string

    Examples:
        >>> parse_bool("true")
        True
        >>> parse_bool("1")
        True
        >>> parse_bool("YES")
        True
        >>> parse_bool("false")
        False
        >>> parse_bool("invalid")
        ValueError: Invalid boolean value 'invalid'...
    """
    lower_value = value.lower()
    if lower_value in ("true", "1", "yes", "on"):
        return True
    elif lower_value in ("false", "0", "no", "off"):
        return False
    else:
        raise ValueError(
            f"Invalid boolean value '{value}'. "
            f"Valid values: true/false, yes/no, on/off, 1/0 (case-insensitive)"
        )


def parse_env_value(value: str, target_type: Type) -> Any:
    """
    Convert environment variable string to target type.

    Args:
        value: String value from environment variable
        target_type: Target type to convert to

    Returns:
        Converted value

    Raises:
        EnvVarError: If conversion fails

    Examples:
        >>> parse_env_value("42", int)
        42
        >>> parse_env_value("3.14", float)
        3.14
        >>> parse_env_value("true", bool)
        True
        >>> parse_env_value('["a","b"]', list)
        ['a', 'b']
    """
    try:
        # Handle string type
        if target_type is str:
            return value

        # Handle boolean with flexible parsing
        if target_type is bool:
            return parse_bool(value)

        # Handle int
        if target_type is int:
            return int(value)

        # Handle float
        if target_type is float:
            return float(value)

        # Handle list and dict with JSON parsing
        origin = get_origin(target_type)
        if origin is list or target_type is list:
            try:
                result = json.loads(value)
                if not isinstance(result, list):
                    raise EnvVarError(
                        f"Expected list for type {target_type}, got {type(result).__name__}"
                    )
                return result
            except json.JSONDecodeError as e:
                raise EnvVarError(f"Invalid JSON for list type: {value}. Error: {e}")

        if origin is dict or target_type is dict:
            try:
                result = json.loads(value)
                if not isinstance(result, dict):
                    raise EnvVarError(
                        f"Expected dict for type {target_type}, got {type(result).__name__}"
                    )
                return result
            except json.JSONDecodeError as e:
                raise EnvVarError(f"Invalid JSON for dict type: {value}. Error: {e}")

        # For other types, try direct construction
        return target_type(value)

    except (ValueError, TypeError) as e:
        raise EnvVarError(f"Failed to convert '{value}' to type {target_type}: {e}")


def _reconstruct_nested_dict(flat_data: Dict[str, Any]) -> Dict[str, Any]:
    """
    Reconstruct nested dictionary from flattened keys.

    Args:
        flat_data: Dictionary with dotted keys (e.g., {"database.host": "localhost"})

    Returns:
        Nested dictionary (e.g., {"database": {"host": "localhost"}})

    Examples:
        >>> _reconstruct_nested_dict({"database.host": "localhost", "debug": True})
        {'database': {'host': 'localhost'}, 'debug': True}
    """
    result: Dict[str, Any] = {}

    for key, value in flat_data.items():
        if "." in key:
            # Split on first dot to handle nested structure
            parts = key.split(".")
            current = result

            # Navigate/create nested structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]

            # Set the final value
            current[parts[-1]] = value
        else:
            # Top-level key
            result[key] = value

    return result


def load_from_env(
    dataclass_type: Type,
    env_prefix: str,
    environ: Optional[Any] = None,
) -> Dict[str, Any]:
    """
    Load dataclass values from environment variables.

    Args:
        dataclass_type: The dataclass type to load
        env_prefix: Environment variable prefix (e.g., "MYAPP_")
        environ: Environment dict to use (defaults to os.environ)

    Returns:
        Dictionary of values ready for dataclass instantiation

    Raises:
        EnvVarError: If environment variable parsing fails or name collision detected

    Examples:
        Given environment variables:
        - MYAPP_DATABASE_HOST=localhost
        - MYAPP_DATABASE_PORT=5432
        - MYAPP_DEBUG=true

        And dataclass:
        @dataclass
        class AppConfig:
            database: DatabaseConfig
            debug: bool = False

        Returns:
        {
            'database': {'host': 'localhost', 'port': 5432},
            'debug': True
        }
    """
    if environ is None:
        environ = os.environ

    # Get flattened field mapping
    field_mapping = flatten_dataclass_fields(dataclass_type)

    # Collect values from environment
    flat_values: Dict[str, Any] = {}

    for env_name, (field_path, field, field_type) in field_mapping.items():
        # Build full env var name with prefix
        full_env_name = f"{env_prefix}{env_name}"

        if full_env_name in environ:
            env_value = environ[full_env_name]

            # Parse the value to the target type
            try:
                parsed_value = parse_env_value(env_value, field_type)
                flat_values[field_path] = parsed_value
            except EnvVarError as e:
                raise EnvVarError(f"Error parsing environment variable '{full_env_name}': {e}")

    # Reconstruct nested structure
    nested_values = _reconstruct_nested_dict(flat_values)

    return nested_values


def detect_name_collisions(dataclass_type: Type) -> None:
    """
    Detect and raise error for environment variable name collisions.

    This is called during load to validate the dataclass structure.

    Args:
        dataclass_type: The dataclass type to validate

    Raises:
        EnvVarError: If name collision is detected
    """
    # flatten_dataclass_fields already detects collisions and raises EnvVarError
    flatten_dataclass_fields(dataclass_type)
