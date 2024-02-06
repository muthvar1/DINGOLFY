import ipaddress
from ....infra.utils import sendCmd
from typing import Optional

def collect_logs(vrf:str, neighbor_ip: Optional[str] = None, leafName: Optional[str] = 'all',version: Optional[str] = '4'):
    '''
    Collect all the logs for BGP debug
    '''
    if version == '4':
        ospf_info(vrf=vrf,leafName=leafName)
        ospf_neighbors(vrf=vrf, leafName=leafName)
        ospf_interface(vrf=vrf, leafName=leafName)
        ospf_traffic(vrf=vrf,leafName=leafName)
        ospfEventDebug(leafName=leafName)
        ospfDatabase(vrf=vrf,leafName=leafName)
        if neighbor_ip not in [None,""]:
            ospf_event_history(neighbor_ip=neighbor_ip,leafName=leafName)
    else:
        ospf_info(vrf=vrf,leafName=leafName)
        ospfv6_neighbors(vrf=vrf, leafName=leafName)
        ospfv6_interface(vrf=vrf, leafName=leafName)
        ospfv6_traffic(vrf=vrf,leafName=leafName)
        ospfv3EventDebug(leafName=leafName)
        ospfDatabase(vrf=vrf,leafName=leafName)
        if neighbor_ip not in [None,""]:
            ospfv6_event_history(neighbor_ip=neighbor_ip,leafName=leafName)
    

def ospf_info(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf vrf <>
    '''
    cmd=f'show ip ospf vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv3_info(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ipv6 ospf vrf <>
    '''
    cmd=f'show ipv6 ospf vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfDatabase(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf database vrf <>
    '''
    cmd=f'show ip ospf database vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv3Database(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ospfv3 database vrf <>
    '''
    cmd=f'show ospfv3 database vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)



def ospf_neighbors(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf neighbors vrf <>
    '''
    cmd=f'show ip ospf neighbors vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospf_traffic(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf traffic vrf <>
    '''
    cmd=f'show ip ospf traffic vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospf_interface(vrf:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf interface vrf <>
    '''
    cmd=f'show ip ospf interface vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospf_event_history(neighbor_ip:str,leafName: Optional[str] = 'all'):
    '''
    show ip ospf event-history event | grep <neighbor-ip>
    '''
    cmd=f'show ip ospf event-history event | grep {neighbor_ip}'
    sendCmd(cmd=cmd,leafName=leafName)


def ospfv6_neighbors(vrf:str,leafName:str):
    '''
    show ipv6 ospf neighbors vrf <>
    '''
    cmd=f'show ipv6 ospf neighbors vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv6_traffic(vrf:str,leafName:str):
    '''
    show ipv6 ospf traffic vrf <>
    '''
    cmd=f'show ipv6 ospf traffic vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv6_interface(vrf:str,leafName:str):
    '''
    show ipv6 ospf interface vrf <>
    '''
    cmd=f'show ipv6 ospf interface vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv6_event_history(neighbor_ip:str,leafName:str):
    '''
    show ipv6 ospf event-history event | grep <neighbor-ip>
    '''
    cmd=f'show ipv6 ospf event-history event | grep {neighbor_ip}'
    sendCmd(cmd=cmd,leafName=leafName)

def ospfEventDebug(leafName:str):
    '''
    show ip ospf event-history adjacency
    show ip ospf event-history detail
    show ip ospf event-history event
    show ip ospf event-history flooding
    show ip ospf event-history lsa
    show ip ospf event-history rib
    show ip ospf event-history msgs
    '''
    cmd = []
    cmd.append('show ip ospf event-history adjacency')
    cmd.append('show ip ospf event-history detail')
    cmd.append('show ip ospf event-history event')
    cmd.append('show ip ospf event-history flooding')
    cmd.append('show ip ospf event-history lsa')
    cmd.append('show ip ospf event-history rib')
    cmd.append('show ip ospf event-history msgs')
    
    sendCmd(cmd=cmd,leafName=leafName)

def ospfv3EventDebug(leafName: str):
    '''
    show ospfv3 event-history adjacency
    show ospfv3 event-history detail
    show ospfv3 event-history event
    show ospfv3 event-history flooding
    show ospfv3 event-history lsa
    show ospfv3 event-history rib
    show ospfv3 event-history msgs
    '''
    cmd = []
    cmd.append('show ospfv3 event-history adjacency')
    cmd.append('show ospfv3 event-history detail')
    cmd.append('show ospfv3 event-history event')
    cmd.append('show ospfv3 event-history flooding')
    cmd.append('show ospfv3 event-history lsa')
    cmd.append('show ospfv3 event-history rib')
    cmd.append('show ospfv3 event-history msgs')

    sendCmd(cmd=cmd,leafName=leafName)