from ....infra.utils import sendCmd, sendCmdApic
from ....infra.globals import handles
from typing import Optional
from ....infra import richWrapper


def collect_logs():
    '''
    Collect all the logs to debug APIC UPGRADE/DOWNGRADE related issues
    '''
    cmd = []
    cmd.append('show firmware upgrade status controller-group')
    cmd.append('df -h /firmware/')
    

    sendCmdApic(cmd = cmd, allApics = True)
    
    maintCtrlrMaintP = handles.ifc_sdk_handle.lookupByClass('maintCtrlrMaintP')
    for each in maintCtrlrMaintP:
        handles.ifc_sdk_handle.printMo(each)
    
    firmwareCtrlrFwP = handles.ifc_sdk_handle.lookupByClass('firmwareCtrlrFwP')
    for each in firmwareCtrlrFwP:
        handles.ifc_sdk_handle.printMo(each)
    
    maintUpgJob = handles.ifc_sdk_handle.lookupByClass('maintUpgJob')
    for each in maintUpgJob:
        handles.ifc_sdk_handle.printMo(each)

    firmwareFirmware = handles.ifc_sdk_handle.lookupByClass('firmwareFirmware')
    for each in firmwareFirmware:
        handles.ifc_sdk_handle.printMo(each)
    
    
