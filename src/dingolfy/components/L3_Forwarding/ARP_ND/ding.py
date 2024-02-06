from ....infra.utils import sendCmd
from typing import Optional

def collect_logs(vrf:str, ip:Optional[str] = None, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for ARP/ND debug
    '''
    arp_detail(vrf=vrf, leafName=leafName)
    arp_statistics(vrf=vrf, leafName=leafName)
    ipv6_adjacency(vrf=vrf, leafName=leafName)
    if ip:
        forwarding_ipv6_adjacency(ip=ip,leafName=leafName)
        hal_l3_routes(vrf=vrf,ip=ip,leafName=leafName)  

def arp_detail(vrf:str,leafName:str):
    '''
    show ip arp detail vrf <>
    '''
    cmd=f'show ip arp detail vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

    


def arp_statistics(vrf:str,leafName: str):
    '''
    show ip arp statistics vrf <>
    '''
    cmd=f'show ip arp statistics vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)
    


def ipv6_adjacency(vrf:str, leafName: str):
    '''
    show ipv6 adjacency detail vrf <>
    '''
    cmd=f'show ipv6 adjacency detail vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)
    


def forwarding_ipv6_adjacency(ip:str, leafName: str):
    '''
    show forwarding ipv6 adjacency <ip/ipv6>
    '''
    cmd=f'show forwarding ipv6 adjacency {ip}'
    sendCmd(cmd=cmd,leafName=leafName)


def hal_l3_routes(vrf:str,ip:str, leafName: str):
    '''
    vsh_lc -c "show platform internal hal l3 routes vrf t13:ctx0" | grep <ip/ipv6>
    '''
    cmd=f'vsh_lc -c "show platform internal hal l3 routes vrf {vrf}" | grep {ip}'
    sendCmd(cmd=cmd,leafName=leafName)