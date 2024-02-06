from . import ding
from ....infra.utils import leafTable, vrfTable, ipValidation, versionValidation
import typer
import ipaddress
app = typer.Typer()



@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='OSPF: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='OSPF: Please provide leafName in format ifav21-leaf1',),
                version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation),
                neighbor_ip:str = typer.Option(default="",prompt="Please provide ospf neighbor_ip, eg: 1.1.1.1 ",callback=ipValidation),
                prefix: str = typer.Option(default="",prompt="Please provide interested ipv4/ipv6 prefix, eg:")
                ):
    '''
    Collect all necessary OSPF logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='OSPF:')
    if not leafName: leafName = leafTable(messagePrefix='OSPF:')
    ding.collect_logs(vrf=vrf,neighbor_ip=neighbor_ip,leafName=leafName,version=version,prefix=prefix)




@app.command()
def ospf_neighbors(vrf: str = typer.Option(default=False,help='OSPF: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='OSPF: Please provide leafName in format ifav21-leaf1',),
                version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation)
                  ):
    '''
    show ip ospf neighbors vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='OSPF:')
    if not leafName: leafName = leafTable(messagePrefix='OSPF:')
    if version == '4':
        ding.ospf_neighbors(vrf=vrf,leafName=leafName)
    elif version == '6':
        ding.ospfv6_neighbors(vrf=vrf,leafName=leafName)


@app.command()
def ospf_traffic(vrf: str = typer.Option(default=False,help='OSPF: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='OSPF: Please provide leafName in format ifav21-leaf1',),
                version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation)):
    '''
    show ip/ipv6 ospf traffic vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='OSPF:')
    if not leafName: leafName = leafTable(messagePrefix='OSPF:')
    if version == '4':
        ding.ospf_traffic(vrf=vrf,leafName=leafName)
    elif version == '6':
        ding.ospfv6_traffic(vrf=vrf,leafName=leafName)

@app.command()
def ospf_interface(vrf: str = typer.Option(default=False,help='OSPF: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='OSPF: Please provide leafName in format ifav21-leaf1',),
               version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation)
               ):
    '''
    show ip/ipv6 ospf interface vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='OSPF:')
    if not leafName: leafName = leafTable(messagePrefix='OSPF:')
    if version == '4':
        ding.ospf_interface(vrf=vrf,leafName=leafName)
    elif version == '6':
        ding.ospfv6_interface(vrf=vrf,leafName=leafName)

@app.command()
def ospf_event_history(leafName: str = typer.Option(default=False,help='OSPF: Please provide leafName in format ifav21-leaf1',),
               neighbor_ip: str = typer.Option(default=...,prompt='Please provide neighbor ip',callback=ipValidation)):
    '''
    show ip/ipv6 ospf event-history event | grep <neighbor-ip>
    '''
    if not leafName: leafName = leafTable(messagePrefix='OSPF:')
    if ipaddress.ip_address(str(neighbor_ip)).version == 4:
        ding.ospf_event_history(leafName=leafName,neighbor_ip=neighbor_ip)
    elif ipaddress.ip_address(str(neighbor_ip)).version == 6:
        ding.ospfv6_event_history(leafName=leafName,neighbor_ip=neighbor_ip)
    


    
if __name__ == "__main__":
    app()