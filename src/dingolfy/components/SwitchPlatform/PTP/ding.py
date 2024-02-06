from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for PTP feature
    '''
    cmd = []
    cmd.append(f'show ptp brief')
    cmd.append(f'show ptp clock')
    cmd.append(f'show ptp corrections')
    cmd.append(f'show ptp clock foreign-master record')
    cmd.append(f'show ptp counters all')
    cmd.append(f'show ptp parent')
    cmd.append(f'show ptp time-property')
    cmd.append(f'show ptp port all')
    cmd.append(f'vsh -c "show tech-support ptp"')
    # cmd.append(f'cat /mnt/ifc/log/*ptp*')
    # cmd.append(f'cat /var/sysmgr/tmp_logs/*ptp*')
    sendCmd(cmd=cmd,leafName=leafName,timeout=360)

    

    
