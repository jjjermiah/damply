import rich_click as click


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
            'name': 'Info Commands',
            'commands': ['view', 'whose', 'add-field', 'log', 'config', 'init', 'size'],
        },
        {
            'name': 'Audit Commands',
            'commands': ['audit', 'plot', ],
        }
    ]
}


help_config = click.RichHelpConfiguration(
    show_arguments=True,
    option_groups={'damply': [{'name': 'Arguments', 'panel_styles': {'box': 'ASCII'}}]},
)
