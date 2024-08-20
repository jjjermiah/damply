from damply.utils import ByteSize

import datetime  # Add this import
import re
import stat
from dataclasses import dataclass, field
import subprocess
from pathlib import Path
from typing import Type

import rich.repr

MANDATORY_FIELDS = ['OWNER', 'DATE', 'DESC']


def is_file_writable(file_path: Path) -> bool:
    import os

    return file_path.exists() and os.access(file_path, os.W_OK)

def get_directory_size(directory: Path) -> ByteSize:
    # may raise   subprocess.CalledProcessError
    result = subprocess.run(['du', '-s', '-B 1', str(directory)], capture_output=True, text=True, check=True)
    size_ =  ByteSize(int(result.stdout.split()[0])) 
    print(f"Size in bytes: {size_.B}")
    return size_

@dataclass
class DMPMetadata:
    fields: dict = field(default_factory=dict)
    content: str = field(default_factory=str, repr=False)
    path: Path = field(default=Path().cwd())
    permissions: str = field(default='---------')
    logs: list = field(default_factory=list, repr=True)
    readme: Path = field(default=Path().cwd() / 'README')
    size: ByteSize = field(default=None, repr=False)
    size_measured_at: datetime.datetime = field(default=None, repr=False)


    @classmethod
    def from_path(cls: Type['DMPMetadata'], path: Path) -> 'DMPMetadata':
        readme: Path = cls._find_readme(path)

        metadata = cls()
        metadata.path = readme.resolve().parent
        metadata.permissions = cls.evaluate_permissions(readme)
        metadata.readme = readme
        if not metadata.is_readable():
            raise PermissionError(f'{readme} is not readable: {metadata.permissions}')

        metadata.fields = cls._parse_readme(readme)
        # remove the content field from the fields dict
        metadata.content = metadata.fields.pop('content', '')

        return metadata

    @staticmethod
    def _find_readme(path: Path) -> Path:
        if path.is_dir():
            readmes = [f for f in path.glob('README*') if f.is_file()]
            if len(readmes) == 0:
                raise ValueError('No README file found.')
            elif len(readmes) > 1:
                print('Multiple README files found. Using the first one.')
                readme = readmes[0]
            else:
                readme = readmes[0]
        else:
            readme = path
            
        if 'README' not in readme.stem.upper():
            raise ValueError('The file is not a README file.')
        
        return readme

    def _dirsize(self) -> ByteSize:
        size = get_directory_size(self.path)
        self.size = size
        self.size_measured_at = datetime.datetime.now().strftime('%Y-%m-%d-%H:%M')
        return size

    def write_dirsize(self) -> None:
        if not self.size:
            self._dirsize()
        dirsize_str = f"{self.size.B} - {self.size_measured_at}"
        self.fields['SIZE'] = dirsize_str
        print(f"Writing size: {self.size.B}")
        self.write_to_file()

    def read_dirsize(self) -> ByteSize:
        dirsize_str = self.fields.get('SIZE', None)        
        if dirsize_str:
            print(f"using size from README: {dirsize_str}")
            self.size = ByteSize(int(dirsize_str.split()[0]))
            self.size_measured_at = datetime.datetime.strptime(dirsize_str.split()[2], '%Y-%m-%d-%H:%M')
            print(f"Read size: {self.size.B}")
            print(f"Read size measured at: {self.size_measured_at}")
            return self.size
        else:
            self.write_dirsize()
            return self.size

    def log_change(self, description: str) -> None:
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M')
        self.logs.append(f'{timestamp}: {description}')

    def add_field(self, field: str, value: str) -> None:
        """Assuming the field is not already present, add it to the fields dict.
        
        If the field is already present, add the value to the existing field.

        Args:
            field (str): name of the field, i.e OWNER, DATE, DESC, STATUS
            value (str): value of the field
        """
        field = field.upper()
        if field in self.fields:
            self.fields[field] += f' {value}'
        else:
            self.fields[field] = value

    def write_to_file(self, newpath: Path | None = None) -> None:
        newpath = newpath or self.readme
        newpath = newpath.resolve()
        # create the newpath file if it doesn't exist
        newpath.parent.mkdir(parents=True, exist_ok=True)
        newpath.touch(exist_ok=True)

        if not is_file_writable(newpath):
            raise PermissionError(f'{newpath} is not writable: {self.permissions}')

        # with newpath.open(mode='w') as file:
        file = newpath.open(mode='w')
        for fld, value in self.fields.items():
            line = f'#{fld}: {value}'
            if len(line) > 80:
                # If the line length exceeds 80,
                # split it into multiple lines without breaking words
                words = line.split()
                lines = []
                current_line = ''
                for word in words:
                    if len(current_line) + len(word) + 1 <= 80:
                        current_line += word + ' '
                    else:
                        lines.append(current_line.strip())
                        current_line = word + ' '
                if current_line:
                    lines.append(current_line.strip())
                file.write('\n'.join(lines))
            else:
                file.write(line)
            file.write('\n\n')
        if self.content:
            file.write(f'\n{self.content}')
        if self.logs:
            file.write('\n\n\n')
            for log in self.logs:
                file.write(f'\n{log}')
        file.close()

    def check_fields(self) -> None:
        missing = [fld for fld in MANDATORY_FIELDS if fld not in self.fields]
        if missing:
            raise ValueError(f'The following fields are missing: {missing}' f' in {self.readme}')

    @classmethod
    def _parse_readme(
        cls: Type['DMPMetadata'],
        readme: Path,
        pattern: re.Pattern[str] = re.compile(r'^#([A-Z]+): (.+)$'),
    ) -> dict:
        current_field = None
        current_value = []
        content_lines = []
        metadata = {}
        with readme.open(mode='r') as file:
            for line in file:
                if line.strip() == '' and current_field:
                    # End current field on double newline
                    metadata[current_field] = ' '.join(current_value).strip()
                    current_field = None
                    current_value = []
                else:
                    match = pattern.match(line.strip())
                    if match:
                        if current_field:
                            metadata[current_field] = ' '.join(current_value).strip()
                        current_field, current_value = (
                            match.groups()[0],
                            [match.groups()[1]],
                        )
                    elif current_field:
                        current_value.append(line.strip())
                    else:
                        content_lines.append(line.strip())
            
            
            if current_field:
                metadata[current_field] = ' '.join(current_value).strip()

        metadata['content'] = '\n'.join(content_lines).strip()
        return metadata

    def __getitem__(self, item: str) -> str:
        return self.fields.get(item, None)

    def __setitem__(self, key: str, value: str) -> None:
        self.fields[key] = value

    @staticmethod
    def evaluate_permissions(path: Path) -> str:
        permissions = path.stat().st_mode
        is_dir = 'd' if stat.S_ISDIR(permissions) else '-'
        perm_bits = [
            (permissions & stat.S_IRUSR, 'r'),
            (permissions & stat.S_IWUSR, 'w'),
            (permissions & stat.S_IXUSR, 'x'),
            (permissions & stat.S_IRGRP, 'r'),
            (permissions & stat.S_IWGRP, 'w'),
            (permissions & stat.S_IXGRP, 'x'),
            (permissions & stat.S_IROTH, 'r'),
            (permissions & stat.S_IWOTH, 'w'),
            (permissions & stat.S_IXOTH, 'x'),
        ]
        formatted_permissions = is_dir + ''.join(bit[1] if bit[0] else '-' for bit in perm_bits)
        return formatted_permissions

    def get_permissions(self) -> str:
        if not self.permissions:
            return 'No permissions set.'
        return self.permissions

    def is_writeable(self) -> bool:
        return 'w' in self.permissions

    def is_readable(self) -> bool:
        return 'r' in self.permissions

    def __rich_repr__(self) -> rich.repr.Result:
        yield 'path', self.path
        yield 'fields', self.fields
        yield 'content', self.content
        yield 'permissions', self.permissions
        yield 'logs', self.logs
        yield 'size', self.size
        yield 'size_measured_at', self.size_measured_at
