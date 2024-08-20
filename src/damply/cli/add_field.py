import rich_click as click
from rich import print
from pathlib import Path
from damply.metadata import MANDATORY_FIELDS, DMPMetadata

@click.command(context_settings={'help_option_names': ['-h', '--help']})
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
@click.argument(
    'field',
    type=str,
)
@click.argument(
    'value',
    type=str,
)
def add_field(path: Path, field: str, value: str) -> None:
    """Add a field to the README file."""
    
    if field.upper() in MANDATORY_FIELDS:
        print(f'Error: The field {field} is a mandatory field. Use the config command to modify it.')
        return
    try:
        metadata = DMPMetadata.from_path(path)
        metadata.check_fields()
    except ValueError as e:
        print(f'Error: No log entry added.\n{e}')
        return

    metadata.add_field(field, value)
    metadata.log_change(f'Added {field} to README file.')
    metadata.write_to_file()
