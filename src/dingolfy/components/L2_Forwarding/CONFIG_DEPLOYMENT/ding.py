from ....infra.utils import sendCmd
from ....infra.globals import handles, dingolfyGlobal
from ....infra.utils import vrf_callback, vrf_options,leaf_callback,leaf_options,ipValidation,versionValidation
from ..utils import EP
from typing import Optional
import typer
from ....infra import richWrapper
from rich.panel import Panel
from rich.markup import escape

def collect_logs(vlan:str, interface: Optional[str] = None, leafName: Optional[str] = 'all'):
    '''
    Collect all the logs for L2 Forwarding CONFIG_DEPLOYMENT logs
    '''
    show_vlan(vlan=vlan,leafName=leafName,extended=True)
    if interface not in [None,""]:
        show_int(interface=interface,leafName=leafName)
    

def show_vlan(vlan:str,leafName: Optional[str] = 'all', extended: Optional[bool] = False):
    '''
    Check for Vlan and/and bd-vnid deployment in Leaf. If extended option is used,
    bd-vnid info is also provided
    show vlan id <vlan>
    show vlan id <vlan> extended
    '''
    if extended:
        cmd=f'show vlan id {vlan} extended'
    else:
        cmd=f'show vlan id {vlan}'
    sendCmd(cmd=cmd,leafName=leafName)

def show_int(interface:str,leafName: Optional[str] = 'all'):
    '''
    Check for interface deployment in Leaf
    show interface <> brief
    '''
    
    cmd=f'show interface {interface} brief'
    
    sendCmd(cmd=cmd,leafName=leafName)

def validate_config():
    '''
    Given a list of user provided inputs, validate if the config is deployed correctly
    '''
    EP_info = None
    ip = typer.prompt("Please provide interested ip , eg: 1.1.1.1. If not needed, press enter")
    verbose = typer.confirm("Please opt for verbose output, eg: True/False. If not needed, press enter",default=True)
    
    def ip_not_found():
        
        richWrapper.console.print(f'Will use other inputs to validate config')
        epg = EP.epgOptions()
        #Extract the fvAEPg dn from the epg
        #epg is in format fvTenantName:fvApName:epg-fvAEPgName or fvTenantName:fvApName:esg-fvESgName
        #fvAEPg dn is in format uni/tn-{fvTenantName}/ap-{fvApName}/epg-{fvAEPgName} or uni/tn-{fvTenantName}/ap-{fvApName}/esg-fvESgName}
        
        fvAEPg_dn = f'uni/tn-{epg.split(":")[0]}/ap-{epg.split(":")[1]}/{epg.split(":")[2]}'
        richWrapper.console.print(f'fvAEPg dn: {fvAEPg_dn}')
        EP_info=EP.getlocationInfofromEpg(fvAEPgdn=fvAEPg_dn,verbose=verbose)
        if not EP_info:
            richWrapper.console.warning('vlanCktEp does not seem to be deployed. Please check the fabric for issues')
        return epg.split(":")[0]
    fvNWIssues = handles.ifc_sdk_handle.lookupByClass('fvNwIssues')
    if ip not in [None,""]:
        EP_info = EP.ip_location(ip=ip,comprehensive=True,verbose=verbose)
        fvNWIssues = [fvNWIssue for fvNWIssue in fvNWIssues if any(location['fvTenantName'] in str(fvNWIssue.dn) for location in EP_info)]
    if not EP_info:
        richWrapper.console.warning('EP not found')
        fvTenantName = ip_not_found()
        fvNWIssues = [fvNWIssue for fvNWIssue in fvNWIssues if fvTenantName in str(fvNWIssue.dn)]
    
    
    
    
    
    if fvNWIssues:

        richWrapper.console.warning('fvNwIssues found in the fabric. Please check the fabric for issues')
        
        #Display the fvNWIssues dn, configQual, descr and configSt
        issues = ''
        for fvNWIssue in fvNWIssues:
            dnFormatted = richWrapper.highlight(str(fvNWIssue.dn))
            issues = issues+dnFormatted+'\n'
            issues = issues+f'\tconfigQual: {escape(fvNWIssue.configQual)}'+'\n'
            issues = issues+f'\tdescr: {escape(fvNWIssue.descr)}'+'\n'
            issues = issues+f'\tconfigSt: {escape(fvNWIssue.configSt)}'+'\n'
        richWrapper.console.print(Panel.fit(issues))
            
            
            
        
        
        
        


    
    

