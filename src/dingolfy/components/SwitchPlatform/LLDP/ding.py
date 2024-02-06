from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(leafName: Optional[str] = 'all',interface:Optional[str] = None):
    '''
    Collect all the logs for LLDP
    '''
    lldp_traffic(leafName=leafName, interface=interface)
    platform_counters(leafName=leafName, interface=interface)
    lldp_summary(leafName=leafName)
    copp_stats(leafName=leafName)

    

def lldp_traffic(leafName: Optional[str] = 'all', interface: Optional[str] = None):
    '''
    show lldp traffic on interface
    '''
    cmd=f'show lldp traffic interface {interface}'
    sendCmd(cmd=cmd,leafName=leafName)

def platform_counters(leafName: Optional[str] = 'all', interface: Optional[str] = None):
    '''
    show platform counters on interface
    '''
    portId = interface.split('/')[1]
    cmd=f'vsh_lc -c "show platform internal counters port {portId}"'
    sendCmd(cmd=cmd,leafName=leafName)

def lldp_summary(leafName: Optional[str] = 'all'):
    '''
    show lldp summary on leaf
    '''
    cmd=f'cat /mit/sys/copp/classp-lldp/summary'
    sendCmd(cmd=cmd,leafName=leafName)

def copp_stats(leafName: Optional[str] = 'all'):
    '''
    show copp policy stats on leaf
    '''
    cmd=f'show copp policy stats'
    sendCmd(cmd=cmd,leafName=leafName)

