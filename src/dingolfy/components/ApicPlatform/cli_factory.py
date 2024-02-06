from .BRINGUP import cli_factory as BRINGUP_cli_factory
from .UPGRADE import cli_factory as UPGRADE_cli_factory

import typer
app = typer.Typer()
#Add all the subcommands here
app.add_typer(BRINGUP_cli_factory.app, name="bringup",help='Helps user collect APIC platform level info for BRINGUP Debugging')
app.add_typer(UPGRADE_cli_factory.app, name="upgrade",help='Helps user collect APIC platform level info for UPGRADE Debugging')
if __name__ == "__main__":
    app()