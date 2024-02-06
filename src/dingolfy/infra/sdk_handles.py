import os
import time
import os
import random
import requests
from requests.exceptions import ConnectionError, RequestException
from rich.panel import Panel
from rich.markup import escape
from . import richWrapper
import ipaddress



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

def getSystemMemory():
    import psutil

    # Get the total system memory in bytes
    total_memory = psutil.virtual_memory().total

    # Convert to a more human-readable format (e.g., megabytes)
    total_memory_mb = total_memory / (1024 * 1024)
    return total_memory_mb
    #print(f"Total system memory: {total_memory_mb:.2f} MB")


import sys
import threading
import urllib3
urllib3.disable_warnings()
try:
    gitdir = os.environ['gitdir']
except KeyError as e:
    msg = f'''gitdir details should be updated in environment variables:
    {e}
    Please update ~/.bashrc or ~/.profile with the folllowing
    export gitdir=<git staging and api directory>
    '''
    raise Exception(msg)

sys.path.append(os.path.abspath(gitdir+'/staging/mgmt/ifc/insieme.app.ishell/mgmt/opt/controller/ishell'))
sys.path.append(os.path.abspath(gitdir+'/staging/mgmt/ifc/insieme.app.ishell/mgmt/opt/controller/ishell/ct64'))
sys.path.append(os.path.abspath(gitdir+'/api'))



from cobra.mit.request import DnQuery
from cobra.mit.request import ClassQuery
from cobra.mit.session import LoginSession
from cobra.mit.access import MoDirectory
from cobra.model.fabric import RsOosPath
from cobra.mit.request import ConfigRequest
# from cobramo import DirectRestAccess, CobraMoDirectory
from cobra.mit.request import TroubleshootingQuery



from cobra.internal.codec.jsoncodec import toJSONStr, fromJSONStr, parseJSONError
from cobra.internal.codec.xmlcodec import toXMLStr, fromXMLStr, parseXMLError
from cobra.mit.access import MoDirectory
from cobra.mit.request import ConfigRequest, DnQuery, ClassQuery
from cobra.mit.session import LoginSession, AbstractSession
from cobra.mit.request import QueryError, CommitError, RestError

systemMemory = getSystemMemory()

class RestartableGenerator:
    '''
    This class is used to restart a generator. 
    Use case: If the consuming function uses the generator as a persistent list for reuse
    Supports indexing to get the nth element of the generator
    '''
    def __init__(self, generator_function, *args, **kwargs):
        self.generator_function = generator_function
        self.args = args
        self.kwargs = kwargs

    def __iter__(self):
        return self.generator_function(*self.args, **self.kwargs)

    def __getitem__(self, index):
        if not isinstance(index, int):
            raise TypeError("Index must be an integer")
        if index < 0:
            raise IndexError("Index must be non-negative")

        generator = self.generator_function(*self.args, **self.kwargs)

        try:
            for _ in range(index):
                next(generator)
            return next(generator)
        except StopIteration:
            raise IndexError("Index out of range")

class ThreadSafeSingleton(type):
    _instances = {}
    _singleton_lock = threading.Lock()

    def __call__(cls, *args, **kwargs):
        # double-checked locking pattern (https://en.wikipedia.org/wiki/Double-checked_locking)
        if cls not in cls._instances:
            with cls._singleton_lock:
                if cls not in cls._instances:
                    cls._instances[cls] = super(ThreadSafeSingleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


class IterClass(type):

    # METACLASS FOR ITERATING CLASS INSTANCES
    def __iter__(cls):
        return iter(cls._instances)

class switchMoDir(object, metaclass=IterClass):
    _instances = []
    def __init__(self,ip,name):
        self.ip = ip
        self.name = name
        self.username = apicUname
        self.password = apicPwd
        self._switch_handle = self.switch_handle
        self.version = self.switch_handle.lookupByClass('topSystem')[0].version 
        switchMoDir._instances.append(self)

    @property
    def switch_handle(self):
        # Run the code below for 3 times to get a valid handle
        retry = 2
        for retry in range(retry):
            try:
                return ReturnMoDir(apicHostname=self.ip,username=self.username,password=self.password)
            except ConnectionError as e:
                msg =  f'Connection failed on host: {self.ip} with \nConnection error: {e}. \n{retry+1} try out of {retry} retries'
                print (msg)
                time.sleep(5)
                
            except Exception as e:
                msg = f'Got an Unhandled Exception:{e}'
                raise Exception(msg)
        else:
            raise Exception(f'Connection failed on host: {self.ip} after {retry} tries')
        
    def printMo(self, mo):
        richWrapper.console.print(str(self.name) + ': MO Details: for class: ' + mo.meta.moClassName + '\n', style=richWrapper.StyleGuide.command_style)
        props = sorted([(pn, str(getattr(mo, pn))) for pn in mo.meta.props.names])
        moPrint = ''
        moPrint += mo.meta.moClassName + '\n'
        #print (mo.meta.moClassName)
        for each in props:
            moPrint += escape(each[0]) + ' : ' + escape(each[1]) + '\n'
        richWrapper.console.print(Panel.fit(moPrint))
        richWrapper.console.print('\n')

    # Gets called when the item is not found via __getattribute__
    def __getattr__(self, attr):
        #print("Calling __getattr__: "+attr)
        #import pdb;pdb.set_trace()
        retries = 3
        if hasattr(self._switch_handle, attr):
            def wrapper(*args, **kw):
                for retry in range(retries):
                    try:
                        return getattr(self._switch_handle, attr)(*args, **kw)
                    except ConnectionError as e:
                        msg =  f'{attr} failed on host: {self.ip} with \nConnection error: {e}. \n{retry+1} try out of {retries} retries'
                        print (msg)
                        time.sleep(5)
                        # Ressume connectivity to SDK with a different ip if there are a cluster of APICs
                        
                    except QueryError as e:
                        if 'Token timeout' in str(e):
                            msg = f'{attr} failed on host: {self.ip} with QueryError: {e} for attr:{attr}, with args:{args} and kw:{kw}'
                            print (msg)
                            
                            self._switch_handle = self.switch_handle
                        
                        else:
                            msg = f'{attr} failed on host: {self.ip} with Unhandled Exception in QueryError: {e} for attr:{attr}, with args:{args} and kw:{kw}'
                            print (msg)
                            
                    except Exception as e:
                        msg = f'Got an Unhandled Exception:{e} for attr:{attr}, with args:{args} and kw:{kw}'
                        if 'result dataset is too big' in str(e):
                            print (msg)
                            raise Exception(f'Please use a filter to reduce the result set for {attr}')
                        print (msg)
                raise Exception(f'{attr} failed on host: {self.ip} after {retries} tries')
            return wrapper
        raise AttributeError(f'attr:{attr} not found for apic: {self.ip}')
 





class apicMoDir(object, metaclass=ThreadSafeSingleton):
    def __init__(self):
        self.ip = random.choice(apicIp)
        self.username = apicUname
        self.password = apicPwd
        self._ifc_handle = self.ifc_handle
        self.version = self.ifc_handle.lookupByClass('firmwareCtrlrRunning')[0].version 
    
    @property
    def ifc_handle(self):
        # Run the code below for 3 times to get a valid handle
        for retry in range(3):
            try:
                return ReturnMoDir(apicHostname=self.ip,username=self.username,password=self.password)
            except ConnectionError as e:
                msg =  f'Connection failed on host: {self.ip} with \nConnection error: {e}. \n{retry+1} try out of 3 retries'
                print (msg)
                time.sleep(5)
                # Ressume connectivity to SDK with a different ip if there are a cluster of APICs
                if len(apicIp) != 1:
                    self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                else:
                    time.sleep(60)
                
            except Exception as e:
                msg = f'Got an Unhandled Exception:{e}'
                raise Exception(msg)
        
    def printMo(self, mo):
        richWrapper.console.print('Apic-' +  str(self.ip) + ': MO Details: for class: ' + mo.meta.moClassName + '\n', style=richWrapper.StyleGuide.command_style)
        props = sorted([(pn, str(getattr(mo, pn))) for pn in mo.meta.props.names])
        moPrint = ''
        moPrint += mo.meta.moClassName + '\n'
        #print (mo.meta.moClassName)
        for each in props:
            moPrint += escape(each[0]) + ' : ' + escape(each[1]) + '\n'
        richWrapper.console.print(Panel.fit(moPrint))
        richWrapper.console.print('\n')
    def checkObjectCount(self, query):
        # query = ClassQuery(klass)
        # query.subtree = 'no'
        import copy
        countQuery = copy.deepcopy(query)
        countQuery.subtreeInclude='count'
        # query.queryTarget = 'self'
        retries = 3
        for retry in range(retries):
            try:
                count = self._ifc_handle.query(countQuery)[0].count
                return count
            except ConnectionError as e:
                msg =  f'count query failed on host: {self.ip} with \nConnection error: {e}. \n{retry+1} try out of {retries} retries'
                print (msg)
                time.sleep(5)
                # Ressume connectivity to SDK with a different ip if there are a cluster of APICs
                if len(apicIp) != 1:
                    self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                
                self._ifc_handle = self.ifc_handle
            except QueryError as e:
                if 'Token timeout' in str(e):
                    msg = f'count query failed on host: {self.ip} with QueryError: {e}'
                    print (msg)
                    # Resume connectivity to SDK with a different ip if there are a cluster of APICs
                    # if len(apicIp) != 1:
                    #     self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                    
                    self._ifc_handle = self.ifc_handle
                else:
                    msg = f'count query failed on host: {self.ip} with Unhandled Exception in QueryError: {e}'
                    print (msg)
                    break
            except Exception as e:
                msg = f'Got an Unhandled Exception:{e}'
                print (msg)
                break
        raise Exception(f'count query failed on host: {self.ip} after {retries} tries')
        
    
    def batchGenerator(self,*args, **kwargs):
        
        
        def calculate_batch_size(moCount, systemMemoryInMB):
            # Calculate the memory required for one Mo in MB
            mo_memory_MB = 0.5  # 0.5 MB per Mo

            # Calculate the available memory in MB as 70% of systemMemoryInMB
            available_memory_MB = 0.7 * systemMemoryInMB

            # Calculate the maximum number of Mos that can fit in the available memory
            max_mo_count = available_memory_MB / mo_memory_MB

            # The batch size should be the smaller of moCount and max_mo_count to not exceed available memory
            batch_size = min(moCount, max_mo_count)

            return int(batch_size)  # Convert to integer



        def getParentDnQuery(parentDn,classNames):
            dnQuery = DnQuery(parentDn)
            dnQuery.classFilter = classNames
            dnQuery.queryTarget = 'subtree'
            return dnQuery
        
        #args are set as such. 1st element if present is the class name. 2nd element if present is the parentDn, everything else will be named and thereby will be part of the kwargs
        #It is possible that the parentDn is not present. In that case the first element will be the class name and the rest will be kwargs
        #It is also possible that there is nothing in the args and everything is in kwargs
        #If there is a parentDn, then we need to use a DnQuery instead of a ClassQuery

        if len(args) == 2:
            query = getParentDnQuery(args[1],args[0])
            klass = args[0]
            for key in kwargs:
                setattr(query, key, kwargs[key])
        elif len(args) == 1:
            klass = args[0]
            if kwargs.get('parentDn'):
                query = getParentDnQuery(kwargs.pop('parentDn'),args[0])
                for key in kwargs:
                    setattr(query, key, kwargs[key])
            else:
                query = ClassQuery(args[0])
                for key in kwargs:
                    setattr(query, key, kwargs[key])

        elif len(args) == 0:
            try:
                klass = kwargs.pop('classNames')
            except KeyError:
                raise Exception(f'Please provide a class name in the kwargs')
            if kwargs.get('parentDn'):
                klass = kwargs.get('classNames')
                query = getParentDnQuery(kwargs.pop('parentDn'),klass)
                for key in kwargs:
                    setattr(query, key, kwargs[key])
                
            else:
                query = ClassQuery(klass)
                for key in kwargs:
                    setattr(query, key, kwargs[key])
        elif len(args) > 2:
            raise Exception(f'Args are not in right format. Got more than 2 args: {args}')
        else:
            raise Exception(f'Please provide a class name in the args or kwargs')
        
        count = int(self.checkObjectCount(query))
        batchSize = 50000
        # systemMemoryinmegabytes = systemMemory
        # batchSize = calculate_batch_size(count, systemMemoryinmegabytes)
        retries = 3
        for retry in range(retries):
            try:
                #yield from self._ifc_handle.query(query)
                if count > batchSize:
                    #print(f'Object count for {klass} with args: {args} and kw:{kwargs} is {count}. Using batch generator')
                    for page in range(0, count, batchSize):
                        query.page = page
                        query.pageSize = batchSize
                        yield from self._ifc_handle.query(query)
                    break
                else:
                    yield from self._ifc_handle.query(query)
                    break
                    
            except ConnectionError as e:
                msg =  f'{klass} failed on host: {self.ip} with \nConnection error: {e}. \n{retry+1} try out of {retries} retries'
                print (msg)
                time.sleep(5)
                # Ressume connectivity to SDK with a different ip if there are a cluster of APICs
                if len(apicIp) != 1:
                    self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                
                self._ifc_handle = self.ifc_handle
            except QueryError as e:
                if 'Token timeout' in str(e):
                    msg = f'lookupByClass failed on host: {self.ip} with QueryError: {e} for attr:lookupByClass, with args:{args} and kw:{kwargs}'
                    print (msg)
                    # Resume connectivity to SDK with a different ip if there are a cluster of APICs
                    # if len(apicIp) != 1:
                    #     self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                    
                    self._ifc_handle = self.ifc_handle
                else:
                    msg = f'lookupByClass failed on host: {self.ip} with Unhandled Exception in QueryError: {e} for attr:lookupByClass, with args:{args} and kw:{kwargs}'
                    print (msg)
                    raise Exception(f'lookupByClass failed on host: {self.ip}')
                                        
            except Exception as e:
                if 'result dataset is too big' in str(e):
                    msg = f'Dataset from query is too big with args{args} and kw{kwargs}. Trying to reduce the batch size'
                    print (msg)
                    # Here we can force the batchset to be
                    # We would get here only if the memory on the system is so lareg that the 30% of system memory which is the batch size is still too large for the query
                    # In this case re run the query with a batch size of 20000. Warning this may take time. So warn the users of the same
                    
                    for page in range(0, count, batchSize):
                        query.page = page
                        query.pageSize = batchSize
                        yield from self._ifc_handle.query(query)
                    break
                            
                else:
                    msg = f'Got an Unhandled Exception:{e} for attr:lookupByClass, with args:{args} and kw:{kwargs}'
                    print (msg)
                    raise Exception(f'lookupByClass failed on host: {self.ip} after {retries} tries')
        else:
            raise Exception(f'lookupByClass failed on host: {self.ip}')

    # Gets called when the item is not found via __getattribute__
    def __getattr__(self, attr):
        #print("Calling __getattr__: "+attr)
        #import pdb;pdb.set_trace()
        retries = 3
        if hasattr(self._ifc_handle, attr):
            def wrapper(*args, **kw):
                if attr == 'lookupByClass':
                    #Return an iterator with the results for lookupByClass. This is primarily for memory optimization
                    return RestartableGenerator(self.batchGenerator, *args, **kw)
                for retry in range(retries):
                    #print('IFC MO Object called with %r and %r' % (args, kw))
                    try:
                        return getattr(self._ifc_handle, attr)(*args, **kw)
                    except ConnectionError as e:
                        msg =  f'{attr} failed on host: {self.ip} with \nConnection error: {e}. \n{retry+1} try out of {retries} retries'
                        print (msg)
                        time.sleep(5)
                        # Ressume connectivity to SDK with a different ip if there are a cluster of APICs
                        if len(apicIp) != 1:
                            self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                        
                        self._ifc_handle = self.ifc_handle
                    except QueryError as e:
                        if 'Token timeout' in str(e):
                            msg = f'{attr} failed on host: {self.ip} with QueryError: {e} for attr:{attr}, with args:{args} and kw:{kw}'
                            print (msg)
                            # Resume connectivity to SDK with a different ip if there are a cluster of APICs
                            # if len(apicIp) != 1:
                            #     self.ip = random.choice([ip for ip in apicIp if ip != self.ip])
                            
                            self._ifc_handle = self.ifc_handle
                        else:
                            msg = f'{attr} failed on host: {self.ip} with Unhandled Exception in QueryError: {e} for attr:{attr}, with args:{args} and kw:{kw}'
                            print (msg)
                            
                    except Exception as e:
                        msg = f'Got an Unhandled Exception:{e} for attr:{attr}, with args:{args} and kw:{kw}'
                        print (msg)
                raise Exception(f'{attr} failed on host: {self.ip} after {retries} tries')
            return wrapper
        raise AttributeError(f'attr:{attr} not found for apic: {self.ip}')
    
    

def getIfcHndl():
    MoDir = apicMoDir()
    return MoDir#._ifc_handle


def getswitchSdkHandles(role: str='leaf'):
    handles = []
    for node in getIfcHndl().lookupByClass('top.System'):
        if node.role == role:
            for handle in switchMoDir:
                if handle.name == node.name:
                    handles.append(handle)
                    break
            else:
                try:
                    try:
                        validate =ipaddress.ip_address(node.oobMgmtAddr)
                        hostname = node.oobMgmtAddr
                    except ValueError:
                        if node.oobMgmtAddr6 != '::':
                            hostname = node.oobMgmtAddr6
                        else:
                            raise Exception(f'{node.name} does not have oob v4: {node.oobMgmtAddr} or v6:{node.oobMgmtAddr6} address configured')
                    handles.append(switchMoDir(ip=hostname,name=node.name))
                    msg = f'Got switch sdk handle for {node.name}'
                    #print(msg)
                except Exception as e:
                    msg = f'switch{node.name} could not be accessed and will not be used to collect Logs:\n\t{e}'
                    print(msg)

def getSwitchSdkHandlebyName(leafName: str):
    
    for switchHandle in switchMoDir:
        if switchHandle.name == leafName:
            return switchHandle
    else:
        try:
            for node in getIfcHndl().lookupByClass('top.System'):
                if node.name == leafName:
                    try:
                        validate =ipaddress.ip_address(node.oobMgmtAddr)
                        hostname = node.oobMgmtAddr
                    except ValueError:
                        if node.oobMgmtAddr6 != '::':
                            hostname = node.oobMgmtAddr6
                        else:
                            raise Exception(f'{node.name} does not have oob v4: {node.oobMgmtAddr} or v6:{node.oobMgmtAddr6} address configured')
                    return switchMoDir(ip=hostname,name=node.name)
            else:
                raise Exception(f'Could not find leaf:{leafName} in topSystem')
        except Exception as e:
            raise Exception(f'Could not find switch handle for {leafName}: Exception: {e}')
    
def ReturnMoDir(apicHostname='ifav230-apic1.insieme.local', username='admin', password='ins3965!', capic=False):
    if capic:
        os.environ['http_proxy'] = "proxy-wsa.esl.cisco.com:80"
        os.environ['https_proxy'] = "proxy-wsa.esl.cisco.com:80"
    apicUrl = 'https://' + apicHostname
    loginSession = LoginSession(apicUrl, username, password, secure=False, timeout=100)
    ifc_handle = MoDirectory(loginSession)
    ifc_handle.login()
    msg = f'Got IFC Handle for {apicHostname}'
    #print(msg)
    return ifc_handle


def printMo(mo):
    props = sorted([(pn, str(getattr(mo, pn))) for pn in mo.meta.props.names])
    moPrint = ''
    moPrint += mo.meta.moClassName + '\n'
    #print (mo.meta.moClassName)
    for each in props:
        moPrint += escape(each[0]) + ' : ' + escape(each[1]) + '\n'
    richWrapper.console.print(Panel.fit(moPrint))
    richWrapper.console.print('\n')


    

