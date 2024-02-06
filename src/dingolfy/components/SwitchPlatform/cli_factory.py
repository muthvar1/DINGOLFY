from .LINK import cli_factory as LINK_cli_factory
from .LLDP import cli_factory as LLDP_cli_factory
from .MACSEC import cli_factory as MACSEC_cli_factory
from .PTP import cli_factory as PTP_cli_factory
from .BRINGUP import cli_factory as BRINGUP_cli_factory

import typer
app = typer.Typer()
#Add all the subcommands here
app.add_typer(LINK_cli_factory.app, name="link",help='Helps user collect platform level info for LINK Debugging')
app.add_typer(LLDP_cli_factory.app, name="lldp",help='Helps user collect platform level info for LLDP Debugging')
app.add_typer(MACSEC_cli_factory.app, name="macsec",help='Helps user collect platform level info for MACSEC Debugging')
app.add_typer(PTP_cli_factory.app, name="ptp",help='Helps user collect platform level info for PTP Debugging')
app.add_typer(BRINGUP_cli_factory.app, name="bringup",help='Helps user collect platform level info for BRINGUP Debugging')

if __name__ == "__main__":
    app()