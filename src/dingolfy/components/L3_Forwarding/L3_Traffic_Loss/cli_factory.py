from . import ding
from ....infra.utils import vrfTable,leafTable, ipValidation, versionValidation
from ..utils import L3
import typer
import ipaddress
from ..ARP_ND import ding as ARP_ND_ding
from ..STATIC_ROUTE import ding as STATIC_ROUTE_ding


app = typer.Typer()



@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
                ip:str = typer.Option(default="",prompt="L3_TLOSS: Please provide interested ipv4/ipv6address, eg: 1.1.1.1",callback=ipValidation),
                ):
    '''
    Collect all necessary OSPF logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    try:
        if ipaddress.ip_address(str(ip)).version == 4:
            ding.collect_logs(vrf=vrf,ip=ip,version='4',leafName=leafName)
        else:
            ding.collect_logs(vrf=vrf,ip=ip,version='6',leafName=leafName)
    except ValueError as e:
            ding.collect_logs(vrf=vrf,ip=None,version='4',leafName=leafName)
            ding.collect_logs(vrf=vrf,ip=None,version='6',leafName=leafName)


@app.command()
def ip_route(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
            leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
            ip:str = typer.Option(default="",prompt="Please provide interested ipv4/ipv6address, eg: 1.1.1.1",callback=ipValidation),
            ):
    '''
    show ip/ipv6 arp detail vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    if ipaddress.ip_address(str(ip)).version == 4:
        ding.ip_route(vrf=vrf,ip=ip,leafName=leafName)
    else:
        ding.ipv6_route(vrf=vrf,ip=ip,leafName=leafName)


@app.command()
def ospfRoute(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
            leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
            version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation),
            ):
    '''
    show ip/ipv6 ospf/ospfv3 route vrf <>


    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    if version == '4':
        ding.ospfRoute(vrf=vrf,leafName=leafName)
    else:
        ding.ospfv3Route(vrf=vrf,leafName=leafName)


@app.command()
def bgpRoute(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
            leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
            version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation),
            ):
    '''
    show bgp ipv4/ipv6 unicast vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    if version == '4':
        ding.bgpRoute(vrf=vrf,leafName=leafName)
    else:
        ding.bgpv6Route(vrf=vrf,leafName=leafName)

@app.command()
def ip_staticRoute(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
            version: str = typer.Option(default='4',prompt='Please provide ip version 4/6',callback=versionValidation),
            ):
    '''
    show bgp ipv4/ipv6 unicast vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    if version == '4':
        STATIC_ROUTE_ding.ip_staticRoute(vrf=vrf,leafName=leafName)
    else:
        STATIC_ROUTE_ding.ipv6_staticRoute(vrf=vrf,leafName=leafName)

@app.command()
def forwardingRoute(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
            ip: str = typer.Option(default=...,prompt='Please provide interested ipv4/ipv6address, eg: 1.1.1.1',callback=ipValidation),
            ):
    '''
    show bgp ipv4/ipv6 unicast vrf <>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    ding.forwardingRoute(vrf=vrf,ip=ip,leafName=leafName)


@app.command()
def hal_l3_routes(vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='L3_TLOSS: Please provide leafName in format ifav21-leaf1',),
                  ip:str = typer.Option(default=...,prompt="Please provide ipv4/ipv6address, eg: 1.1.1.1",callback=ipValidation),
                  ):
    '''
    vsh_lc -c "show platform internal hal l3 routes vrf t13:ctx0" | grep <ip/ipv6>
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if not leafName: leafName = leafTable(messagePrefix='L3_TLOSS:')
    ARP_ND_ding.hal_l3_routes(vrf=vrf,ip=ip,leafName=leafName)






@app.command()
def locate_ip(ip:str = typer.Option(default=...,prompt="Please provide interested ipv4/ipv6address",callback=ipValidation),
                       vrf: str = typer.Option(default=False,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all')):
    '''
    Locate an externally learnt ip address.
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if vrf=='all':
        vrf = None
    L3.locate_ip(externalIp=ip,l3ctxName=vrf)

if __name__ == "__main__":
    app()