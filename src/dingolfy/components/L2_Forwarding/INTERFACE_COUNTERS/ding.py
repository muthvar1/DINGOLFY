from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for L2 Forwarding interface counter logs
    '''
    interface_counters(leafName=leafName)
    



def interface_counters(leafName: Optional[str] = 'all'):
    '''
    Platform Interface Counters to match the traffic ingress/egress in a Tor, to be executed in vsh_lc
    vsh_lc -c "show platform internal counters port nz"
    '''
    cmd='vsh_lc -c "show platform internal counters port nz"'
    sendCmd(cmd=cmd,leafName=leafName)