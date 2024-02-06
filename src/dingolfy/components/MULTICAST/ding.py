import ipaddress
from ...infra.utils import sendCmd
from ...infra import richWrapper
from typing import Optional

def collect_logs(vrf: Optional[str] = 'all', leafName: Optional[str] = 'all',
                 grp: Optional[str] = None, version: Optional[str] = '4',
                 vlan: Optional[str] = None, subFeature: Optional[str] = None):
    
    richWrapper.console.print(f'Collecting MCAST logs for vrf: {vrf}, leafName: {leafName}, grp: {grp}, version: {version}, vlan: {vlan}, subFeature: {subFeature}')
    if subFeature == 'IGMP':
        show_groups(vrf=vrf, leafName=leafName, version=version)
    
    elif subFeature == 'PIM':
        show_mroute(vrf=vrf, leafName=leafName, version=version)
        show_pim_neighbor(vrf=vrf, leafName=leafName, version=version)
        show_pim_rp(vrf=vrf, leafName=leafName, version=version)
        show_pim_event_history(leafName=leafName, version=version)
        if grp not in [None,'']: show_pim_route(vrf=vrf, leafName=leafName, grp=grp, version=version)
        show_pim_interface(vrf=vrf, leafName=leafName, version=version)

    
    elif subFeature == 'FABRIC_MULTICAST':
        if grp not in [None,'']: show_fabric_multicast_mroute(vrf=vrf, leafName=leafName, grp=grp, version=version)
        show_fabric_multicast_vrf(vrf=vrf, leafName=leafName)
        show_active_bl(vrf=vrf, leafName=leafName)

    elif subFeature == 'MFDM':
        if grp not in [None,'']: show_forwarding_distribution(vrf=vrf, leafName=leafName, grp=grp, version=version)
        show_bd_gipo(leafName=leafName)
    
    elif subFeature == 'L2-MCAST':
        show_igmp_snooping_groups(leafName=leafName, version=version)
        if vlan not in [None,'']: show_igmp_snooping_vlans(leafName=leafName, version=version, vlan=vlan)

    else:
        show_groups(vrf=vrf, leafName=leafName, version=version)
        show_mroute(vrf=vrf, leafName=leafName, version=version)
        show_pim_neighbor(vrf=vrf, leafName=leafName, version=version)
        show_pim_rp(vrf=vrf, leafName=leafName, version=version)
        show_pim_event_history(leafName=leafName, version=version)
        if grp not in [None,'']: show_pim_route(vrf=vrf, leafName=leafName, grp=grp, version=version)
        show_pim_interface(vrf=vrf, leafName=leafName, version=version)
        if grp not in [None,'']: show_fabric_multicast_mroute(vrf=vrf, leafName=leafName, grp=grp, version=version)
        show_fabric_multicast_vrf(vrf=vrf, leafName=leafName)
        show_active_bl(vrf=vrf, leafName=leafName)
        if grp not in [None,'']: show_forwarding_distribution(vrf=vrf, leafName=leafName, grp=grp, version=version)
        show_bd_gipo(leafName=leafName)
        show_igmp_snooping_groups(leafName=leafName, version=version)
        if vlan not in [None,'']: show_igmp_snooping_vlans(leafName=leafName, version=version, vlan=vlan)

def show_groups(vrf: str, leafName: str, version: str):
    '''
    if version is 4, then use cmd, show ip igmp groups vrf <vrf>
    if version is 6, then use cmd, show ipv6 mld groups vrf <vrf>
    '''
    if version == '4':
        cmd = f'show ip igmp groups vrf {vrf}'
    elif version == '6':
        cmd = f'show ipv6 mld groups vrf {vrf}'
    sendCmd(cmd, leafName)

def show_mroute(vrf: str, leafName: str, version: str):
    '''
    if version is 4, then use cmd, show ip mroute vrf <vrf>
    if version is 6, then use cmd, show ipv6 mroute vrf <vrf>
    '''
    if version == '4':
        cmd = f'show ip mroute vrf {vrf}'
    elif version == '6':
        cmd = f'show ipv6 mroute vrf {vrf}'
    sendCmd(cmd, leafName)

def show_pim_neighbor(vrf: str, leafName: str, version: str):
    '''
    if version is 4, then use cmd, show ip pim neighbor vrf <vrf>
    if version is 6, then use cmd, show ipv6 pim neighbor vrf <vrf>
    '''
    if version == '4':
        cmd = f'show ip pim neighbor vrf {vrf}'
    elif version == '6':
        cmd = f'show ipv6 pim neighbor vrf {vrf}'
    sendCmd(cmd, leafName)

def show_pim_rp(vrf: str, leafName: str, version: str):
    '''
    if version is 4, then use cmd, show ip pim rp vrf <vrf>
    if version is 6, then use cmd, show ipv6 pim rp vrf <vrf>
    '''
    if version == '4':
        cmd = f'show ip pim rp vrf {vrf}'
    elif version == '6':
        cmd = f'show ipv6 pim rp vrf {vrf}'
    sendCmd(cmd, leafName)

def show_pim_event_history(leafName: str, version: str):
    '''
    if version is 4, then use cmd, show ip pim event-history join-prune
    if version is 6, then use cmd, show ipv6 pim event-history join-prune
    '''
    if version == '4':
        cmd = f'show ip pim event-history join-prune'
    elif version == '6':
        cmd = f'show ipv6 pim event-history join-prune'
    sendCmd(cmd, leafName)

def show_fabric_multicast_mroute(vrf: str, leafName: str, grp: str, version: str):
    '''
    if version is 4, then use cmd, show fabric multicast ipv4 mroute  <grp> vrf <vrf>
    if version is 6, then use cmd, show fabric multicast ipv6 mroute  <grp> vrf <vrf>
    '''
    if version == '4':
        cmd = f'show fabric multicast ipv4 mroute {grp} vrf {vrf}'
    elif version == '6':
        cmd = f'show fabric multicast ipv6 mroute {grp} vrf {vrf}'
    sendCmd(cmd, leafName)

def show_pim_route(vrf: str, leafName: str, grp: str, version: str):
    '''
    if version is 4, then use cmd, show ip pim route internal detail vrf <vrf> | grep -A 14  <grp>
    if version is 6, then use cmd, show ipv6 pim route internal detail vrf<vrf>| grep -A 20  <grp>
    '''
    if version == '4':
        cmd = f'show ip pim route internal detail vrf {vrf} | grep -A 14 {grp}'
    elif version == '6':
        cmd = f'show ipv6 pim route internal detail vrf {vrf} | grep -A 20 {grp}'

def show_forwarding_distribution(vrf: str, leafName: str, grp: str, version: str):
    '''
    if version is 4, then use cmd, show forwarding distribution multicast route vrf  <vrf> group <grp>
    if version is 6, then use cmd, show forwarding distribution ipv6 multicast route <vrf> group <grp>
    '''
    if version == '4':
        cmd = f'show forwarding distribution multicast route vrf {vrf} group {grp}'
    elif version == '6':
        cmd = f'show forwarding distribution ipv6 multicast route {vrf} group {grp}'
    sendCmd(cmd, leafName)

def show_pim_interface(vrf:str, leafName: str, version: str):
    '''
    if version is 4, then use cmd, show ip pim interface vrf <vrf>
    if version is 6, then use cmd, show ipv6 pim interface vrf <vrf>
    '''
    if version == '4':
        cmd = f'show ip pim interface vrf {vrf}'
    elif version == '6':
        cmd = f'show ipv6 pim interface vrf {vrf}'
    sendCmd(cmd, leafName)

def show_fabric_multicast_vrf(vrf: str, leafName: str):
    '''
    show fabric multicast vrf <vrf>
    '''
    cmd = f'show fabric multicast vrf {vrf}'
    sendCmd(cmd, leafName)

def show_active_bl(vrf:str, leafName:str):
    '''
    show fabric multicast internal active-bl-list vrf <vrf>
    '''
    cmd = f'show fabric multicast internal active-bl-list vrf {vrf}'
    sendCmd(cmd, leafName)

def show_bd_gipo(leafName):
    '''
    show forwarding distribution multicast bd_gipo
    ''' 
    cmd = f'show forwarding distribution multicast bd_gipo'
    sendCmd(cmd, leafName)

def show_igmp_snooping_groups(leafName: str,version: str):
    '''
    if version is 4, then use cmd, show ip igmp snooping groups
    if version is 6, then use cmd, show ipv6 mld snooping groups
    '''
    if version == '4':
        cmd = f'show ip igmp snooping groups'
    elif version == '6':
        cmd = f'show ipv6 mld snooping groups'
    sendCmd(cmd, leafName)

def show_igmp_snooping_vlans(leafName: str,version: str, vlan: str):
    '''
    if version is 4, then use cmd, show ip igmp snooping querier vlan <vlan>
    if version is 6, then use cmd, show ipv6 mld snooping querier vlan <vlan>
    '''
    if version == '4':
        cmd = f'show ip igmp snooping querier vlan {vlan}'
    elif version == '6':
        cmd = f'show ipv6 mld snooping querier vlan {vlan}'
    sendCmd(cmd, leafName)

    