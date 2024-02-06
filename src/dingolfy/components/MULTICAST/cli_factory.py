from . import ding
from ...infra.utils import leafTable, vrfTable, versionValidation
from ...infra import richWrapper
from . import ding
import typer
app = typer.Typer()




@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='MULTICAST: Please provide vrf name in format tn1:ctx1 or all'),
                 leafName: str = typer.Option(default=False,help='MULTICAST: Please provide leafName in format ifav21-leaf1'),
                 version: str = typer.Option(default="4",prompt='Please provide version 4 or 6',callback=versionValidation),
                 grp: str = typer.Option(default="",prompt="Please provide multicast group ip address in format 228.1.1.12"),
                 vlan: str = typer.Option(default="",prompt="Please provide vlan id"),
                 subFeature: str = typer.Option(default="",prompt="Please provide subFeature name IGMP/PIM/FABRIC_MULTICAST/MFDM/L2-MCAST")):

    '''
    Collect all necessary MCAST logs that are documented in the MCAST Debugging QA Wiki
    https://wiki.cisco.com/pages/viewpage.action?pageId=1530299502
    
    '''
    if not vrf: vrf = vrfTable(messagePrefix='EPM:')
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.collect_logs(vrf=vrf,leafName=leafName, version=version, grp=grp, vlan=vlan,subFeature=subFeature)


if __name__ == "__main__":
    app()