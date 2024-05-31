from pathlib import Path
from typing import Literal

import rich_click as click
from rich import print

from damply.metadata import DMPMetadata
from damply.utils import whose as whose_util

click.rich_click.OPTION_GROUPS = {
    'damply': [
        {
            'name': 'Basic options',
            'options': ['--help'],
        },
    ]
}

click.rich_click.COMMAND_GROUPS = {
    'damply': [
        {
            'name': 'Subcommands',
            'commands': ['version', 'view', 'whose'],
        }
    ]
}

help_config = click.RichHelpConfiguration(
    show_arguments=True,
    option_groups={'damply': [{'name': 'Arguments', 'panel_styles': {'box': 'ASCII'}}]},
)


@click.group(name='damply', context_settings={'help_option_names': ['-h', '--help']})
def cli() -> None:
    """A tool to interact with systems implementing the Data Management Plan (DMP) standard."""
    pass


@cli.command()
def version() -> None:
    """Print the version of damply."""
    from . import __version__ as ver

    print(f'damply version {ver}')


@cli.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument(
    'directory',
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
    readmes = [f for f in directory.glob('README*') if f.is_file()]

    if len(readmes) == 0:
        print('No README file found.')
        return
    elif len(readmes) > 1:
        print('Multiple README files found. Using the first one.')
        readme = readmes[0]
    else:
        readme = readmes[0]

    metadata = DMPMetadata.from_path(readme)

    from rich.console import Console
    from rich.markdown import Markdown
    from rich.table import Table

    console = Console()

    table = Table.grid(padding=1, pad_edge=True, expand=True)
    table.title = f'[bold]Metadata for {metadata.path.absolute()}[/bold]'
    table.add_column('Field', justify='right', style='cyan')
    table.add_column('Value', style='yellow')

    for field, value in metadata.fields.items():
        table.add_row(field, value)

    console.print(table)
    console.print(Markdown(metadata.content))
    console.print(Markdown('\n'.join(metadata.logs)))


@cli.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument(
    'path',
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

    print(f'The owner of [bold magenta]{path}[/bold magenta] is [bold cyan]{result}[/bold cyan]')


def hello() -> Literal['Hello, World!']:
    return 'Hello, World!'
