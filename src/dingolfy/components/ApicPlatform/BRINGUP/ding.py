from ....infra.utils import sendCmd, sendCmdApic
from ....infra.globals import handles
from ....infra import richWrapper
from typing import Optional


def collect_logs():
    '''
    Collect all the logs to debug APIC BRINGUP related issues
    '''
    cmd = []
    cmd.append('avread')
    cmd.append('acidiag fnvread')
    cmd.append('acidiag rvreadle')
    cmd.append('ethtool eth2-1')
    cmd.append('ethtool eth2-2')
    cmd.append('cluster health')
    cmd.append('cat /proc/net/bonding/bond0')
    cmd.append('show lldp')

    sendCmdApic(cmd = cmd, allApics = True)
    cmd = []
    cmd.append('acidiag avread')
    cmd.append('acidiag fnvread')
    cmd.append('show discoveryissues')
    cmd.append('show lldp neighbors')

    sendCmd(cmd = cmd, leafName='all')

    lldpAdj = handles.ifc_sdk_handle.lookupByClass('lldpAdjEp')
    for each in lldpAdj:
        if any(substring in each.sysName for substring in ['apic', 'ifc']):
            handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(each.dn))
    
    nodes = []
    for tS in handles.ifc_sdk_handle.lookupByClass('topSystem'):
        if tS.role in ['leaf','spine']:
            nodes.append(tS)

    for handle in handles.apic_ssh_handles:
        cmd = 'acidiag fnvread | grep active | wc -l'
        output = sendCmdApic(cmd = cmd, hostname = handle.hostname)
        for line in output.split('\n'):
            try:
                if int(line) != len(nodes):
                    richWrapper.console.error(f'{handle.hostname} has {line} active nodes whereas {len(nodes)} expected\nPLease check the output of acidiag fnvread below')
                    cmd = 'acidiag fnvread'
                    output = sendCmdApic(cmd = cmd, hostname = handle.hostname)
                    break
                else:
                    richWrapper.console.log(f'{handle.hostname} has {line} active nodes')
                    break
            except ValueError:
                continue
    
        else:
            richWrapper.console.error(f'{handle.hostname} did not return any output')
    
            
    
