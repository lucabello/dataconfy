"""Tests for default filename usage in all methods."""

from dataclasses import dataclass

from dataconfy import ConfigManager, DataManager


@dataclass
class SampleData:
    """Test dataclass."""

    value: int = 42


class TestDefaultFilenameInAllMethods:
    """Test that default filename works in all methods."""

    def test_config_exists_with_default(self, tmp_path):
        """Test exists() with default filename."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        # Should not exist initially
        assert not config.exists()

        # Save with default
        config.save(SampleData())

        # Should exist now using default
        assert config.exists()

    def test_config_get_path_with_default(self, tmp_path):
        """Test get_path() with default filename."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        # Get path with default
        path = config.get_path()

        assert path == tmp_path / "config.yaml"

    def test_data_exists_with_default(self, tmp_path):
        """Test exists() with default filename for Data."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        # Should not exist initially
        assert not data.exists()

        # Save with default
        data.save(SampleData())

        # Should exist now using default
        assert data.exists()

    def test_data_get_path_with_default(self, tmp_path):
        """Test get_path() with default filename for Data."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        # Get path with default
        path = data.get_path()

        assert path == tmp_path / "data.yaml"

    def test_exists_explicit_filename_still_works(self, tmp_path):
        """Test that explicit filename still works with exists()."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        config.save(SampleData(), "custom.yaml")

        assert config.exists("custom.yaml")
        assert not config.exists("other.yaml")
        assert not config.exists()  # default doesn't exist

    def test_get_path_explicit_filename_still_works(self, tmp_path):
        """Test that explicit filename still works with get_path()."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)

        path = config.get_path("custom.yaml")

        assert path == tmp_path / "custom.yaml"

    def test_workflow_all_defaults(self, tmp_path):
        """Test complete workflow using only defaults."""
        config = ConfigManager(app_name="testapp", config_dir=tmp_path)
        test_data = SampleData(value=100)

        # Check doesn't exist
        assert not config.exists()

        # Get default path
        expected_path = config.get_path()
        assert expected_path == tmp_path / "config.yaml"

        # Save with default
        saved_path = config.save(test_data)
        assert saved_path == expected_path

        # Check exists with default
        assert config.exists()

        # Load with default
        loaded = config.load(SampleData)
        assert loaded.value == 100
