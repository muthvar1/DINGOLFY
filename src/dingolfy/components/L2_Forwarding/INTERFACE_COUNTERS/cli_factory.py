from . import ding
from ....infra.utils import leafTable
import typer
app = typer.Typer()


@app.command()
def collect_logs(leafName: str = typer.Option(default=False,help='IC: Please provide leafName in format ifav21-leaf1')
                  ):
    '''
    Collect all necessary ARP/ND logs
    '''
    if not leafName: leafName = leafTable(messagePrefix='IC:')
    ding.collect_logs(leafName=leafName)





@app.command()
def interface_counters(leafName: str = typer.Option(default=False,help='IC: Please provide leafName in format ifav21-leaf1')):
    '''
    Platform Interface Counters to match the traffic ingress/egress in a Tor, to be executed in vsh_lc
    vsh_lc -c "show platform internal counters port nz"
    
    '''
    if not leafName: leafName = leafTable(messagePrefix='IC:')
    ding.interface_counters(leafName=leafName)

if __name__ == "__main__":
    app()