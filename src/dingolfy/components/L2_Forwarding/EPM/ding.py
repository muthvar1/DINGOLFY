from ....infra.utils import sendCmd
from ....infra.ftriage import FTRIAGE
from ..utils import EP
from ....infra import richWrapper
from ....infra.utils import getLeafIdfromLeaName
from typing import Optional
import typer
'''
1) Show system internal epm endpoint ip <>

2) Show system internal epm endpoint mac <>

3) Show system internal epm endpoint vrf all | <vrf name>

4) Show endpoint summary
'''

def collect_logs(ip:Optional[str] = None, mac: Optional[str] = None, vrf:Optional[str] = None, tunnel_id:Optional[str] = None, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for L2 Forwarding EPM logs
    '''
    if ip not in [None,""]:
        epm_ip(ip=ip,leafName=leafName)
    if mac not in [None,""]:
        epm_mac(mac=mac,leafName=leafName)
    if vrf not in [None,""]:
        epm_vrf(vrf=vrf,leafName=leafName)
    if tunnel_id not in [None,""]:
        epm_tunnel(tunnel_id=tunnel_id,leafName=leafName)
    epm_summary(leafName=leafName)
    
    
    

def epm_ip(ip:str,leafName: Optional[str] = 'all'):
    '''
    verify the EPM o/p of the source EP for correct mapping of below entities in source TOR for the given ip
    VRF vnid, BD vnid, port of learning, SCLASS
    '''
    cmd=f'show system internal epm endpoint ip {ip}'
    sendCmd(cmd=cmd,leafName=leafName)

def epm_mac(mac:str,leafName: Optional[str] = 'all'):
    '''
    verify the EPM o/p of the source EP for correct mapping of below entities in source TOR for the given mac
    VRF vnid, BD vnid, port of learning, SCLASS
    '''
    cmd=f'show system internal epm endpoint mac {mac}'
    sendCmd(cmd=cmd,leafName=leafName)

def epm_vrf(vrf:str,leafName: Optional[str] = 'all'):
    '''
    verify the EPM o/p of the source EP for correct mapping of below entities in source TOR for the given vrf
    VRF vnid, BD vnid, port of learning, SCLASS
    '''
    cmd=f'show system internal epm endpoint vrf {vrf}'
    sendCmd(cmd=cmd,leafName=leafName)

def epm_summary(leafName: Optional[str] = 'all'):
    '''
    verify the EPM summary on TOR
    
    '''
    cmd=f'show endpoint summary'
    sendCmd(cmd=cmd,leafName=leafName)


def epm_tunnel(tunnel_id:str,leafName: Optional[str] = 'all'):
    '''
    verify the tunnel destination is same as the destination TOR dtep or the vpc tep based on the location of EP
    '''
    cmd = f'show system internal epm interface tunnel {tunnel_id}'
    sendCmd(cmd=cmd,leafName=leafName)


def ftriage(src_ip:str,dst_ip:str,src_leaf: str=None,dst_leaf: str=None, traffic_type:str=None,
            src_vrf: str=None,dst_vrf: str=None):
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
    def leaf_list(leafList:list):
        leafList = '\n'.join(leaf for leaf in leafList)
        msg = f'''
{leafList}
'''
        return msg         
    if not src_leaf: 
        srcEPInfo = EP.ip_location(ip=src_ip,comprehensive=True,printTable=False)
    else:
        srcEPInfo = EP.ip_location(ip=src_ip,comprehensive=True,printTable=False,leaf=src_leaf)
    if not srcEPInfo:
        richWrapper.console.error(f'No EP found for {src_ip}')
        raise typer.Exit()
    
    if not dst_leaf: 
        dstEPInfo = EP.ip_location(ip=dst_ip,comprehensive=True,printTable=False)
    else:
        dstEPInfo = EP.ip_location(ip=dst_ip,comprehensive=True,printTable=False,leaf=dst_leaf)
    if not dstEPInfo:
        richWrapper.console.error(f'No EP found for {dst_ip}')
        raise typer.Exit()
    
    
    # If the src_leaves or dst_leaves are 2, then we need to find the VPC name from the apic
    if not src_leaf: 
        src_leaves = [location['vpcName'] if location['vpcName'] else location['leaf'] for location in srcEPInfo]
        #eliminate the duplicate entries of the src_leaves
        src_leaves = list(set(src_leaves))
        if len(src_leaves)>1:
            src_leaf = typer.prompt(f'Please select the possible source leaf/VPC from the list below:{leaf_list(src_leaves)}')
            #eliminate the srcEPInfo entries which are not on the src_leaf
            
        else:
            src_leaf = src_leaves[0]
        srcEPInfo = [location for location in srcEPInfo if location['leaf']==src_leaf or location['vpcName']==src_leaf]
    if not src_vrf:
        src_vrfs = [f"{location['fvTenantName']}:{location['fvCtxName']}" for location in srcEPInfo]
        #eliminate the duplicate entries of the src_vrfs
        src_vrfs = list(set(src_vrfs))
        if len(src_vrfs)>1:
            src_vrf = typer.prompt(f'Please select the possible source VRF from the list below:{leaf_list(src_vrfs)}')
            #eliminate the srcEPInfo entries which are not on the src_vrf
            
        else:
            src_vrf = src_vrfs[0]
        srcEPInfo = [location for location in srcEPInfo if f"{location['fvTenantName']}:{location['fvCtxName']}"==src_vrf]
    if not dst_leaf: 
        dst_leaves = [location['vpcName'] if location['vpcName'] else location['leaf'] for location in dstEPInfo]
        #eliminate the duplicate entries of the dst_leaves
        dst_leaves = list(set(dst_leaves))
        if len(dst_leaves)>1:
            dst_leaf = typer.prompt(f'Please select the possible destination leaf/VPC from the list below:{leaf_list(dst_leaves)}')
            #eliminate the dstEPInfo entries which are not on the dst_leaf
            
        else:
            dst_leaf = dst_leaves[0]
        dstEPInfo = [location for location in dstEPInfo if location['leaf']==dst_leaf or location['vpcName']==dst_leaf]
    if not dst_vrf:
        dst_vrfs = [f"{location['fvTenantName']}:{location['fvCtxName']}" for location in dstEPInfo]
        #eliminate the duplicate entries of the dst_vrfs
        dst_vrfs = list(set(dst_vrfs))
        if len(dst_vrfs)>1:
            dst_vrf = typer.prompt(f'Please select the possible destination VRF from the list below:{leaf_list(dst_vrfs)}')
            #eliminate the dstEPInfo entries which are not on the dst_vrf
            
        else:
            dst_vrf = dst_vrfs[0]
        dstEPInfo = [location for location in dstEPInfo if f"{location['fvTenantName']}:{location['fvCtxName']}"==dst_vrf]
        
    if not traffic_type:
        richWrapper.console.print('User did not provide traffic Type. Checking if the traffic is routed or switched')
        if EP.bridgedTraffic(srcEPInfo[0]['fvSubnetDn'], dstEPInfo[0]['fvSubnetDn']):
            traffic_type = 'switched'
        else:
            traffic_type = 'routed'
        #traffic_type= typer.prompt('Please specify routed or switched traffic:\n1) Routed\n2) Switched\n')
    if traffic_type in ['1', 'routed', 'Routed']:
        FTRIAGE.route(src_leaf=src_leaf,dst_leaf=dst_leaf,src_ip=src_ip,dst_ip=dst_ip)
    if traffic_type in ['2', 'switched', 'Switched']:
        FTRIAGE.bridge(src_leaf=src_leaf,dst_leaf=dst_leaf,src_ip=src_ip,dst_ip=dst_ip)
    
    from ....infra.ftriage import FT
    if FT.errors:
        richWrapper.console.error(f'FTRIAGE failed with the following errors:\n{FT.errors}')
    
    for node in FT.nodes:
        if node.entry:
            src_leaf = getLeafIdfromLeaName(node.nodename)
            break
    else:
        richWrapper.console.error(f'Could not find src_leaf for src_ip: {src_ip} in Ftriage output\n\tPlease check config')
        src_leaf = None
    
    for node in FT.nodes:
        if node.egress:
            dst_leaf = getLeafIdfromLeaName(node.nodename)
            break
    else:
        richWrapper.console.error(f'Could not find dst_leaf for dst_ip: {dst_ip} in Ftriage output\n\tPlease check config')
        dst_leaf = None

    if srcEPInfo:
        #remove the entries from the srcEPInfo which are not on the src_leaf and fvTenantName and fvCtxName do not match src_vrf:fvTenantName:fvCtxName
        if src_leaf: srcEPInfo = [location for location in srcEPInfo if location['leaf']==src_leaf]
        if src_vrf: srcEPInfo = [location for location in srcEPInfo if f"{location['fvTenantName']}:{location['fvCtxName']}"==src_vrf]
        EP.printLocationTable(srcEPInfo)
    if dstEPInfo:
        #remove the entries from the dstEPInfo which are not on the dst_leaf
        if dst_leaf: dstEPInfo = [location for location in dstEPInfo if location['leaf']==dst_leaf]
        if dst_vrf: dstEPInfo = [location for location in dstEPInfo if f"{location['fvTenantName']}:{location['fvCtxName']}"==dst_vrf]
        EP.printLocationTable(dstEPInfo)

    return srcEPInfo,dstEPInfo

