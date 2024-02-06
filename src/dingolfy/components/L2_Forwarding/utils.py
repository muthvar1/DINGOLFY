from ...infra.globals import handles, dingolfyGlobal
from typing import Optional
import typer
import ipaddress
import re
from typing import Optional
from ...infra import richWrapper
from rich.table import Table
from rich.markup import escape
from rich.pretty import pprint
from ...infra.utils import getLeafIdfromLeaName, getLeafNamefromLeafId, sendCmd



class EP_location:
    '''
    list of attributes for an EP
    '''
    type = "fabricEndpoint"
    leaf = None
    ip = None
    mac = None
    ifId = None
    vpcName = None
    fvTenantName = None
    fvCtxName = None
    fvBDName = None
    fvAEPgName = None
    fvAEPgDn= None
    baseEpgDn = None
    fvApName = None
    vlan_id = None
    fvSubnetDn = None
    _pcTag = None
    _epmFlags = None
    _vrfvnid = None
    _bdvnid = None
    _bdhwId = None
    _bdid = None
    _vlanCktEphwId = None
    _vlanCktEpid = None
    _l3CtxpcEnfDir = None
    _l3CtxpcEnfPref = None
    _vpc = False
    _epmIpEpDn = None
    _vlanCktEpDn = None
    _l2BD = None
    _l3Ctx = None

    
    
    
    @staticmethod
    def getTable(leaf: str,remoteEntry: Optional[bool] = False):
        if remoteEntry:
            table = Table(title=f"EP Remote entry located at: {leaf}", style=richWrapper.StyleGuide.title_style,title_justify="left")
        else:
            table = Table(title=f"EP located at: {leaf}", style=richWrapper.StyleGuide.title_style,title_justify="left")
        table.add_column("Field", style="magenta")
        table.add_column("Value", style="green")
        return table
    

class EP:
    @staticmethod
    def printLocationTable(EP_info,verbose: Optional[bool] = True, remoteEntry: Optional[bool] = False):
        def addRow(table,key,value,hint=None):
            if value is None: return
            if key.startswith('_'):
                key = key[1:]
            if hint:
                key = f'{key}({hint})'
            table.add_row(escape(str(key)),escape(str(value)))

        for location in EP_info:
            table = EP_location.getTable(location['leaf'],remoteEntry=remoteEntry)
            for key,value in location.items():
                if key.startswith('__'): continue
                if not verbose and key.startswith('_'): continue
                if key == 'vlan_id':
                    addRow(table,key,value,hint='encap_vlan')
                    continue
                if key == '_vlanCktEpid':
                    addRow(table,key,value,hint='HW vlan id')
                    continue
                if key == '_bdid':
                    addRow(table,key,value,hint='HW BD vlan id')
                    continue
                if key == 'leaf':
                    hint = getLeafNamefromLeafId(value)
                    addRow(table,key,value,hint=hint)
                addRow(table,key,value)
            
            table.pad_edge = True
            richWrapper.console.print('\n')
            richWrapper.console.print(table)
            richWrapper.console.print('\n')
    @staticmethod
    def epgOptions(messagePrefix='',vrf=None,tenantName=None):
        '''
        return a list of epgs in the format fvTenant.name: fvAp.name: fvAEPg.name extracted from the fvAEPg dn and fvESg dn
        Example fvAEPg dn = uni/tn-t0/ap-a0/epg-g1
        Example fvESg dn = uni/tn-t20/ap-customer-521/esg-esg1
        Here we will return t0:a0:g1 and t20:customer-521:esg-esg1(esg)
        '''
        tenantList = []
        for fvTenant in handles.ifc_sdk_handle.lookupByClass('fvTenant'):
            if tenantName and tenantName != fvTenant.name: continue
            tenantList.append(fvTenant.name)
        #msgPrefix = richWrapper.highlight(f'{messagePrefix}Please select the tenant from the list below')
        msgPrefix = f'{messagePrefix}Please select the tenant from the list below'
        table = Table(title=msgPrefix, style=richWrapper.StyleGuide.title_style,title_justify="left")
        for i in range(0, len(tenantList), 4):
            table.add_row(*tenantList[i:i+4])
        table.pad_edge = True
        richWrapper.console.print(table)
        msgPrefix = richWrapper.highlight(f"{messagePrefix}Please select the tenant from the list above")
        richWrapper.console.print(msgPrefix)
        tenant = typer.prompt(f"Default",default=False)
        if not tenant: return None
        if tenant not in tenantList:
            tenant = typer.prompt(f'Invalid Selection:Please select a valid tenant from the list above')
        if tenant not in tenantList:
            richWrapper.console.error(f'Invalid Selection: Aborting')
            typer.Abort()
            return None
        
        tenantDn = f'uni/tn-{tenant}'

        epgList = []
        for fvAEpg in handles.ifc_sdk_handle.lookupByClass('fvAEPg',parentDn=tenantDn):
            fvTenantName = str(fvAEpg.dn).split('/')[1].split('-')[1]
            fvAPName = str(fvAEpg.dn).split('/')[2].split('-')[1]
            fvAEpgName = str(fvAEpg.dn).split('/')[3].split('-')[1]
            epgList.append(f'{fvTenantName}:{fvAPName}:{fvAEpgName}')
        for fvESg in handles.ifc_sdk_handle.lookupByClass('fvESg',parentDn=tenantDn):
            fvTenantName = str(fvESg.dn).split('/')[1].split('-')[1]
            fvAPName = str(fvESg.dn).split('/')[2].split('-')[1]
            fvESgName = str(fvESg.dn).split('/')[3].split('-')[1]
            epgList.append(f'{fvTenantName}:{fvAPName}:{fvESgName}')
        
        #msgPrefix = richWrapper.highlight(f'{messagePrefix}Please select the epg from the list below')
        msgPrefix = f'{messagePrefix}Please select the epg from the list below'
        table = Table(title=msgPrefix, style=richWrapper.StyleGuide.title_style,title_justify="left")
        #Iterate trough epg list and add four epgs per row till the end of the list
        for i in range(0, len(epgList), 4):
            table.add_row(*epgList[i:i+4])
        table.pad_edge = True
        richWrapper.console.print(table)
        msgPrefix = richWrapper.highlight(f'{messagePrefix}Please select the epg from the list above')
        richWrapper.console.print(msgPrefix)
        epg = typer.prompt(f"Default",default=False)
        if not epg: return None
        if epg not in epgList:
            epg = typer.prompt(f'Invalid Selection:Please select a valid epg from the list above',default=False)
            if not epg: return None
        if epg not in epgList:
            richWrapper.console.error(f'Invalid Selection: Aborting')
            typer.Abort()
        return epg

    @staticmethod
    def getVPCnamefromPortChannel(portChannel:str, nodeId:str):
        '''
        Given a portChannel and nodeId, retrieve the vpc name
        '''
        
        for pcRtVpcConf in handles.ifc_sdk_handle.lookupByClass('pcRtVpcConf'):
            if nodeId == str(pcRtVpcConf.dn).split('/')[2].split('-')[1]:
                if portChannel == pcRtVpcConf.parentSKey:
                    return handles.ifc_sdk_handle.lookupByDn(pcRtVpcConf.tDn).name
        return None
    @staticmethod
    def debugEPMos(EPlocation):
        leafName = getLeafNamefromLeafId(EPlocation['leaf'])
        fvAEPgName = EPlocation['fvAEPgName']
        fvTenantName = EPlocation['fvTenantName']
        fvCtxName = EPlocation['fvCtxName']
        fvBDName = EPlocation['fvBDName']
        fvApName = EPlocation['fvApName']
        epg_dn = EPlocation['fvAEPgDn']
        tenant_dn = f'uni/tn-{fvTenantName}'
        ctx_dn = f'uni/tn-{fvTenantName}/ctx-{fvCtxName}'
        bd_dn = f'uni/tn-{fvTenantName}/BD-{fvBDName}'

        # richWrapper.pageSeparator(text='MO Details for ip address: ' + EPlocation['ip'],title='EPM MOs',subtitle=f'located at leaf {leafName}')

        if EPlocation['_epmIpEpDn']: handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(EPlocation['_epmIpEpDn']))
        if epg_dn: 
            handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(epg_dn))
            for mo in handles.ifc_sdk_handle.lookupByClass('fvEpP'):
                if mo.epgPKey == epg_dn:
                    handles.ifc_sdk_handle.printMo(mo)
                    break
            else:
                richWrapper.console.error(f'fvEpP not found for epg_dn:{epg_dn}')
            if EPlocation['_vlanCktEpDn']: handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(EPlocation['_vlanCktEpDn']))
        handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(tenant_dn))
        handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(ctx_dn))
        for mo in handles.ifc_sdk_handle.lookupByClass('fvCtxDef'):
            if mo.ctxDn == ctx_dn:
                handles.ifc_sdk_handle.printMo(mo)
                break
        else:
            richWrapper.console.error(f'fvCtxDef not found for ctx_dn:{ctx_dn}')
        if EPlocation['_l3Ctx']: handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(EPlocation['_l3Ctx']))
        handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(bd_dn))
        if EPlocation['_l2BD']: handles.ifc_sdk_handle.printMo(handles.ifc_sdk_handle.lookupByDn(EPlocation['_l2BD']))

        

        
        
    @staticmethod
    def debugHalRoute(EPlocation,remoteLeafId):
        leafName = getLeafNamefromLeafId(remoteLeafId)
        if not EPlocation['fvSubnetDn']: return None
        if not EPlocation['_l3Ctx']: return None
        vrfName = handles.ifc_sdk_handle.lookupByDn(EPlocation['_l3Ctx']).name
        prefix = handles.ifc_sdk_handle.lookupByDn(EPlocation['fvSubnetDn']).ip
        prefix = str(ipaddress.ip_network(prefix,strict=False))
        ip = prefix.split('/')[0]
        prefixLen = prefix.split('/')[1]
        grep_pattern = f'grep "{ip}/ {prefixLen}"'
        cmd = f'vsh_lc -c "show platform internal hal l3 routes vrf {vrfName}" | {grep_pattern}'
        output = sendCmd(cmd,leafName)
        for line in output.split('\n'):
            if ip in line and prefixLen in line:
                parts = line.split("|")
                # Extract the vrf_hwId and NB-ID
                vrf_hwId = parts[1].strip()
                nb_id = parts[-13].strip()
                msg = richWrapper.highlight(f'NextHop Info for L3 Route - {prefix} on leaf {leafName}')
                richWrapper.console.print(msg)
                cmd = f'vsh_lc -c "show platform internal hal l3 nexthops nexthop-id 0x{nb_id}"'
                op = sendCmd(cmd,leafName)
                for ln in op.split('\n'):
                    if 'L2 Ifindex' in ln:
                        l2ifIndex = ln.split(': ')[1].strip()
                        if l2ifIndex == '0x0':
                            raise Exception(f'Could not find L2 Ifindex for {nb_id} on {leafName} got 0x0')
                        break
                else:
                    raise Exception(f'Could not find L2 Ifindex for {nb_id} on {leafName}')
                cmd = f'show interface snmp | grep "{l2ifIndex}"'
                op = sendCmd(cmd,leafName)
                pattern = r"(\S+)(?:\s+\d+\s+\(0x[\da-fA-F]+\))?"
                for ln in op.split('\n'):
                    match = re.search(pattern, ln)
                    if match:
                        interface_name = match.group(1)
                        break
                else:
                    raise Exception(f'Could not find interface name for {l2ifIndex} on {leafName}')
    @staticmethod
    def debugEPcli(EPlocation):
        '''
        Given an EP location, debug the EP using the cli
        '''
        def epmMac_cli(mac: str)->list:
            '''
            Given a mac address, return the epmMacEp cli commands
            '''
            cmdList = []
            cmdList.append(f'show  system internal epm endpoint mac {mac}')
            return cmdList
        def epmIp_cli(ip)->list:
            '''
            Given an ip address, return the epmIpEp cli commands
            '''
            cmdList = []
            cmdList.append(f'show  system internal epm endpoint ip {ip}')
            return cmdList
        def epmIf_cli(interface)->list:
            '''
            Given an interface, return the epmIfEp cli commands
            '''
            cmdList = []
            cmdList.append(f'show system internal epm interface {interface}')

            return cmdList
        def epmcMac_cli(mac)->list:
            '''
            Given a mac address, return the epmcMacEp cli commands
            '''
            cmdList = []
            cmdList.append(f'vsh_lc -c "show system internal epmc endpoint mac {mac}"')
            return cmdList
        def epmcIp_cli(ip)->list:
            '''
            Given an ip address, return the epmcIpEp cli commands
            '''
            cmdList = []
            cmdList.append(f'vsh_lc -c "show system internal epmc endpoint ip {ip}"')
            return cmdList
        def epmcVlan_cli(vlan)->list:
            '''
            Given a vlan, return the epmcVlanEp cli commands
            '''
            cmdList = []
            cmdList.append(f'vsh_lc -c "show system internal epmc vlan {vlan} detail"')
            return cmdList
        
        def eltmcIf_cli(interface)->list:
            '''
            Given an interface, return the eltmc interface cli commands
            '''
            cmdList = []
            cmdList.append(f'vsh_lc -c "show  system internal eltmc info interface {interface}"')
            return cmdList
        def eltmc_access_encap_cli(vlan):
            '''
            Given a vlan, return the eltmc access encap cli commands
            '''
            cmdList = []
            cmdList.append(f'vsh_lc -c "show  system internal eltmc info vlan access_encap_vlan {vlan}"')
            return cmdList
        
        def zoningRules_cli(scope):
            '''
            Given a scope, return the zoning rules cli commands
            '''
            cmdList = []
            cmdList.append(f'show zoning-rule scope {scope}')
            return cmdList


        leafName = getLeafNamefromLeafId(EPlocation['leaf'])
        mac = EPlocation['mac']
        ip = EPlocation['ip']
        ifId = EPlocation['ifId']
        encap_vlan = EPlocation['vlan_id']
        hw_vlan = EPlocation['_vlanCktEpid']
        bd_vlan = EPlocation['_bdid']
        vrfvnid = EPlocation['_vrfvnid']
        bdvnid = EPlocation['_bdvnid']
        bd_vlan = EPlocation['_bdid']

        cmdList = []
        if mac: 
            cmdList.extend(epmMac_cli(mac))
            cmdList.extend(epmcMac_cli(mac))
        if ip: 
            cmdList.extend(epmIp_cli(ip))
            cmdList.extend(epmcIp_cli(ip))
        if ifId:
            cmdList.extend(epmIf_cli(ifId))
            cmdList.extend(eltmcIf_cli(ifId))
        if hw_vlan: cmdList.extend(epmcVlan_cli(hw_vlan))
        if bd_vlan: cmdList.extend(epmcVlan_cli(bd_vlan))
        if encap_vlan: cmdList.extend(eltmc_access_encap_cli(encap_vlan))
        
        cmdList.extend(zoningRules_cli(vrfvnid))

        richWrapper.console.print(f'EP debug cli for leaf {leafName}')
        sendCmd(cmdList,leafName=leafName)
    


    @staticmethod
    def coop_debug_cli(EPlocation):
        '''
        Given an EP location, debug the EP using coop cli
        '''
        leafName = getLeafNamefromLeafId(EPlocation['leaf'])
        mac = EPlocation['mac']
        ip = EPlocation['ip']
        ifId = EPlocation['ifId']
        encap_vlan = EPlocation['vlan_id']
        hw_vlan = EPlocation['_vlanCktEpid']
        bd_vlan = EPlocation['_bdid']
        vrfvnid = EPlocation['_vrfvnid']
        bdvnid = EPlocation['_bdvnid']
        bd_vlan = EPlocation['_bdid']
        cmdList = []    
        if ip:
            cmdList.append(f'show coop internal info ip-db key {vrfvnid} {ip}')
        if mac:
            cmdList.append(f'show coop internal info repo ep key {bdvnid} {mac}')
        sendCmd(cmdList,spine=True)





    @staticmethod
    def getlocationInfofromEpg(fvAEPgdn,verbose: Optional[bool] = True,printTable: Optional[bool] = True):
        '''
        Given an fvAEPg dn, retrieve the location information
        Derive the vlanCktEp by querying vlanCktEp with fvAEPg.pcTag
        Use the vlanCktEp to derive the l2BD
        Use the l2BD to derive the l3Ctx
        '''
        EP_info = []
        
        fvAEPg = handles.ifc_sdk_handle.lookupByDn(fvAEPgdn)
        if fvAEPg.configSt != 'applied':
            richWrapper.console.warning(f'fvAEPg {fvAEPgdn} is not in applied state, configSt is:{fvAEPg.configSt}')
            
        try:
            int(fvAEPg.pcTag)
        except ValueError:
            richWrapper.console.warning(f'fvAEPg {fvAEPgdn} does not have a valid pcTag:{fvAEPg.pcTag}')
        
        def getVrfScopefromEpg(fvAEPg):
            '''
            Given an epg MO, derive the fvCtx and the fvCtx.scope
            '''
            fvRsBd = handles.ifc_sdk_handle.lookupByClass('fvRsBd',parentDn=fvAEPg.dn)[0]
            fvBD = handles.ifc_sdk_handle.lookupByDn(fvRsBd.tDn)
            fvRsCtx = handles.ifc_sdk_handle.lookupByClass('fvRsCtx',parentDn=fvBD.dn)[0]
            fvCtx = handles.ifc_sdk_handle.lookupByDn(fvRsCtx.tDn)
            return fvCtx.scope
        
        vrfvnid = getVrfScopefromEpg(fvAEPg)

        for vlanCktEp in handles.ifc_sdk_handle.lookupByClass('vlanCktEp'):
            if vlanCktEp.pcTag == fvAEPg.pcTag:
                match = re.search(r'ctx-\[vxlan-(\d+)\]', str(vlanCktEp.dn))
                if match:
                    ctxScope = match.group(1)
                    if ctxScope != vrfvnid:
                        continue    
                else:
                    richWrapper.console.error(f'ctxScope not found vlanCktEp dn - {vlanCktEp.dn}')
                    continue
                richWrapper.console.print(richWrapper.highlight(f'Found vlanCktEp with pcTag:{vlanCktEp.pcTag} for fvAEPg:{fvAEPg.name}'))
                location = dict()
                
                #populate the keys of the location dict with all the attributes of the EP_location class
                for key in EP_location.__dict__.keys():
                    location[key] = None
                location['leaf'] = str(vlanCktEp.dn).split('/')[2].split('-')[1]
                location['fvAEPgName'] = fvAEPg.name
                location['fvApName'] = handles.ifc_sdk_handle.lookupByDn(fvAEPg.parentDn).name
                location['_vlanCktEpDn'] = str(vlanCktEp.dn)
                location['_pcTag'] = vlanCktEp.pcTag
                location['vlan_id'] = vlanCktEp.encap.split('-')[1]
                location['_vlanCktEphwId'] = vlanCktEp.hwId
                location['_vlanCktEpid'] = vlanCktEp.id
                pattern = r"^(topology\/pod-\d+\/node-\d+\/sys\/ctx-\[vxlan-\d+\])\/.*"
                result = re.search(pattern,str(vlanCktEp.dn))
                if result:
                    location['_l3Ctx'] = result.group(1)
                    _l3Ctx = handles.ifc_sdk_handle.lookupByDn(location['_l3Ctx'])
                    location['_vrfvnid'] = _l3Ctx.scope
                    location['_l3CtxpcEnfDir'] = _l3Ctx.pcEnfDir
                    location['_l3CtxpcEnfPref'] = _l3Ctx.pcEnfPref

                # result = re.search(r'ctx-\[vxlan-(\d+)\]',str(mo.dn))
                # if result: location['_vrfvnid'] = result.group(1)
                pattern = r"^(topology\/pod-\d+\/node-\d+\/sys\/ctx-\[vxlan-\d+\]\/bd-\[vxlan-\d+\])\/.*"
                result = re.search(pattern,str(vlanCktEp.dn))
                if result:
                    location['_l2BD'] = result.group(1)
                    _l2BD = handles.ifc_sdk_handle.lookupByDn(location['_l2BD'])
                    location['_bdvnid'] = _l2BD.fabEncap.split('-')[1]
                    location['_bdhwId'] = _l2BD.hwId
                    location['_bdid'] = _l2BD.id
                #Extract fvCtxName and tenantName from the vrfvnid
                for mo in handles.ifc_sdk_handle.lookupByClass('fvCtx'):
                    if mo.scope == location['_vrfvnid']:
                        location['fvCtxName'] = mo.name
                        location['fvTenantName'] = handles.ifc_sdk_handle.lookupByDn(mo.parentDn).name
                #Extract fvBDName from the bdvnid
                for mo in handles.ifc_sdk_handle.lookupByClass('fvBD'):
                    if mo.seg == location['_bdvnid']:
                        location['fvBDName'] = mo.name
                
                EP_info.append(location)
                #pprint(location)
        if not EP_info: richWrapper.console.print(f'seems like the fvAEPg {fvAEPgdn} is not deployed')
        if printTable: EP.printLocationTable(EP_info)
        return EP_info

    
    @staticmethod
    def updateLocationInfo(epm):
        def uSegEsgCheck(addr,fvApDn,epgDn):
            '''
            1. Check if the addr is a mac or ipv4 or ipv6 addr
            2. If mac, then query for all fvCEp under the fvApDn, and retrieve the fvCEp.addr
            3. If ip, then query for all fvIp under the fvApDn, and retrieve the fvIp.addr
            3. if the fvCEp or fvIp has a .baseEpgDn that matches the epgDn, Then it likely is a useg or esg epg. In this case return the parentDn of the fvCEp/FvIp
            '''
            #check if it is an ipv4,ipv6 or mac address
            mac_pattern = re.compile(r'^([0-9A-Fa-f]{2}[:-]){5}([0-9A-Fa-f]{2})$')
            ipv4_pattern = re.compile(r'^(\d{1,3}\.){3}\d{1,3}$')
            ipv6_pattern = re.compile(r'^(([0-9a-fA-F]{1,4}):){0,7}([0-9a-fA-F]{1,4})::?(([0-9a-fA-F]{1,4}):){0,7}([0-9a-fA-F]{1,4})$')
            if re.match(mac_pattern, addr):
                moClass = 'fvCEp'
                attribute = 'mac'
            elif re.match(ipv4_pattern, addr):
                moClass = 'fvIp'
                attribute = 'addr'
            elif re.match(ipv6_pattern, addr):
                moClass = 'fvIp'
                attribute = 'addr'
                #convert ipv6 address to compressed format
                addr = str(ipaddress.ip_address(addr).compressed)
            else:
                msg = f'Invalid address format:{addr}'
                richWrapper.console.error(msg)
                raise typer.Exit(f'Invalid address format:{addr}')
            
            for mo in handles.ifc_sdk_handle.lookupByClass(moClass,parentDn=fvApDn):
                if getattr(mo,attribute) == addr:
                    if mo.baseEpgDn == epgDn:
                        if moClass == 'fvCEp':
                            return str(mo.parentDn)
                        elif moClass == 'fvIp':
                            fvCEPDn = str(mo.parentDn)
                            fvCEP = handles.ifc_sdk_handle.lookupByDn(fvCEPDn)
                            return str(fvCEP.parentDn)
            return None

        location = dict()
        #populate the keys of the location dict with all the attributes of the EP_location class
        for key in EP_location.__dict__.keys():
            location[key] = None
        
        location['_epmIpEpDn'] = str(epm.dn)
        location['_pcTag'] = epm.pcTag
        location['_epmFlags'] = epm.flags
        leaf = str(epm.dn).split('/')[2].split('-')[1]
        location['leaf'] = leaf
        location['ip'] = epm.addr
        location['ifId'] = epm.ifId
        if 'vpc-attached'in epm.flags:
            location['vpc'] = True
            location['vpcName'] = EP.getVPCnamefromPortChannel(epm.ifId,leaf)
        
        #Extract vrfvnid,bdvnid,vlanCktEpDn, l2BD from the dn, 
        # example 1: topology/pod-2/node-409/sys/ctx-[vxlan-2588674]/bd-[vxlan-14680094]/db-ep/ip-[2011:59:20::9]
        # example 2: topology/pod-2/node-413/sys/ctx-[vxlan-2097209]/bd-[vxlan-15761597]/vlan-[vlan-855]/db-ep/ip-[8.5.5.168]
        # where the vlanCktEpDn is topology/pod-2/node-413/sys/ctx-[vxlan-2097209]/bd-[vxlan-15761597]/vlan-[vlan-855] in example 2
        # where the l2BD is topology/pod-2/node-413/sys/ctx-[vxlan-2097209]/bd-[vxlan-15761597] in example 2
        
        pattern = r"^(topology\/pod-\d+\/node-\d+\/sys\/ctx-\[vxlan-\d+\])\/.*"
        result = re.search(pattern,str(epm.dn))
        if result:
            location['_l3Ctx'] = result.group(1)
            _l3Ctx = handles.ifc_sdk_handle.lookupByDn(location['_l3Ctx'])
            location['_vrfvnid'] = _l3Ctx.scope
            location['_l3CtxpcEnfDir'] = _l3Ctx.pcEnfDir
            location['_l3CtxpcEnfPref'] = _l3Ctx.pcEnfPref

        # result = re.search(r'ctx-\[vxlan-(\d+)\]',str(mo.dn))
        # if result: location['_vrfvnid'] = result.group(1)
        pattern = r"^(topology\/pod-\d+\/node-\d+\/sys\/ctx-\[vxlan-\d+\]\/bd-\[vxlan-\d+\])\/.*"
        result = re.search(pattern,str(epm.dn))
        if result:
            location['_l2BD'] = result.group(1)
            _l2BD = handles.ifc_sdk_handle.lookupByDn(location['_l2BD'])
            location['_bdvnid'] = _l2BD.fabEncap.split('-')[1]
            location['_bdhwId'] = _l2BD.hwId
            location['_bdid'] = _l2BD.id
        
        pattern = r"topology\/pod-\d+\/node-\d+\/sys\/ctx-\[vxlan-\d+\]\/bd-\[vxlan-\d+\]\/vlan-\[vlan-\d+\]"
        result = re.search(pattern,str(epm.dn))
        if result: 
            location['_vlanCktEpDn'] = result.group()
            _vlanCktEpDn = handles.ifc_sdk_handle.lookupByDn(location['_vlanCktEpDn'])
            
            location['vlan_id'] = _vlanCktEpDn.encap.split('-')[1]
            location['_vlanCktEphwId'] = _vlanCktEpDn.hwId
            location['_vlanCktEpid'] = _vlanCktEpDn.id
            
        #Extract fvCtxName and tenantName from the vrfvnid
        for mo in handles.ifc_sdk_handle.lookupByClass('fvCtx'):
            if mo.scope == location['_vrfvnid']:
                location['fvCtxName'] = mo.name
                location['fvTenantName'] = handles.ifc_sdk_handle.lookupByDn(mo.parentDn).name
        #Extract fvBDName from the bdvnid
        for mo in handles.ifc_sdk_handle.lookupByClass('fvBD'):
            if mo.seg == location['_bdvnid']:
                location['fvBDName'] = mo.name
        #Extract fvAEPgName from the vlanCktEpDn
        if location['_vlanCktEpDn']:
            location['fvAEPgDn'] = handles.ifc_sdk_handle.lookupByDn(location['_vlanCktEpDn']).epgDn
            location['fvAEPgName'] = handles.ifc_sdk_handle.lookupByDn(location['fvAEPgDn']).name
            fvApDn = handles.ifc_sdk_handle.lookupByDn(location['fvAEPgDn']).parentDn
            location['fvApName'] = handles.ifc_sdk_handle.lookupByDn(fvApDn).name
            uSegEsgCheckDn = uSegEsgCheck(location['ip'],fvApDn,location['fvAEPgDn'])
            if uSegEsgCheckDn:
                #Then we now update the basePgDn and the fvAEPgDn 
                location['baseEpgDn'] = location['fvAEPgDn']
                location['fvAEPgDn'] = uSegEsgCheckDn


            # for mo in handles.ifc_sdk_handle.lookupByClass('fvAEPg'):
            #     if mo.pcTag == location['_pcTag']:
            #         location['fvAEPgName'] = mo.name
            #         location['fvAP'] = handles.ifc_sdk_handle.lookupByDn(mo.parentDn).name
            #         location['fvAEPgDn'] = str(mo.dn)
            #         break
            # else:
            #     #check for esg
            #     for mo in handles.ifc_sdk_handle.lookupByClass('fvESg'):
            #         if mo.pcTag == location['_pcTag']:
            #             location['fvAEPgName'] = mo.name
            #             location['fvAP'] = handles.ifc_sdk_handle.lookupByDn(mo.parentDn).name
            #             location['fvAEPgDn'] = str(mo.dn)
            #             break
            
        epmMacEps = handles.ifc_sdk_handle.lookupByClass('epmMacEp',parentDn=epm.parentDn)
        for macEp in epmMacEps:
            epmRsMacEpToIpEpAtts = handles.ifc_sdk_handle.lookupByClass('epmRsMacEpToIpEpAtt',parentDn=macEp.dn)
            for epmRsMacEpToIpEpAtt in epmRsMacEpToIpEpAtts:
                if epmRsMacEpToIpEpAtt.tDn == epm.dn:
                    location['mac'] = macEp.addr
                    break
            
        for fvSubnet in handles.ifc_sdk_handle.lookupByClass('fvSubnet'):
            #Check if ip address falls under fvSubnet.ip prtefix
            if ipaddress.ip_address(location['ip']) in ipaddress.ip_network(fvSubnet.ip,strict=False):
                location['fvSubnetDn'] = str(fvSubnet.dn)
        
        return location

    @staticmethod
    def locate_ip(*args,**kwargs):
        return EP.ip_location(*args,**kwargs)

    @staticmethod
    def ip_location(ip: str,comprehensive: Optional[bool] = False,verbose: Optional[bool] = False,printTable: Optional[bool] = True, 
                    vrfName: Optional[str]=None,leafName: Optional[str]=None,checkExternalIp: Optional[bool] = True,remoteEntry: Optional[bool] = False):
        '''
        Given an ip address, find the location of the ip address
        :param ip: ip address to find the location of
        :param comprehensive: if True, will provide comprehensive information about the ip address, including bdvnid, vrfvnid, etc
        :return: EP location information
        '''
        
        def basic_info(ip):
            #Deprecated
            raise typer.Exit('basic_info is deprecated, please use comprehensive_info instead')
            
            EP.validate_ip(ip)
            leaves = []
            for mo in handles.ifc_sdk_handle.lookupByClass('epmIpEp'):
                ip = str(ipaddress.ip_address(ip).compressed)
                if ip != mo.addr:
                    continue
                if 'local' in mo.flags:
                    leaf = str(mo.dn).split('/')[2].split('-')[1]
                    if leaf not in leaves:
                        leaves.append(leaf)
                        richWrapper.console.print(f'EP {ip} is local to leaf {leaf} on interface: {mo.ifId}')
            if not leaves: richWrapper.console.print(f'EP {ip} is not local to any leaf')
            if len(leaves) > 1: 
                richWrapper.console.print(f'EP {ip} is local to multiple leaves:{leaves}. Checking if there is an associated VPC')
                vpcName=EP.retrieveVPCnamefromIp(ip)
                if vpcName: leaves.append(vpcName)
            return leaves
        def comprehensive_info(ip,verbose: Optional[bool] = False,vrfName: Optional[str]=None,checkExternalIp: Optional[bool] = True,leafId: Optional[str]=None):
            
            EP_info = []
            
            EP.validate_ip(ip)
            if vrfName:
                #vrfName is in format t0:ctx1, where t0 is the tenant name and ctx1 is the vrf name
                #Extrapolate fvCtx dn from this in the format uni/tn-t0/ctx-ctx1
                vrfDn = f'uni/tn-{vrfName.split(":")[0]}/ctx-{vrfName.split(":")[1]}'
                _vrfvnid=handles.ifc_sdk_handle.lookupByDn(vrfDn).scope

            
            for fabricNode in handles.ifc_sdk_handle.lookupByClass('fabricNode'):
                if leafId:
                    if leafId != fabricNode.id: continue
                epmIpEps = handles.ifc_sdk_handle.lookupByClass('epmIpEp',parentDn=fabricNode.dn)
                for epm in epmIpEps:
                    ip = str(ipaddress.ip_address(ip).compressed)
                    if ip != epm.addr:
                        continue
                    if remoteEntry:
                        if 'local' in epm.flags: continue
                    else:
                        if 'local' not in epm.flags: continue
                    # if local,psvi flags are present, then this would most likely be a pervasive bd subnet, so skip
                    if 'psvi' in epm.flags: continue 
                    if vrfName and not remoteEntry: #if it is a remoteEnty then there is a possibility that the ip is not in the vrf(shared service)
                        if 'vxlan-'+_vrfvnid not in str(epm.dn): continue
                    
                    if 'local-aged' in epm.flags:continue #for locally aged entries, skip. Quite possibly a stale entry resulting from an ep move

                    location = EP.updateLocationInfo(epm)
                    EP_info.append(location)
            if not EP_info:
                loc = 'remote' if remoteEntry else 'local' 
                richWrapper.console.print(f'EP {ip} does not have a {loc} entry on any leaf')
                if checkExternalIp:
                    from ...components.L3_Forwarding.utils import L3
                    richWrapper.console.print(f'Checking if {ip} is an external ip')
                    return L3.locate_ip(externalIp=ip,l3ctxName=vrfName,checkFabricEndpoint=False)

            #else: richWrapper.console.print(f'\n####### EP {ip} has been located as below #######\n')
            #Print all the EP_info by printing all keys and values except hidden keys
            

            
            
            if printTable: 
                if remoteEntry: EP.printLocationTable(EP_info,verbose=verbose,remoteEntry=remoteEntry)
                else: EP.printLocationTable(EP_info,verbose=verbose)
            
            return EP_info


        leafId = None if not leafName else getLeafIdfromLeaName(leafName)

        
        if comprehensive: return comprehensive_info(ip,verbose=verbose,vrfName=vrfName,checkExternalIp=checkExternalIp,leafId=leafId)
        else: return basic_info(ip)

    @staticmethod
    def retrieveVPCnamefromIp(ip:str):
        for mo in handles.ifc_sdk_handle.lookupByClass('fvIp'):
            if ip != mo.addr:
                continue
            try:
                return handles.ifc_sdk_handle.lookupByDn(mo.fabricPathDn).name
                
            except Exception as e:
                msg = f'Got Exception:{e} when trying to retrieve vpcName from ip:{ip}'
                richWrapper.console.print(msg)
                return None

    
    @staticmethod
    def validate_ip(ip: str):
        try:
            ipaddress.ip_address(ip)
        except ValueError:
            raise typer.BadParameter(f'Please provide correct ip/ipv6 format:{ip}')
        return ip
        

    def mac_location(mac:str):
        EP.validate_mac(mac)
        leaves = []
        for mo in handles.ifc_sdk_handle.lookupByClass('epmMacEp'):
            if mac != mo.addr:
                continue
            if 'local' in mo.flags:
                leaf = str(mo.dn).split('/')[2]
                if leaf not in leaves:
                    leaves.append(leaf)
                    richWrapper.console.print(f'MAC {mac} is local to leaf {leaf} on interface: {mo.ifId}')
        if not leaves: richWrapper.console.print(f'MAC {mac} is not local to any leaf')
        return leaves
    

    def validate_mac(mac: str):
        '''
        Given a mac address validate that it is a valid mac address
        Also validate that it is in the correct format and has no special characters
        :param mac: mac address to validate
        :return: mac address

        '''
        if mac is None:
            raise typer.BadParameter(f'Please provide mac address')
        mac = mac.replace(':', '')
        if len(mac) != 12:
            raise typer.BadParameter(f'Please provide correct mac address format:{mac}')
        try:
            int(mac, 16)
        except ValueError:
            raise typer.BadParameter(f'Please provide correct mac address format:{mac}')
        
    def locate_epg(epg:str):
        '''
        
        '''
        pass
    def bridgedTraffic(subnetDn1,subnetDn2):
        '''
        Given two subnetDns, determine if they are routed or bridged.
        If routed return False, if bridged return True
        '''

        subnet1 = ipaddress.ip_network(handles.ifc_sdk_handle.lookupByDn(subnetDn1).ip,strict=False)
        subnet2 = ipaddress.ip_network(handles.ifc_sdk_handle.lookupByDn(subnetDn2).ip,strict=False)
        if subnet1.overlaps(subnet2):
            return True
        else:
            return False