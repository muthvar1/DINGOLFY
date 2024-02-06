from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(leafName: Optional[str] = 'all'):
    '''
    Collect all the logs to debug BRINGUP related issues
    '''
    cmd = []
    cmd.append(f'show version')
    cmd.append(f'show inventory')
    cmd.append(f'show cores')
    cmd.append(f'ls -lrth /logflash/core')
    cmd.append(f'show diagnostic result module all | grep -I “F” | grep -v “Test”')
    cmd.append(f'cat /mit/sys/summary | grep “in-service”')
    cmd.append(f'show module internal event-history module 1')
    cmd.append(f'show module internal activity module 1')
    cmd.append(f'show system internal platform internal event-history module 1')
    
    # show cores

    # ls -lrth /logflash/core

    # show diagnostic result module all | grep -I “F” | grep -v “Test”

    # cat /mit/sys/summary | grep “in-service”

    # show module internal event-history module 1

    # show module internal activity module 1

    # show system internal platform internal event-history module 1

    # show environment
    sendCmd(cmd=cmd,leafName=leafName)

    

    
