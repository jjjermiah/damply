import os
from dataclasses import dataclass
from pathlib import Path
from typing import List

"""
This module contains functions to find symlinks in a directory.
For the most part, projects implementing the standard should use symbolic links when possible.

i.e

|_ PROJECT_NAME
|_ rawdata -> /path_to_rawdata_dir/PROJECT_NAME/
|_ procdata -> /path_to_procdata_dir/PROJECT_NAME/
|_ references -> /path_to_references_dir/GENCODE/...

OR

|_ PROJECT_NAME
|_ rawdata
  |_ rnaseq -> /path_to_rawdata_dir/PROJECT_NAME/rnaseq/
  |_ methylation -> /path_to_rawdata_dir/PROJECT_NAME/methylation/
|_ procdata
  |_ rnaseq -> /path_to_procdata_dir/PROJECT_NAME/rnaseq/
  |_ methylation -> /path_to_procdata_dir/PROJECT_NAME/methylation/

We should be able to determine quickly if a directory has any symlinks up to 2 levels deep.
"""


@dataclass
class SymlinkInfo:
    path: Path
    target: Path

def find_symlinks(directory: Path, max_depth: int = 3) -> List[SymlinkInfo]:
    """
    Find symlinks in a directory up to a specified depth.

    Args:
        directory (Path): The directory to search in.
        max_depth (int): The maximum depth to search for symlinks.

    Returns:
        List[SymlinkInfo]: A list of SymlinkInfo objects containing the symlink and its target.
    """
    symlinks = []

    def search_dir(current_path: Path, current_depth: int):
        if current_depth > max_depth:
            return

        if current_path.is_symlink():
            symlinks.append(SymlinkInfo(path=current_path, target=current_path.resolve()))

        if current_path.is_dir():
            for entry in current_path.iterdir():
                search_dir(entry, current_depth + 1)

    search_dir(directory, 0)
    return symlinks

# Example usage
if __name__ == "__main__":
    project_dir = Path("/cluster/projects/bhklab/projects/BTCIS")
    print(f"{project_dir=}")
    symlinks = find_symlinks(project_dir)
    for symlink in symlinks:
        print(f"Symlink: {symlink.path}, Target: {symlink.target}")
