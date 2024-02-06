from . import ding
from ....infra.utils import ipValidation, vrfTable, leafTable
import typer
app = typer.Typer()




@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='ARP_ND: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='ARP_ND: Please provide leafName in format ifav21-leaf1',),
                  ip:str = typer.Option(default="",prompt="Please provide ipv4/ipv6address, eg: 1.1.1.1 ",callback=ipValidation),
                  
                  ):
    '''
    Collect all necessary ARP/ND logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='ARP_ND:')
    if not leafName: leafName = leafTable(messagePrefix='ARP_ND:')
    ding.collect_logs(vrf=vrf,ip=ip,leafName=leafName)




@app.command()
def arp_detail(vrf: str = typer.Option(default=False,help='ARP_ND: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='ARP_ND: Please provide leafName in format ifav21-leaf1',)):
    '''
    show ip arp detail vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='ARP_ND:')
    if not leafName: leafName = leafTable(messagePrefix='ARP_ND:')
    ding.arp_detail(vrf=vrf,leafName=leafName)

@app.command()
def arp_statistics(vrf: str = typer.Option(default=False,help='ARP_ND: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='ARP_ND: Please provide leafName in format ifav21-leaf1',)):
    '''
    show ip arp statistics vrf <>
    
    '''
    if not vrf: vrf = vrfTable(messagePrefix='ARP_ND:')
    if not leafName: leafName = leafTable(messagePrefix='ARP_ND:')
    ding.arp_statistics(vrf=vrf,leafName=leafName)
    

@app.command()
def ipv6_adjacency(vrf: str = typer.Option(default=False,help='ARP_ND: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='ARP_ND: Please provide leafName in format ifav21-leaf1',)):
    '''
    show ipv6 adjacency detail vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='ARP_ND:')
    if not leafName: leafName = leafTable(messagePrefix='ARP_ND:')
    ding.ipv6_adjacency(vrf=vrf,leafName=leafName)

@app.command()
def forwarding_ipv6_adjacency(ip:str = typer.Option(default=...,prompt="Please provide ipv4/ipv6address, eg: 1.1.1.1 "),
                              leafName: str = typer.Option(default=False,help='ARP_ND: Please provide leafName in format ifav21-leaf1',)):
    '''
    show forwarding ipv6 adjacency <ip/ipv6>
    '''
    if not leafName: leafName = leafTable(messagePrefix='ARP_ND:')
    ding.forwarding_ipv6_adjacency(ip=ip,leafName=leafName)

@app.command()
def hal_l3_routes(vrf: str = typer.Option(default=False,help='ARP_ND: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='ARP_ND: Please provide leafName in format ifav21-leaf1',),
                ip:str = typer.Option(default=...,prompt="Please provide ipv4/ipv6address, eg: 1.1.1.1",callback=ipValidation),
                ):
    '''
    vsh_lc -c "show platform internal hal l3 routes vrf t13:ctx0" | grep <ip/ipv6>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='ARP_ND:')
    if not leafName: leafName = leafTable(messagePrefix='ARP_ND:')
    ding.hal_l3_routes(vrf=vrf,ip=ip,leafName=leafName)

if __name__ == "__main__":
    app()

