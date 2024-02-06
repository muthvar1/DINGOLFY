import ipaddress
from ....infra.utils import sendCmd
from typing import Optional

def collect_logs(vrf:str, neighbor_ip: Optional[str] = None, 
                 leafName: Optional[str] = 'all',version: Optional[str] = '4',
                 prefix: Optional[str] = None):
    '''
    Collect all the logs for BGP debug
    '''

    
    #bgp_detail(vrf=vrf,leafName=leafName)
    bgp_sessions(vrf=vrf,leafName=leafName)

    if version == '4':
        
        bgp_neighbors(vrf=vrf,leafName=leafName)
        bgp_unicast_neighbors(vrf=vrf,leafName=leafName)
        bgp_unicast_route(vrf=vrf,leafName=leafName)
        bgp_unicast_summary(vrf=vrf,leafName=leafName)

    else:
        bgp_v6neighbors(vrf=vrf,leafName=leafName)
        bgp_v6_unicast_neighbors(vrf=vrf,leafName=leafName)
        bgp_v6_unicast_route(vrf=vrf,leafName=leafName)
        bgp_v6_unicast_summary(vrf=vrf,leafName=leafName)
    if prefix not in [None,""]:
        #If the prefix is provided, then we will collect the logs for that prefix
        #If the prefix is an ipv4 prefix then collect using bgp_unicast_route_prefix
        #If the prefix is an ipv6 prefix then collect using bgp_v6_unicast_route_prefix
        # where prefix is in the format of 2002:1:1a1::/64 or 2.2.2.2/24
        if ipaddress.ip_network(str(prefix)).version == 4:
            bgp_unicast_route_prefix(prefix=prefix,vrf=vrf,leafName=leafName)
        else:
            bgp_v6_unicast_route_prefix(prefix=prefix,vrf=vrf,leafName=leafName)
                
           
    if neighbor_ip not in [None,""]:
        bgp_event_history(neighbor_ip=neighbor_ip,leafName=leafName)

    
    
    

def bgp_detail(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp vrf <>
    '''
    cmd=f'show bgp vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_sessions(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp sessions vrf <>
    '''
    cmd=f'show bgp sessions vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_neighbors(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip bgp neighbors vrf <>
    '''
    cmd=f'show ip bgp neighbors vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_v6neighbors(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ipv6 bgp neighbors vrf <>
    '''
    cmd=f'show ipv6 bgp neighbors vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_event_history(neighbor_ip:str,leafName: Optional[str] = 'all'):
    '''
    vsh -c "show bgp event-history events" | grep <ip>
    '''
    cmd=f'vsh -c "show bgp event-history events" | grep "{neighbor_ip}"'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_unicast_neighbors(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv4 unicast neighbors vrf <>
    '''
    cmd=f'show bgp ipv4 unicast neighbors vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_v6_unicast_neighbors(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv6 unicast neighbors vrf <>
    '''
    cmd=f'show bgp ipv6 unicast neighbors vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_unicast_summary(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv4 unicast summary vrf <>
    '''
    cmd=f'show bgp ipv4 unicast summary vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_v6_unicast_summary(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv6 unicast summary vrf <>
    '''
    cmd=f'show bgp ipv6 unicast summary vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_unicast_route(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv4 unicast vrf <>
    '''
    cmd=f'show bgp ipv4 unicast vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_v6_unicast_route(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv6 unicast vrf <>
    '''
    cmd=f'show bgp ipv6 unicast vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_unicast_route_prefix(prefix:str,vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv4 unicast <prefix> vrf <> 
    '''
    cmd=f'show bgp ipv4 unicast {prefix} vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def bgp_v6_unicast_route_prefix(prefix:str,vrf:str,leafName: Optional[str] = 'all'):
    '''
    show bgp ipv6 unicast <prefix> vrf <> 
    '''
    cmd=f'show bgp ipv6 unicast {prefix} vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)