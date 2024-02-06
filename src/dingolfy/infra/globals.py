import time
import re
from .logger import Logger
from ..__init__ import __version__



'''
define a singleton class to hold global variables
'''
class Singleton(type):
    _instances = {}
    def __call__(cls, *args, **kwargs):
        print ('Singleton class called')
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
            
        return cls._instances[cls]
    

class handles_class(metaclass=Singleton):
    def __init__(self):
        pass
    @property
    def ifc_sdk_handle(self):
        from .sdk_handles import getIfcHndl
        return getIfcHndl()
    @property
    def leaf_ssh_handles(self):
        from .cli_handles import getswitchHandles
        return getswitchHandles(role='leaf')
    @property
    def spine_ssh_handles(self):
        from .cli_handles import getswitchHandles
        return getswitchHandles(role='spine')
    @property
    def apic_ssh_handle(self):
        from .cli_handles import getapicHandle
        return getapicHandle()
    @property
    def apic_ssh_handles(self):
        from .cli_handles import getAllapicHandles
        return getAllapicHandles()
    @property
    def leaf_sdk_handles(self):
        from .sdk_handles import getswitchSdkHandles
        return getswitchSdkHandles(role='leaf')
    @property
    def spine_sdk_handles(self):
        from .sdk_handles import getswitchSdkHandles
        return getswitchSdkHandles(role='spine')
    @property
    def switchSdkHdlbyName(self):
        from .sdk_handles import getSwitchSdkHandlebyName
        return getSwitchSdkHandlebyName

handles = handles_class()

# class handles:
#     from .sdk_handles import getIfcHndl
#     from .cli_handles import getapicHandle
#     from .cli_handles import getswitchHandles
#     from .cli_handles import getAllapicHandles
#     from .sdk_handles import getswitchSdkHandles
#     from .sdk_handles import getSwitchSdkHandlebyName
#     ifc_sdk_handle = getIfcHndl()
#     leaf_ssh_handles = getswitchHandles(role='leaf')
#     spine_ssh_handles = getswitchHandles(role='spine')
#     apic_ssh_handle = getapicHandle()
#     apic_ssh_handles = getAllapicHandles()
#     leaf_sdk_handles = getswitchSdkHandles(role='leaf')
#     spine_sdk_handles = getswitchSdkHandles(role='spine')
#     switchSdkHdlbyName = getSwitchSdkHandlebyName
    




def getOutputLogFile():
    Loop_String = ''
    Base_Date_String = str(re.sub('\s|\:', '_', time.asctime()))
    dateString = '_' + re.sub(':', '_', Base_Date_String)
    Base_Log_Path = '/tmp/'
    
    Logfile_Filename = 'Dingolfy_cli_output' + dateString + '.txt'
    Logfile_Filename = re.sub(':', '_', Logfile_Filename)
    Logfile_Filepath = Base_Log_Path + Logfile_Filename

    with open(Logfile_Filepath, 'w') as f:
        print (f'Dingolfy Cli output log stored at: {Logfile_Filepath}\n\n')
    return Logfile_Filepath

def getLogger():
    
    Loop_String = ''
    Base_Date_String = str(re.sub('\s|\:', '_', time.asctime()))
    dateString = '_' + re.sub(':', '_', Base_Date_String)
    Base_Log_Path = '/tmp/'
    
    Logfile_Filename = 'dingolfy_automation_log' + dateString + '.txt'
    Logfile_Filename = re.sub(':', '_', Logfile_Filename)
    Logfile_Filepath = Base_Log_Path + Logfile_Filename
    
    Harness_Logfile_Filename = 'dingolfy_harness_bld' + dateString + '.txt'
    Harness_Logfile_Filepath = Base_Log_Path + Harness_Logfile_Filename
    
    with open(Logfile_Filepath, 'w') as f:
        print (f'Dingolfy Automation Log: {Logfile_Filepath}')
    
    with open(Harness_Logfile_Filepath, 'w') as f:
        msg = f'Dingolfy Harness Automation Log: {Harness_Logfile_Filepath}'
    
    File_List = [
        {
            'Type': 'User_Logfile',
            'Name': 'user',
            'Filename': Logfile_Filepath,
            'Default': True,
        },
    
        {
            'Type': 'Harness_Logfile',
            'Name': 'harness',
            'Filename': Harness_Logfile_Filepath,
        },
    
        {
            'Type': 'User_Logfile',
            'Name': 'root',
            'Filename': Logfile_Filepath,
        },
    
    ]
    
    logger = Logger(File_List=File_List)
    return logger

class dingolfyGlobal:
    logger = getLogger()
    cliOutput = getOutputLogFile()
    coar_key = 'ac344f5e-f2c3-4518-b935-a076a251a689'
    coar_secret = 'vrkASjjB3kHG4eOURCWaHNj3w4hFjxD9'
    version=__version__
    FilesToUpload = []
    cdetsUploaded = False
    
    

    
class LoadedObjects:
    '''
    Use this to load classes to optimize memory usage and reduce queries to the apic   
    '''
    pass 
    


    