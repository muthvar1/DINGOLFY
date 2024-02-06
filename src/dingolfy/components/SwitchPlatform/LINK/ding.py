from ....infra.utils import sendCmd
from typing import Optional


def collect_logs(leafName: Optional[str] = 'all',interface:Optional[str] = None):
    '''
    Collect all the logs LINK/Port debugging
    '''
    show_module(leafName=leafName)
    show_interface(leafName=leafName, interface=interface, viewOptions='all')
    show_usd_info(leafName=leafName, interface=interface, viewOptions='all')
    

def show_module(leafName: Optional[str] = 'all'):
    '''
    show module on leaf provided
    '''
    cmd=f'show module'
    sendCmd(cmd=cmd,leafName=leafName)

def show_interface(leafName: Optional[str] = 'all', interface: Optional[str] = None,
                   viewOptions: Optional[str] = None):
    '''
    show interface on leaf with different viewoptions
    '''
    if viewOptions == None:
        cmd=f'show interface ethernet {interface}'
    if viewOptions == 'all':
        cmd = []
        cmd.append(f'show interface {interface}')
        cmd.append(f'show interface {interface} transceiver details')
        cmd.append(f'show interface {interface} status')
    if viewOptions == 'brief':
        cmd=f'show interface {interface} brief'
    if viewOptions == 'transciver':
        cmd=f'show interface {interface} transceiver details'
    if viewOptions == 'status':
        cmd=f'show interface {interface} status'
    if viewOptions == 'flap':
        cmd=f'show interface {interface} | grep -Ei "flap|reset"'
    sendCmd(cmd=cmd,leafName=leafName)

def show_usd_info(leafName: Optional[str] = 'all', interface: Optional[str] = None,
                  viewOptions: Optional[str] = None):
    '''
    show usd info on port. Extract port id from the interface
    In the example Eth1/16, 16 is the port id
    '''
    portId = interface.split('/')[1]
    if viewOptions == None:
        cmd=f'vsh_lc -c "show platform internal usd port info"'
    if viewOptions == 'all':
        cmd = []
        cmd.append(f'vsh_lc -c "show platform internal usd port info"')
        cmd.append(f'vsh_lc -c "show  platform internal tah event-history trace asic 0  port 100"')
        cmd.append(f'vsh_lc -c "show system internal port-client link-event"')
        if interface != None:
            cmd.append(f'vsh_lc -c "show platform internal usd dfe values front-port {portId}"')

            cmd.append(f'vsh_lc -c "show  platform internal usd xcvr dom raw port {portId}"')
    if viewOptions == 'event-history':
        cmd=f'vsh_lc -c "show  platform internal tah event-history trace asic 0  port 100"'
    if viewOptions == 'link-event':
        cmd=f'vsh_lc -c "show system internal port-client link-event"'
    if viewOptions == 'dfe':
        cmd=f'vsh_lc -c "show platform internal usd dfe values front-port {portId}"'
    if viewOptions == 'xcvr':
        cmd=f'vsh_lc -c "show  platform internal usd xcvr dom raw port {portId}"'

    sendCmd(cmd=cmd,leafName=leafName)