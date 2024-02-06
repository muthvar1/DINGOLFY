import ipaddress
from ....infra.utils import sendCmd
from typing import Optional
from ..ARP_ND import ding as ARP_ND_ding

def collect_logs(vrf:str, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for BGP debug
    '''
    ARP_ND_ding.arp_detail(vrf=vrf,leafName=leafName)
    ARP_ND_ding.arp_statistics(vrf=vrf,leafName=leafName)
    ARP_ND_ding.ipv6_adjacency(vrf=vrf,leafName=leafName)
    ip_staticRoute(vrf=vrf,leafName=leafName)
    ipv6_staticRoute(vrf=vrf,leafName=leafName)
    

def ip_staticRoute(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip static-route vrf <>
    '''
    cmd=f'show ip static-route vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ipv6_staticRoute(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ipv6 static-route vrf <>
    '''
    cmd=f'show ipv6 static-route vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName) 