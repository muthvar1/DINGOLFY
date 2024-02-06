import re
import typer
from ...infra.globals import handles
from ...infra.globals import dingolfyGlobal
import datetime
import ipaddr
import ipaddress
import gc
from typing import Optional
from rich.progress import Progress
from ...infra import richWrapper
from rich.table import Table
from rich.markup import escape
from rich.pretty import pprint
from enum import Enum
from ...infra.ftriage import FTRIAGE
from ...infra.utils import getLeafNamefromLeafId, sendCmd, getLeafIdfromLeaName, can_be_int




class L3_location:
    '''
    list of attributes for an EP
    '''
    type = "externalEndpoint"
    leaf = None #Leaf Id of the leaf where the external IP is located
    ip = None #IP address of the external IP
    mac = None #MAC address of the external IP
    ifId = None #Interface Id of the external IP
    vpcName = None #VPC name of the leaf where the external IP is located
    l3ctxName = None #L3 context name of the external IP
    fvTenantName = None #Tenant name of the external IP
    fvCtxName = None #VRF name of the external IP
    prefix = None #Prefix of the external IP
    nhIp = None #Next hop IP of the external IP
    nhDn = None #Next hop Dn of the external IP
    l3InstPDn = None #list: l3InstP Dn of the external IP
    l3extSubnetDn = None #list: l3extSubnet Dn of the external IP
    routeType = None #Route type of the external IP
    routeOwner = None #Route owner of the external IP
    routeTag = None #Route tag of the external IP
    _vrfvnid = None #vrfVnid of the ctx where the prefix is learnt
    _l3CtxpcEnfDir = None #pcEnfDir of the ctx where the prefix is learnt
    _l3CtxpcEnfPref = None #pcEnfPref of the ctx where the prefix is learnt
    _vpc = False #Flag to indicate if the external IP is located on a VPC
    _pcTag = None #list: pcTag of the instP where the prefix is learnt
    vrfhwId = None #vrfhwId of the ctx where the prefix is learnt
    nexthop_id = None #nexthop_id of the external IP
    egress_IF = None #Egress interface of the external IP
    _l3Ctx = None #l3Ctx dn of the ctx where the prefix is learnt

    @staticmethod
    def getTable(leaf):
        table = Table(title=f"L3 IP located at: {leaf}", style=richWrapper.StyleGuide.title_style,title_justify="left")
        table.add_column("Field", style="magenta")
        table.add_column("Value", style="green")
        return table

class L3DebugHelp:
    remoteIpRouteNotFound = '''A remote route for the destination IP address was not found in the VRF.
    This could mean a few things:
    1. You may not have a contract that stiches both the l3instPs/epgs together
    2. If contract exists, there could be a bug in importing the route to the vrf. Please contact the respective developer to debug Further
        Please provide the collected utility logs to the developer including the EP/ExtIp location info.   
'''
    notImplementedTriage = '''Debug Triage for this case is not implemented yet. Please contact the respective developer to debug Further
    Please provide the collected utility logs to the developer including the EP/ExtIp location info.
'''
    leafingressmismatch = '''The leaf where the external IP is located is not the same as the leaf where the Ftriage leaf entry is pointing to.
    This could mean a few things:
    1. Could you check your config to see where the l3InstP is deployed?
    2. Could you check if the l3InstP is deployed on the leaf where the external IP is located?
    3. Could you check if the l3InstP is deployed on the leaf where the Ftriage leaf entry is pointing to?
    4. If all the above checks out then please contact the respective developer to debug Further
        Please provide the collected utility logs to the developer including the EP/ExtIp location info.
'''
    securityDeny = '''The packet is being dropped due to contract.
    This could mean a few things:
    1. Could you check your config to see if the contract is configured correctly? Specifically check the extSubnet flags and l3InstP
    2. Could you check if the contract is configured correctly on the leaf where the external IP is located?
    3. Could you check if the contract is configured correctly on the leaf where the Ftriage leaf entry is pointing to?
    4. If all the above checks out then please contact the respective developer to debug Further
        Please provide the collected utility logs to the developer including the EP/ExtIp location info.
'''

class L3:
    @staticmethod
    def checkHalRoute(prefix,leafName,l3ctxName):
        ip = prefix.split('/')[0]
        prefixLen = prefix.split('/')[1]
        grep_pattern = f'grep "{ip}/ {prefixLen}"'
        cmd = f'vsh_lc -c "show platform internal hal l3 routes vrf {l3ctxName}" | {grep_pattern}'
        output = sendCmd(cmd,leafName)
        for line in output.split('\n'):
            if ip in line:
                return True
        return False
    @staticmethod
    def checkRemoteRoute(leafName,ip,l3ctxName,prefix=None,src_vrfvnid=None, dst_vrfvnid=None, srcPcTag=None, dstPcTag=None):
        
        cmd = f'show ip route {ip} vrf {l3ctxName}'
        output = sendCmd(cmd,leafName)
        for line in output.split('\n'):
            if 'Route not found' in line:
                if prefix:
                    cmd = f'show bgp vpnv4 unicast {prefix} vrf overlay-1'
                    output = sendCmd(cmd,leafName)
                    
                cmd = f"show bgp process vrf {l3ctxName}"
                output = sendCmd(cmd,leafName)
                if dst_vrfvnid:
                    for ln in output.split('\n'):
                        if f':{dst_vrfvnid}' in ln:
                            break
                    else:
                        richWrapper.console.error(f'Import RT list does not include dest vrf vnid:{dst_vrfvnid} on leaf:{leafName}, ctx:{l3ctxName}')
                if src_vrfvnid and dst_vrfvnid and srcPcTag and dstPcTag: 
                    cmd = f'show route-map {src_vrfvnid}-shared-svc-leak'
                    output = sendCmd(cmd,leafName)
                    for ln in output.split('\n'):
                        # Check if the following line is present if the ip is ipv4
                        # ip address prefix-lists: IPv4-2752513-11329-5904-2949151-shared-svc-leak.
                        # Where 2752513 is the dst_vrfvnid and 2949151 is the src_vrfvnid, 11329 is the dstPcTag and 5904 is the srcPcTag
                        if ipaddress.ip_address(ip).version == 4:
                            if f'IPv4-{dst_vrfvnid}-{dstPcTag}-{srcPcTag}-{src_vrfvnid}-shared-svc-leak' in ln:
                                #show ip prefix-list IPv4-2752513-11329-5904-2949151-shared-svc-leak
                                cmd = f'show ip prefix-list {ln.split()[-1]}'
                                output = sendCmd(cmd,leafName)
                                #show ip extcommunity-list 2752513-11329-5904-2949151-shared-svc-leak-excom
                                cmd = f'show ip extcommunity-list {ln.split()[-1]}-excom'
                                output = sendCmd(cmd,leafName)
                                #In vsh_lc , dump  show platform internal hal l3 routes v4 vrf  <srcvrf> 
                                cmd = f"vsh_lc -c 'show platform internal hal l3 routes v4 vrf {l3ctxName}'"
                                output = sendCmd(cmd,leafName)
                    else:
                        richWrapper.console.error(f'Route map: {src_vrfvnid}-shared-svc-leak not found on leaf:{leafName}, ctx:{l3ctxName}')
                #dump show bgp sessions vrf overlay-1 on spines
                cmd = f'show bgp sessions vrf overlay-1'
                sendCmd(cmd,spine=True)
                return False
            if '*via' in line:
                return True
    @staticmethod
    def getdstPcTagHal(leafName,l3ctxName,prefix):
        ip = prefix.split('/')[0]
        prefixLen = prefix.split('/')[1]
        grep_pattern = f'grep "{ip}/ {prefixLen}"'
        cmd = f'vsh_lc -c "show platform internal hal l3 routes vrf {l3ctxName}" | {grep_pattern}'
        output = sendCmd(cmd,leafName)
        for line in output.split('\n'):
            if prefixLen in line:
                # Extract the pcTag
                pcTag = line.split('|')[-6].strip()
                return pcTag
        else:
            richWrapper.console.error(f'Could not find route for {prefix} on {leafName}')
            return None
    @staticmethod
    def ftriageResolution(srcL3Info, dstL3Info):
        def debugRemoteRoute(node):
            for location in srcL3Info:
                if location['leaf'] == getLeafIdfromLeaName(node.nodename):
                    
                    l3ctxName = f"{location['fvTenantName']}:{location['fvCtxName']}"
                    if not L3.checkRemoteRoute(node.nodename,dstL3Info[0]['ip'],l3ctxName,src_vrfvnid=location['_vrfvnid'], dst_vrfvnid=dstL3Info[0]['_vrfvnid'], srcPcTag=location['_pcTag'][0], dstPcTag=dstL3Info[0]['_pcTag'][0]):
                        richWrapper.console.error(f'Could not find route for {dstL3Info[0]["ip"]} in vrf: {l3ctxName} on {node.nodename}')
                        return False
                    else:
                        richWrapper.console.print(f'Found route for {dstL3Info[0]["ip"]} in vrf: {l3ctxName} on {node.nodename}')
                        if dstL3Info[0]['prefix']:
                            prefix = dstL3Info[0]['prefix']
                        elif dstL3Info[0]['fvSubnetDn']:
                            prefix = handles.ifc_sdk_handle.lookupByDn(dstL3Info[0]['fvSubnetDn']).ip 
                            prefix = str(ipaddress.ip_network(prefix,strict=False))
                        if L3.checkHalRoute(prefix,node.nodename,l3ctxName):
                            richWrapper.console.print(f'Found route for {dstL3Info[0]["ip"]} in vrf: {l3ctxName} on {node.nodename} in HAL')
                            return True
                        else:
                            richWrapper.console.error(f'Did not find route for {dstL3Info[0]["ip"]} in vrf: {l3ctxName} on {node.nodename} in HAL')
                            return False
            else:
                richWrapper.console.error(f"Ftriage leaf: {node.nodename} is not in Leaf where src Ip is found {[getLeafNamefromLeafId(loc['leaf']) for loc in srcL3Info]}")
                richWrapper.console.error(L3DebugHelp.leafingressmismatch)
                return False
        def debugSecurityDeny(node):
            RV = True
            def getSubnetDef(leafName,l3extSubnetDns):
                try:
                    int(leafName)
                    leafName = getLeafNamefromLeafId(leafName)
                except ValueError:
                    leafName=leafName
                for l3extSubnetDn in l3extSubnetDns:
                    l3extSubnetDefs = handles.switchSdkHdlbyName(leafName).lookupByClass('l3extSubnetDef')
                    for l3extSubnetDef in l3extSubnetDefs:
                        if l3extSubnetDef.subnetKey == l3extSubnetDn:
                            handles.switchSdkHdlbyName(leafName).printMo(l3extSubnetDef)
                            break
                    else:
                        richWrapper.console.error(f'Could not find l3extSubnetDef for {l3extSubnetDn} on {leafName}')
                        return None
                
            for location in srcL3Info:
                if location['leaf'] == getLeafIdfromLeaName(node.nodename):
                    
                    l3ctxName = f"{location['fvTenantName']}:{location['fvCtxName']}"
                    if dstL3Info[0]['prefix']:
                        prefix = dstL3Info[0]['prefix']
                    elif dstL3Info[0]['fvSubnetDn']:
                        prefix = handles.ifc_sdk_handle.lookupByDn(dstL3Info[0]['fvSubnetDn']).ip 
                        prefix = str(ipaddress.ip_network(prefix,strict=False))
                    if handles.ifc_sdk_handle.lookupByDn(location['l3extSubnetDn'][0]).ip in ['0.0.0.0/0','::/0']:
                        #This is a case where the subnet is default Route and sPcTag would be the vrfVnid
                        sPctag = location['_vrfvnid']
                        msg = richWrapper.highlight(f'Found default route for {location["ip"]} in vrf: {l3ctxName} on {node.nodename}. sPcTag is set to vrfVnid: {sPctag}')
                        richWrapper.console.print(msg)
                    else:
                        sPctag = location['_pcTag'][0]
                    #get the dPctag as installed in the src leaf
                    if handles.ifc_sdk_handle.lookupByDn(dstL3Info[0]['l3extSubnetDn'][0]).ip in ['0.0.0.0/0','::/0']:
                        #This is a case where the subnet is default Route and dPcTag would be 15
                        dPctag = '15'
                        msg = richWrapper.highlight(f'Found default route for {dstL3Info[0]["ip"]} in vrf: {l3ctxName} on {node.nodename}. dPcTag is set to 15')
                        richWrapper.console.print(msg)
                    else:
                        dPctag = dstL3Info[0]['_pcTag'][0]
                    haldpcTag = L3.getdstPcTagHal(node.nodename,l3ctxName,prefix)
                    haldpcTag = str(int(haldpcTag,16))
                    if not haldpcTag:
                        richWrapper.console.error(f'Could not find hal route for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                        return RV
                    if dPctag != haldpcTag:
                        richWrapper.console.error(f'dPctag from hal route:{haldpcTag} does not match the expected dPctag in dst ip location:{dPctag} in hal route for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                    else:
                        msg = richWrapper.highlight(f'dPctag from hal route:{haldpcTag} matches the expected dPctag in dst ip location:{dPctag} in hal route for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        richWrapper.console.print(msg)
                    
                    
                    sclass,dclass = FTRIAGE.getpctagfromelam(prettyelam=node.prettyelamrep)
                    if sclass != sPctag:
                        richWrapper.console.error(f'spcTag from ip location:{sPctag} does not match ftriage derived sclass: {sclass} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                    else:
                        msg = richWrapper.highlight(f'spcTag from ip location:{sPctag} matches ftriage derived sclass: {sclass} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        richWrapper.console.print(msg)
                    if dclass != dPctag:
                        richWrapper.console.error(f'dpcTag from hal route:{dPctag} does not match ftriage derived dclass: {dclass} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                    else:
                        msg = richWrapper.highlight(f'dpcTag from hal route:{dPctag} matches ftriage derived dclass: {dclass} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        richWrapper.console.print(msg)
                    aclqosId = FTRIAGE.getAclqosStatsIdfromelam(prettyelam=node.prettyelamrep)
                    if not aclqosId:
                        richWrapper.console.error(f'Could not find aclqosId in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                        return RV
                    vsh_lc_cmd = "show sys int aclqos zoning-rules"
                    grep_pattern = f'grep -B 9 "Idx: {aclqosId}"'
                    cmd = f'vsh_lc -c "{vsh_lc_cmd}" | {grep_pattern}'
                    output = sendCmd(cmd,node.nodename)
                    for line in output.split('\n'):
                        #Extract srcEPGTag and dstEPGTag from the line
                        #where the line is of the form Rule ID: 15310 Scope 120 Src EPG: 0 Dst EPG: 13 Filter 65534
                        # and the srcEPGTag is 0 and dstEPGTag is 13
                        if 'Rule ID' in line:
                            srcEPGTag = line.split('Src EPG: ')[1].split(' ')[0]
                            dstEPGTag = line.split('Dst EPG: ')[1].split(' ')[0]
                            break
                    else:
                        richWrapper.console.error(f'Could not find srcEPGTag and dstEPGTag in aclqos Rule {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                        return RV
                    if int(srcEPGTag) != int(node.policyrec['rule_nxos']['sclass']):
                        richWrapper.console.error(f'srcEPGTag from aclqos:{srcEPGTag} does not match ftriage derived sclass:{node.policyrec["rule_nxos"]["sclass"]} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                        return RV
                    else:
                        msg = richWrapper.highlight(f'srcEPGTag from aclqos:{srcEPGTag} matches ftriage derived sclass:{node.policyrec["rule_nxos"]["sclass"]} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        richWrapper.console.print(msg)
                    if int(dstEPGTag) != int(node.policyrec['rule_nxos']['dclass']):
                        richWrapper.console.error(f'dstEPGTag from aclqos:{dstEPGTag} does not match ftriage derived dclass:{node.policyrec["rule_nxos"]["dclass"]} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                        return RV
                    else:
                        msg = richWrapper.highlight(f'dstEPGTag from aclqos:{dstEPGTag} matches ftriage derived dclass:{node.policyrec["rule_nxos"]["dclass"]} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        richWrapper.console.print(msg)
                    vsh_lc_cmd = 'show platform internal hal objects policy zoningrule extensions asic-unit all'
                    grep_pattern = f'grep -A 5 -B 42 {hex(int(aclqosId))}'
                    cmd = f'vsh_lc -c "{vsh_lc_cmd}" | {grep_pattern}'
                    output = sendCmd(cmd,node.nodename)
                    for line in output.split('\n'):
                        if 'sclass' in line and 'sclass_mask' not in line:
                            sclass = line.split(': ')[1].strip()
                            #change sclass to decimal from hex
                            sclass = str(int(sclass,16))
                        if 'dclass' in line and 'dclass_mask' not in line:
                            dclass = line.split(': ')[1].strip()
                            #change dclass to decimal from hex
                            dclass = str(int(dclass,16))
                        if 'action_flags' in line:
                            action_flags = line.split(': ')[1].strip()
                            break
                    else:
                        richWrapper.console.error(f'Could not find sclass,dclass and action_flags in policy zoningrule extensions for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                        return RV
                    if sclass != sPctag:
                        richWrapper.console.error(f'sclass from policy zoningrule extensions:{sclass} does not match src ip location sclass: {sPctag} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        RV&=False
                    else:
                        msg = richWrapper.highlight(f'sclass from policy zoningrule extensions:{sclass} matches src ip location sclass: {sPctag} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}')
                        richWrapper.console.print(msg)
                    if dclass != dPctag:
                        richWrapper.console.error(f"dclass from policy zoningrule extensions:{dclass} does not match dst ip location dclass: {dPctag} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}")
                        RV&=False
                    else:
                        msg = richWrapper.highlight(f"dclass from policy zoningrule extensions:{dclass} matches dst ip location dclass: {dPctag} in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}")
                        richWrapper.console.print(msg)
                    if 'deny' in action_flags:
                        richWrapper.console.error(f"action_flags from policy zoningrule extensions:'{action_flags}' indicates deny in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}\n\tThis would mean the packet will be dropped.")
                        RV&=False
                        #Display the l3extSubnetDef for the subnet to check the flags
                        richWrapper.console.warning(f"Please find below the l3extSubnetDef for {prefix} in vrf: {l3ctxName} on {dstL3Info[0]['leaf']}")
                        getSubnetDef(dstL3Info[0]['leaf'],dstL3Info[0]['l3extSubnetDn'])
                    else:
                        msg = richWrapper.highlight(f"action_flags from policy zoningrule extensions:'{action_flags}' does not indicate deny in elam for {prefix} in vrf: {l3ctxName} on {node.nodename}\n\tThis would mean the packet will be permitted.")
                        richWrapper.console.print(msg)
                return RV
            else:
                richWrapper.console.error(f"Ftriage leaf: {node.nodename} is not in Leaf where src Ip is found {[getLeafNamefromLeafId(loc['leaf']) for loc in srcL3Info]}")
                richWrapper.console.error(L3DebugHelp.leafingressmismatch)
                return False
        
        from ...infra.ftriage import FT
        if FT.errors:
            richWrapper.console.error(f'Errors found in ftriage route Looking at resolution: {FT.errors}')
            for node in FT.nodes:
                if node.drop_err_code in ['UC_PC_CFG_TABLE_DROP: Indicates there is no route for that destination within the VRF or there is a route with drop adjacency']:
                    msg = richWrapper.highlight(f'Debug on node: {node.nodename} for route not found')
                    richWrapper.console.print(msg)
                    richWrapper.console.error(f'Errors found in leaf:{node.nodename}: {node.drop_err_code}')
                    if not debugRemoteRoute():
                        richWrapper.console.error(L3DebugHelp.remoteIpRouteNotFound)
                        return None
                    else:
                        richWrapper.console.error(L3DebugHelp.notImplementedTriage)
                        return None

                if node.drop_err_code in ['SECURITY_GROUP_DENY:Indicates the packet/frame is being dropped due to contract']:
                    richWrapper.console.error(f'Errors found in leaf:{node.nodename}: {node.drop_err_code}')
                    msg = richWrapper.highlight(f'Debug on node: {node.nodename} for security denny drop')
                    richWrapper.console.print(msg)
                    if not debugRemoteRoute(node):
                        richWrapper.console.error(L3DebugHelp.remoteIpRouteNotFound)
                        return None
                    else:
                        if not debugSecurityDeny(node):
                            richWrapper.console.error(L3DebugHelp.securityDeny)
                            return None
                        else:
                            msg = richWrapper.highlight(f'Could not find any issues with security deny on node: {node.nodename}')
                            richWrapper.console.print(msg)
                            richWrapper.console.error(L3DebugHelp.notImplementedTriage)
                            return None


                        

                     
            else:
                richWrapper.console.error(L3DebugHelp.notImplementedTriage)
                

                



                    
                    
                    


    @staticmethod
    def ftriage_route(src_ip:str,dst_ip:str,src_leaf:Optional[str]=None,dst_leaf:Optional[str]=None,src_vrf:Optional[str]=None, dst_vrf:Optional[str]=None):
        '''
        Given a source and destination IP address, run ftriage route between them
        if src leaf and dst leaf are not provided, then the function will try to locate the ip on the fabric
        '''
        def vrf_list(vrfList:list):
            vrfList = '\n'.join(vrf for vrf in vrfList)
            msg = f'''
{vrfList}
'''
            return msg

        def leaf_list(leafList:list):
            leafList = '\n'.join(leaf for leaf in leafList)
            msg = f'''
{leafList}
'''
            return msg
        srcL3Info=[]
        dstL3Info=[]
        if src_leaf in [None,'']:
            srcL3Info = L3.locate_ip(src_ip,l3ctxName=src_vrf)
            if not srcL3Info:
                return None,None
        if dst_leaf in [None,'']:
            dstL3Info = L3.locate_ip(dst_ip,l3ctxName=dst_vrf)
            if not dstL3Info:
                return None,None
        if srcL3Info:
            src_leaves = [location['vpcName'] if location['vpcName'] else location['leaf'] for location in srcL3Info]
            #remove duplicates
            src_leaves = list(dict.fromkeys(src_leaves))
            if len(src_leaves)>1:
                msg = f"Got more than one src leaf: {src_leaves}. Will run ftriage route with no src_leaf"
                richWrapper.console.warning(msg)
                src_leaf = None#typer.prompt(f'Please select the possible source leaf/VPC from the list below:{leaf_list(src_leaves)}',default=None)
            else:
                src_leaf = src_leaves[0]
        if dstL3Info:
            dst_leaves = [location['vpcName'] if location['vpcName'] else location['leaf'] for location in dstL3Info]
            #remove duplicates
            dst_leaves = list(dict.fromkeys(dst_leaves))
            if len(dst_leaves)>1:
                dst_leaf = None#typer.prompt(f'Please select the possible destination leaf/VPC from the list below:{leaf_list(dst_leaves)}',default=None)
                msg = f"Got more than one dst leaf: {dst_leaves}. Will run ftriage route with no dst_leaf"
                richWrapper.console.warning(msg)
            else:
                dst_leaf = dst_leaves[0]
        
        if not src_leaf or not dst_leaf:
            typer.BadParameter('Please provide src_leaf and dst_leaf: Locate IP failed')
        FTRIAGE.route(src_ip=src_ip,dst_ip=dst_ip,src_leaf=src_leaf,dst_leaf=dst_leaf)
        from ...infra.ftriage import FT
        
        if not src_leaf or not can_be_int(src_leaf): #Check if src_leaf is not there or src_leaf is a VPC(would be a string)
            for node in FT.nodes:
                if node.entry:
                    src_leaf = getLeafIdfromLeaName(node.nodename)
                    break
            else:
                richWrapper.console.error(f'Could not find src_leaf for src_ip: {src_ip} in Ftriage output\n\tPlease check config')
                src_leaf = None
                raise typer.Exit()
            
        if not dst_leaf or not can_be_int(dst_leaf): #Check if dst_leaf is not there or dst_leaf is a VPC(would be a string)
            for node in FT.nodes:
                if node.egress:
                    dst_leaf = getLeafIdfromLeaName(node.nodename)
                    break
            else:
                richWrapper.console.error(f'Could not find dst_leaf for dst_ip: {dst_ip} in Ftriage output\n\tPlease check config')
                dst_leaf = None
                
        if FT.errors:
            richWrapper.console.error(f'Errors found in ftriage route: {FT.errors}')
            if not srcL3Info or len(srcL3Info)>1:
                msg = richWrapper.highlight(f'Get Ip location for src_ip: {src_ip} on leaf: {src_leaf} derived from ftriage')
                richWrapper.console.print(msg)
                if not srcL3Info: 
                    srcL3Info = L3.locate_ip(src_ip,l3ctxName=src_vrf,leafId=src_leaf)
                if not srcL3Info:
                    richWrapper.console.error(f'Could not find src_ip: {src_ip} on leaf: {src_leaf}')
                elif len(srcL3Info)>1:
                    richWrapper.console.warning(f'Got more than one src_ip location: {src_ip} on leaf: {[getLeafNamefromLeafId(location["leaf"]) for location in srcL3Info]}')
                    richWrapper.console.print('Please select the vrf you want to debug from the list below:')
                    l3ctxName = typer.prompt(vrf_list([f"{location['fvTenantName']}:{location['fvCtxName']}" for location in srcL3Info]))
                    srcL3Info = [location for location in srcL3Info if f"{location['fvTenantName']}:{location['fvCtxName']}" == l3ctxName]
                    if len(srcL3Info)>1:
                        richWrapper.console.error(f'Got more than one src_ip location: {src_ip} on leaf: {[getLeafNamefromLeafId(location["leaf"]) for location in srcL3Info]}')
                        richWrapper.console.error(f'This is not expected. There is a possiblity that the traffic is not hitting any of the leaves')
                        raise typer.Exit()
                    
            if not dstL3Info or len(dstL3Info)>1:
                msg = richWrapper.highlight(f'Get Ip location for dst_ip: {dst_ip} on leaf: {dst_leaf} derived from ftriage')
                richWrapper.console.print(msg)
                if not dstL3Info:
                    dstL3Info = L3.locate_ip(dst_ip,l3ctxName=dst_vrf,leafId=dst_leaf)
                if not dstL3Info:
                    richWrapper.console.error(f'Could not find dst_ip: {dst_ip} on leaf: {dst_leaf}')
                elif len(dstL3Info)>1:
                    richWrapper.console.warning(f'Got more than one dst_ip location: {dst_ip} on leaf: {[getLeafNamefromLeafId(location["leaf"]) for location in dstL3Info]}')
                    #check if there is more than one vrf in the list of dstL3Info
                    if len(set([f"{location['fvTenantName']}:{location['fvCtxName']}" for location in dstL3Info]))>1:
                        richWrapper.console.print(f'Got more than one dst_ip vrf: {dst_ip} on leaf: {[getLeafNamefromLeafId(location["leaf"]) for location in dstL3Info]}')
                        richWrapper.console.print('Please select the vrf you want to debug from the list below:')
                        l3ctxName = typer.prompt(vrf_list([f"{location['fvTenantName']}:{location['fvCtxName']}" for location in dstL3Info]))
                        dstL3Info = [location for location in dstL3Info if f"{location['fvTenantName']}:{location['fvCtxName']}" == l3ctxName]
        
        return srcL3Info, dstL3Info
    @staticmethod
    def printLocationTable(extInfo,verbose: Optional[bool] = True):
        richWrapper.console.print('\n')
        for location in extInfo:
            table = L3_location.getTable(location['leaf'])
            for key,value in location.items():
                if key.startswith('__'): continue
                if not verbose and key.startswith('_'): continue
                if value is None: continue
                if key.startswith('_'):
                    table.add_row(escape(str(key[1:])),escape(str(value)))
                else:
                    if key == 'leaf':
                        leafName = getLeafNamefromLeafId(value)
                        table.add_row(escape(str(key)),f'{escape(str(value))}:{escape(str(leafName))}')
                    else:
                        table.add_row(escape(str(key)),escape(str(value)))
            table.pad_edge = True
            richWrapper.console.print('\n')
            richWrapper.console.print(table)
            richWrapper.console.print('\n')

    @staticmethod
    def spine_proxy_list(ifc_handle):
        propFilter = 'and(wcard(ipv4If.mode,"anycast"))'
        ipv4if = [mo for mo in ifc_handle.lookupByClass('ipv4If',propFilter=propFilter)]
        for each in ipv4if:
            if each.mode == 'anycast-v6':
                parentDn = str(each.dn)
                addr = [mo for mo in ifc_handle.lookupByClass('ipv4Addr',parentDn=parentDn)]
                if len(addr) != 1:
                    msg = "Cannot have more or less than one address for anycast interface - %s" % (each.dn)
                    richWrapper.console.error(msg)
                    raise Exception(msg)
                v6_proxy = '::ffff:' + addr[0].addr.split('/')[0] + '/' + '128'
            elif each.mode == 'anycast-v4':
                parentDn = str(each.dn)
                addr = [mo for mo in ifc_handle.lookupByClass('ipv4Addr',parentDn=parentDn)]
                if len(addr) != 1:
                    msg = "Cannot have more or less than one address for anycast interface - %s" % (each.dn)
                    richWrapper.console.error(msg)
                    raise Exception(msg)
                v4_proxy = addr[0].addr

            elif each.mode == 'anycast-mac':
                parentDn = str(each.dn)
                addr = [mo for mo in ifc_handle.lookupByClass('ipv4Addr',parentDn=parentDn)]
                if len(addr) != 1:
                    msg = "Cannot have more or less than one address for anycast interface - %s" % (each.dn)
                    richWrapper.console.error(msg)
                    raise Exception(msg)
                mac_proxy = addr[0].addr
        return [v6_proxy, v4_proxy, mac_proxy]

    

    @staticmethod
    def locate_ip(externalIp, l3ctxName: Optional[str] = None,checkFabricEndpoint: Optional[bool] = True, leafId: Optional[str] = None):
        extInfo = []
        nhList = []
        version = ipaddr.IPAddress(externalIp).version
        if version == 6:
            externalIp = ipaddr.IPAddress(externalIp).compressed
        
        def checkBDRoute():
            for fvSubnet in handles.ifc_sdk_handle.lookupByClass('fvSubnet'):
                #Check if externalIp is part pf the fvSubnet.ip network
                if ipaddr.IPAddress(externalIp) in ipaddr.IPNetwork(fvSubnet.ip):
                    return True
            return False
        def updateLocation(ip,nhDn,prefix):

            def getInstP_Subnets(fvTenantName: str,fvCtxName:str, pcTag: Optional[str] = None):
                defaultRoutes = []
                l3extSubnets = []
                l3InstPs = []
                tenant_dn = f'uni/tn-{fvTenantName}'
                if tenant_dn == 'uni/tn-common':
                    #If tenant is common tenant, then set tenant_dn to None, as the ctx could be attached to any tenant
                    tenant_dn = None

                ctx_dn = f'uni/tn-{fvTenantName}/ctx-{fvCtxName}'
                l3extOuts = []
                for mo in handles.ifc_sdk_handle.lookupByClass('l3extRsEctx',parentDn=tenant_dn):
                    if mo.tDn == ctx_dn:
                        l3extOuts.append(handles.ifc_sdk_handle.lookupByDn(str(mo.parentDn)))
                        
                if not l3extOuts:
                    msg = f'Could not find l3extOut for {ctx_dn}'
                    richWrapper.console.error(msg)
                    raise typer.Exit()
                    
                
                if pcTag not in ['0',0,None]:
                    # This is a case where dynamic external classification may be enabled and
                    # the pcTag is not 0 on the nextHop. Here the subnet is dervied from 
                    # the route map associated to the l3extepg
                    for l3extOut in l3extOuts:
                        for mo in handles.ifc_sdk_handle.lookupByClass('l3extInstP',parentDn=l3extOut.dn):
                            if mo.pcTag == pcTag:
                                l3InstPs.append(mo)
                                break
                        else:
                            continue
                        break
                    else:
                        msg = f'Could not find l3extInstP for ip: {ip} with pcTag: {pcTag} under l3extOut: {[str(l3extOut.dn) for l3extOut in l3extOuts]}'
                        richWrapper.console.error(msg)
                        raise typer.Exit()
                    
                    #Find the rtctrlRsSetPolicyTagToInstP which has the tDn set to the l3extInstP
                    for mo in handles.ifc_sdk_handle.lookupByClass('rtctrlRsSetPolicyTagToInstP',parentDn=tenant_dn):
                        if mo.tDn == str(l3InstPs[0].dn):
                            rtctrlSetPolicyTagToInstP = mo
                            break
                    else:
                        msg = f'Could not find rtctrlRsSetPolicyTagToInstP for l3extInstP: {l3InstPs[0].dn} for ip: {ip}'
                        richWrapper.console.error(msg)
                        raise typer.Exit()

                    rtctrlAttrPDn = handles.ifc_sdk_handle.lookupByDn(rtctrlSetPolicyTagToInstP.parentDn).parentDn
                    #Find the rtctrlRsScopeToAttrP which has the tDn set to the rtctrlAttrP
                    for mo in handles.ifc_sdk_handle.lookupByClass('rtctrlRsScopeToAttrP',parentDn=tenant_dn):
                        if mo.tDn == str(rtctrlAttrPDn):
                            rtctrlRsScopeToAttrP = mo
                            break
                    else:
                        msg = f'Could not find rtctrlRsScopeToAttrP for rtctrlAttrP: {rtctrlAttrPDn} for ip: {ip}'
                        richWrapper.console.error(msg)
                        raise typer.Exit()
                    
                    rtctrlCtxPDn = handles.ifc_sdk_handle.lookupByDn(rtctrlRsScopeToAttrP.parentDn).parentDn

                    #Find all the rtctrlRsCtxPToSubjP under the rtctrlCtxP
                    rtctrlSubjPs = [handles.ifc_sdk_handle.lookupByDn(mo.tDn) for mo in handles.ifc_sdk_handle.lookupByClass('rtctrlRsCtxPToSubjP',parentDn=rtctrlCtxPDn)]
                    
                    for parent in rtctrlSubjPs:
                        for mo in handles.ifc_sdk_handle.lookupByClass('rtctrlMatchRtDest',parentDn=str(parent.dn)):
                            if mo.ip in ['0.0.0.0/0','::/0']:
                                defaultRoutes.append(mo)
                                continue
                            if ipaddress.ip_address(ip) in ipaddress.ip_network(mo.ip,strict=False):
                                l3extSubnets.append(mo)
                    
                    if not l3extSubnets:
                        if defaultRoutes:
                            #may do something else here
                            l3extSubnets = defaultRoutes
                        else:
                            msg = f'Could not find l3extSubnet for {ip} in l3extOut: {l3extOut.dn}'
                            richWrapper.console.error(msg)
                            raise typer.Exit()


                else:
                    for l3extOut in l3extOuts:
                        for mo in handles.ifc_sdk_handle.lookupByClass('l3extSubnet',parentDn=l3extOut.dn):
                            #Skip if it is a default Route
                            if mo.ip in ['0.0.0.0/0','::/0']:
                                defaultRoutes.append(mo)
                                continue
                            #Check if ip falls under the mo.ip subnet 
                            if ipaddress.ip_address(ip) in ipaddress.ip_network(mo.ip,strict=False):
                                l3extSubnets.append(mo)
                    

                    if not l3extSubnets:
                        if defaultRoutes:
                            #may do something else here
                            l3extSubnets = defaultRoutes
                        else:
                            msg = f'Could not find l3extSubnet for {ip} in l3extOut: {l3extOut.dn}'
                            richWrapper.console.error(msg)
                            raise typer.Exit()
                    l3InstPs = [handles.ifc_sdk_handle.lookupByDn(str(mo.parentDn)) for mo in l3extSubnets]

                
                
                return l3InstPs, l3extSubnets
            
            def getIfId(leafName,nb_id):
                cmd = f'vsh_lc -c "show platform internal hal l3 nexthops nexthop-id {nb_id}"'
                op = sendCmd(cmd,leafName)
                for ln in op.split('\n'):
                    if 'L2 Ifindex' in ln:
                        l2ifIndex = ln.split(': ')[1].strip()
                        if l2ifIndex == '0x0':
                            msg = f'Could not find L2 Ifindex for {nb_id} on {leafName} got 0x0'
                            richWrapper.console.error(msg)
                            raise typer.Exit()
                            
                        break
                else:
                    msg = f'Could not find L2 Ifindex for {nb_id} on {leafName}'
                    richWrapper.console.error(msg)
                    raise typer.Exit()
                    
                cmd = f'show interface snmp | grep "{l2ifIndex}"'
                op = sendCmd(cmd,leafName)
                pattern = r"(\S+)(?:\s+\d+\s+\(0x[\da-fA-F]+\))?"
                for ln in op.split('\n'):
                    match = re.search(pattern, ln)
                    if match:
                        interface_name = match.group(1)
                        break
                else:
                    msg = f'Could not find interface name for {l2ifIndex} on {leafName}'
                    richWrapper.console.error(msg)
                    raise typer.Exit()
                return interface_name
            def getHalData(leafId,prefix,vrfName):
                
                leafName = getLeafNamefromLeafId(leafId)
                # cmd = f'vsh_lc -c "show system internal eltmc info vrf {vrfName}" | grep hw_vrf_idx'
                # output = sendCmd(cmd,leafName)
                # #output would be 
                # for line in output.split('\n'):
                #     if 'hw_vrf_idx' in line:
                #         vrf_hwId = line.split(':')[1].strip()
                #         break
                ip = prefix.split('/')[0]
                prefixLen = prefix.split('/')[1]
                grep_pattern = f'grep "{ip}/ {prefixLen}"'
                cmd = f'vsh_lc -c "show platform internal hal l3 routes vrf {vrfName}" | {grep_pattern}'
                
                output = sendCmd(cmd,leafName)
                nb_id = []
                interface_name = []
                for line in output.split('\n'):
                    if ip in line and prefixLen in line:
                        parts = line.split("|")
                        # Extract the vrf_hwId and NB-ID
                        vrf_hwId = parts[1].strip()
                        if parts[-14].rstrip() == 'E':
                            #This is an ECMP route, so we need to get two NbIds
                            ecmp_id = parts[-13].strip()
                            #convert ecmp_id to decimal
                            ecmp_id = int(ecmp_id,16)
                            cmd = f'vsh_lc -c "show platform internal hal l3 ecmp ecmp-id {ecmp_id}"'
                            op = sendCmd(cmd,leafName)
                            for ln in op.split('\n'):
                                if 'NhopId' in ln:
                                    #Strip nb_id from Mbr[0] LID:80 NhopId:38222 L2ptr:0x9faa where nb_id is 38222
                                    nb_id.append(str(hex(int(ln.split('NhopId:')[1].split()[0]))))
                                    
                        else: 
                            nb_id.append(f'0x{parts[-13].strip()}')
                            
                        msg = richWrapper.highlight(f'NextHop Info for L3 Route - {prefix} on leaf {leafName}')
                        richWrapper.console.print(msg)
                        interface_name = [getIfId(leafName,id) for id in nb_id]
                        return vrf_hwId, nb_id, interface_name
                return None, None, None
            def isLeafpartofVPC(leaf):
                GEp = handles.ifc_sdk_handle.lookupByClass('fabricExplicitGEp')
                for each in GEp:
                    for fabricNodePEp in handles.ifc_sdk_handle.lookupByClass('fabricNodePEp',parentDn=each.dn):
                        if leaf == str(fabricNodePEp.id):
                            return [vpcNode.id for vpcNode in handles.ifc_sdk_handle.lookupByClass('fabricNodePEp',parentDn=each.dn)]
            
            location = {}
            for key in L3_location.__dict__.keys():
                location[key] = None
            #Extract fvTenant Name and ctx name from the nhDn
            #where nhDn is topology/pod-1/node-107/sys/uribv4/dom-decOspf:ctx0/db-rt/rt-[34.89.1.0/24]/nh-[ospf-default]-[7.0.9.4/32]-[vlan349]-[decOspf:ctx0]
            # and ctx name is decOspf:ctx0
            strnh = str(nhDn) # This is just for traceback info.
            location['leaf'] = str(nhDn).split('/')[2].split('-')[1]
            location['l3ctxName'] = str(nhDn).split('/')[5].split('dom-')[1]
            location['fvTenantName'] = location['l3ctxName'].split(':')[0]
            location['fvCtxName'] = location['l3ctxName'].split(':')[1]
            for l3ctx in handles.ifc_sdk_handle.lookupByClass('l3Ctx'):
                if l3ctx.name == location['l3ctxName'] and location['leaf'] in str(l3ctx.dn):
                    location['_l3Ctx'] = str(l3ctx.dn)
            location['ip'] = ip
            nhMo = handles.ifc_sdk_handle.lookupByDn(str(nhDn))
            location['ifId'] = getattr(nhMo,'if')
            location['routeType'] = nhMo.routeType
            location['routeOwner'] = nhMo.owner
            location['routeTag'] = nhMo.tag
            location['nhIp'] = nhMo.addr
            location['nhDn'] = str(nhDn)
            #uni/tn-t0/ctx-ctxMpod
            ctxDn = f"/uni/tn-{location['fvTenantName']}/ctx-{location['fvCtxName']}"
            ctxMo = handles.ifc_sdk_handle.lookupByDn(ctxDn)
            location['_vrfvnid'] = ctxMo.scope
            location['_l3CtxpcEnfDir'] = ctxMo.pcEnfDir
            location['_l3CtxpcEnfPref'] = ctxMo.pcEnfPref
            # routeDn = str(nhDn).split('nh-[')[0]
            # routeMo= handles.ifc_sdk_handle.lookupByDn(routeDn)
            # location['prefix'] = routeMo.prefix
            location['prefix'] = prefix
            vrfhwId, nbid, egress_IF = getHalData(location['leaf'],location['prefix'],vrfName=location['l3ctxName'])
            location['vrfhwId'] = vrfhwId
            location['nexthop_id'] = nbid
            location['egress_IF'] = egress_IF
            l3InstPs, l3extSubnets = getInstP_Subnets(location['fvTenantName'],location['fvCtxName'],pcTag=nhMo.PcTag)
            location['l3InstPDn'] = [str(l3InstP.dn) for l3InstP in l3InstPs]
            location['_pcTag'] = [str(l3InstP.pcTag) for l3InstP in l3InstPs]
            location['l3extSubnetDn'] = [str(l3extSubnet.dn) for l3extSubnet in l3extSubnets]

            for interface in egress_IF:
                if 'po' in interface.lower():
                    cmd = 'show vpc brief'
                    leafName = getLeafNamefromLeafId(location['leaf'])
                    output = sendCmd(cmd,leafName)
                    for line in output.split('\n'):
                        if interface in line:
                            cmd = f'show port-channel extended interface {interface}'
                            #cmd = f'show port-channel extended | grep {interface}'
                            op = sendCmd(cmd,leafName)
                            for ln in op.split('\n'):
                                # Extract vpcName from the line where line is "3     Po3(SU)     accBndlGrp_402_404_v     LACP      Eth1/42(P)""
                                # and the vpcName is accBndlGrp_402_404_v
                                if interface in ln:
                                    vpcName = ln.split()[2]
                                    #In certain cases the vpcName is split across two lines
                                    next_line_index = op.split('\n').index(ln) + 1
                                    try:
                                        vpcName = vpcName + op.split('\n')[next_line_index].strip()
                                    except IndexError:
                                        pass
                                    location['_vpc'] = True
                                    location['vpcName'] = vpcName
                                    break
                    break
        
                        
            return location
        
        def filteredLookupwithParentDn(klass:str,parentDn: Optional[str] = None):
            try:
                return handles.ifc_sdk_handle.lookupByClass(klass,parentDn=parentDn)
            except Exception as e:
                print(f'Error in filteredLookupwithParentDn: {e} for class {klass} and parentDn {parentDn}')
        
        def locateTask(progress):
            progress.update(task, advance=15,description='[magenta bold]Locating IP: Check if ip is BD route')
            if checkFabricEndpoint:
                from ...components.L2_Forwarding.utils import EP
                if checkBDRoute():
                    richWrapper.console.print(f'IP {externalIp} is found in a BD subnet. Will check if it is a fabric Endpoint')
                    EP_info = EP.locate_ip(ip=externalIp,comprehensive=True, verbose=True,checkExternalIp=False)
                    if EP_info: 
                        return EP_info
                    
            progress.update(task, advance=15,description='[magenta bold]Locating IP: Retrieving ipv4if and ipv4ifaddr')
            #since lookupclass returns a generator and we plan to use it multiple times, we convert it to a list for optimization
            
            tS = handles.ifc_sdk_handle.lookupByClass('top.System')
            spine_proxies = L3.spine_proxy_list(handles.ifc_sdk_handle)
            
            if version == 4: tepIps = [each.address + '/32' for each in tS]
            else: tepIps = ['::ffff:' + each.address + '/128' for each in tS]
            
            def checkForDefaultRoute(ctxName, uribEntityDn):
                routes = []
                nhs = []
                if not uribEntityDn: return False
                if version == 4: klass = 'uribv4.Route'; parentKlass = 'uribv4.Entity'
                else: klass = 'uribv6.Route'; parentKlass = 'uribv6.Entity'
                rtes = filteredLookupwithParentDn(klass,uribEntityDn)
                rtes = [x for x in rtes if ctxName in str(x.dn)]
                if version == 4:
                    rtes = [x for x in rtes if x.prefix == '0.0.0.0/0']
                else:
                    rtes = [x for x in rtes if x.prefix == '::/0']
                routes.extend(rtes)
                for rte in routes:
                    if version == 4: klass = 'uribv4.Nexthop'
                    else: klass = 'uribv6.Nexthop'
                    nhs.extend(handles.ifc_sdk_handle.lookupByClass(klass,parentDn=rte.dn))
                return routes, nhs
            
            def getRoutesAndNh(externalIp, ctxName: Optional[str] = None, uribEntityDn: Optional[str] = None, leafId: Optional[str] = None):
                routes = []
                nhs = []
                
                if version == 4: klass = 'uribv4.Route'; parentKlass = 'uribv4.Entity'
                else: klass = 'uribv6.Route'; parentKlass = 'uribv6.Entity'
                
                if uribEntityDn:
                    rtes = filteredLookupwithParentDn(klass,uribEntityDn)
                    if ctxName: rtes = [x for x in rtes if ctxName in str(x.dn)]
                    if leafId: rtes = [x for x in rtes if leafId in str(x.dn)]
                    rtes = [x for x in rtes if ipaddr.IPAddress(externalIp) in ipaddr.IPNetwork(x.prefix)]
                    rtes = [x for x in rtes if x.prefix != '0.0.0.0/0' and x.prefix != '::/0']
                    routes.extend(rtes)
                else:
                    for parent in handles.ifc_sdk_handle.lookupByClass(parentKlass):    
                        rtes = filteredLookupwithParentDn(klass,parent.dn)
                        if ctxName: rtes = [x for x in rtes if ctxName in str(x.dn)]
                        if leafId: rtes = [x for x in rtes if leafId in str(x.dn)]
                        rtes = [x for x in rtes if ipaddr.IPAddress(externalIp) in ipaddr.IPNetwork(x.prefix)]
                        rtes = [x for x in rtes if x.prefix != '0.0.0.0/0' and x.prefix != '::/0']
                        routes.extend(rtes)
                
                for rte in routes:
                    if version == 4: klass = 'uribv4.Nexthop'
                    else: klass = 'uribv6.Nexthop'
                    nhs.extend(handles.ifc_sdk_handle.lookupByClass(klass,parentDn=rte.dn))
                return routes, nhs

            def getRLDPTEPs():
                RL_dp_teps = []
                RL_node_list = [each for each in tS if each.remoteNode == 'yes']
                if not RL_node_list: return []
                for node in RL_node_list:
                    parentDn = str(node.dn)
                    ipv4_list = [x for x in handles.ifc_sdk_handle.lookupByClass('ipv4If',parentDn=parentDn)]
                    for if_int in ipv4_list:
                        if if_int.modeExtn == 'dp-ptep':
                            parentDn = str(if_int.dn)
                            ipv4addr_list = [x for x in handles.ifc_sdk_handle.lookupByClass('ipv4Addr',parentDn=parentDn)]
                            if version == 4:
                                RL_dp_teps.append(ipv4addr_list[0].addr)
                            else:
                                prefixedAddr = ipv4addr_list[0].addr.split('/')[0] + '/128'
                                RL_dp_teps.append('::ffff:' + prefixedAddr)
                if not RL_dp_teps:
                    msg = f'No RL DP TEPs were found, with RL configurations: RL NODE LIST: {RL_node_list}'
                    richWrapper.console.error(msg)
                    raise typer.Exit()
                return RL_dp_teps

            progress.update(task, advance=15,description='[magenta bold]Locating IP: Retrieving RL DP TEPs')
            RL_dp_teps = getRLDPTEPs()
            if RL_dp_teps:
                RoutablePools = [each.pool for each in handles.ifc_sdk_handle.lookupByClass('fabric.ExtRoutablePodSubnet')]
                
            else: RoutablePools = []
            # Get the routes and nexthops for the l3ctxDn
            
            def recursiveRouteSearch():
                def recursiveNhLookup(nextHops):
                    def checkRoutablePools(nhMo,pools,vsion):
                        
                        for RoutablePool in pools:
                            #This is a fabric route pointing to a remote leaf as next hop since it is pointing to a routable ip
                            
                            if vsion == 4:
                                if ipaddr.IPAddress(nhMo.addr.split('/')[0]) in ipaddr.IPNetwork(RoutablePool): return True
                            else:
                                if '::ffff:' in nh.addr:
                                    if ipaddr.IPAddress(nhMo.addr.split('/')[0].split('::ffff:')[1]) in ipaddr.IPNetwork(RoutablePool): return True
                        else:
                            return False
                    for nh in nextHops:
                        if nh.addr in tepIps and 'dom-overlay-1' in str(nh.dn): continue
                        if nh.addr in spine_proxies: continue
                        if nh.addr in RL_dp_teps: continue
                        if nh.mplsLabel != '0': continue
                        if nh.routeType == 'discard': continue #This is an am route that is set to discard, so we need to ignore it
                        if RoutablePools:
                            if checkRoutablePools(nh, RoutablePools, version): continue
                        # There could be nexthop propogation enabled in some vrfs, which need to be ignored
                        # So, Check the nexthop dn for the following conditions in order
                        # If the nextHop ifId is not unspecified, then it is not a propogated route
                        # if each.owner != 'bgp-asnNumber' and each.routeType != 'ibgp', then it is not a propagated route
                        # if the above condition is true, then we need to do another recursive search for the nexthop ip till we get to the border node
                        # print(f'\tChecking nextHop {nh.addr} as a possible candidate for leaf with dn {nh.dn}\n\t NextHop ifId: {getattr(nh,"if")}\n\t NextHop Owner: {nh.owner}\n\t NextHop RouteType: {nh.routeType} ')
                        asn = handles.ifc_sdk_handle.lookupByClass('bgpInst')[0].asn
                        if nh.routeType != 'ibgp':
                            return nh
                        if nh.owner != 'bgp-'+asn:
                            return nh
                            
                        if 'vlan' in getattr(nh,'if'):
                            return nh
                            
                        if 'po' in getattr(nh,'if'):
                            return nh
                            
                        if 'eth' in getattr(nh,'if'):
                            return nh
                            
                        if 'null0' in getattr(nh,'if') and getattr(nh,'owner') == 'static':
                            return nh
                            
                        else:
                            # This could be a propogated route, so we need to do a recursive search for the nexthop ip
                            #get ctxName from the nh.dn where nh.dn would be
                            #'topology/pod-2/node-409/sys/uribv4/dom-l3outRLvpc:ctx1/db-rt/rt-[21.59.21.0/24]/nh-[direct]-[21.59.21.4/32]-[vlan58]-[l3outRLvpc:ctx1]'
                            # and the ctxName would be l3outRLvpc:ctx1
                            # and the uribEntityDn would be topology/pod-2/node-409/sys/uribv4
                            cName = str(nh.dn).split('[')[-1].split(']')[0]
                            uribEntityDn = str(nh.dn).split('/dom-')[0]
                            routes,nhs = getRoutesAndNh(nh.addr.split('/')[0], ctxName=cName,uribEntityDn=uribEntityDn)
                            if not routes:
                                # print(f'\tNo routes found in Recursive check for {nh.addr.split("/")[0]} in {cName}, check for Default Route')
                                routes,nhs = checkForDefaultRoute(ctxName=cName, uribEntityDn=uribEntityDn)
                                if not routes:
                                    msg = f'No routes found in Recursive check for {nh.addr.split("/")[0]} in {cName}, check for Default Route'
                                    richWrapper.console.error(msg)
                                    raise typer.Exit()
                                    
                                if len(routes)>1:
                                    for each in routes:
                                        print(f'\t\t{each.dn}')
                                    msg = f'More than one default route found in Recursive check for {nh.addr.split("/")[0]} in {cName}'
                                    richWrapper.console.error(msg)
                                    raise typer.Exit()
                                
                            # print (f'\tRecursive check for nextHop Ip {nh.addr.split("/")[0]} in {cName} for nhdn {nh.dn}')
                            for rte in routes:
                                # print(f'\t\tRecursive check: route {rte.dn}')
                                parentDn=re.escape(str(rte.dn))
                                nextHops = [x for x in nhs if (re.search(parentDn, str(x.dn)) != None)]
                                if not nextHops: continue
                                return recursiveNhLookup(nextHops)
                    return None

                routes,nhs = getRoutesAndNh(externalIp,l3ctxName,leafId=leafId)
                
                for rte in routes:
                    # print(f'\nChecking route {rte.dn}')
                    parentDn=re.escape(str(rte.dn))
                    nextHops = [x for x in nhs if (re.search(parentDn, str(x.dn)) != None)]
                    if not nextHops: continue
                    nh = recursiveNhLookup(nextHops)
                    if nh:
                        leaf = str(nh.dn).split('/')[2].split('-')[1]
                        ctxName = str(nh.dn).split('/')[5].split('dom-')[1]
                        if (ctxName,leaf) not in nhList:
                            nhList.append((ctxName,leaf))
                        else:
                            continue
                        # print(f'Found leaf {leaf} for {externalIp}')
                        extInfo.append(updateLocation(externalIp,nhDn=nh.dn,prefix=rte.prefix))
                    # else:
                    #     print(f'Could not find leaf for {externalIp}')
                return extInfo
            
            progress.update(task, advance=15,description='[magenta bold]Locating IP: Recursive search for IP')
            return recursiveRouteSearch()
        
        with Progress() as progress:
            task = progress.add_task("[magenta bold]Locating IP...", total=100)
            
            while not progress.finished:
                extInfo = locateTask(progress=progress)
                progress.update(task, advance=100)
                if extInfo: 
                    L3.printLocationTable(extInfo)
                else:
                    richWrapper.console.warning(f'External IP {externalIp} not found in the fabric')
            return extInfo
        




