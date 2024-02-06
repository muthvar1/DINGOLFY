from . import ding
from ....infra.utils import vrfTable,leafTable
import typer
import ipaddress
from ..L3_Traffic_Loss import ding as L3_Traffic_Loss_ding
app = typer.Typer()



@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='BFD: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BFD: Please provide leafName in format ifav21-leaf1',),
                srcip:str = typer.Option(default="",prompt="Please provide interested BFD src ipv4/ipv6address, eg: 1.1.1.1"),
                dstip:str = typer.Option(default="",prompt="Please provide interested BFD dst ipv4/ipv6address, eg: 1.1.1.1"),
                ):
    '''
    Collect all necessary BFD logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BFD:')
    if not leafName: leafName = leafTable(messagePrefix='BFD:')
    ding.collect_logs(vrf=vrf,srcip=srcip,dstip=dstip,leafName=leafName)








if __name__ == "__main__":
    app()