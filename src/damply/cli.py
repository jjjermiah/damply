from pathlib import Path
from typing import Literal
import rich_click as click
from rich import print
from click_didyoumean import DYMGroup

from damply import __version__ 
from damply.metadata import DMPMetadata
from damply.utils import whose as whose_util

click.rich_click.STYLE_OPTIONS_TABLE_BOX = "SIMPLE"
click.rich_click.STYLE_COMMANDS_TABLE_SHOW_LINES = True
click.rich_click.STYLE_COMMANDS_TABLE_PAD_EDGE = True

click.rich_click.OPTION_GROUPS = {
    "damply": [
        {
            "name": "Basic options",
            "options": ["--help", "--version"],
        },
    ]
}

click.rich_click.COMMAND_GROUPS = {
    "damply": [
        {
            "name": "Subcommands",
            "commands": ["version", "view", "whose"],
        }
    ]
}

help_config = click.RichHelpConfiguration(
    show_arguments=True,
    option_groups={"damply": [{"name": "Arguments", "panel_styles": {"box": "ASCII"}}]},
)


class AliasedGroup(click.RichGroup, DYMGroup):
    command_class = click.RichCommand
    max_suggestions = 3
    cutoff = 0.5
    
    def get_command(self, ctx, cmd_name):
        rv = click.Group.get_command(self, ctx, cmd_name)
        if rv is not None:
            return rv
        matches = [x for x in self.list_commands(ctx) if x.startswith(cmd_name)]
        if not matches:
            return None
        elif len(matches) == 1:
            return click.Group.get_command(self, ctx, matches[0])
        ctx.fail(f"Too many matches: {', '.join(sorted(matches))}")

    def resolve_command(self, ctx, args):
        # always return the full command name
        _, cmd, args = super().resolve_command(ctx, args)

        if cmd is not None:
            return cmd.name, cmd, args
        else:
            return None, None, args


@click.group(
    cls=AliasedGroup,
    name="damply",
    context_settings={"help_option_names": ["-h", "--help"]},
)
@click.version_option("1.23", prog_name="damply")
def cli() -> None:
    """A tool to interact with systems implementing the Data Management Plan (DMP) standard."""
    pass




@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "directory",
    type=click.Path(
        exists=True,
        path_type=Path,
        file_okay=False,
        dir_okay=True,
        readable=True,
    ),
    default=Path().cwd(),
)
@click.rich_config(help_config=help_config)
def view(directory: Path) -> None:
    """View the DMP Metadata of a valid DMP Directory."""
    readmes = [f for f in directory.glob("README*") if f.is_file()]

    if len(readmes) == 0:
        print("No README file found.")
        return
    elif len(readmes) > 1:
        print("Multiple README files found. Using the first one.")
        readme = readmes[0]
    else:
        readme = readmes[0]

    metadata = DMPMetadata.from_path(readme)

    from rich.console import Console
    from rich.markdown import Markdown
    from rich.table import Table

    console = Console()

    table = Table.grid(padding=1, pad_edge=True, expand=True)
    table.title = f"[bold]Metadata for {metadata.path.absolute()}[/bold]"
    table.add_column("Field", justify="right", style="cyan")
    table.add_column("Value", style="yellow")

    for field, value in metadata.fields.items():
        table.add_row(field, value)

    console.print(table)
    console.print(Markdown(metadata.content))
    console.print(Markdown("\n".join(metadata.logs)))


@cli.command(context_settings={"help_option_names": ["-h", "--help"]})
@click.argument(
    "path",
    type=click.Path(
        exists=True,
        path_type=Path,
        file_okay=True,
        dir_okay=True,
        readable=True,
    ),
    default=Path().cwd(),
)
@click.rich_config(help_config=help_config)
def whose(path: Path) -> None:
    """Print the owner of the file or directory."""
    result = whose_util.get_file_owner_full_name(path)

    print(
        f"The owner of [bold magenta]{path}[/bold magenta] is [bold cyan]{result}[/bold cyan]"
    )

if __name__ == "__main__":
    cli()
