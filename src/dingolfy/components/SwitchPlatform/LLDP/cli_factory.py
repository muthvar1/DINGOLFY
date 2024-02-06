from . import ding
from ....infra.utils import leafTable
from ....infra import richWrapper
import typer
app = typer.Typer()


@app.command()
def collect_logs(leafName: str = typer.Option(default=False,help='LLDP: Please provide leafName in format ifav21-leaf1'),
                 interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 ")
                 
                  ):
    '''
    Collect all necessary LLDP logs
    '''
    if not leafName: leafName = leafTable(messagePrefix='LLDP:')
    ding.collect_logs(interface=interface, leafName=leafName)


@app.command()
def lldp_traffic(leafName: str = typer.Option(default=False,help='LLDP: Please provide leafName in format ifav21-leaf1'), 
                 interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 ")):
    '''
    show lldp traffic on interface
    '''
    if not leafName: leafName = leafTable(messagePrefix='LLDP:')
    ding.lldp_traffic(leafName=leafName,interface=interface)

@app.command()
def platform_counters(leafName: str = typer.Option(default=False,help='LLDP: Please provide leafName in format ifav21-leaf1'), 
                 interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 ")):
    '''
    show platform counters on interface
    '''
    if not leafName: leafName = leafTable(messagePrefix='LLDP:')
    ding.platform_counters(leafName=leafName,interface=interface)

@app.command()
def lldp_summary(leafName: str = typer.Option(default=False,help='LLDP: Please provide leafName in format ifav21-leaf1')):
    '''
    show lldp summary on leaf
    '''
    if not leafName: leafName = leafTable(messagePrefix='LLDP:')
    ding.lldp_summary(leafName=leafName)

@app.command()
def copp_stats(leafName: str = typer.Option(default=False,help='LLDP: Please provide leafName in format ifav21-leaf1')):
    '''
    show copp policy stats on leaf
    '''
    if not leafName: leafName = leafTable(messagePrefix='LLDP:')
    ding.copp_stats(leafName=leafName)


    

if __name__ == "__main__":
    app()