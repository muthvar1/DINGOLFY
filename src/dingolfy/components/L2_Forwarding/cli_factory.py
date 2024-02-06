from .CONFIG_DEPLOYMENT import cli_factory as CONFIG_DEPLOYMENT_cli_factory
from .INTERFACE_COUNTERS import cli_factory as INTERFACE_COUNTERS_cli_factory
from .EPM import cli_factory as EPM_cli_factory
from .ELTMC import cli_factory as ELTMC_cli_factory
from .utils import EP
from ...infra.utils import ipValidation,getLeafIdfromLeaName,getLeafNamefromLeafId
from .EPM import ding as EPM_ding
import typer
from typing import Optional
from ...infra import richWrapper
from ...infra.utils import vrfTable, getLeafIdfromLeaName, getLeafNamefromLeafId
app = typer.Typer()
app.add_typer(CONFIG_DEPLOYMENT_cli_factory.app, name="config_deployment",help='Helps user collect relevant info for CONFIG_DEPLOYMENT Debugging')
app.add_typer(INTERFACE_COUNTERS_cli_factory.app, name="interface_counters",help='Helps user collect relevant info for INTERFACE_COUNTERS Debugging')
app.add_typer(EPM_cli_factory.app, name="epm",help='Helps user collect relevant info for EPM Debugging')
app.add_typer(ELTMC_cli_factory.app, name="eltmc",help='Helps user collect relevant info for ELTMC Debugging')

@app.command()
def locate_ip(ip:str = typer.Option(default="",prompt="Please provide ip to locate , eg:1.1.1.1",callback=ipValidation),
              vrf: str = typer.Option(default=None,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=None,help='L3_TLOSS: Please provide leaf name: eg: ifav21-leaf1')):
           
    '''
    verify the location of the given ip
    '''
    #verbose = typer.confirm("Please opt for verbose output, eg: True/False. If not needed, press enter",default=True)
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if vrf=='all':
        vrf = None
    if leafName:
        leafId = getLeafIdfromLeaName(leafName=leafName)
    else:
        leafId = None
    local_location = EP.ip_location(ip=ip,comprehensive=True,vrfName=vrf,leafName=leafName,verbose=True)
    
    
@app.command()
def locate_mac(mac:str = typer.Option(default="",prompt="Please provide mac to locate , eg:00:00:01:00:d2:38")):
           
    '''
    verify the location of the given mac
    '''
    EP.mac_location(mac=mac)
    
               
@app.command()
def ftriage(src_ip: str = typer.Option(default=...,help="Please provide source ip , eg:1.1.1.1,",callback=ipValidation),
            dst_ip: str = typer.Option(default=...,help="Please provide destination ip , eg:1.1.1",callback=ipValidation),
            src_leaf: str = typer.Option(default=None,help="Please provide source leaf , eg:101"),
            dst_leaf: str = typer.Option(default=None,help="Please provide destination leaf , eg:101"),
            traffic_type: str = typer.Option(default=None,help="Please specify routed or switched traffic:\n1) Routed\n2) Switched\n")
            ):
    

    '''
    Given the src ip and dst ip, verify the forwarding path by running 
    ftriage on the fabric and verify the path on the leaf and spine.
    Also, validate and provide information on the following:
    - Policy drops
    - Hardware drops
    - EPM drops
    - Path drops
    - Path drops on the leaf
    - Path drops on the spine
    

    '''
    EPM_ding.ftriage(src_ip=src_ip,dst_ip=dst_ip, src_leaf=src_leaf,dst_leaf=dst_leaf, traffic_type=traffic_type)


@app.command()
def flow_debug(src_ip: str = typer.Option(default=...,help="Please provide source ip , eg:1.1.1.1,",callback=ipValidation),
            dst_ip: str = typer.Option(default=...,help="Please provide destination ip , eg:1.1.1",callback=ipValidation),
            src_leaf: str = typer.Option(default=None,help="Please provide source leaf , eg:101"),
            dst_leaf: str = typer.Option(default=None,help="Please provide destination leaf , eg:101"),
            src_vrf: str = typer.Option(default=None,help="Please provide source vrf , eg:tn2:ctx1"),
            dst_vrf: str = typer.Option(default=None,help="Please provide destination vrf , eg:tn2:ctx1"),
            traffic_type: str = typer.Option(default=None,help="Please specify routed or switched traffic:\n1) Routed\n2) Switched\n")
            ):
    

    '''
    Given the src ip and dst ip, verify the forwarding path by running 
    ftriage on the fabric and verify the path on the leaf and spine.
    Also, validate and provide information on the following:
    - Policy drops
    - Hardware drops
    - EPM drops
    - Path drops
    - Path drops on the leaf
    - Path drops on the spine
    
    Subsequently provide the src EP and dst EP information.
    as per the wiki below
    https://wiki.cisco.com/display/ACIQA/End-End+info+based+on+flow

    '''
    def leaf_list(leafList:list):
        leafList = '\n'.join(leaf for leaf in leafList)
        msg = f'''
{leafList}
'''
    richWrapper.pageSeparator(text="FTRIAGE output for the given src and dst ip", title="FTRIAGE", subtitle="FTRIAGE")
    src_local_info, dst_local_info= EPM_ding.ftriage(src_ip=src_ip,dst_ip=dst_ip, src_leaf=src_leaf,dst_leaf=dst_leaf, src_vrf=src_vrf, dst_vrf=dst_vrf, traffic_type=traffic_type)
    from ...infra.ftriage import FT, reInitFT
    #Check of the errors may be due to the traffic being routes within the subnet(Proxy arp or cases where traffic is destined to fabric MAC)
    if FT.errors:
        richWrapper.console.error(f'Errors found in ftriage route Looking at resolution: {FT.errors}')
        for error in FT.errors:
            if 'Ftriage Completed with' in error \
            and 'unicast' in error \
            and 'not same as RMAC' in error:
                #We need to rerun ftriage with the traffic_type as routed
                msg = richWrapper.highlight(f'Traffic is supposed to be routed based on ftriage error: {FT.errors}')
                richWrapper.console.print(msg)
                msg = richWrapper.highlight(f'Re-running ftriage with traffic_type as Routed')
                richWrapper.console.print(msg)
                reInitFT()
                src_local_info, dst_local_info= EPM_ding.ftriage(src_ip=src_ip,dst_ip=dst_ip, src_leaf=src_leaf,dst_leaf=dst_leaf, src_vrf=src_vrf, dst_vrf=dst_vrf, traffic_type='routed')
    
            
    
    src_remote_info = EP.ip_location(ip=src_ip,comprehensive=True,verbose=True,remoteEntry=True,leafName=getLeafNamefromLeafId(dst_local_info[0]['leaf']),checkExternalIp=False)
    dst_remote_info = EP.ip_location(ip=dst_ip,comprehensive=True,verbose=True,remoteEntry=True,leafName=getLeafNamefromLeafId(src_local_info[0]['leaf']),checkExternalIp=False)
    if not src_remote_info:
        richWrapper.console.error(f"No Remote XR entry found for {src_ip} on leaf {dst_local_info[0]['leaf']}")
    if not dst_remote_info:
        richWrapper.console.error(f"No Remote XR entry found for {dst_ip} on leaf {src_local_info[0]['leaf']}")

    # #There should be only one entry for src_local_info, dst_local_info, src_remote_info and dst_remote_info
    # if len(src_local_info)>1 or len(dst_local_info)>1 or len(src_remote_info)>1 or len(dst_remote_info)>1:
    #     richWrapper.console.error(f"More than one entry found for the given src and dst ip")
    #     raise typer.Exit()
    


    for src_info in src_local_info:
        richWrapper.pageSeparator(text=f"EP DEBUG info for the src IP: {src_info['ip']} on the src Leaf: {src_info['leaf']} and on the dst Leaf: {dst_local_info[0]['leaf']}", title="EP DEBUG", subtitle="EP DEBUG")
        EP.debugEPMos(EPlocation = src_info)
        EP.debugEPcli(EPlocation = src_info)
        msg = richWrapper.highlight(f"REMOTE EP INFO for the src IP: {src_info['ip']} on the dst Leaf: {dst_local_info[0]['leaf']}")
        richWrapper.console.print(msg)
        EP.debugHalRoute(EPlocation = dst_local_info[0],remoteLeafId=dst_local_info[0]['leaf'])
        msg = richWrapper.highlight(f"COOP DEBUG INFO for the src IP: {src_info['ip']}")
        richWrapper.console.print(msg)
        EP.coop_debug_cli(EPlocation=src_info)
    

    for dst_info in dst_local_info:
        richWrapper.pageSeparator(text=f"EP DEBUG info for the dst IP: {dst_info['ip']} on the dst Leaf: {dst_info['leaf']} and on the src Leaf: {src_local_info[0]['leaf']}", title="EP DEBUG", subtitle="EP DEBUG")
        EP.debugEPMos(EPlocation = dst_info)
        EP.debugEPcli(EPlocation = dst_info)
        msg = richWrapper.highlight(f"REMOTE EP INFO for the dst IP: {dst_info['ip']} on the src Leaf: {src_local_info[0]['leaf']}")
        richWrapper.console.print(msg)
        EP.debugHalRoute(EPlocation = src_local_info[0],remoteLeafId=src_local_info[0]['leaf'])
        msg = richWrapper.highlight(f"COOP DEBUG INFO for the dst IP: {dst_info['ip']}")
        richWrapper.console.print(msg)
        EP.coop_debug_cli(EPlocation=dst_info)

   


    
    
    
    
if __name__ == "__main__":
    app()