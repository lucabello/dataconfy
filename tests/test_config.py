"""Tests for dataconfy configuration management."""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest

from dataconfy import ConfigManager, InvalidDataclassError, UnsupportedFormatError


@dataclass
class SampleConfig:
    """Sample configuration dataclass for testing."""

    name: str = "test"
    value: int = 42
    enabled: bool = True


@dataclass
class NestedConfig:
    """Configuration with nested data."""

    title: str = "Nested"
    settings: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.settings is None:
            self.settings = {"key": "value"}


class TestConfig:
    """Test suite for Config class."""

    def test_init_with_app_name(self):
        """Test Config initialization with app name."""
        config = ConfigManager(app_name="testapp")
        assert config.app_name == "testapp"
        assert "testapp" in str(config.config_dir)

    def test_init_with_custom_dirs(self, tmp_path):
        """Test Config initialization with custom directory."""
        config_dir = tmp_path / "config"

        config = ConfigManager(app_name="testapp", config_dir=config_dir)

        assert config.config_dir == config_dir

    def test_save_and_load_yaml_config(self, tmp_path):
        """Test saving and loading config in YAML format."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="yaml_test", value=100)

        # Save
        filepath = config.save(sample, "test.yaml")
        assert filepath.exists()
        assert filepath.suffix == ".yaml"

        # Load
        loaded = config.load(SampleConfig, "test.yaml")
        assert loaded.name == "yaml_test"
        assert loaded.value == 100
        assert loaded.enabled is True

    def test_save_and_load_yml_config(self, tmp_path):
        """Test saving and loading config with .yml extension."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="yml_test", value=200)

        # Save
        filepath = config.save(sample, "test.yml")
        assert filepath.exists()

        # Load
        loaded = config.load(SampleConfig, "test.yml")
        assert loaded.name == "yml_test"
        assert loaded.value == 200

    def test_save_and_load_json_config(self, tmp_path):
        """Test saving and loading config in JSON format."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="json_test", value=300, enabled=False)

        # Save
        filepath = config.save(sample, "test.json")
        assert filepath.exists()
        assert filepath.suffix == ".json"

        # Verify JSON format
        with open(filepath) as f:
            data = json.load(f)
        assert data["name"] == "json_test"
        assert data["value"] == 300

        # Load
        loaded = config.load(SampleConfig, "test.json")
        assert loaded.name == "json_test"
        assert loaded.value == 300
        assert loaded.enabled is False

    def test_get_path(self, tmp_path):
        """Test getting full path for a filename."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        path = config.get_path("settings.yaml")
        assert path == tmp_path / "settings.yaml"

    def test_format_override(self, tmp_path):
        """Test format override parameter."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="override_test")

        # Save as JSON even though extension is .txt
        config.save(sample, "test.txt", format="json")

        # Load with format override
        loaded = config.load(SampleConfig, "test.txt", format="json")
        assert loaded.name == "override_test"

    def test_nested_config(self, tmp_path):
        """Test configuration with nested data structures."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        nested = NestedConfig(title="Test Nested", settings={"debug": True, "port": 8080})

        # Save and load
        config.save(nested, "nested.yaml")
        loaded = config.load(NestedConfig, "nested.yaml")

        assert loaded.title == "Test Nested"
        assert loaded.settings["debug"] is True
        assert loaded.settings["port"] == 8080

    def test_invalid_dataclass_save(self, tmp_path):
        """Test error when trying to save non-dataclass."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        with pytest.raises(InvalidDataclassError):
            config.save({"not": "dataclass"}, "test.yaml")

    def test_invalid_dataclass_load(self, tmp_path):
        """Test error when trying to load into non-dataclass."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        # Create a valid file first
        sample = SampleConfig()
        config.save(sample, "test.yaml")

        # Try to load into non-dataclass
        with pytest.raises(InvalidDataclassError):
            config.load(dict, "test.yaml")

    def test_unsupported_format(self, tmp_path):
        """Test error with unsupported file format."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig()

        with pytest.raises(UnsupportedFormatError):
            config.save(sample, "test.txt")

    def test_load_nonexistent_file(self, tmp_path):
        """Test error when loading nonexistent file."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            config.load(SampleConfig, "nonexistent.yaml")

    def test_config_file_exists(self, tmp_path):
        """Test checking if config file exists."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig()

        assert not config.exists("test.yaml")

        config.save(sample, "test.yaml")

        assert config.exists("test.yaml")

    def test_base_dir_property(self, tmp_path):
        """Test base_dir property alias."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        assert config.base_dir == tmp_path
        assert config.config_dir == config.base_dir

    def test_directories_created_automatically(self, tmp_path):
        """Test that directories are created automatically when saving."""
        base_dir = tmp_path / "nonexistent"
        config = ConfigManager(app_name="testapp", config_dir=base_dir / "config")

        assert not config.config_dir.exists()

        sample = SampleConfig()
        config.save(sample, "test.yaml")

        assert config.config_dir.exists()
        assert (config.config_dir / "test.yaml").exists()

    def test_yaml_format_readable(self, tmp_path):
        """Test that saved YAML is human-readable."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="readable", value=123)

        filepath = config.save(sample, "test.yaml")
        content = filepath.read_text()

        # Check that it's readable YAML (not flow style)
        assert "name: readable" in content
        assert "value: 123" in content
        assert "enabled: true" in content

    def test_json_format_indented(self, tmp_path):
        """Test that saved JSON is properly indented."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="indented", value=456)

        filepath = config.save(sample, "test.json")
        content = filepath.read_text()

        # Check that it's indented (contains newlines)
        assert "\n" in content
        assert '"name": "indented"' in content

    def test_empty_yaml_file(self, tmp_path):
        """Test loading from empty YAML file."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        # Create empty file
        filepath = config.config_dir
        filepath.mkdir(parents=True, exist_ok=True)
        (filepath / "empty.yaml").write_text("")

        # Should handle gracefully with defaults
        loaded = config.load(SampleConfig, "empty.yaml")
        assert loaded.name == "test"  # default value
        assert loaded.value == 42  # default value


class TestMultipleApps:
    """Test handling multiple applications."""

    def test_separate_app_directories(self, tmp_path):
        """Test that different apps get separate directories."""
        config1 = ConfigManager(app_name="app1", config_dir=tmp_path / "app1")
        config2 = ConfigManager(app_name="app2", config_dir=tmp_path / "app2")

        sample1 = SampleConfig(name="app1_config")
        sample2 = SampleConfig(name="app2_config")

        config1.save(sample1, "settings.yaml")
        config2.save(sample2, "settings.yaml")

        loaded1 = config1.load(SampleConfig, "settings.yaml")
        loaded2 = config2.load(SampleConfig, "settings.yaml")

        assert loaded1.name == "app1_config"
        assert loaded2.name == "app2_config"
