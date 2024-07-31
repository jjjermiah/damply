from datetime import datetime
from pathlib import Path
from typing import List

import pandas as pd
import plotly.graph_objects as go

from damply.utils import Directory, DirectoryList

"""This is a sandbox script to plot a sankey diagram of the dmp"""

MANDATORY_COLUMNS = ['abspath', 'size_GB']

"""
The input file should contain the mandatory columns and optionally other columns.
The mandatory columns are:
- abspath: the absolute path of the directory
- size_GB: the size of the directory in GB

Column Headings:
owner	full_name	abspath	relative_path	directory	parent_dir	permissions	creation_date
last_modified	has_README	OWNER	DATE	DESC	size_MB	size_GB

Goal:
"""


def permutate_path(path: Path) -> List[Path]:
    """
    Given a path, return all possible paths from the root to the path
    """
    assert path.is_absolute(), 'The path must be absolute'

    nodes = []
    while path != Path('/'):
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


def damplyplot(
    file_path: Path,
    threshold_gb: int = 100,
    fig_width: int = 3340,
    fig_height: int = 1440,
    depth_from_common_root: int = 3,
) -> Path:
    """

    The goal is to create a sankey diagram of the directories where the source of
    each flow is the parent directory and the target is the child directory with
    the width of the flow being the size of the directory
    """

    # Read the file
    df = pd.read_csv(file_path, sep='\t')

    if not all(col in df.columns for col in MANDATORY_COLUMNS):
        raise ValueError(
            f"The file must contain the following columns: {', '.join(MANDATORY_COLUMNS)}"
        )

    # Filter the dataframe
    df = df[df['size_GB'] > threshold_gb]

    dirlist: DirectoryList = DirectoryList(
        directories=[
            Directory(directory=Path(row['abspath']), size_GB=row['size_GB'])
            for index, row in df.iterrows()
        ]
    )
    nodes = generate_node_list(dirlist)

    links = []
    for _dir in dirlist:
        target = nodes.index(_dir.directory)
        source = nodes.index(_dir.parent)
        links.append({'source': source, 'target': target, 'value': _dir.size_GB})

    label_with_sizes = []
    for node in nodes:
        label = node.name
        size = dirlist.dir_size_dict().get(node, 0)

        if size == 0:
            children = [child for child in dirlist.directories if child.parent == node]
            size = sum([child.size_GB for child in children])

            # add to dirlist
            dirlist.directories.append(Directory(directory=node, size_GB=size))

        label_with_sizes.append(f'{label} ({size} GB)')

    nodes_whose_parent_is_common_root = [
        node for node in nodes if node.parent == dirlist.common_root
    ]

    # add a link from the common root to the nodes whose parent is the common root
    common_root_size = sum(
        [_dir.size_GB for _dir in dirlist.directories if _dir.parent == dirlist.common_root]
    )
    for node in nodes_whose_parent_is_common_root:
        target = nodes.index(node)
        source = nodes.index(dirlist.common_root)
        size = dirlist.dir_size_dict().get(node, 0)
        links.append({'source': source, 'target': target, 'value': size})

    # get the index of the common root so that we can update the label_with_sizes index
    common_root_index = nodes.index(dirlist.common_root)
    label_with_sizes[common_root_index] = f'{dirlist.common_root} ({common_root_size} GB)'

    fig_layout = {'width': fig_width, 'height': fig_height}

    fig = go.Figure(
        data=[
            go.Sankey(
                node={
                    'pad': 30,
                    'thickness': 10,
                    'line': {'color': 'black', 'width': 0.5},
                    'label': label_with_sizes,
                    'color': 'blue',
                },
                link={
                    'source': [link['source'] for link in links],
                    'target': [link['target'] for link in links],
                    'value': [link['value'] for link in links],
                },
                textfont={'color': 'black', 'size': 20},
            )
        ],
        layout=fig_layout,
    )

    # save the figure using todays date as damplyplot_{MM-DD-YYYY}.png
    date_str = datetime.now().strftime('%m-%d-%Y')

    output_path = Path(f'damplyplot_{date_str}.png')
    fig.write_image(output_path)

    return output_path
