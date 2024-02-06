from .globals import handles
from typing import Optional
import typer
import ipaddress
#import ipaddr
import re
from typing import Optional
import pickle
import datetime
#import time
from threading import Thread
#import gc
#from pympler import asizeof
from . import richWrapper
from rich.panel import Panel
from rich.markup import escape
from typing import Union, List
from rich.table import Table
from rich.markup import escape
#from rich.pretty import pprint
from rich.progress import Progress
from enum import Enum


can_be_int = lambda s: s.isdigit() if s.lstrip('-').isdigit() else s[0].isdigit() and s[1:].isdigit()

class ThreadWithReturnValue(Thread):
    
    def __init__(self, group=None, target=None, name=None,
                 args=(), kwargs={}, Verbose=None):
        Thread.__init__(self, group, target, name, args, kwargs)
        self._return = None

    def run(self):
        if self._target is not None:
            self._return = self._target(*self._args,
                                                **self._kwargs)
    def join(self, *args):
        Thread.join(self, *args)
        return self._return

def sendCmd(cmd: Union[List, str], leafName: Union[List, str] = 'all', interactivecommand: Optional[str] = None,
            noexitcode: Optional[bool] = False,
            timeout: Optional[int] = 180,
            To_Screen: Optional[bool]=True,
            progress=None, task=None,
            spineName: Union[List, str] = 'all',
            spine: Optional[bool] = False,
            title: Optional[str] = None):
    def checkHandle(handle,name):
        if isinstance(name,list):
            if handle.name in name: 
                return True
            else:
                return False
        if name == 'all': 
            return True
        if name == handle.name:
            return True
    if title:
        title = richWrapper.highlight(title)
        richWrapper.console.print(title)
    if spine:
        hdls = handles.spine_ssh_handles
        switchName = spineName
    else:
        hdls = handles.leaf_ssh_handles
        switchName = leafName
    richWrapper.console.print('\n')
    for handle in hdls:
        if checkHandle(handle,switchName):
            try:
                if isinstance(cmd,list):
                    aggregate_results = ''
                    for command in cmd:
                        result = handle.send_command(cmd=command,interactivecommand=interactivecommand,timeout=timeout,progress=progress,task=task)
                        cmd_msg = richWrapper.style_command(devicename=handle.name,text=command)
                        result_msg = f'{cmd_msg}\n{escape(result)}'
                        aggregate_results += result_msg
                    richWrapper.console.print(Panel.fit(aggregate_results))
                    richWrapper.console.print('\n')
                else:
                    result = handle.send_command(cmd=cmd,interactivecommand=interactivecommand,timeout=timeout,progress=progress,task=task)
                    cmd_msg = richWrapper.style_command(devicename=handle.name,text=cmd)
                    result_msg = f'{cmd_msg}\n{escape(result)}'
                    richWrapper.console.print(Panel.fit(result_msg))
                    richWrapper.console.print('\n')
                
                #Consumer may want to do further operations with the result
                if switchName != 'all' and not isinstance(cmd,list) and not isinstance(switchName,list): return result 
            except Exception as e:
                raise Exception(f'send cmd:{cmd} to leaf: {handle.name} failed Exception:{e}')
        else:
            continue

def sendCmdApic(cmd: Union[List, str], allApics: Optional[bool] = False, interactivecommand: Optional[str] = None,
                noexitcode: Optional[bool] = False,
                timeout: Optional[int] = 180,
                To_Screen: Optional[bool]=True,
                progress=None, task=None,
                hostname: Optional[str] = None):
    
    def sendCommand(handle,cmd,interactivecommand,noexitcode,timeout,To_Screen,progress=None,task=None):
        try:
            if isinstance(cmd,list):
                aggregate_results = ''
                for command in cmd:
                    result = handle.send_command(cmd=command,interactivecommand=interactivecommand,timeout=timeout,progress=progress,task=task)
                    cmd_msg = richWrapper.style_command(devicename=handle.name +': ' + handle.hostname ,text=command)
                    result_msg = f'{cmd_msg}\n{escape(result)}\n'
                    aggregate_results += result_msg
                richWrapper.console.print(Panel.fit(aggregate_results))
                richWrapper.console.print('\n')
            else:
                result = handle.send_command(cmd=cmd,interactivecommand=interactivecommand,timeout=timeout,progress=progress,task=task)
                cmd_msg = richWrapper.style_command(devicename=handle.name + ': ' + handle.hostname ,text=cmd)
                result_msg = f'{cmd_msg}\n{escape(result)}'
                richWrapper.console.print(Panel.fit(result_msg))
                richWrapper.console.print('\n')
            #Consumer may want to do further operations with the result
            if not isinstance(cmd,list): return result 
        except Exception as e:
            raise Exception(f'send cmd to apic:{cmd} failed Exception:{e}')
    if allApics:
        for handle in handles.apic_ssh_handles:
            result = sendCommand(handle,cmd,interactivecommand,noexitcode,timeout,To_Screen,progress=progress,task=task)
    elif hostname:
        for handle in handles.apic_ssh_handles:
            if handle.hostname == hostname:
                result = sendCommand(handle,cmd,interactivecommand,noexitcode,timeout,To_Screen,progress=progress,task=task)
                return result
    else:
        result = sendCommand(handles.apic_ssh_handle,cmd,interactivecommand,noexitcode,timeout,To_Screen,progress=progress,task=task)
        return result
    
def ipValidation(value:str):
    if value in [None,""]: return value
    try:
        if ipaddress.ip_address(str(value)).version not in [4,6]:
            raise typer.BadParameter(f'Please provide correct ip/ipv6 format:{value}')
    except ValueError as e:
        raise typer.BadParameter(f'Please provide correct ip/ipv6 format and not:{value} Exception:{e}')
    return value


def versionValidation(value:str):
    if value in [None,""]: return value
    if value not in ['4','6']:
        raise typer.BadParameter(f'Version can only be 4/6 and not:{value}')
    return value



def vrfTable(messagePrefix=''):
    '''
    return a list of vrfs in the format fvTenant.name:fvCtx.name 
    '''
    tenantList = []
    for fvTenant in handles.ifc_sdk_handle.lookupByClass('fvTenant'):
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

    tenant = typer.prompt(f"Default",default="all")
    if tenant=='all': return tenant
    if tenant not in tenantList:
        tenant = typer.prompt(f'Invalid Selection:Please select a valid tenant from the list above')
    if tenant not in tenantList:
        richWrapper.console.error(f'Invalid Selection: Aborting')
        typer.Abort()
        return 'all'
    
    tenantDn = f'uni/tn-{tenant}'
    vrfList = []
    for fvCtx in handles.ifc_sdk_handle.lookupByClass('fvCtx',parentDn=tenantDn):
        vrfList.append(f'{tenant}:{fvCtx.name}')
    #msgPrefix = richWrapper.highlight(f'{messagePrefix}Please select the vrf from the list below')
    msgPrefix = f'{messagePrefix}Please select the vrf from the list below'
    table = Table(title=msgPrefix, style=richWrapper.StyleGuide.title_style,title_justify="left")
    #Iterate trough epg list and add four epgs per row till the end of the list
    for i in range(0, len(vrfList), 4):
        table.add_row(*vrfList[i:i+4])
    table.pad_edge = True
    richWrapper.console.print(table)
    msgPrefix = richWrapper.highlight(f'{messagePrefix}Please select the vrf from the list above')
    richWrapper.console.print(msgPrefix)
    vrf = typer.prompt(f"Default",default='all')
    return vrf

def vrf_callback(value:str):
    vrfList = ['tn1:ctx1', 'tn1:ctx2']
    
    if value not in ['tn1:ctx1', 'tn1:ctx2']:
        raise typer.BadParameter(f"Only {vrfList} is allowed")
    return value


def leaf_callback(value:str):
    pass

def leafTable(messagePrefix=''):
    '''
    return a list of vrfs in the format fvTenant.name:fvCtx.name 
    '''
    leafList = []
    for leaf in handles.ifc_sdk_handle.lookupByClass('fabricNode'):
        if leaf.role=='leaf': leafList.append(leaf.name)
    msgPrefix = f'{messagePrefix}Please select the leaf from the list below'
    table = Table(title=msgPrefix, style=richWrapper.StyleGuide.title_style,title_justify="left")
    for i in range(0, len(leafList), 4):
        table.add_row(*leafList[i:i+4])
    table.pad_edge = True
    richWrapper.console.print(table)
    msgPrefix = richWrapper.highlight(f"{messagePrefix}Please select the leaf from the list above or provide a comma separated list of leaves")
    richWrapper.console.print(msgPrefix)

    leaf = typer.prompt(f"Default",default="all")
    if ',' in leaf:
        leaves = [l.strip() for l in leaf.split(',')]
        for leaf in leaves:
            if leaf not in leafList:
                richWrapper.console.error(f'Invalid Selection: {leaf} Aborting')
                raise typer.Exit()
                
        return leaves

    

    if leaf not in leafList and leaf != 'all':
        richWrapper.console.error(f'Invalid Selection: {leaf}: Aborting')
        raise typer.Exit()
        
    
    return leaf


def leaf_options():
    raise Exception(f'leaf_options is deprecated. Please use leafTable instead')
    fName = '/usr/share/dingolfyData.pkl'
    try:
        pkl_file = open(fName,'rb')
        data = pickle.load(pkl_file)
        pkl_file.close()
        leafList = data['leafList']
        pkl_file.close()
        if not leafList:
            msg = "leafList is empty: Are no VRFs configured?"
            print(msg)
            #raise Exception(f'leafList is missing form file:{fName}')
        prefix = '''Please provide leafName from following list:'''
        leafList = '\n'.join(leaf for leaf in leafList)
        msg = f'''
{prefix}
{leafList}
all
'''     
        
        return msg
    except FileNotFoundError:
        raise Exception(f'pkl file: {fName} missing. Please check if dataWatch process is running in background\nps -aux | grep dataWatch.py ')
    except Exception as e:
        raise Exception(f'Got Exception:{e} when trying to update from pkl file:{fName}')
    


def vrfList():
    fName = '/usr/share/dingolfyData.pkl'
    try:
        pkl_file = open(fName,'rb')
        data = pickle.load(pkl_file)
        vList = data['vrfList']
        pkl_file.close()
        if not vList:
            msg = "vrfList is empty: Are no VRFs configured?"
            print(msg)
            #raise Exception(f'vrfList is missing form file:{fName}')
        
        return vList
    except FileNotFoundError:
        raise Exception(f'pkl file: {fName} missing. Please check if dataWatch process is running in background\nps -aux | grep dataWatch.py ')
    except Exception as e:
        raise Exception(f'Got Exception:{e} when trying to update from pkl file:{fName}')



def vrf_options():
    
    raise Exception(f'vrf_options is deprecated. Please use vrfTable instead')
    vList = '\n'.join(item for item in vrfList())
    
    

    prefix = '''Please provide vrf from following list below:'''

    msg = f'''
{prefix}
{vList}
all
Please provide vrf from following list above:
'''
    return msg


      

def getLeafNamefromLeafId(leafId:str):
    for leaf in handles.ifc_sdk_handle.lookupByClass('fabricNode'):
        if leaf.id == leafId:
            return leaf.name
    typer.Abort(f'Could not find leafName for leafId:{leafId}')
    richWrapper.console.error(f'Could not find leafName for leafId:{leafId}')

def getLeafIdfromLeaName(leafName:str):
    for leaf in handles.ifc_sdk_handle.lookupByClass('fabricNode'):
        if leaf.name == leafName:
            return leaf.id
    typer.Abort(f'Could not find leafId for leafName:{leafName}')
    richWrapper.console.error(f'Could not find leafId for leafName:{leafName}')

def compare_versions(version1, version2):
    v1_parts = re.split(r'[\.\(\)]', version1)
    v2_parts = re.split(r'[\.\(\)]', version2)

    for i in range(len(v1_parts)):
        if v1_parts[i].isdigit() and v2_parts[i].isdigit():
            if int(v1_parts[i]) < int(v2_parts[i]):
                return True
            elif int(v1_parts[i]) > int(v2_parts[i]):
                return False
        elif v1_parts[i] < v2_parts[i]:
            return True
        elif v1_parts[i] > v2_parts[i]:
            return False

    return False






        




       
    

