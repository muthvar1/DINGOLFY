from ...infra.utils import sendCmd, sendCmdApic
from ...infra.globals import handles, dingolfyGlobal
from ...infra import richWrapper
from typing import Optional


def collect_logs(leafName: Optional[str] = None):
    '''
    Collect all the logs to debug AAA related issues
    '''
    fileName = 'nginx.bin.log'
    remote_path = '/var/log/dme/log/nginx.bin.log'
    local_path = '/root/'
    local_filename = f'{local_path}{fileName}'
    handles.apic_ssh_handle.scp_remote_to_local(remote_path=remote_path,local_path=local_path)

    richWrapper.console.print(f'AAA nginx log file location for apic:{local_filename}')
    dingolfyGlobal.FilesToUpload.append(local_filename)
    for handle in handles.leaf_ssh_handles:
        if leafName not in ['all', None,""]:
            if handle.name != leafName:
                continue
        fileName = f'{handle.name}_nginx_bin.log'
        remote_path = '/tmp/logs/dme_logs/nginx.log'
        local_path = '/root/'
        local_filename = f'{local_path}{fileName}'
        handle.scp_remote_to_local(remote_path=remote_path,local_path=local_path,local_filename=fileName)
        richWrapper.console.print(f'AAA nginx log file location for switch:{handle.name}:{local_filename}')
        dingolfyGlobal.FilesToUpload.append(local_filename)

        fileName = f'{handle.name}_pam_module.log'
        remote_path = '/var/sysmgr/tmp_logs/pam.module.log'
        local_path = '/root/'
        local_filename = f'{local_path}{fileName}'
        handle.scp_remote_to_local(remote_path=remote_path,local_path=local_path,local_filename=fileName)
        richWrapper.console.print(f'AAA pam.module log file location for switch:{handle.name}:{local_filename}')
        dingolfyGlobal.FilesToUpload.append(local_filename)




    

    
