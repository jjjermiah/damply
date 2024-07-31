from pathlib import Path

import rich_click as click
from rich import print

from damply.metadata import DMPMetadata
from damply.plot import damplyplot
from damply.utils import whose as whose_util
from damply.utils.alias_group import AliasedGroup

click.rich_click.STYLE_OPTIONS_TABLE_BOX = 'SIMPLE'
click.rich_click.STYLE_COMMANDS_TABLE_SHOW_LINES = True
click.rich_click.STYLE_COMMANDS_TABLE_PAD_EDGE = True

click.rich_click.OPTION_GROUPS = {
    'damply': [
        {
            'name': 'Basic options',
            'options': ['--help', '--version'],
        },
    ]
}

click.rich_click.COMMAND_GROUPS = {
    'damply': [
        {
            'name': 'Subcommands',
            'commands': ['plot', 'view', 'whose'],
        }
    ]
}

help_config = click.RichHelpConfiguration(
    show_arguments=True,
    option_groups={'damply': [{'name': 'Arguments', 'panel_styles': {'box': 'ASCII'}}]},
)


@click.group(
    cls=AliasedGroup,
    name='damply',
    context_settings={'help_option_names': ['-h', '--help']},
)
@click.version_option('1.23', prog_name='damply')
def cli() -> None:
    """A tool to interact with systems implementing the Data Management Plan (DMP) standard."""
    pass


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


if __name__ == '__main__':
    cli()


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
@click.option('--threshold_gb', type=int, default=100)
@click.rich_config(help_config=help_config)
def plot(path: Path, threshold_gb: int = 100) -> None:
    """Plot the results of a damply audit using the path to the output csv file."""
    output_path = damplyplot(path, threshold_gb=threshold_gb)
    print(f'The plot is saved to {output_path}')
