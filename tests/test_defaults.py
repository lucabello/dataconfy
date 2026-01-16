"""Tests for default filename behavior."""

from dataclasses import dataclass

from dataconfy import ConfigManager, DataManager


@dataclass
class TestConfig:
    """Test configuration dataclass."""

    setting: str = "default"
    value: int = 42


class TestDefaultFilenames:
    """Test default filename behavior."""

    def test_config_default_filename_save(self, tmp_path):
        """Test that Config saves to config.yaml by default."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        test_config = TestConfig(setting="test", value=100)

        # Save without specifying filename
        filepath = config.save(test_config)

        assert filepath == tmp_path / "config.yaml"
        assert filepath.exists()

    def test_config_default_filename_load(self, tmp_path):
        """Test that Config loads from config.yaml by default."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        test_config = TestConfig(setting="loaded", value=200)

        # Save with default filename
        config.save(test_config)

        # Load without specifying filename
        loaded = config.load(TestConfig)

        assert loaded.setting == "loaded"
        assert loaded.value == 200

    def test_config_explicit_filename_overrides_default(self, tmp_path):
        """Test that explicit filename overrides default."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        test_config = TestConfig(setting="custom", value=300)

        # Save with explicit filename
        filepath = config.save(test_config, "custom.yaml")

        assert filepath == tmp_path / "custom.yaml"
        assert filepath.exists()
        assert not (tmp_path / "config.yaml").exists()

    def test_data_default_filename_save(self, tmp_path):
        """Test that Data saves to data.yaml by default."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        test_data = TestConfig(setting="data_test", value=400)

        # Save without specifying filename
        filepath = data.save(test_data)

        assert filepath == tmp_path / "data.yaml"
        assert filepath.exists()

    def test_data_default_filename_load(self, tmp_path):
        """Test that Data loads from data.yaml by default."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        test_data = TestConfig(setting="data_loaded", value=500)

        # Save with default filename
        data.save(test_data)

        # Load without specifying filename
        loaded = data.load(TestConfig)

        assert loaded.setting == "data_loaded"
        assert loaded.value == 500

    def test_data_explicit_filename_overrides_default(self, tmp_path):
        """Test that explicit filename overrides default for Data."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        test_data = TestConfig(setting="custom_data", value=600)

        # Save with explicit filename
        filepath = data.save(test_data, "mydata.yaml")

        assert filepath == tmp_path / "mydata.yaml"
        assert filepath.exists()
        assert not (tmp_path / "data.yaml").exists()

    def test_config_and_data_different_defaults(self, tmp_path):
        """Test that Config and Data use different default filenames."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        config_obj = TestConfig(setting="config", value=100)
        data_obj = TestConfig(setting="data", value=200)

        # Save both with defaults
        config_path = config.save(config_obj)
        data_path = data.save(data_obj)

        # Should be different files
        assert config_path == tmp_path / "config.yaml"
        assert data_path == tmp_path / "data.yaml"

        # Load both
        loaded_config = config.load(TestConfig)
        loaded_data = data.load(TestConfig)

        assert loaded_config.setting == "config"
        assert loaded_data.setting == "data"

    def test_exists_with_default_filename(self, tmp_path):
        """Test exists() method with default filename."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        # Should not exist initially
        assert not config.exists("config.yaml")

        # Save with default
        config.save(TestConfig())

        # Should exist now
        assert config.exists("config.yaml")

    def test_get_path_with_default_filename(self, tmp_path):
        """Test get_path() returns correct path for default filename."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        path = config.get_path("config.yaml")

        assert path == tmp_path / "config.yaml"
