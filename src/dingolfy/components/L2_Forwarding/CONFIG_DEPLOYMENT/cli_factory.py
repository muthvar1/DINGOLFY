from . import ding
from ....infra.utils import leafTable
import typer
app = typer.Typer()


@app.command()
def collect_logs(vlan: str = typer.Option(default=...,prompt="Please provide PI vlan id , eg: 256 "),
                 interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16"),
                  leafName: str = typer.Option(default=False,help='CD: Please provide leafName in format ifav21-leaf1')
                  ):
    '''
    Collect all necessary L2 Forwarding CONFIG DEPLOYMENT logs
    '''
    if not leafName: leafName = leafTable(messagePrefix='CD:')
    ding.collect_logs(vlan=vlan, interface=interface, leafName=leafName)




@app.command()
def show_vlan(vlan: str = typer.Option(default=...,prompt="Please provide PI vlan id , eg: 256 "),
               leafName: str = typer.Option(default=False,help='CD: Please provide leafName in format ifav21-leaf1'),
               extended: bool = typer.Option(default=False, prompt="Please opt for extended if bd-vnid deployment info is needed")):
    '''
    Check for Vlan and/and bd-vnid deployment in Leaf. If extended option is used,
    bd-vnid info is also provided
    show vlan id <vlan>
    show vlan id <vlan> extended
    '''
    if not leafName: leafName = leafTable(messagePrefix='CD:')
    ding.show_vlan(vlan=vlan,leafName=leafName, extended=extended)

@app.command()
def show_int(interface: str = typer.Option(default=...,prompt="Please provide interface id , eg: Eth1/16 "),
               leafName: str = typer.Option(default=False,help='CD: Please provide leafName in format ifav21-leaf1')):
    '''
    Check for interface deployment in Leaf
    show interface <> brief
    
    '''
    if not leafName: leafName = leafTable(messagePrefix='CD:')
    ding.show_int(interface=interface,leafName=leafName)

@app.command()
def validate_config():
    '''
    Given a list of user provided inputs, validate if the config is deployed correctly
    '''
    ding.validate_config()

if __name__ == "__main__":
    app()