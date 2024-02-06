from . import ding
from ....infra.utils import leafTable
import typer
app = typer.Typer()


@app.command()
def collect_logs(interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 "),
                 vlan: str = typer.Option(default="",prompt='Please provide PI vlan id , eg: 256 '),
                 access_encap: str = typer.Option(default="",prompt='Please provide access encap vlan id , eg: 256 '),
                 leafName: str = typer.Option(default=False,help='ELTMC: Please provide leafName in format ifav21-leaf1')
                  ):
    '''
    Collect all necessary L2 Forwarding CONFIG DEPLOYMENT logs
    '''
    if not leafName: leafName = leafTable(messagePrefix='ELTMC:')
    ding.collect_logs(interface=interface, vlan=vlan,access_encap=access_encap, leafName=leafName)




@app.command()
def eltmc_interface(interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 "),
           leafName: str = typer.Option(default=False,help='ELTMC: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    show system internal eltmc info interface ethernet 1/5
    '''
    if not leafName: leafName = leafTable(messagePrefix='ELTMC:')
    ding.eltmc_interface(interface=interface,leafName=leafName)

@app.command()
def eltmc_vlan(vlan: str = typer.Option(default="",prompt='Please provide PI vlan id , eg: 256 '),
               leafName: str = typer.Option(default=False,help='ELTMC: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    show system internal eltmc info vlan 14
    '''
    if not leafName: leafName = leafTable(messagePrefix='ELTMC:')
    ding.eltmc_vlan(vlan=vlan,leafName=leafName)

@app.command()
def eltmc_access_encap(access_encap: str = typer.Option(default="",prompt='Please provide access encap vlan id , eg: 256 '),
           leafName: str = typer.Option(default=False,help='ELTMC: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    show system internal eltmc info vlan access_encap_vlan <>
    '''
    if not leafName: leafName = leafTable(messagePrefix='ELTMC:')
    ding.eltmc_access_encap(access_encap=access_encap,leafName=leafName)


if __name__ == "__main__":
    app()