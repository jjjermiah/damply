import rich_click as click
from rich import print

from damply.cli.click_config import help_config
from pathlib import Path
from damply.metadata import MANDATORY_FIELDS, DMPMetadata


@click.command(context_settings={'help_option_names': ['-h', '--help']})
@click.argument(
    'path',
    type=click.Path(
        exists=False,
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

    if not path.exists():
        print(f'WARNING: Directory {path} does not exist. Creating it now.')
        path.mkdir(parents=True)


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

    new_metadata.write_to_file()
    console.print(new_metadata)