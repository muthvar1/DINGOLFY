from . import ding
from ....infra.utils import vrfTable, leafTable, ipValidation, versionValidation
import typer
import ipaddress
from ..L3_Traffic_Loss import ding as L3_Traffic_Loss_ding
app = typer.Typer()



@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='BD_RTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BD_RTE: Please provide leafName in format ifav21-leaf1',),
                ip:str = typer.Option(default="",prompt="Please provide interested BD ipv4/ipv6address, eg: 1.1.1.1",callback=ipValidation),
                ):
    '''
    Collect all necessary OSPF logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BD_RTE:')
    if not leafName: leafName = leafTable(messagePrefix='BD_RTE:')
    if ipaddress.ip_address(str(ip)).version == 4:
        L3_Traffic_Loss_ding.ip_route(vrf=vrf,ip=ip,leafName=leafName)
    else:
        L3_Traffic_Loss_ding.ipv6_route(vrf=vrf,ip=ip,leafName=leafName)




@app.command()
def ip_route(vrf: str = typer.Option(default=False,help='BD_RTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BD_RTE: Please provide leafName in format ifav21-leaf1',),
            ip:str = typer.Option(default="",prompt="Please provide interested BD ipv4/ipv6address, eg: 1.1.1.1",callback=ipValidation),
            ):
    '''
    show ip/ipv6 arp detail vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BD_RTE:')
    if not leafName: leafName = leafTable(messagePrefix='BD_RTE:')

    if ipaddress.ip_address(str(ip)).version == 4:
        L3_Traffic_Loss_ding.ip_route(vrf=vrf,ip=ip,leafName=leafName)
    else:
        L3_Traffic_Loss_ding.ipv6_route(vrf=vrf,ip=ip,leafName=leafName)





if __name__ == "__main__":
    app()