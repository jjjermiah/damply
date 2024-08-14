import rich_click as click
from rich import print

from damply.plot import damplyplot
from damply.cli.click_config import help_config

from pathlib import Path

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
)
@click.option('--threshold_gb', type=int, default=100)
@click.option('--fig_width', type=int, default=3340)
@click.option('--fig_height', type=int, default=1440)
@click.rich_config(help_config=help_config)
def plot(
    path: Path,
    threshold_gb: int = 100,
    fig_width: int = 3340,
    fig_height: int = 1440,
) -> None:
    """Plot the results of a damply audit using the path to the output csv file."""
    output_path = damplyplot(
        file_path=path,
        threshold_gb=threshold_gb,
        fig_width=fig_width,
        fig_height=fig_height,
    )
    print(f'The plot is saved to {output_path}')
