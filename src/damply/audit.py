import os
from re import I
import pandas as pd
from io import StringIO
from typing import List, Dict
import stat
from datetime import datetime, timezone, date
from pathlib import Path

from dataclasses import dataclass
from rich import print
import rich.repr

@dataclass
class DirectoryAudit:
    path: Path
    owner: str
    full_name: str
    permissions: str
    a_time: datetime
    m_time: datetime
    c_time: datetime

    @classmethod
    def from_path(cls, path: Path) -> 'DirectoryAudit':
      stats = os.stat(path)
      
      try:
        from pwd import getpwuid
        pwuid_name = getpwuid(stats.st_uid).pw_name
        pwuid_gecos = getpwuid(stats.st_uid).pw_gecos
      except ImportError:
        pwuid_name = "Unknown"
        pwuid_gecos = "Unknown"
      except KeyError:
        pwuid_name = "Unknown"
        pwuid_gecos = "Unknown"

      return DirectoryAudit(
        path=path,
        owner=pwuid_name,
        full_name=pwuid_gecos,
        permissions=stat.filemode(stats.st_mode),
        a_time=datetime.fromtimestamp(stats.st_atime, tz= timezone.utc),
        m_time=datetime.fromtimestamp(stats.st_mtime, tz = timezone.utc),
        c_time=datetime.fromtimestamp(stats.st_ctime, tz = timezone.utc),
      )

    def format_date(self, date: datetime) -> str:
      return date.strftime("%Y-%m-%d %H:%M:%S")

    def __rich_repr__(self) -> rich.repr.Result:
        yield 'path', self.path.absolute()
        yield 'owner', self.owner
        yield 'full_name', self.full_name
        yield 'permissions', self.permissions
        yield 'a_time', self.format_date(self.a_time)
        yield 'm_time', self.format_date(self.m_time)
        yield 'c_time', self.format_date(self.c_time)

if __name__ == "__main__":
    audit = DirectoryAudit.from_path(Path("/cluster/projects/bhklab/projects/BTCIS"))
    print(audit)