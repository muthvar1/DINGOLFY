from trex_hltapi import TRexHLTAPI
import threading
from ...infra import richWrapper

richWrapper.console.print

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


class Singleton(type):
    _instances = {}

    def __call__(cls, *args, **kwargs):
        if cls not in cls._instances:
            cls._instances[cls] = super(Singleton, cls).__call__(*args, **kwargs)
        return cls._instances[cls]


def singleton(cls):
    instances = {}

    def getinstance(*args, **kwargs):
        if cls not in instances:
            instances[cls] = cls(*args, **kwargs)
        return instances[cls]

    return getinstance


class TrexSession(object):
    '''
    Trex LIbraries that wrap around trex apis
    
    Trex Connect **args
    device: IP or hostname of target TRex machine
    port_list: Specified ports will be acquired by TRex on connection
    username: Username to acquire TRex ports (no specifix username required, 
                        this will only be shown in port info for other users, so others could know who owns the port right now
    reset: If True it resets captures, active traffic and port configurations
    break_locks: When acquiring specified ports and it’s acquired by someone else, 
                        if True force acquires specified ports on connect, othewise raise error
    verbose: Verbosity level 'none' | 'critical' | 'error' | 'info' | 'debug'
    raise_errors: If True on error or failre HLTAPI will raise error, otherwise result of method call will have error message
    async_port: TRex ZMQ async queue port. Useful if you have several TRex instances on single machine or 
                        complext setup and TRex instance reachability
    sync_port: TRex ZMQ sync queue port
    timeout: Timeout for HLTAPI to TRex connection, may be increased if network connection to TRex has delays
    config_file: Path to JSON config (snapshot) of TRex
    '''
  
    
    def __init__(self, **connectkwargs):
        msg = 'Trex LIbraries that wrap around trex apis'
        richWrapper.console.print (msg)
        connectkwargs.setdefault('device', 'localhost')
        connectkwargs.setdefault('username', 'TRexUser')
        connectkwargs.setdefault('port_list', 'all')
        connectkwargs.setdefault('reset', True)
        connectkwargs.setdefault('break_locks', True)
        self.connectkwargs = connectkwargs
       
        trexArgs = ['device',
                  'port_list',
                  'username',
                  'reset',
                  'break_locks',
                  'verbose',
                  'raise_errors',
                  'async_port',
                  'sync_port',
                  'timeout',
                  'config_file'
                  ]
        [exec("raise Exception(f'Unrecognized Trex Arg: {key}')") for key in list(connectkwargs) if key not in trexArgs]
        
        self._handle = TRexHLTAPI()
        self.port_list = self.connectkwargs['port_list']
        self.connect(handle=self._handle)
        if self.port_list == 'all':
            self.port_list = list(self.handle.session_info()['info']['ports'].keys())
        self._activePortList = dict([(i, []) for i in self.port_list])
        
    @property
    def handle(self):
        if not self._handle.is_connected():
            self._handle = TRexHLTAPI()
            self.reconnect(handle=self._handle)
        return self._handle

    
    def connect(self, handle):
        '''
        Description
        This method connects to the TRex, takes ownership of selected ports, and optionally loads a configuration on the TRex or resets the targeted ports to defaults.
        Returns
        Available port IDs.
        '''
        richWrapper.console.print (self.connectkwargs)
        handle.connect(**self.connectkwargs)
    
    @property
    
    def activePortList(self):
        
        return [port for port in self._activePortList if self._activePortList[port]]
    
    
    def reconnect(self, handle):
        richWrapper.console.print(f'Reconnecting and setting reset to False')
        self.connectkwargs['reset'] = False  # Reconnect should not reset the config
        handle.connect(**self.connectkwargs)
    
    
    def load_file(self, config_file, reset=True, port_list='all'):
        '''
        Description:
        This method loads previously saved configuration (snapshot) to TRex.
        '''
        self.handle.load_file(config_file=config_file,  # Path to json config (snapshot)
                              reset=reset,  # If True, then all will be reset before config is uploaded
                              port_handle=port_list)  # Port handles to apply config from file
    
    def save_file(self):
        pass
    
    
    def emulation_subinterface_stats(self, mode='clients', version='ipv4'):
        '''
       Gets info about actually configured IPv4/IPv6 clients on TRex side
       
       https://trex.cisco.com/hltapi/commands.html#emulation-subinterface-stats
        '''
        try:
            stats = self.handle.emulation_subinterface_stats(mode=mode, version=version).stats
            
        except Exception as e:
            raise Exception(f' : {e}')
        return stats

    
    def emulation_subinterface_control(self, **kwargs):
        '''
        Configures IPv4/IPv6 subinterfaces, that capable to reply ARP/NS and ICMP requests, as well as send GARP and unsolicited NA on bringup. 
        Subinterfaces are emulated independently from Routem/IOL/DHCP and can be used simultaneously, 
        however, if IPs used by Routem/IOL/DHCP are overlapping with Subinterfaces, then behaviour is undefined.
        
        return {'handle': '2'}. 
        
        https://trex.cisco.com/hltapi/commands.html#subinterface-api
        
        '''
        try:
            status = self.handle.emulation_subinterface_control(**kwargs)

        except Exception as e:
            raise Exception(f' : {e}')
        
        return status
    
    
    def traffic_config(self, **kwargs):
        '''
        This method configures traffic streams on TRex. It can be used. to load native API TRex profile, or create your own using arguments.
        
        Returns
        ID of created stream or stream group, it can be used then to remove stream, or get stats for the stream.    
        
        https://trex.cisco.com/hltapi/commands.html#traffic-config
        '''
        try:
            status = self.handle.traffic_config(**kwargs)

        except Exception as e:
            raise Exception(f' : {e}')
        if kwargs['mode'] == 'create':
            self._activePortList[kwargs['port_handle']].append(status.stream_id)
        if kwargs['mode'] == 'remove':
            self._activePortList[kwargs['port_handle']].remove(kwargs['stream_id'])
            
        return status
        
   
    def start_capture(self, port):
        try:
            self.handle.packet_config_buffers(
                port_handle=port,
                capture_mode='continuous',
                capture_tx=True
            )
        
            self.handle.packet_control(
                port_handle=port,
                action='start'
            )
        except Exception as e:
            raise Exception(f' : {e}')

    
    def stop_capture(self, port, output_filename):
        try:
            self.handle.packet_control(
                port_handle=port,
                action='stop'
            )
        
            self.handle.packet_stats(
                port_handle=port,
                filename=output_filename,
                format='pcap'
            )
        except Exception as e:
            raise Exception(f' : {e}')
    
    
    def traffic_control(self, **kwargs):
        '''
        Description
        This method starts, stops or resets traffic transmission on TRex.
        
        Returns
        Traffic status, whether it’s stopped or not.
        
        https://trex.cisco.com/hltapi/commands.html#traffic-control
        '''
        if 'port_handle' not in kwargs:
            kwargs['port_handle'] = self.activePortList
            action = kwargs['action']
            msg = f'{action} traffic on ports: {self.activePortList}'
            richWrapper.console.print (msg)
            if not self.activePortList:
                msg = f'Active port list is empty portLIst: {self.activePortList}'
                richWrapper.console.print (msg)
                import pdb; pdb.set_trace()
                msg = 'Will not be sending any traffic'
                richWrapper.console.print (msg)
                return None
        try:
            status = self.handle.traffic_control(**kwargs)
        except Exception as e:
            raise Exception(f' : {e}') 
        return status
    
    
    def traffic_stats(self, **kwargs):
        '''
        Description
        This method queries TRex for traffic stats stats.
        
        Returns
        Aggregated by stream ID or by port ID or both.
        
        https://trex.cisco.com/hltapi/commands.html#traffic-stats
        '''
        if 'port_handle' not in kwargs:
            kwargs['port_handle'] = self.port_list
            msg = f"getting traffic stats on all ports: {kwargs['port_handle']}"
            richWrapper.console.print (msg)
        try:
            status = self.handle.traffic_stats(**kwargs)
        except Exception as e:
            raise Exception(f' : {e}') 
        return status
    
    
    def removeAllStreams(self, port_handle, stream_id=None):
        '''
        Description
        This method removes all streams on a given port_handle and stream_id 
        or all streams across the port if None is provided
        
        Returns
        Status
        
        https://trex.cisco.com/hltapi/commands.html#traffic-config
        '''
        
        if not stream_id: stream_id = 'all'
        try:
            status = self.traffic_config(
                mode='remove',
                port_handle=port_handle,
                stream_id=stream_id
                )
        except Exception as e:
            raise Exception(f' : {e}') 
        return status
    
    
    def emulation_iol_config(self, **kwargs):
        '''
        Description
        This method configures IOL instances to be used in emulation
        
        Returns
        Nothing.
        
        https://trex.cisco.com/hltapi/commands.html#emulation-iol-config
        '''
        try:
            status = self.handle.emulation_iol_config(**kwargs)
        except Exception as e:
            raise Exception(f' : {e}') 
        return status
    
    
    def emulation_iol_topology_config(self, **kwargs):
        '''
        Description
        This method configures connections between previously created IOL instances, or TRex ports. 
        target_id and target_interface_id are used to connection one IOL to another, target_port_handle 
        is used to connect existing IOL to TRex port.
        
        Returns
        Nothing.
        
        https://trex.cisco.com/hltapi/commands.html#emulation-iol-topology-config
        '''
        try:
            status = self.handle.emulation_iol_topology_config(**kwargs)
        except Exception as e:
            raise Exception(f' : {e}') 
        return status
    
    
    def emulation_iol_control(self, **kwargs):
        '''
        Description
        This method controls IOL emulation. Workflow is configure instances and topology, then send_testbed and then start.
        
        Returns
        Nothing.
        
        https://trex.cisco.com/hltapi/commands.html#emulation_iol_control
        '''
        try:
            status = self.handle.emulation_iol_control(**kwargs)
        except Exception as e:
            raise Exception(f' : {e}') 
        return status
    
    
    def iol_telnet_configure(self, iol, cmd, bulkCommit=False):
        if bulkCommit:
            try:
                msg = f'IOL BulkCommit: Will add the required stashed cmd to iol {iol} later'
                iolCommandLIst.addIol(iol, cmd)
                return ''
            except Exception as e:
                raise Exception(f' : {e}') 
        try:
            op = self.handle._hltapi_impl.rpc.iol_telnet_configure(iol, cmd)
        except Exception as e:
            raise Exception(f' : {e}') 
        return op

    
    def iol_bulkCommit(self, startdevice=False):
        try:
            if startdevice:
                self.emulation_iol_control(mode='send_testbed')
                self.emulation_iol_control(mode='start')
            for iol, cmd in iolCommandLIst.iolDevices.items():
                op = self.iol_telnet_configure(iol, cmd)
                output = op['output']
                msg = f'Output for bulkcommit on IOL: {iol} is :\n{output}'
                richWrapper.console.print (msg)
                
        except Exception as e:
            raise Exception(f' : {e}') 
        return None
    
    
class iolCommandLIst:
    iolDevices = {}

    @staticmethod
    def addIol(iol, cmd):
        if iol in iolCommandLIst.iolDevices:
            iolCommandLIst.iolDevices[iol] = iolCommandLIst.iolDevices[iol] + cmd + '\n'
        else:
            iolCommandLIst.iolDevices[iol] = cmd + '\n'
        
