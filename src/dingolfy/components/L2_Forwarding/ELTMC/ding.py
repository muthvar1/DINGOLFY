from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(interface:Optional[str] = None, vlan: Optional[str] = None, access_encap: Optional[str] = None, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for L2 Forwarding ELTMC logs
    '''
    if interface not in [None,""]:
        eltmc_interface(interface=interface,leafName=leafName)
    if vlan not in [None,""]:
        eltmc_vlan(vlan=vlan,leafName=leafName)
    if access_encap not in [None,""]:
        eltmc_access_encap(access_encap=access_encap,leafName=leafName)
    

def eltmc_interface(interface:str,leafName: Optional[str] = 'all'):
    '''
     or the actual encap (for actual encap vlan use the cli: module-1# show system internal eltmc info vlan access_encap_vlan <>)
    show system internal eltmc info interface ethernet 1/5
    '''
    cmd=f'vsh_lc -c "show system internal eltmc info interface {interface}"'
    sendCmd(cmd=cmd,leafName=leafName)

def eltmc_vlan(vlan:str,leafName: Optional[str] = 'all'):
    '''
    fabric_encap, native vlan tag, access vlan tag, ifindex, feature interaction info like storm control etc are available in this command
    for vlan id, you have to use PI vlan id
    show system internal eltmc info vlan 14
    '''
    cmd=f'vsh_lc -c "show system internal eltmc info vlan {vlan}"'
    sendCmd(cmd=cmd,leafName=leafName)

def eltmc_access_encap(access_encap:str,leafName: Optional[str] = 'all'):
    '''
    fabric_encap, native vlan tag, access vlan tag, ifindex, feature interaction info like storm control etc are available in this command
    for vlan id, you have to use actual encap
    show system internal eltmc info vlan access_encap_vlan <>
    '''
    cmd=f'vsh_lc -c "show system internal eltmc info vlan access_encap_vlan {access_encap}"'
    sendCmd(cmd=cmd,leafName=leafName)
