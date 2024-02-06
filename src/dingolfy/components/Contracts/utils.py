from ...infra.globals import handles
from ...infra import richWrapper
from rich.table import Table
from rich.markup import escape
from rich.pretty import pprint
import typer
from ...infra import richWrapper
from typing import Optional
from ...infra.utils import getLeafNamefromLeafId, vrfTable, leafTable
from ..L2_Forwarding.utils import EP
from ...infra.utils import sendCmd

class Contracts:

    @staticmethod
    def getFilterIdfromFilterName(filterName,fvTenantDn):
        for filter in handles.ifc_sdk_handle.lookupByClass('vzFilter'):
            if filter.name == filterName:
                return filter.fwdId
        richWrapper.console.warning(f'Filter {filterName} not found in tenant {fvTenantDn}')
        return None
    
    @staticmethod
    def filterIdOptions(fvTenantDn):
        msgPrefix = richWrapper.highlight(f'Please select the filterName or filterId from the list below')
        table = Table(title=msgPrefix, style=richWrapper.StyleGuide.title_style,title_justify="left")
        filterList = []
        for filter in handles.ifc_sdk_handle.lookupByClass('vzFilter',parentDn=fvTenantDn):
            filterList.append(f'{filter.name}: {filter.fwdId}')
        for i in range(0, len(filterList), 4):
            table.add_row(*filterList[i:i+4])
        table.pad_edge = True
        richWrapper.console.print(table)
        msgPrefix = richWrapper.highlight(f'Please select the filterName or filterId from the list above')
        filterOption = typer.prompt(f'Please only select one or the other filterName/filterId. Default'
                                    ,default=False)
        
        return filterOption

    @staticmethod
    def zoning_rule(vrf=None,leafName=None,srcEpg=None,dstEpg=None):
        if not vrf: l3ctxName = vrfTable(messagePrefix='Contracts:')
        else: l3ctxName = vrf
        if l3ctxName not in [None,'all']:
            tenantName = l3ctxName.split(":")[0]
        else:
            richWrapper.console.error(f'A valid vrf is needed for all contracts related commands')
        if not leafName: leafName = leafTable(messagePrefix='Contracts:')
        if not srcEpg: srcEpg = EP.epgOptions(messagePrefix='For source EPG ',tenantName=tenantName)
        if not dstEpg: dstEpg = EP.epgOptions(messagePrefix='For destination EPG ',tenantName=tenantName)
        
        
        


        
        def constructZoningCmd(srcPctag: Optional[str]=None,dstPctag: Optional[str] = None ,
                            scopeId: Optional[str] = None,filterId: Optional[str] = None):
            cmd = 'show zoning-rule'
            if srcPctag and dstPctag and scopeId:
                cmd = cmd + f' | grep {srcPctag} | grep {dstPctag} | grep {scopeId}'
            elif srcPctag and dstPctag and not scopeId:
                cmd = cmd + f' | grep {srcPctag} | grep {dstPctag}'
            elif srcPctag and not dstPctag and scopeId:
                cmd = cmd + f' | grep {srcPctag} | grep {scopeId}'
            elif srcPctag and not dstPctag and not scopeId:
                cmd = cmd + f' | grep {srcPctag}'
            elif not srcPctag and dstPctag and scopeId:
                cmd = cmd + f' | grep {dstPctag} | grep {scopeId}'
            elif not srcPctag and dstPctag and not scopeId:
                cmd = cmd + f' | grep {dstPctag}'
            elif not srcPctag and not dstPctag and not scopeId:
                return cmd
            elif srcPctag and dstPctag and scopeId and filterId:
                cmd = 'show zoning-rule' + f' filter {filterId} | grep {srcPctag} | grep {dstPctag} | grep {scopeId}'
            else:
                return cmd
            
            return cmd


        if l3ctxName:
            for l3ctx in handles.ifc_sdk_handle.lookupByClass('l3Ctx'):
                if l3ctx.name == l3ctxName:
                    userScopeId = l3ctx.scope
                    break
        if srcEpg:
            #srcEpg is in the format fvTenantName:fvApName:fvAEPgName
            srcEpgDn = f'uni/tn-{srcEpg.split(":")[0]}/ap-{srcEpg.split(":")[1]}/epg-{srcEpg.split(":")[2]}'
            srcEPInfo = EP.getlocationInfofromEpg(fvAEPgdn=srcEpgDn,verbose=True)
            if not srcEPInfo:
                richWrapper.console.warning(f'srcEpg does not seem to be deployed. Please check the fabric for issues')
                srcEpg = None
            else:
                srcFilter = Contracts.filterIdOptions(fvTenantDn=f'uni/tn-{srcEpg.split(":")[0]}')
                if srcFilter:
                    if srcFilter.isdigit():
                        srcFilterId = srcFilter
                    else:
                        fvTenantDn = f'uni/tn-{srcEpg.split(":")[0]}'

                        srcFilterId = Contracts.getFilterIdfromFilterName(filterName=srcFilter,fvTenantDn=fvTenantDn)

                    if not srcFilterId:
                        richWrapper.console.warning(f'srcFilter does not seem to be deployed. Please check the fabric for issues')
                        srcFilter = None
                    else:
                        srcFilter = srcFilterId

        
        if dstEpg:
            #dstEpg is in the format fvTenantName:fvApName:fvAEPgName
            dstEpgDn = f'uni/tn-{dstEpg.split(":")[0]}/ap-{dstEpg.split(":")[1]}/epg-{dstEpg.split(":")[2]}'
            dstEPInfo = EP.getlocationInfofromEpg(fvAEPgdn=dstEpgDn,verbose=True)
            if not dstEPInfo:
                richWrapper.console.warning(f'dstEpg does not seem to be deployed. Please check the fabric for issues')
                dstEpg = None
            else:
                dstFilter = Contracts.filterIdOptions(fvTenantDn=f'uni/tn-{dstEpg.split(":")[0]}')
                if dstFilter:
                    if dstFilter.isdigit():
                        dstFilterId = dstFilter
                    else:
                        fvTenantDn = f'uni/tn-{dstEpg.split(":")[0]}'
                        dstFilterId = Contracts.getFilterIdfromFilterName(filterName=dstFilter,fvTenantDn=fvTenantDn)

                    if not dstFilterId:
                        richWrapper.console.warning(f'dstFilter does not seem to be deployed. Please check the fabric for issues')
                        dstFilter = None
                    else:
                        dstFilter = dstFilterId

        if srcEpg and dstEpg and l3ctx and leafName:
            # If srcEPG and dstEPG are in the same VRF, then use the scope id of the VRF to derive the zoning rules
            if srcEPInfo[0]['_vrfvnid'] == dstEPInfo[0]['_vrfvnid'] == userScopeId:
                richWrapper.console.print(f'Both srcEpg and dstEpg are in the same VRF')
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                sendCmd(cmd=cmd,leafName=leafName)
            elif srcEPInfo[0]['_vrfvnid'] == userScopeId and dstEPInfo[0]['_vrfvnid'] != userScopeId:
                richWrapper.console.print(f'srcEpg is in the same VRF as the user provided VRF but not dstEpg')
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"])
                sendCmd(cmd=cmd,leafName=leafName)

            elif srcEPInfo[0]['_vrfvnid'] != userScopeId and dstEPInfo[0]['_vrfvnid'] == userScopeId:
                richWrapper.console.print(f'dstEpg is in the same VRF as the user provided VRF but not srcEpg')
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"])
                sendCmd(cmd=cmd,leafName=leafName)
                
            else:
                richWrapper.console.print(f'Both srcEpg and dstEpg are not in the same VRF as the user provided VRF')
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"])
                sendCmd(cmd=cmd,leafName=leafName)

        elif l3ctxName and leafName and not srcEpg and not dstEpg:
            richWrapper.console.print(f'Only the user provided VRF is provided')
            cmd = f'show zoning-rule | grep {userScopeId}'
            sendCmd(cmd=cmd,leafName=leafName)
        
        elif l3ctxName and leafName and srcEpg and not dstEpg:
            if srcEPInfo[0]['_vrfvnid'] == userScopeId:
                richWrapper.console.print(f'Only the user provided VRF and srcEpg are provided')
                cmd = f'show zoning-rule | grep {srcEPInfo[0]["_pcTag"]} | grep {userScopeId}'
                sendCmd(cmd=cmd,leafName=leafName)
            else:
                richWrapper.console.print(f'Only the user provided VRF and srcEpg are provided')
                cmd = f'show zoning-rule | grep {srcEPInfo[0]["_pcTag"]} | grep {userScopeId}'
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = f'show zoning-rule | grep {srcEPInfo[0]["_pcTag"]} | grep {srcEPInfo[0]["_vrfvnid"]}'
                sendCmd(cmd=cmd,leafName=leafName)
        
        elif l3ctxName and leafName and dstEpg and not srcEpg:
            if dstEPInfo[0]['_vrfvnid'] == userScopeId:
                richWrapper.console.print(f'Only the user provided VRF and dstEpg are provided')
                cmd = f'show zoning-rule | grep {dstEPInfo[0]["_pcTag"]} | grep {userScopeId}'
                sendCmd(cmd=cmd,leafName=leafName)
            else:
                richWrapper.console.print(f'Only the user provided VRF and dstEpg are provided')
                cmd = f'show zoning-rule | grep {dstEPInfo[0]["_pcTag"]} | grep {userScopeId}'
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = f'show zoning-rule | grep {dstEPInfo[0]["_pcTag"]} | grep {dstEPInfo[0]["_vrfvnid"]}'
                sendCmd(cmd=cmd,leafName=leafName)
        elif l3ctxName and srcEpg and dstEpg and not leafName:
            leafList = []
            for location in srcEPInfo:
                try:
                    int(location['leaf'])
                    leafName = getLeafNamefromLeafId(location['leaf'])
                    if leafName in leafList:
                        continue
                    else:
                        leafList.append(leafName)
                except ValueError:
                    continue
                richWrapper.console.print(f'Only the user provided VRF, srcEpg and dstEpg are provided')
                if srcEPInfo[0]['_vrfvnid'] == dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                elif srcEPInfo[0]['_vrfvnid'] == userScopeId and dstEPInfo[0]['_vrfvnid'] != userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                elif srcEPInfo[0]['_vrfvnid'] != userScopeId and dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                else:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
            for location in dstEPInfo:
                leafName = getLeafNamefromLeafId(location['leaf'])
                richWrapper.console.print(f'Only the user provided VRF, srcEpg and dstEpg are provided')
                try:
                    int(location['leaf'])
                    leafName = getLeafNamefromLeafId(location['leaf'])
                    if leafName in leafList:
                        continue
                    else:
                        leafList.append(leafName)
                except ValueError:
                    continue
                richWrapper.console.print(f'Only the user provided VRF, srcEpg and dstEpg are provided')
                if srcEPInfo[0]['_vrfvnid'] == dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                elif srcEPInfo[0]['_vrfvnid'] == userScopeId and dstEPInfo[0]['_vrfvnid'] != userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                elif srcEPInfo[0]['_vrfvnid'] != userScopeId and dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                else:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
        elif l3ctxName and srcEpg and dstEpg and leafName and srcFilter and dstFilter:
            if srcEPInfo[0]['_vrfvnid'] == dstEPInfo[0]['_vrfvnid'] == userScopeId:
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=dstFilter)
                sendCmd(cmd=cmd,leafName=leafName)
            elif srcEPInfo[0]['_vrfvnid'] == userScopeId and dstEPInfo[0]['_vrfvnid'] != userScopeId:
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"], filterId=dstFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"], filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=dstFilter)
            elif srcEPInfo[0]['_vrfvnid'] != userScopeId and dstEPInfo[0]['_vrfvnid'] == userScopeId:
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"], filterId=dstFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"], filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=dstFilter)
                sendCmd(cmd=cmd,leafName=leafName)
            else:
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"], filterId=dstFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"], filterId=srcFilter)
                sendCmd(cmd=cmd,leafName=leafName)
                cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId, filterId=dstFilter)
        
        elif l3ctxName and srcEpg and dstEpg and srcFilter and dstFilter and not leafName:
            leafList = []
            for location in srcEPInfo:
                try:
                    int(location['leaf'])
                    leafName = getLeafNamefromLeafId(location['leaf'])
                    if leafName in leafList:
                        continue
                    else:
                        leafList.append(leafName)
                except ValueError:
                    continue
                if srcEPInfo[0]['_vrfvnid'] == dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                elif srcEPInfo[0]['_vrfvnid'] == userScopeId and dstEPInfo[0]['_vrfvnid'] != userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"],filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"],filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=dstFilter)
                elif srcEPInfo[0]['_vrfvnid'] != userScopeId and dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"],filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"],filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                else:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],filterId=srcFilter,scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],filterId=dstFilter,scopeId=dstEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],filterId=srcFilter,scopeId=srcEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],filterId=dstFilter,scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
            for location in dstEPInfo:
                leafName = getLeafNamefromLeafId(location['leaf'])
                richWrapper.console.print(f'Only the user provided VRF, srcEpg and dstEpg are provided')
                try:
                    int(location['leaf'])
                    leafName = getLeafNamefromLeafId(location['leaf'])
                    if leafName in leafList:
                        continue
                    else:
                        leafList.append(leafName)
                except ValueError:
                    continue
                if srcEPInfo[0]['_vrfvnid'] == dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                elif srcEPInfo[0]['_vrfvnid'] == userScopeId and dstEPInfo[0]['_vrfvnid'] != userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"],filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=dstEPInfo[0]["_vrfvnid"],filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=dstFilter)
                elif srcEPInfo[0]['_vrfvnid'] != userScopeId and dstEPInfo[0]['_vrfvnid'] == userScopeId:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"],filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],scopeId=srcEPInfo[0]["_vrfvnid"],filterId=srcFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],scopeId=userScopeId,filterId=dstFilter)
                    sendCmd(cmd=cmd,leafName=leafName)
                else:
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],filterId=srcFilter,scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],filterId=dstFilter,scopeId=dstEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd = constructZoningCmd(srcPctag=srcEPInfo[0]["_pcTag"],dstPctag=dstEPInfo[0]["_pcTag"],filterId=srcFilter,scopeId=srcEPInfo[0]["_vrfvnid"])
                    sendCmd(cmd=cmd,leafName=leafName)
                    cmd=constructZoningCmd(srcPctag=dstEPInfo[0]["_pcTag"],dstPctag=srcEPInfo[0]["_pcTag"],filterId=dstFilter,scopeId=userScopeId)
                    sendCmd(cmd=cmd,leafName=leafName)




        else:   
            richWrapper.console.error(f'Please provide the supported combination of inputs as below')
            richWrapper.console.print(f'1. VRF and leafName')
            richWrapper.console.print(f'2. VRF, leafName and srcEpg')
            richWrapper.console.print(f'3. VRF, leafName and dstEpg')
            richWrapper.console.print(f'4. VRF, leafName, srcEpg and dstEpg')
            richWrapper.console.print(f'5. VRF, srcEpg and dstEpg')
            richWrapper.console.print(f'6. VRF leafName, srcEpg, dstEpg and src and dest filtId/filtName')
            richWrapper.console.print(f'7. VRF, srcEpg, dstEpg and src and dest filtId/filtName')