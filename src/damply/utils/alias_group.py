import rich_click as click

from click_didyoumean import DYMGroup

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