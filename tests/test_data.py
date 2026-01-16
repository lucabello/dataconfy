"""Tests for dataconfy Data class."""

import json
from dataclasses import dataclass
from typing import Any, Dict, Optional

import pytest

from dataconfy import DataManager, InvalidDataclassError, UnsupportedFormatError


@dataclass
class UserData:
    """Sample user data for testing."""

    username: str = "user"
    score: int = 0
    level: int = 1


@dataclass
class GameProgress:
    """Game progress data."""

    current_level: int = 1
    achievements: Optional[Dict[str, Any]] = None

    def __post_init__(self):
        if self.achievements is None:
            self.achievements = {}


class TestData:
    """Test suite for Data class."""

    def test_init_with_app_name(self):
        """Test Data initialization with app name."""
        data = DataManager(app_name="testapp")
        assert data.app_name == "testapp"
        assert "testapp" in str(data.data_dir)

    def test_init_with_custom_dir(self, tmp_path):
        """Test Data initialization with custom directory."""
        data_dir = tmp_path / "data"

        data = DataManager(app_name="testapp", data_dir=data_dir)

        assert data.data_dir == data_dir

    def test_save_and_load_yaml(self, tmp_path):
        """Test saving and loading data in YAML format."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        user = UserData(username="alice", score=100, level=5)

        # Save
        filepath = data.save(user, "user.yaml")
        assert filepath.exists()
        assert filepath.suffix == ".yaml"

        # Load
        loaded = data.load(UserData, "user.yaml")
        assert loaded.username == "alice"
        assert loaded.score == 100
        assert loaded.level == 5

    def test_save_and_load_json(self, tmp_path):
        """Test saving and loading data in JSON format."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        user = UserData(username="bob", score=200, level=10)

        # Save
        filepath = data.save(user, "user.json")
        assert filepath.exists()

        # Verify JSON format
        with open(filepath) as f:
            json_data = json.load(f)
        assert json_data["username"] == "bob"
        assert json_data["score"] == 200

        # Load
        loaded = data.load(UserData, "user.json")
        assert loaded.username == "bob"
        assert loaded.score == 200

    def test_format_override(self, tmp_path):
        """Test format override parameter."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        user = UserData(username="charlie")

        # Save as JSON with custom extension
        data.save(user, "user.dat", format="json")

        # Load with format override
        loaded = data.load(UserData, "user.dat", format="json")
        assert loaded.username == "charlie"

    def test_nested_data(self, tmp_path):
        """Test data with nested structures."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        progress = GameProgress(
            current_level=5, achievements={"first_win": True, "high_score": 1000}
        )

        # Save and load
        data.save(progress, "progress.yaml")
        loaded = data.load(GameProgress, "progress.yaml")

        assert loaded.current_level == 5
        assert loaded.achievements["first_win"] is True
        assert loaded.achievements["high_score"] == 1000

    def test_exists(self, tmp_path):
        """Test checking if data file exists."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        user = UserData()

        assert not data.exists("user.yaml")

        data.save(user, "user.yaml")

        assert data.exists("user.yaml")

    def test_get_path(self, tmp_path):
        """Test getting full path for a filename."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        path = data.get_path("data.yaml")
        assert path == tmp_path / "data.yaml"

    def test_base_dir_property(self, tmp_path):
        """Test base_dir property alias."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        assert data.base_dir == tmp_path
        assert data.data_dir == data.base_dir

    def test_directories_created_automatically(self, tmp_path):
        """Test that directories are created automatically when saving."""
        base_dir = tmp_path / "nonexistent"
        data = DataManager(app_name="testapp", data_dir=base_dir / "data")

        assert not data.data_dir.exists()

        user = UserData()
        data.save(user, "user.yaml")

        assert data.data_dir.exists()
        assert (data.data_dir / "user.yaml").exists()

    def test_invalid_dataclass_save(self, tmp_path):
        """Test error when trying to save non-dataclass."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        with pytest.raises(InvalidDataclassError):
            data.save({"not": "dataclass"}, "test.yaml")

    def test_invalid_dataclass_load(self, tmp_path):
        """Test error when trying to load into non-dataclass."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        # Create a valid file first
        user = UserData()
        data.save(user, "test.yaml")

        # Try to load into non-dataclass
        with pytest.raises(InvalidDataclassError):
            data.load(dict, "test.yaml")

    def test_unsupported_format(self, tmp_path):
        """Test error with unsupported file format."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)
        user = UserData()

        with pytest.raises(UnsupportedFormatError):
            data.save(user, "test.txt")

    def test_load_nonexistent_file(self, tmp_path):
        """Test error when loading nonexistent file."""
        data = DataManager(app_name="testapp", data_dir=tmp_path)

        with pytest.raises(FileNotFoundError):
            data.load(UserData, "nonexistent.yaml")


class TestConfigAndDataSeparation:
    """Test that Config and Data work independently."""

    def test_separate_directories(self, tmp_path):
        """Test that Config and Data use separate directories."""
        from dataconfy import ConfigManager

        config = ConfigManager(app_name="testapp", config_dir=tmp_path / "config")
        data = DataManager(app_name="testapp", data_dir=tmp_path / "data")

        config_data = UserData(username="config_user")
        data_data = UserData(username="data_user")

        config.save(config_data, "user.yaml")
        data.save(data_data, "user.yaml")

        loaded_config = config.load(UserData, "user.yaml")
        loaded_data = data.load(UserData, "user.yaml")

        assert loaded_config.username == "config_user"
        assert loaded_data.username == "data_user"
