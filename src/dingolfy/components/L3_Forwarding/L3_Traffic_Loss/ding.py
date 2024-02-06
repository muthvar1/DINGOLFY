import ipaddress
from ....infra.utils import sendCmd
from typing import Optional
from ..ARP_ND import ding as ARP_ND_ding
from ..STATIC_ROUTE import ding as STATIC_ROUTE_ding


def collect_logs(vrf:str, ip: Optional[str] = None, version: Optional[str] = None, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for BGP debug
    '''
    if version in ['4',None,""]:
        ip_route(vrf=vrf,ip=ip,leafName=leafName)
        ospfRoute(vrf=vrf,leafName=leafName)
        bgpRoute(vrf=vrf,leafName=leafName)
    if version in ['6',None,""]:
        ipv6_route(vrf=vrf,ip=ip,leafName=leafName)
        ospfv3Route(vrf=vrf,leafName=leafName)
        bgpv6Route(vrf=vrf,leafName=leafName)
    if ip not in [None,""]:
        forwardingRoute(vrf=vrf,ip=ip,leafName=leafName)
        ARP_ND_ding.hal_l3_routes(vrf=vrf,ip=ip,leafName=leafName)

def ip_route(vrf:str,ip: str, leafName: Optional[str] = 'all'):
    '''
    show ip route <x.x.x.> vrf <>
    '''
    cmd=f'show ip route {ip} vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ipv6_route(vrf:str,ip: str, leafName: Optional[str] = 'all'):
    '''
    show ipv6 route <x.x.x.> vrf <>
    '''
    cmd=f'show ipv6 route {ip} vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)


def ospfRoute(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf route vrf <>
    '''
    cmd=f'show ip ospf route vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv3Route(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ipv6 ospfv3 route vrf <>
    '''
    cmd=f'show ipv6 ospfv3 route vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgpRoute(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv4 unicast vrf <>
    '''
    cmd=f'show bgp ipv4 unicast vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgpv6Route(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv6 unicast vrf <>
    '''
    cmd=f'show bgp ipv6 unicast vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def forwardingRoute(vrf:str,ip: str, leafName: Optional[str] = 'all'):
    '''
    vsh_lc -c "show forwarding route vrf  <>" | grep <ip/ipv6
    '''
    cmd=f'vsh_lc -c "show forwarding route vrf {vrf}" | grep {ip}'
    sendCmd(cmd=cmd,leafName=leafName)

