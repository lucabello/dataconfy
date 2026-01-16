"""Tests for dataconfy configuration management."""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest

from dataconfy import Config, InvalidDataclassError, UnsupportedFormatError


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
        config = Config(app_name="testapp")
        assert config.app_name == "testapp"
        assert "testapp" in str(config.config_dir)
        assert "testapp" in str(config.data_dir)

    def test_init_with_custom_dirs(self, tmp_path):
        """Test Config initialization with custom directories."""
        config_dir = tmp_path / "config"
        data_dir = tmp_path / "data"

        config = Config(app_name="testapp", config_dir=config_dir, data_dir=data_dir)

        assert config.config_dir == config_dir
        assert config.data_dir == data_dir

    def test_save_and_load_yaml_config(self, tmp_path):
        """Test saving and loading config in YAML format."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="yaml_test", value=100)

        # Save
        filepath = config.save_config(sample, "test.yaml")
        assert filepath.exists()
        assert filepath.suffix == ".yaml"

        # Load
        loaded = config.load_config(SampleConfig, "test.yaml")
        assert loaded.name == "yaml_test"
        assert loaded.value == 100
        assert loaded.enabled is True

    def test_save_and_load_yml_config(self, tmp_path):
        """Test saving and loading config with .yml extension."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="yml_test", value=200)

        # Save
        filepath = config.save_config(sample, "test.yml")
        assert filepath.exists()

        # Load
        loaded = config.load_config(SampleConfig, "test.yml")
        assert loaded.name == "yml_test"
        assert loaded.value == 200

    def test_save_and_load_json_config(self, tmp_path):
        """Test saving and loading config in JSON format."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="json_test", value=300, enabled=False)

        # Save
        filepath = config.save_config(sample, "test.json")
        assert filepath.exists()
        assert filepath.suffix == ".json"

        # Verify JSON format
        with open(filepath) as f:
            data = json.load(f)
        assert data["name"] == "json_test"
        assert data["value"] == 300

        # Load
        loaded = config.load_config(SampleConfig, "test.json")
        assert loaded.name == "json_test"
        assert loaded.value == 300
        assert loaded.enabled is False

    def test_save_and_load_data(self, tmp_path):
        """Test saving and loading data files."""
        config = Config(app_name="testapp", data_dir=tmp_path)
        sample = SampleConfig(name="data_test", value=400)

        # Save data
        filepath = config.save_data(sample, "data.yaml")
        assert filepath.exists()

        # Load data
        loaded = config.load_data(SampleConfig, "data.yaml")
        assert loaded.name == "data_test"
        assert loaded.value == 400

    def test_format_override(self, tmp_path):
        """Test format override parameter."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="override_test")

        # Save as JSON even though extension is .txt
        config.save_config(sample, "test.txt", format="json")

        # Load with format override
        loaded = config.load_config(SampleConfig, "test.txt", format="json")
        assert loaded.name == "override_test"

    def test_nested_config(self, tmp_path):
        """Test configuration with nested data structures."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        nested = NestedConfig(title="Test Nested", settings={"debug": True, "port": 8080})

        # Save and load
        config.save_config(nested, "nested.yaml")
        loaded = config.load_config(NestedConfig, "nested.yaml")

        assert loaded.title == "Test Nested"
        assert loaded.settings["debug"] is True
        assert loaded.settings["port"] == 8080

    def test_invalid_dataclass_save(self, tmp_path):
        """Test error when trying to save non-dataclass."""
        config = Config(app_name="testapp", config_dir=tmp_path)

        with pytest.raises(InvalidDataclassError):
            config.save_config({"not": "dataclass"}, "test.yaml")

    def test_invalid_dataclass_load(self, tmp_path):
        """Test error when trying to load into non-dataclass."""
        config = Config(app_name="testapp", config_dir=tmp_path)

        # Create a valid file first
        sample = SampleConfig()
        config.save_config(sample, "test.yaml")

        # Try to load into non-dataclass
        with pytest.raises(InvalidDataclassError):
            config.load_config(dict, "test.yaml")

    def test_unsupported_format(self, tmp_path):
        """Test error with unsupported file format."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig()

        with pytest.raises(UnsupportedFormatError):
            config.save_config(sample, "test.txt")

    def test_load_nonexistent_file(self, tmp_path):
        """Test error when loading nonexistent file."""
        config = Config(app_name="testapp", config_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            config.load_config(SampleConfig, "nonexistent.yaml")

    def test_config_file_exists(self, tmp_path):
        """Test checking if config file exists."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig()

        assert not config.config_file_exists("test.yaml")

        config.save_config(sample, "test.yaml")

        assert config.config_file_exists("test.yaml")

    def test_data_file_exists(self, tmp_path):
        """Test checking if data file exists."""
        config = Config(app_name="testapp", data_dir=tmp_path)
        sample = SampleConfig()

        assert not config.data_file_exists("test.yaml")

        config.save_data(sample, "test.yaml")

        assert config.data_file_exists("test.yaml")

    def test_directories_created_automatically(self, tmp_path):
        """Test that directories are created automatically when saving."""
        base_dir = tmp_path / "nonexistent"
        config = Config(app_name="testapp", config_dir=base_dir / "config")

        assert not config.config_dir.exists()

        sample = SampleConfig()
        config.save_config(sample, "test.yaml")

        assert config.config_dir.exists()
        assert (config.config_dir / "test.yaml").exists()

    def test_yaml_format_readable(self, tmp_path):
        """Test that saved YAML is human-readable."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="readable", value=123)

        filepath = config.save_config(sample, "test.yaml")
        content = filepath.read_text()

        # Check that it's readable YAML (not flow style)
        assert "name: readable" in content
        assert "value: 123" in content
        assert "enabled: true" in content

    def test_json_format_indented(self, tmp_path):
        """Test that saved JSON is properly indented."""
        config = Config(app_name="testapp", config_dir=tmp_path)
        sample = SampleConfig(name="indented", value=456)

        filepath = config.save_config(sample, "test.json")
        content = filepath.read_text()

        # Check that it's indented (contains newlines)
        assert "\n" in content
        assert '"name": "indented"' in content

    def test_empty_yaml_file(self, tmp_path):
        """Test loading from empty YAML file."""
        config = Config(app_name="testapp", config_dir=tmp_path)

        # Create empty file
        filepath = config.config_dir
        filepath.mkdir(parents=True, exist_ok=True)
        (filepath / "empty.yaml").write_text("")

        # Should handle gracefully with defaults
        loaded = config.load_config(SampleConfig, "empty.yaml")
        assert loaded.name == "test"  # default value
        assert loaded.value == 42  # default value


class TestMultipleApps:
    """Test handling multiple applications."""

    def test_separate_app_directories(self, tmp_path):
        """Test that different apps get separate directories."""
        config1 = Config(app_name="app1", config_dir=tmp_path / "app1")
        config2 = Config(app_name="app2", config_dir=tmp_path / "app2")

        sample1 = SampleConfig(name="app1_config")
        sample2 = SampleConfig(name="app2_config")

        config1.save_config(sample1, "settings.yaml")
        config2.save_config(sample2, "settings.yaml")

        loaded1 = config1.load_config(SampleConfig, "settings.yaml")
        loaded2 = config2.load_config(SampleConfig, "settings.yaml")

        assert loaded1.name == "app1_config"
        assert loaded2.name == "app2_config"
