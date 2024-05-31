import pytest
from damply.utils.byte_size import ByteSize


def test_byte_size_creation():
    bs = ByteSize(1024)
    assert bs.bytes == 1024
    assert bs.kilobytes == 1.0
    assert bs.megabytes == 0.0009765625
    assert bs.gigabytes == 9.5367431640625e-07
    assert bs.terabytes == 9.313225746154785e-10
    assert bs.readable == ("KB", 1.0)


def test_byte_size_representation():
    bs = ByteSize(2048)
    assert str(bs) == "2.00 KB"
    assert repr(bs) == "ByteSize(2048)"


def test_byte_size_arithmetic():
    bs1 = ByteSize(1024)
    bs2 = ByteSize(512)
    bs3 = bs1 + bs2
    assert bs3.bytes == 1536
    assert bs3.kilobytes == 1.5
    assert bs3.megabytes == 0.00146484375
    assert bs3.gigabytes == 1.430511474609375e-06
    assert bs3.terabytes == 1.3969838619232178e-09
    assert bs3.readable == ("KB", 1.5)

    bs4 = bs3 - bs1
    assert bs4.bytes == 512
    assert bs4.kilobytes == 0.5
    assert bs4.megabytes == 0.00048828125
    assert bs4.gigabytes == 4.76837158203125e-07
    assert bs4.readable == ("B", 512)

    bs5 = bs4 * 2
    assert bs5.bytes == 1024
    assert bs5.kilobytes == 1.0
    assert bs5.megabytes == 0.0009765625
    assert bs5.gigabytes == 9.5367431640625e-07
    assert bs5.readable == ("KB", 1.0)


if __name__ == "__main__":
    pytest.main()