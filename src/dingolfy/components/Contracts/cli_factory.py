from . import ding
from ...infra.utils import leaf_options
from ...infra import richWrapper
import typer
app = typer.Typer()


@app.command()
def collect_logs(vrf: str = typer.Option(default=None,help='Contracts: Please provide vrf name in format tn1:ctx1 or all'),
                       leafName: str = typer.Option(default=None,help='Contracts: Please provide leaf name: eg: ifav21-leaf1'),
                       srcEpg: str = typer.Option(default=None,help='Contracts: Please provide source EPG name in the format tenantName:ApName:EpgName, e.g: t18:a18:epg18'),
                       dstEpg: str = typer.Option(default=None,help='Contracts: Please provide destination EPG name in the format tenantName:ApName:EpgName, e.g: t18:a18:epg18')):
    '''
    Collect all necessary APIC BRINGUP logs
    '''
    ding.collect_logs(vrf=vrf,leafName=leafName,srcEpg=srcEpg,dstEpg=dstEpg)
   

if __name__ == "__main__":
    app()