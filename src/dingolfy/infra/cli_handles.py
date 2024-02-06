import os
import ipaddress
from .sshConn import paramikoSSHClient as ConnectHandler
import random
import socket

try:
    apicIp = os.environ['apicIp'].split(',')
    apicPwd = os.environ['apicPassword']
    apicUname = os.environ['apicUsername']
except KeyError as e:
    msg = f'''apic details should be updated in environment variables:
    {e}
    Please update ~/.bashrc or ~/.profile with the folllowing
    export apicIp=<apic hostname> or export apicIp=<apic hostname>,<apic hostname>,<apic hostname>
    export apicUsername='apic username'
    export apicPassword='apic password'
    
    '''
    raise Exception(msg)
from typing import Optional

from scrapli import Scrapli



class IterClass(type):

    # METACLASS FOR ITERATING CLASS INSTANCES
    def __iter__(cls):
        return iter(cls._instances)


class sshHandles(object, metaclass=IterClass):
    '''
    https://github.com/carlmontanari/scrapli/blob/68f144b6b32e44792785bb95b26981959845616f/scrapli/driver/network/sync_driver.py
    '''
    _instances = []
    def __init__(self,hostname: str,username: str,password:str,driver: Optional[str] = 'NXOSDriver')->None:
        self.hostname = hostname
        self.username = username
        self.password = password
        self.driver = driver
        self._sshHandle = None
        sshHandles._instances.append(self)


        
    
    @property
    def loginCred(self):
        return {  
                "host": self.hostname,
                "username": self.username,
                "password": self.password,
                }
    
    
    

    @property
    def sshHandle(self):
        if self._sshHandle and self._sshHandle.is_alive():return self._sshHandle
        
        try:
            self._sshHandle = ConnectHandler(**self.loginCred)
            #print(net_connect.find_prompt())
        except Exception as e:
            raise Exception(f'Cannot connect to host:{self.hostname}, with Exception:{e}')

        return self._sshHandle


    
    
    def disconnect(self):
        if self._sshHandle:
            self._sshHandle.disconnect()
            self._sshHandle = None
        return
    
    #self, cmd, interactivecommand=None, noexitcode=False, timeout=60
    def send_command(self,cmd: str, interactivecommand: Optional[str] = None, 
                     noexitcode: Optional[bool] = False,
                     timeout: Optional[int]=60,
                     progress: Optional[bool]=None,
                     task: Optional[bool]=None)->str:
        '''
        Sends a command to the host and returns the output
        :param cmd: command to be sent to the host
        :param interactivecommand: If the command requires a secondary input, add the input here. 
            For example, if the command is "confirm y/n:", the interactivecommand will be "y"
        :param noexitcode: if True, does not check the exit code of the command and will return None
        :return: output of the command
        '''
        retryMax = 3
        for retry in range(1,retryMax+1):
            try:
                result = self.sshHandle.send_command(cmd, interactivecommand=interactivecommand,noexitcode=noexitcode,timeout=timeout,progress=progress,task=task)
                return result
            except Exception as e:
                msg = f'Could not send command {cmd} to host {self.hostname} with exception:\n\t{e}, sendCommand Retry:{retry}'
                print (msg)
                #raise Exception(f'Could not send command {cmd} with exception:\n\t{e}')
        msg = f'Could not send command {cmd} to host {self.hostname}, after {retryMax} retries\n'
        print(msg)
        result = ''
        return result

    def scp_remote_to_local(self,remote_path: str, local_path: Optional[str] = '/root/', local_filename: Optional[str] = None)->None:
        try:
            self.sshHandle.scp_remote_to_local(remote_path=remote_path, local_path=local_path, local_filename=local_filename)
        except Exception as e:
            raise Exception(f'Could not scp file {remote_path} to {local_path} with exception:\n\t{e}')
        

    
    
class apic_sshHandle(sshHandles):
    def __init__(self,hostname: str,username: str,password:str,driver: Optional[str] = None)->None:
        self.name = 'apic'
        super(apic_sshHandle, self).__init__(hostname=hostname,username=username,password=password,driver=driver)
        
    


class switch_sshHandle(sshHandles):
    def __init__(self,nodeMo,username: str,password:str, driver: Optional[str] = 'NXOSDriver')->None:
        self.name = nodeMo.name
        self.role = nodeMo.role
        self.id = nodeMo.id
        try:
            validate =ipaddress.ip_address(nodeMo.oobMgmtAddr)
            hostname = nodeMo.oobMgmtAddr
        except ValueError:
            if nodeMo.oobMgmtAddr6 != '::':
                hostname = nodeMo.oobMgmtAddr6
            else:
                raise Exception(f'{nodeMo.name} does not have oob v4: {nodeMo.oobMgmtAddr} or v6:{nodeMo.oobMgmtAddr6} address configured')
        super(switch_sshHandle, self).__init__(hostname=hostname,username=username,password=password,driver=driver)
        
        





def getAllapicHandles():
    handles = []
    for ip in apicIp:
        handles.append(apic_sshHandle(hostname=ip,username=apicUname,password=apicPwd))
    return handles
def getapicHandle(ip=None):
    def is_host_alive(host, port, timeout=1):
        try:
            socket.setdefaulttimeout(timeout)
            socket.create_connection((host, port))
            return True
        except (socket.timeout, ConnectionRefusedError):
            return False
    if not ip:
        for iP in apicIp:
            if is_host_alive(iP,22):
                ip = iP
                break

    for handle in apic_sshHandle:
        if handle.hostname == ip:
            return handle
    return apic_sshHandle(hostname=ip,username=apicUname,password=apicPwd)
    
    
    return apic_sshHandle(hostname=ip,username=apicUname, password=apicPwd)

def getswitchHandles(role: str='leaf'):
    from .sdk_handles import getIfcHndl
    handles = []
    for node in getIfcHndl().lookupByClass('top.System'):
        if node.role == role:
            for handle in switch_sshHandle:
                if handle.name == node.name:
                    handles.append(handle)
                    break
            else:
                try:
                    handles.append(switch_sshHandle(nodeMo=node,username=apicUname,password=apicPwd))
                    msg = f'Got switch cli handle for {node.name}'
                    #print(msg)
                except Exception as e:
                    msg = f'switch{node.name} could not be accessed and will not be used to collect Logs:\n{e}'
                    print(msg)
        
    return handles










