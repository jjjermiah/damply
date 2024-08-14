import rich_click as click
from rich import print
from pathlib import Path

from damply.audit import DirectoryAudit


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
def audit(path: Path) -> None:
    """Audit the metadata of a valid DMP Directory."""
    
    print("Auditing DMP Directory...")
    print("[bold red]This has not yet been implemented!!![/bold red]\n\n")
    print("[bold]Here is some summary info of the directory:[/bold]")
    
    try:
        audit = DirectoryAudit.from_path(path)
        print(audit)
    except ValueError as e:
        print(e)
        return
