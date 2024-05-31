import datetime  # Add this import
import re
import stat
from dataclasses import dataclass, field
from pathlib import Path
from typing import Type

from rich import print
import rich.repr

def is_file_writable(file_path: Path) -> bool:
    import os

    return file_path.exists() and os.access(file_path, os.W_OK)


@dataclass
class DMPMetadata:
    fields: dict = field(default_factory=dict)
    content: str = field(default_factory=str, repr=False)
    path: Path = field(default=Path().cwd())
    permissions: str = field(default="---------")
    logs: list = field(default_factory=list, repr=True)

    @classmethod
    def from_path(cls: Type["DMPMetadata"], path: Path) -> "DMPMetadata":
        if "README" not in path.stem.upper():
            raise ValueError("The file is not a README file.")

        metadata = cls()
        metadata.path = path
        metadata.permissions = cls.evaluate_permissions(path)

        if not metadata.is_readable():
            raise PermissionError(f"{path} is not readable: {metadata.permissions}")

        metadata.fields = cls._parse_readme(path)

        # remove the content field from the fields dict
        metadata.content = metadata.fields.pop("content", "")

        return metadata

    def log_change(self, description: str) -> None:
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M")
        self.logs.append(f"{timestamp}: {description}")

    def write_to_file(self, newpath: Path | None = None) -> None:
        newpath = newpath or self.path.with_name(self.path.stem + ".dmp")

        if not is_file_writable(newpath):
            raise PermissionError(f"{newpath} is not writable: {self.permissions}")

        # with newpath.open(mode='w') as file:
        file = newpath.open(mode="w")
        for fld, value in self.fields.items():
            line = f"#{fld}: {value}"
            if len(line) > 80:
                # If the line length exceeds 80,
                # split it into multiple lines without breaking words
                words = line.split()
                lines = []
                current_line = ""
                for word in words:
                    if len(current_line) + len(word) + 1 <= 80:
                        current_line += word + " "
                    else:
                        lines.append(current_line.strip())
                        current_line = word + " "
                if current_line:
                    lines.append(current_line.strip())
                file.write("\n".join(lines))
            else:
                file.write(line)
            file.write("\n\n")
        if self.content:
            file.write(f"\n{self.content}")
        if self.logs:
            file.write("\n\n\n")
            for log in self.logs:
                file.write(f"\n{log}")
        file.close()

    @classmethod
    def _parse_readme(
        cls: Type["DMPMetadata"],
        readme: Path,
        pattern: re.Pattern[str] = re.compile(r"^#([A-Z]+): (.+)$"),
    ) -> dict:
        current_field = None
        current_value = []
        content_lines = []
        metadata = {}
        with readme.open(mode="r") as file:
            for line in file:
                if line.strip() == "" and current_field:
                    # End current field on double newline
                    metadata[current_field] = " ".join(current_value).strip()
                    current_field = None
                    current_value = []
                else:
                    match = pattern.match(line.strip())
                    if match:
                        if current_field:
                            metadata[current_field] = " ".join(current_value).strip()
                        current_field, current_value = (
                            match.groups()[0],
                            [match.groups()[1]],
                        )
                    elif current_field:
                        current_value.append(line.strip())
                    else:
                        content_lines.append(line.strip())

            if current_field:
                metadata[current_field] = " ".join(current_value).strip()

        metadata["content"] = "\n".join(content_lines).strip()
        return metadata

    def __getitem__(self, item: str) -> str:
        return self.fields.get(item, None)

    def __setitem__(self, key: str, value: str) -> None:
        self.fields[key] = value

    @staticmethod
    def evaluate_permissions(path: Path) -> str:
        permissions = path.stat().st_mode
        is_dir = "d" if stat.S_ISDIR(permissions) else "-"
        perm_bits = [
            (permissions & stat.S_IRUSR, "r"),
            (permissions & stat.S_IWUSR, "w"),
            (permissions & stat.S_IXUSR, "x"),
            (permissions & stat.S_IRGRP, "r"),
            (permissions & stat.S_IWGRP, "w"),
            (permissions & stat.S_IXGRP, "x"),
            (permissions & stat.S_IROTH, "r"),
            (permissions & stat.S_IWOTH, "w"),
            (permissions & stat.S_IXOTH, "x"),
        ]
        formatted_permissions = is_dir + "".join(
            bit[1] if bit[0] else "-" for bit in perm_bits
        )
        return formatted_permissions

    def get_permissions(self) -> str:
        if not self.permissions:
            return "No permissions set."
        return self.permissions

    def is_writeable(self) -> bool:
        return "w" in self.permissions

    def is_readable(self) -> bool:
        return "r" in self.permissions

    def __rich_repr__(self) -> rich.repr.Result:
        yield "path", self.path
        yield "fields", self.fields
        yield "content", self.content
        yield "permissions", self.permissions
        yield "logs", self.logs

if __name__ == "__main__":
    # test the function
    cwd = Path.cwd()
    readme_example_dir = cwd / "tests" / "examples"

    all_dirs = list(readme_example_dir.glob("*"))

    all_files = [file for directoru in all_dirs for file in directoru.glob("README*")]

    dmps = []
    for file in all_files:
        dmp = DMPMetadata.from_path(file)
        print()
        dmps.append(dmp)

    print(dmps[3])
    dmps[3].log_change("Added a log entry.")
    dmps[3].log_change("Added another log entry.")
    print(dmps[3])
    dmps[3].write_to_file()
