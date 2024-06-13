import os
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Dict, List

import pandas as pd
import plotly.graph_objects as go
import rich_click as click

"""This is a sandbox script to plot a sankey diagram of the dmp"""

MANDATORY_COLUMNS = ["abspath", "size_GB"]

"""
The input file should contain the mandatory columns and optionally other columns. The mandatory columns are:
- abspath: the absolute path of the directory
- size_GB: the size of the directory in GB

Column Headings:
owner	full_name	abspath	relative_path	directory	parent_dir	permissions	creation_date	last_modified	has_README	OWNER	DATE	DESC	size_MB	size_GB

Goal:
"""


@dataclass
class Directory:
    directory: Path
    size_GB: int

    def __post_init__(self):
        self.parent = self.directory.parent

    def __getitem__(self, key: str) -> Any:
        return self.__dict__[key]

    def __repr__(self):
        return f"Directory({self.directory}, {self.size_GB})"


@dataclass
class DirectoryList:
    directories: List[Directory]

    def __post_init__(self):
        self.common_root = self.get_common_root()

    def get_common_root(self) -> Path:
        return Path(
            os.path.commonprefix(
                [str(directory.directory) for directory in self.directories]
            )
        )

    def __len__(self) -> int:
        return len(self.directories)

    def __getitem__(self, key: int) -> Directory:
        return self.directories[key]

    def __repr__(self):
        fmt_str = ""
        fmt_str += f"CommonPre:{self.common_root}\n"
        for directory in self.directories:
            fmt_str += f"{directory}\n"
        return fmt_str

    def dir_size_dict(self) -> Dict[Path, int]:
        return {
            directory.directory: directory.size_GB for directory in self.directories
        }


def permutate_path(path: Path) -> List[Path]:
    """
    Given a path, return all possible paths from the root to the path
    """
    nodes = []
    while path != Path("/"):
        nodes.append(path)
        path = path.parent
    return nodes


def generate_node_list(dirlist: DirectoryList) -> List[Path]:
    common_root = dirlist.common_root
    nodes = set(permutate_path(common_root))

    for directory in dirlist.directories:
        nodes.update(permutate_path(directory.directory))
    # sort the nodes by # of "/" in the path and then alphabetically
    nodes = sorted(nodes, key=lambda x: (len(x.parts), x))
    return list(nodes)


@click.command()
@click.argument("file_path", type=Path)
@click.option("--threshold_gb", type=int, default=100)
def main(
    file_path: Path,
    threshold_gb: int = 100,
    depth_from_common_root: int = 3,
):
    """

    The goal is to create a sankey diagram of the directories where the source of
    each flow is the parent directory and the target is the child directory with the width of the flow being the size of the director
    """

    # Read the file
    df = pd.read_csv(file_path, sep="\t")

    if not all(col in df.columns for col in MANDATORY_COLUMNS):
        raise ValueError(
            f"The file must contain the following columns: {', '.join(MANDATORY_COLUMNS)}"
        )

    # Filter the dataframe
    df = df[df["size_GB"] > threshold_gb]

    dirlist: DirectoryList = DirectoryList(
        directories=[
            Directory(directory=Path(row["abspath"]), size_GB=row["size_GB"])
            for index, row in df.iterrows()
        ]
    )
    nodes = generate_node_list(dirlist)

    links = []
    for dir in dirlist:
        target = nodes.index(dir.directory)
        source = nodes.index(dir.parent)
        links.append({"source": source, "target": target, "value": dir.size_GB})

    label_with_sizes = []
    for node in nodes:
        label = node.name
        size = dirlist.dir_size_dict().get(node, 0)

        if size == 0:
            children = [child for child in dirlist.directories if child.parent == node]
            size = sum([child.size_GB for child in children])

            # add to dirlist
            dirlist.directories.append(Directory(directory=node, size_GB=size))

        label_with_sizes.append(f"{label} ({size} GB)")

    nodes_whose_parent_is_common_root = [
        node for node in nodes if node.parent == dirlist.common_root
    ]

    # add a link from the common root to the nodes whose parent is the common root
    common_root_size = sum(
        [
            dir.size_GB
            for dir in dirlist.directories
            if dir.parent == dirlist.common_root
        ]
    )
    for node in nodes_whose_parent_is_common_root:
        target = nodes.index(node)
        source = nodes.index(dirlist.common_root)
        size = dirlist.dir_size_dict().get(node, 0)
        links.append({"source": source, "target": target, "value": size})

    # get the index of the common root so that we can update the label_with_sizes index
    common_root_index = nodes.index(dirlist.common_root)
    label_with_sizes[common_root_index] = (
        f"{dirlist.common_root} ({common_root_size} GB)"
    )

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=label_with_sizes,
                    color="blue",
                ),
                link=dict(
                    source=[link["source"] for link in links],
                    target=[link["target"] for link in links],
                    value=[link["value"] for link in links],
                ),
                textfont=dict(color="black", size=20),
            )
        ]
    )

    fig.show()


if __name__ == "__main__":
    main(
        file_path=Path(
            "/Users/bhklab/BHKLAB_Projects/H4H/disk-usage/AUDITS/latest-valid_directories.tsv"
        ),
        threshold_gb=50,
    )
