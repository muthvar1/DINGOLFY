from . import ding
from ....infra.utils import vrfTable,leafTable, vrf_options,leaf_callback,leaf_options, ipValidation, versionValidation
import typer
import ipaddress
from ..ARP_ND import ding as ARP_ND_ding
app = typer.Typer()



@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='SRTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='SRTE: Please provide leafName in format ifav21-leaf1')
                ):
    '''
    Collect all necessary OSPF logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='SRTE:')
    if not leafName: leafName = leafTable(messagePrefix='SRTE:')
    ding.collect_logs(vrf=vrf,leafName=leafName)




@app.command()
def arp_detail(vrf: str = typer.Option(default=False,help='SRTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='SRTE: Please provide leafName in format ifav21-leaf1')
                ):
    '''
    show ip arp detail vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='SRTE:')
    if not leafName: leafName = leafTable(messagePrefix='SRTE:')
    ARP_ND_ding.arp_detail(vrf=vrf,leafName=leafName)


@app.command()
def arp_statistics(vrf: str = typer.Option(default=False,help='SRTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='SRTE: Please provide leafName in format ifav21-leaf1')
                ):
    '''
    show ip arp statistics vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='SRTE:')
    if not leafName: leafName = leafTable(messagePrefix='SRTE:')
    ARP_ND_ding.arp_statistics(vrf=vrf,leafName=leafName)

@app.command()
def ipv6_adjacency(vrf: str = typer.Option(default=False,help='SRTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='SRTE: Please provide leafName in format ifav21-leaf1')
                ):
    '''
    show ipv6 adjacency detail vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='SRTE:')
    if not leafName: leafName = leafTable(messagePrefix='SRTE:')
    ARP_ND_ding.ipv6_adjacency(vrf=vrf,leafName=leafName)

@app.command()
def ip_staticRoute(vrf: str = typer.Option(default=False,help='SRTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='SRTE: Please provide leafName in format ifav21-leaf1')
                ):
    '''
    show ip static-route vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='SRTE:')
    if not leafName: leafName = leafTable(messagePrefix='SRTE:')
    ARP_ND_ding.ip_staticRoute(vrf=vrf,leafName=leafName)

@app.command()
def ipv6_staticRoute(vrf: str = typer.Option(default=False,help='SRTE: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='SRTE: Please provide leafName in format ifav21-leaf1')
                ):
    '''
    show ipv6 static-route vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='SRTE:')
    if not leafName: leafName = leafTable(messagePrefix='SRTE:')
    ARP_ND_ding.ipv6_staticRoute(vrf=vrf,leafName=leafName)

if __name__ == "__main__":
    app()