"""Unit tests for the Serializer class."""

import json
from dataclasses import dataclass

import pytest

from dataconfy import InvalidDataclassError, UnsupportedFormatError
from dataconfy.serializers import Serializer


@dataclass
class SampleDataClass:
    """Test dataclass for serialization tests."""

    name: str = "test"
    value: int = 42


class TestSerializer:
    """Test suite for Serializer class."""

    def test_get_format_from_yaml(self):
        """Test format detection for .yaml files."""
        assert Serializer.get_format_from_filename("file.yaml") == "yaml"

    def test_get_format_from_yml(self):
        """Test format detection for .yml files."""
        assert Serializer.get_format_from_filename("file.yml") == "yaml"

    def test_get_format_from_json(self):
        """Test format detection for .json files."""
        assert Serializer.get_format_from_filename("file.json") == "json"

    def test_get_format_unsupported(self):
        """Test error for unsupported format."""
        with pytest.raises(UnsupportedFormatError):
            Serializer.get_format_from_filename("file.txt")

    def test_serialize_yaml(self):
        """Test YAML serialization."""
        obj = SampleDataClass(name="test_yaml", value=100)
        result = Serializer.serialize(obj, "yaml")

        assert "name: test_yaml" in result
        assert "value: 100" in result
        assert isinstance(result, str)

    def test_serialize_json(self):
        """Test JSON serialization."""
        obj = SampleDataClass(name="test_json", value=200)
        result = Serializer.serialize(obj, "json")

        data = json.loads(result)
        assert data["name"] == "test_json"
        assert data["value"] == 200

    def test_serialize_non_dataclass(self):
        """Test error when serializing non-dataclass."""
        with pytest.raises(InvalidDataclassError):
            Serializer.serialize({"not": "dataclass"}, "yaml")

    def test_serialize_dataclass_type(self):
        """Test error when serializing dataclass type instead of instance."""
        with pytest.raises(InvalidDataclassError):
            Serializer.serialize(SampleDataClass, "yaml")

    def test_serialize_unsupported_format(self):
        """Test error for unsupported serialization format."""
        obj = SampleDataClass()
        with pytest.raises(UnsupportedFormatError):
            Serializer.serialize(obj, "xml")

    def test_deserialize_yaml(self):
        """Test YAML deserialization."""
        content = "name: test_yaml\nvalue: 300\n"
        result = Serializer.deserialize(content, SampleDataClass, "yaml")

        assert result.name == "test_yaml"
        assert result.value == 300

    def test_deserialize_json(self):
        """Test JSON deserialization."""
        content = '{"name": "test_json", "value": 400}'
        result = Serializer.deserialize(content, SampleDataClass, "json")

        assert result.name == "test_json"
        assert result.value == 400

    def test_deserialize_empty_yaml(self):
        """Test deserialization of empty YAML content."""
        content = ""
        result = Serializer.deserialize(content, SampleDataClass, "yaml")

        # Should use default values
        assert result.name == "test"
        assert result.value == 42

    def test_deserialize_non_dataclass(self):
        """Test error when deserializing to non-dataclass."""
        content = "name: test\nvalue: 100\n"
        with pytest.raises(InvalidDataclassError):
            Serializer.deserialize(content, dict, "yaml")

    def test_deserialize_unsupported_format(self):
        """Test error for unsupported deserialization format."""
        content = "some content"
        with pytest.raises(UnsupportedFormatError):
            Serializer.deserialize(content, SampleDataClass, "xml")

    def test_roundtrip_yaml(self):
        """Test YAML serialize/deserialize roundtrip."""
        original = SampleDataClass(name="roundtrip", value=999)

        serialized = Serializer.serialize(original, "yaml")
        deserialized = Serializer.deserialize(serialized, SampleDataClass, "yaml")

        assert deserialized.name == original.name
        assert deserialized.value == original.value

    def test_roundtrip_json(self):
        """Test JSON serialize/deserialize roundtrip."""
        original = SampleDataClass(name="roundtrip", value=888)

        serialized = Serializer.serialize(original, "json")
        deserialized = Serializer.deserialize(serialized, SampleDataClass, "json")

        assert deserialized.name == original.name
        assert deserialized.value == original.value
