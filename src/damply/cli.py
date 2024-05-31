from rich import print
import rich_click as click


@click.command()
@click.option("--name", type=str, prompt="What is your name?")
def cli(name: str):
    """Simple CLI that greets NAME for a total of COUNT times."""
    print(f"Hello, {name}!")

def hello():
    return "Hello, World!"
