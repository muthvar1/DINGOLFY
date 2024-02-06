from . import ding
from ....infra.utils import vrfTable, vrf_options,leaf_options, ipValidation, versionValidation, leafTable
import typer

app = typer.Typer()

# def vrf_callback(value:str):
#     vrfList = ['tn1:ctx1', 'tn1:ctx2']
    
#     if value not in ['tn1:ctx1', 'tn1:ctx2']:
#         raise typer.BadParameter(f"Only {vrfList} is allowed")
#     return value


@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='BGP: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BGP: Please provide leafName in format ifav21-leaf1',),
                version: str = typer.Option(default='4',prompt='BGP: Please provide ip version 4/6',callback=versionValidation),
                neighbor_ip:str = typer.Option(default="",prompt="BGP: Please provide bgp neighbor_ip, eg: 1.1.1.1 ",callback=ipValidation),
                prefix: str = typer.Option(default="",prompt="BGP: Please provide prefix, eg:2002:1:1a1::/64 or 2.2.2.2/24)")
                ):
    '''
    Collect all necessary BGP logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BGP:')
    if not leafName: leafName = leafTable(messagePrefix='BGP:')
    if not prefix: prefix = None
    ding.collect_logs(vrf=vrf,neighbor_ip=neighbor_ip,leafName=leafName,version=version,prefix=prefix)




@app.command()
def bgp_detail(vrf: str = typer.Option(default=False,help='BGP: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BGP: Please provide leafName in format ifav21-leaf1')
                  ):
    '''
    show bgp vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BGP:')
    if not leafName: leafName = leafTable(messagePrefix='BGP:')
    ding.bgp_detail(vrf=vrf,leafName=leafName)


@app.command()
def bgp_sessions(vrf: str = typer.Option(default=False,help='BGP: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BGP: Please provide leafName in format ifav21-leaf1')
                  ):
    '''
    show bgp sessions vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BGP:')
    if not leafName: leafName = leafTable(messagePrefix='BGP:')
    
        
    ding.bgp_sessions(vrf=vrf,leafName=leafName)


@app.command()
def bgp_neighbors(vrf: str = typer.Option(default=False,help='BGP: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='BGP: Please provide leafName in format ifav21-leaf1'),
                version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation),
                ):
    '''
    show ip/ipv6 bgp neighbors vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='BGP:')
    if not leafName: leafName = leafTable(messagePrefix='BGP:')
    if version == '4':
        ding.bgp_neighbors(vrf=vrf,leafName=leafName)
    else:
        ding.bgp_v6neighbors(vrf=vrf,leafName=leafName)

@app.command()
def bgp_event_history(neighbor_ip: str = typer.Option(default=...,prompt='Please provide neighbor ip',callback=ipValidation),
                leafName: str = typer.Option(default=False,help='BGP: Please provide leafName in format ifav21-leaf1')
                  ):
    '''
    vsh -c "show bgp event-history events" | grep <ip>
    '''
    if not leafName: leafName = leafTable(messagePrefix='BGP:')
    ding.bgp_event_history(neighbor_ip=neighbor_ip, leafName=leafName)

if __name__ == "__main__":
    app()