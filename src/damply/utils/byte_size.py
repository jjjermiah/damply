class ByteSize(int):
    """A class that represents a size in bytes and provides readable representations in various units."""

    _KB = 1024
    _suffixes: list[str] = ["B", "KB", "MB", "GB", "TB"]

    def __new__(cls, value):
        """Create a new instance of the ByteSize class."""
        return super().__new__(cls, value)

    def __init__(self, value):
        """Initialize the ByteSize instance with various unit conversions."""
        self.bytes = self.B = int(value)
        self.kilobytes = self.KB = self.bytes / self._KB
        self.megabytes = self.MB = self.bytes / self._KB**2
        self.gigabytes = self.GB = self.bytes / self._KB**3
        self.terabytes = self.TB = self.bytes / self._KB**4
        self.readable = self._get_readable()
        super().__init__()

    def _get_readable(self):
        """
        Determine the most appropriate readable representation.

        """
        first, *suffixes = self._suffixes
        suffix = next(
            (suffix for suffix in suffixes if 1 <= getattr(self, suffix) <= self._KB),
            first,
        )
        return suffix, getattr(self, suffix)

    def __str__(self):
        """Return a formatted string representation of the ByteSize instance."""
        return self.__format__(".2f")

    def __repr__(self):
        """Return the official string representation of the ByteSize instance."""
        return f"{self.__class__.__name__}({int(self)})"

    def __format__(self, format_spec):
        """Return a formatted string based on the specified format."""
        suffix, val = self.readable
        return f"{val:{format_spec}} {suffix}"

    def __sub__(self, other):
        """Subtract another ByteSize or int from this ByteSize."""
        return self.__class__(super().__sub__(other))

    def __add__(self, other):
        """Add another ByteSize or int to this ByteSize."""
        return self.__class__(super().__add__(other))

    def __mul__(self, other):
        """Multiply this ByteSize by another ByteSize or int."""
        return self.__class__(super().__mul__(other))

    def __rsub__(self, other):
        """Subtract this ByteSize from another ByteSize or int (reversed)."""
        return self.__class__(super().__rsub__(other))

    def __radd__(self, other):
        """Add this ByteSize to another ByteSize or int (reversed)."""
        return self.__class__(super().__radd__(other))

    def __rmul__(self, other):
        """Multiply this ByteSize by another ByteSize or int (reversed)."""
        return self.__class__(super().__rmul__(other))
