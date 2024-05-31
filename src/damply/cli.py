from typing import Literal

import rich_click as click
from rich import print

@click.command()
@click.option("--name", type=str, prompt="What is your name?")
def cli(name: str) -> None:
    """Simple CLI that greets NAME for a total of COUNT times."""
    print(f"Hello, {name}!")

def hello() -> Literal['Hello, World!']:
    return "Hello, World!"
