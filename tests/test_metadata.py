import pytest
from pathlib import Path
from damply.metadata import DMPMetadata
import datetime  # Add this import


def test_from_path_valid_readme():
    readme_path = Path("tests/examples/simple/README_simple.md").resolve()
    metadata = DMPMetadata.from_path(readme_path)
    assert metadata.fields["OWNER"] == "Jermiah Joseph"
    assert metadata.fields["DATE"] == "2024-05-30"
    assert metadata.fields["DESC"] == "A simple readme."

def test_from_path_invalid_readme():
    readme_path = Path("tests/examples/invalid_.md").resolve()
    with pytest.raises(ValueError):
        DMPMetadata.from_path(readme_path)


def test_log_change():
    metadata = DMPMetadata()
    metadata.log_change("Added a log entry.")
    metadata.log_change("Added another log entry.")
    # assert that the format is of:
    # timestamp1: Added a log entry.
    # timestamp2: Added another log entry.
    for log in metadata.logs:
        timestamp, message = log.split(": ")
        datetime.datetime.strptime(timestamp, "%Y-%m-%d %H:%M")
        assert message.startswith("Added")


def test_write_to_file():
    metadata = DMPMetadata()
    metadata["FIELD1"] = "value1"
    metadata["FIELD2"] = "value2"
    metadata.content = "Lorem ipsum dolor sit amet, consectetur adipiscing elit."
    metadata.log_change("Added a log entry.")
    metadata.log_change("Added another log entry.")

    tmpdirname = "tests/examples/"

    newpath = Path(tmpdirname) / "test.dmp"

    # create the file with all permissions
    newpath.touch()
    
    metadata.write_to_file(newpath)

    with newpath.open(mode="r") as file:
        content = file.read()

    for i, line in enumerate(content.split("\n")):
        if i == 0:
            assert line == "#FIELD1: value1"
        if i == 2:
            assert line == "#FIELD2: value2"
        if i == 5:
            assert line == "Lorem ipsum dolor sit amet, consectetur adipiscing elit."