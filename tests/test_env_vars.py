"""Tests for environment variable support."""

import os
from dataclasses import dataclass, field
from typing import Dict, List, Optional

import pytest

from dataconfy.env_vars import (
    EnvVarError,
    flatten_dataclass_fields,
    generate_env_prefix,
    load_from_env,
    parse_bool,
    parse_env_value,
)
from dataconfy.managers import ConfigManager, DataManager


class TestEnvPrefix:
    """Tests for environment variable prefix generation."""

    def test_generate_prefix_simple(self):
        """Test simple app name conversion."""
        assert generate_env_prefix("noctua") == "NOCTUA_"

    def test_generate_prefix_with_hyphen(self):
        """Test app name with hyphens."""
        assert generate_env_prefix("docker-captain") == "DOCKER_CAPTAIN_"

    def test_generate_prefix_with_space(self):
        """Test app name with spaces."""
        assert generate_env_prefix("my app") == "MY_APP_"

    def test_generate_prefix_mixed(self):
        """Test app name with mixed separators."""
        assert generate_env_prefix("my-cool app") == "MY_COOL_APP_"


class TestBoolParsing:
    """Tests for boolean value parsing."""

    def test_parse_bool_true_variations(self):
        """Test various true representations."""
        for value in ["true", "True", "TRUE", "1", "yes", "Yes", "YES", "on", "On", "ON"]:
            assert parse_bool(value) is True

    def test_parse_bool_false_variations(self):
        """Test various false representations."""
        for value in ["false", "False", "FALSE", "0", "no", "No", "NO", "off", "Off", "OFF"]:
            assert parse_bool(value) is False

    def test_parse_bool_invalid(self):
        """Test invalid boolean values."""
        with pytest.raises(ValueError) as exc_info:
            parse_bool("invalid")
        assert "Invalid boolean value" in str(exc_info.value)
        assert "true/false" in str(exc_info.value)


class TestTypeConversion:
    """Tests for environment variable type conversion."""

    def test_parse_string(self):
        """Test string parsing."""
        assert parse_env_value("hello", str) == "hello"

    def test_parse_int(self):
        """Test integer parsing."""
        assert parse_env_value("42", int) == 42

    def test_parse_float(self):
        """Test float parsing."""
        assert parse_env_value("3.14", float) == 3.14

    def test_parse_bool(self):
        """Test boolean parsing."""
        assert parse_env_value("true", bool) is True
        assert parse_env_value("0", bool) is False

    def test_parse_list_json(self):
        """Test list parsing from JSON."""
        assert parse_env_value('["a", "b", "c"]', list) == ["a", "b", "c"]
        assert parse_env_value("[1, 2, 3]", list) == [1, 2, 3]

    def test_parse_dict_json(self):
        """Test dict parsing from JSON."""
        result = parse_env_value('{"key": "value"}', dict)
        assert result == {"key": "value"}

    def test_parse_list_invalid_json(self):
        """Test list parsing with invalid JSON."""
        with pytest.raises(EnvVarError) as exc_info:
            parse_env_value("not-json", list)
        assert "Invalid JSON" in str(exc_info.value)

    def test_parse_dict_invalid_json(self):
        """Test dict parsing with invalid JSON."""
        with pytest.raises(EnvVarError) as exc_info:
            parse_env_value("[1,2,3]", dict)
        assert "Expected dict" in str(exc_info.value)

    def test_parse_int_invalid(self):
        """Test integer parsing with invalid value."""
        with pytest.raises(EnvVarError) as exc_info:
            parse_env_value("not-a-number", int)
        assert "Failed to convert" in str(exc_info.value)


class TestFieldFlattening:
    """Tests for dataclass field flattening."""

    def test_flatten_simple_dataclass(self):
        """Test flattening simple dataclass."""

        @dataclass
        class Simple:
            name: str = "test"
            count: int = 0

        result = flatten_dataclass_fields(Simple)
        assert "NAME" in result
        assert "COUNT" in result
        assert result["NAME"][0] == "name"
        assert result["COUNT"][0] == "count"

    def test_flatten_nested_dataclass(self):
        """Test flattening nested dataclass."""

        @dataclass
        class Database:
            host: str = "localhost"
            port: int = 5432

        @dataclass
        class Config:
            database: Database
            debug: bool = False

        result = flatten_dataclass_fields(Config)
        assert "DATABASE_HOST" in result
        assert "DATABASE_PORT" in result
        assert "DEBUG" in result
        assert result["DATABASE_HOST"][0] == "database.host"
        assert result["DATABASE_PORT"][0] == "database.port"

    def test_flatten_with_custom_metadata(self):
        """Test flattening with custom env var names."""

        @dataclass
        class Config:
            api_key: str = field(default="", metadata={"env": "SECRET_KEY"})
            timeout: int = 30

        result = flatten_dataclass_fields(Config)
        assert "SECRET_KEY" in result
        assert "TIMEOUT" in result
        assert result["SECRET_KEY"][0] == "api_key"

    def test_flatten_optional_nested(self):
        """Test flattening with Optional nested dataclass."""

        @dataclass
        class Database:
            host: str = "localhost"

        @dataclass
        class Config:
            database: Optional[Database] = None

        result = flatten_dataclass_fields(Config)
        assert "DATABASE_HOST" in result

    def test_flatten_name_collision_detection(self):
        """Test that name collisions are detected."""

        @dataclass
        class Config:
            database_host: str = "localhost"
            database: Dict[str, str] = field(
                default_factory=dict, metadata={"env": "DATABASE_HOST"}
            )

        with pytest.raises(EnvVarError) as exc_info:
            flatten_dataclass_fields(Config)
        assert "collision" in str(exc_info.value).lower()
        assert "DATABASE_HOST" in str(exc_info.value)


class TestLoadFromEnv:
    """Tests for loading values from environment variables."""

    def test_load_simple_values(self):
        """Test loading simple values from env vars."""

        @dataclass
        class Config:
            name: str = "default"
            count: int = 0

        environ = {
            "MYAPP_NAME": "test",
            "MYAPP_COUNT": "42",
        }

        result = load_from_env(Config, "MYAPP_", environ)
        assert result == {"name": "test", "count": 42}

    def test_load_nested_dataclass(self):
        """Test loading nested dataclass from env vars."""

        @dataclass
        class Database:
            host: str = "localhost"
            port: int = 5432

        @dataclass
        class Config:
            database: Database
            debug: bool = False

        environ = {
            "MYAPP_DATABASE_HOST": "db.example.com",
            "MYAPP_DATABASE_PORT": "3306",
            "MYAPP_DEBUG": "true",
        }

        result = load_from_env(Config, "MYAPP_", environ)
        assert result == {
            "database": {"host": "db.example.com", "port": 3306},
            "debug": True,
        }

    def test_load_partial_values(self):
        """Test loading only some values from env vars."""

        @dataclass
        class Config:
            name: str = "default"
            count: int = 0
            enabled: bool = True

        environ = {
            "MYAPP_NAME": "test",
        }

        result = load_from_env(Config, "MYAPP_", environ)
        assert result == {"name": "test"}

    def test_load_with_custom_metadata(self):
        """Test loading with custom env var names."""

        @dataclass
        class Config:
            api_key: str = field(default="", metadata={"env": "SECRET_KEY"})

        environ = {
            "MYAPP_SECRET_KEY": "secret123",
        }

        result = load_from_env(Config, "MYAPP_", environ)
        assert result == {"api_key": "secret123"}

    def test_load_with_type_error(self):
        """Test loading with type conversion error."""

        @dataclass
        class Config:
            count: int = 0

        environ = {
            "MYAPP_COUNT": "not-a-number",
        }

        with pytest.raises(EnvVarError) as exc_info:
            load_from_env(Config, "MYAPP_", environ)
        assert "MYAPP_COUNT" in str(exc_info.value)

    def test_load_complex_types(self):
        """Test loading complex types (list, dict)."""

        @dataclass
        class Config:
            tags: List[str] = field(default_factory=list)
            metadata: Dict[str, str] = field(default_factory=dict)

        environ = {
            "MYAPP_TAGS": '["tag1", "tag2", "tag3"]',
            "MYAPP_METADATA": '{"key": "value"}',
        }

        result = load_from_env(Config, "MYAPP_", environ)
        assert result == {
            "tags": ["tag1", "tag2", "tag3"],
            "metadata": {"key": "value"},
        }


class TestConfigManagerWithEnvVars:
    """Tests for ConfigManager with environment variable support."""

    def test_config_manager_disabled_by_default(self, tmp_path):
        """Test that env vars are disabled by default."""

        @dataclass
        class Config:
            name: str = "default"

        # Set env var
        os.environ["TESTAPP_NAME"] = "from-env"

        try:
            manager = ConfigManager(app_name="testapp", config_dir=tmp_path)

            # Save config
            config = Config(name="from-file")
            manager.save(config, "test.yaml")

            # Load should only use file, not env var
            loaded = manager.load(Config, "test.yaml")
            assert loaded.name == "from-file"
        finally:
            del os.environ["TESTAPP_NAME"]

    def test_config_manager_with_env_vars_enabled(self, tmp_path):
        """Test ConfigManager with env vars enabled."""

        @dataclass
        class Config:
            name: str = "default"
            count: int = 0

        # Set env vars
        os.environ["TESTAPP_NAME"] = "from-env"
        os.environ["TESTAPP_COUNT"] = "99"

        try:
            manager = ConfigManager(
                app_name="testapp",
                config_dir=tmp_path,
                use_env_vars=True,
            )

            # Save config
            config = Config(name="from-file", count=42)
            manager.save(config, "test.yaml")

            # Load should use env vars (which override file)
            loaded = manager.load(Config, "test.yaml")
            assert loaded.name == "from-env"  # From env var
            assert loaded.count == 99  # From env var
        finally:
            del os.environ["TESTAPP_NAME"]
            del os.environ["TESTAPP_COUNT"]

    def test_config_manager_env_vars_priority(self, tmp_path):
        """Test that env vars have priority over file values."""

        @dataclass
        class Config:
            setting1: str = "default"
            setting2: str = "default"

        # Set only one env var
        os.environ["TESTAPP_SETTING1"] = "from-env"

        try:
            manager = ConfigManager(
                app_name="testapp",
                config_dir=tmp_path,
                use_env_vars=True,
            )

            # Save config
            config = Config(setting1="from-file-1", setting2="from-file-2")
            manager.save(config, "test.yaml")

            # Load should use env var for setting1, file for setting2
            loaded = manager.load(Config, "test.yaml")
            assert loaded.setting1 == "from-env"
            assert loaded.setting2 == "from-file-2"
        finally:
            del os.environ["TESTAPP_SETTING1"]

    def test_config_manager_nested_with_env_vars(self, tmp_path):
        """Test nested dataclass with env vars."""

        @dataclass
        class Database:
            host: str = "localhost"
            port: int = 5432

        @dataclass
        class Config:
            database: Database
            app_name: str = "myapp"

        # Set env vars for nested fields
        os.environ["TESTAPP_DATABASE_HOST"] = "db.example.com"
        os.environ["TESTAPP_APP_NAME"] = "from-env"

        try:
            manager = ConfigManager(
                app_name="testapp",
                config_dir=tmp_path,
                use_env_vars=True,
            )

            # Save config
            config = Config(
                database=Database(host="localhost", port=5432),
                app_name="from-file",
            )
            manager.save(config, "test.yaml")

            # Load should merge nested values
            loaded = manager.load(Config, "test.yaml")
            assert loaded.database.host == "db.example.com"  # From env
            assert loaded.database.port == 5432  # From file
            assert loaded.app_name == "from-env"  # From env
        finally:
            del os.environ["TESTAPP_DATABASE_HOST"]
            del os.environ["TESTAPP_APP_NAME"]

    def test_config_manager_load_without_file(self, tmp_path):
        """Test loading with env vars when file doesn't exist."""

        @dataclass
        class Config:
            name: str = "default"

        os.environ["TESTAPP_NAME"] = "from-env"

        try:
            manager = ConfigManager(
                app_name="testapp",
                config_dir=tmp_path,
                use_env_vars=True,
            )

            # Load without file should work with env vars
            loaded = manager.load(Config, "nonexistent.yaml")
            assert loaded.name == "from-env"
        finally:
            del os.environ["TESTAPP_NAME"]

    def test_config_manager_optional_nested_auto_instantiation(self, tmp_path):
        """Test auto-instantiation of Optional nested dataclass."""

        @dataclass
        class Database:
            host: str = "localhost"
            port: int = 5432

        @dataclass
        class Config:
            database: Optional[Database] = None
            debug: bool = False

        # Set env var for nested field
        os.environ["TESTAPP_DATABASE_HOST"] = "db.example.com"
        os.environ["TESTAPP_DEBUG"] = "true"

        try:
            manager = ConfigManager(
                app_name="testapp",
                config_dir=tmp_path,
                use_env_vars=True,
            )

            # Save config with database=None
            config = Config(database=None, debug=False)
            manager.save(config, "test.yaml")

            # Load should auto-instantiate Database with env values
            loaded = manager.load(Config, "test.yaml")
            assert loaded.database is not None
            assert loaded.database.host == "db.example.com"
            assert loaded.database.port == 5432  # Default value
            assert loaded.debug is True
        finally:
            del os.environ["TESTAPP_DATABASE_HOST"]
            del os.environ["TESTAPP_DEBUG"]


class TestDataManagerWithEnvVars:
    """Tests for DataManager with environment variable support."""

    def test_data_manager_with_env_vars(self, tmp_path):
        """Test DataManager with env vars enabled."""

        @dataclass
        class UserData:
            username: str = "user"
            score: int = 0

        os.environ["TESTAPP_USERNAME"] = "alice"
        os.environ["TESTAPP_SCORE"] = "100"

        try:
            manager = DataManager(
                app_name="testapp",
                data_dir=tmp_path,
                use_env_vars=True,
            )

            # Save data
            data = UserData(username="bob", score=50)
            manager.save(data, "user.yaml")

            # Load should use env vars
            loaded = manager.load(UserData, "user.yaml")
            assert loaded.username == "alice"
            assert loaded.score == 100
        finally:
            del os.environ["TESTAPP_USERNAME"]
            del os.environ["TESTAPP_SCORE"]


class TestNameCollisionDetection:
    """Tests for name collision detection."""

    def test_detect_collision_in_flat_vs_nested(self):
        """Test detection of collision between flat and nested field names."""

        @dataclass
        class Config:
            database_host: str = "localhost"

        @dataclass
        class App:
            database: Config = field(default_factory=Config)
            # This creates: database.database_host -> DATABASE_DATABASE_HOST
            # If we had database_database_host field, it would collide

        # This should work fine (no collision)
        result = flatten_dataclass_fields(App)
        assert "DATABASE_DATABASE_HOST" in result

    def test_collision_with_custom_metadata(self):
        """Test collision detection with custom metadata."""

        @dataclass
        class Config:
            field1: str = field(default="", metadata={"env": "CUSTOM"})
            field2: str = field(default="", metadata={"env": "CUSTOM"})

        with pytest.raises(EnvVarError) as exc_info:
            flatten_dataclass_fields(Config)
        assert "collision" in str(exc_info.value).lower()
