import pytest
from damply.cli import hello


def test_say_hello():
    assert hello() == "Hello, World!"
    

if __name__ == "__main__":
    pytest.main()