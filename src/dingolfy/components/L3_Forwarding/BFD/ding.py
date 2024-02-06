import ipaddress
from ....infra.utils import sendCmd
from typing import Optional
from ..L3_Traffic_Loss import ding as L3_Traffic_Loss_ding


def collect_logs(vrf:str, srcip: Optional[str] = None,
                 dstip: Optional[str] = None, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for BFD debug
    '''
    
    
    
    if srcip not in [None,""] and dstip not in [None,""]:
        cmd = f'show bfd neighbors src-ip {srcip} dest-ip {dstip} vrf {vrf} details'
    if srcip not in [None,""] and dstip in [None,""]:
        cmd = f'show bfd neighbors src-ip {srcip} vrf {vrf} details'
    if srcip in [None,""] and dstip not in [None,""]:
        cmd = f'show bfd neighbors dest-ip {dstip} vrf {vrf} details'
    if srcip in [None,""] and dstip in [None,""]:
        cmd = f'show bfd neighbors vrf {vrf} details'

        
    
    sendCmd(cmd=cmd,leafName=leafName)

