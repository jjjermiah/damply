"""This is a sandbox script to plot a sankey diagram of the dmp"""

"""
Column Headings:
owner	full_name	abspath	relative_path	directory	parent_dir	permissions	creation_date	last_modified	has_README	OWNER	DATE	DESC	size_MB	size_GB

Goal:
"""
import os
from pathlib import Path
from typing import Any

import pandas as pd
import plotly.graph_objects as go

def generate_nodes_levels(
    df: pd.DataFrame, common_root: Path
) -> tuple[list[Any], dict[Any, Any]]:
    """
    Generate nodes and levels for the sankey diagram
    """
    nodes = []
    levels = {}

    for index, row in df.iterrows():
        path_parts = row["abspath"].split("/")[1:]
        for i, part in enumerate(path_parts):
            if i == 0:
                continue
            else:
                parent = "/" + "/".join(path_parts[: i - 1])
            child = "/" + "/".join(path_parts[:i])
            if parent not in levels:
                levels[parent] = len(levels)
                nodes.append(dict(label=parent))
            if child not in levels:
                levels[child] = len(levels)
                nodes.append(dict(label=child))
    return nodes, levels


def filter_depth(df: pd.DataFrame, depth: int, common_root: Path):
    """
    Filter the dataframe to include only the directories at or below a certain depth from the common root
    """

    def get_depth(path: str):
        return len(Path(path).relative_to(common_root).parts)

    df = df[df["abspath"].apply(get_depth) <= depth]
    return df


def main(
    file_path: Path,
    threshold_GB: int = 100,
    depth_from_common_root: int = 3,
):
    """

    The goal is to create a sankey diagram of the directories where the source of
    each flow is the parent directory and the target is the child directory with the width of the flow being the size of the director
    """
    raw_df = pd.read_csv(file_path, delimiter="\t")

    df = raw_df[raw_df["size_GB"] >= threshold_GB]

    # get the common root of all the paths in abspath
    common_root = Path(os.path.commonprefix(df["abspath"].tolist()))
    print(f"Common root: {common_root}")

    filtered_df = filter_depth(df, depth_from_common_root, common_root)
    print(f"Filtered rowcount: {filtered_df.shape[0]} out of {raw_df.shape[0]}")

    nodes, levels = generate_nodes_levels(filtered_df, common_root)

    # Create the links
    links = []

    for index, row in filtered_df.iterrows():
        target = row["abspath"]
        path_parts = target.split("/")

        source_node = "/".join(path_parts[:-1])

        if target not in nodes:
            nodes.append(dict(label=target))
            levels[target] = len(levels) - 1
        # print(f"Source: {source_node}, Target: {target}")
        links.append(
            {
                "source": nodes.index({"label": source_node}),
                "target": nodes.index({"label": target}),
                "value": row["size_GB"],
            }
        )

    node_size_dict = {
        row["abspath"]: row["size_GB"] for index, row in filtered_df.iterrows()
    }

    # label_with_size: list[str] = [f"{label['label'].split('/')[-1]} ({node_size_dict.get(label['label'], 0)} GB)" for label in nodes]
    label_with_size = []
    for node in nodes:
        label = node["label"]
        size = node_size_dict.get(label, 0)
        if size == 0:
            # add up all the children sizes
            children = [
                link["target"] for link in links if link["source"] == nodes.index(node)
            ]
            size = sum(
                [node_size_dict.get(nodes[child]["label"], 0) for child in children]
            )
        label_with_size.append(f"{label.split('/')[-1]} ({size} GB)")

    fig = go.Figure(
        data=[
            go.Sankey(
                node=dict(
                    pad=15,
                    thickness=20,
                    line=dict(color="black", width=0.5),
                    label=label_with_size,
                    color="blue",
                ),
                link=dict(
                    source=[link["source"] for link in links],
                    target=[link["target"] for link in links],
                    value=[link["value"] for link in links],
                ),
            )
        ]
    )
    fig.show()


if __name__ == "__main__":
    main(
        file_path=Path(
            "/Users/bhklab/Documents/GitHub/damply/tests/latest-valid_directories.tsv"
        ),
        threshold_GB=50,
    )
