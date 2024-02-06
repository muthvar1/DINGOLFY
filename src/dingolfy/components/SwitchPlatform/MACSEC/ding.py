from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for MACSEC feature
    '''
    cmd = []
    cmd.append(f'show macsec policy')
    cmd.append(f'show macsec mka summary')
    cmd.append(f'show macsec mka session')
    cmd.append(f'show macsec mka session details')
    cmd.append(f'show macsec mka statistics')
    cmd.append(f'show macsec secy statistics')
    cmd.append(f'vsh -c "show tech-support macsec"')
    cmd.append(f'moquery -c macsecIf')
    cmd.append(f'moquery -c macsecFabIf')
    cmd.append(f'cat /var/sysmgr/tmp_logs/cts*')
    cmd.append(f'cat /mnt/ifc/log/cts.log.*')
    sendCmd(cmd=cmd,leafName=leafName,timeout=360)

    
