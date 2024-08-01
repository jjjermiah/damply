from pathlib import Path

import rich_click as click
from rich import print

from damply import __version__
from damply.metadata import MANDATORY_FIELDS, DMPMetadata
from damply.plot import damplyplot
from damply.utils import whose as whose_util
from damply.utils.alias_group import AliasedGroup

from damply.cli.audit import audit
from damply.cli.plot import plot
from damply.cli.click_config import help_config

@click.group(
    cls=AliasedGroup,
    name='damply',
    context_settings={'help_option_names': ['-h', '--help']},
)
@click.version_option(__version__, prog_name='damply')
def cli() -> None:
    """
    A tool to interact with systems implementing the 
    Data Management Plan (DMP) standard.
    
    This tool is meant to allow sys-admins to easily query and audit the metadata of their
    projects.
    """
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
    try:
        metadata = DMPMetadata.from_path(directory)
        metadata.check_fields()
    except ValueError as e:
        print(e)
        return

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


@cli.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--path',
    type=click.Path(
        exists=True,
        path_type=Path,
        file_okay=True,
        dir_okay=True,
        readable=True,
    ),
    default=Path().cwd(),
)
@click.argument(
    'description',
    type=str,
)
@click.rich_config(help_config=help_config)
def log(description: str, path: Path) -> None:
    """Add a log entry to the metadata."""
    try:
        metadata = DMPMetadata.from_path(path)
        metadata.check_fields()
    except ValueError as e:
        print(f'Error: No log entry added.\n{e}')
        return

    metadata.log_change(description)
    metadata.write_to_file()


@cli.command(context_settings={'help_option_names': ['-h', '--help']})
@click.option(
    '--dry_run',
    is_flag=True,
    default=False,
)
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
def config(path: Path, dry_run: bool) -> None:
    """Modify or add the fields in the README file."""

    try:
        metadata = DMPMetadata.from_path(path)
        metadata.check_fields()
    except ValueError as e:
        print(f'{e}')

    from rich.console import Console

    if dry_run:
        config_path = Path(metadata.readme + '.dmp')
        print(
            f'Dry run mode is on. No changes will be made and'
            f'changes will be written to [bold cyan]{config_path.resolve()}[/bold cyan]'
        )
    else:
        config_path = metadata.readme

    # here, we show a prompt for each field in metadata.fields
    # and show the current value if it exists
    console = Console()
    for field in MANDATORY_FIELDS:
        value = metadata.fields.get(field, '[red]NOT SET[/red]')
        console.print(f'[bold]{field}[/bold]: [cyan]{value}[/cyan]')
        new_value = console.input(f'Enter a new value for {field}: ')

        if not new_value and not metadata.fields.get(field):
            print(f'[red]Field {field} MUST be set.[/red]')
            return
        metadata[field] = new_value

    metadata.log_change('Updated fields in README file.')

    if dry_run:
        metadata.write_to_file(config_path)
        console.print(metadata)


@cli.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument(
    'path',
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
def init(path: Path) -> None:
    """Initialize a new README file."""
    try:
        metadata = DMPMetadata.from_path(path)
        if metadata.readme.exists():
            print(f'Error: README file already exists at {metadata.readme}')
            return
    except ValueError:
        pass

    from rich.console import Console

    console = Console()
    new_readme_path = path / 'README.md'
    console.print(f'Creating a new README file at {new_readme_path}')

    fields = {fld: '' for fld in MANDATORY_FIELDS}
    # create the README file
    for fld in MANDATORY_FIELDS:
        while not fields[fld]:
            print(f'[red]Field {fld} MUST be set.[/red]')
            fields[fld] = console.input(f'Enter a value for {fld}: ')

    new_metadata = DMPMetadata(
        fields=fields,
        content='',
        path=path,
        permissions='---------',
        logs=[],
        readme=new_readme_path,
    )

    try:
        new_metadata.check_fields()
    except ValueError as e:
        print(f'Error: {e}')
        return

    console.print(new_metadata)


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
def size(path: Path) -> None:
    """Print the size of the directory."""
    try:
        metadata = DMPMetadata.from_path(path)
        metadata.check_fields()
    except ValueError as e:
        print(f'{e}')
        return

    size_dir = metadata.read_dirsize()
    from rich.console import Console
    console = Console()
    
    console.print(
        f"The size of [bold magenta]{path}[/bold magenta] is [bold cyan]{size_dir}[/bold cyan]"
    )
    print(metadata)


cli.add_command(audit)
cli.add_command(plot)


if __name__ == '__main__':
    cli()
