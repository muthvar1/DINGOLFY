from .globals import handles
import typer
import re
import datetime
from . import richWrapper
from typing import List
from rich.table import Table
from rich.markup import escape
from rich.progress import Progress
from .utils import sendCmdApic, compare_versions
import json

def reInitFT():
    FT.log_file = None
    FT.data_file = None
    FT.logdata = None
    FT.errors = None
    FT.nodes = []
    

class FT:
    log_file = None
    data_file = None
    logdata = None
    errors = None
    nodes = []

class NodeData:
    nodename = None #Node name
    entry = None #If this is set to True, this is the node where the pkt entered
    inc = None
    out = None
    asictype = None
    nodeid = None
    eprec = None
    fibrec = None
    aclqosrec = None
    policyrec = None
    drop_err_code = None
    prettyelamrep = None
    ingress_lc = None
    egress_lc = None
    egress = None


    


class FTRIAGE:
    # check if the apic version is below 6.0(2)
    # if yes, then use the old ftriage command without -passwd
    # else use the new ftriage command with -passwd
    # Few examples of versions that are below 6.0(2) are: 6.0(1d), 5.2(1e), 5.1(3e), 5.2(1e), 5.0(2)
    # Few examples of versions that are above 6.0(2) are: 6.0(2d), 6.0(3), 6.0(4), 6.1(1), 6.2(1), 6.3(1), 6.4(1), 6.4(1d)
    passwordRequired = False
    @staticmethod
    def prefix():
        version = handles.ifc_sdk_handle.version
        FTRIAGE.passwordRequired = False

        if compare_versions(version, '6.0(2)'):
            prefix = f'ftriage -user {handles.apic_ssh_handle.username}'
            FTRIAGE.passwordRequired = True
        else:
            prefix = f'ftriage -user {handles.apic_ssh_handle.username} -passwd {handles.apic_ssh_handle.password}'
        return prefix
    @staticmethod
    def updateFT(log_file, data_file):
        '''
        Update the FT object with the latest log file and data file
        '''
        
        FT.log_file = log_file
        FT.data_file = data_file
        FT.nodes = []
        with open(FT.data_file) as f:
            FTDATA = json.load(f)
        FT.logdata = FTDATA['logdata']
        FT.errors = FTDATA['errors']
        
        for node in FTDATA['nodes'].values():
            
            nd = NodeData()
            if node['numpkts']!=1: 
                msg = f"Node {node['pktlist'][0]['nodename']} has more than one packet: {node['pktlist']}. Taking the first packet"
                richWrapper.console.warning(msg)
            pkt = node['pktlist'][0]
            for key in NodeData.__dict__.keys():
                try:
                    if key == 'exit':
                        nd.egress = pkt[key]
                    elif key in pkt.keys():
                        setattr(nd, key, pkt[key])
                        
                        
                except KeyError as e: print(e)
            
            FT.nodes.append(nd)
        
    @staticmethod
    def printReturnElamBlock(start_line,end_line,prettyelam,include_last_line=False):
        '''
        Given a start and end line, print the elam block from the prettyelam
        report
        '''
        # The multiline text you provided
        text = prettyelam
        block = ''
        # Split the text into lines
        lines = text.strip().split('\n')

        # Initialize a flag to indicate when to start and stop capturing lines
        capture_lines = False

        # Iterate through the lines
        for line in lines:
            # Check if the current line contains start_line
            if start_line in line:
                capture_lines = True
            
            # Check if the current line contains end_line
            elif end_line in line:
                if not include_last_line:
                    break
                capture_lines = False
                break  # Stop capturing lines
            
            # If the capture_lines flag is True, print the current line
            elif capture_lines:
                print(line.strip())
                block += line.strip() + '\n'
        return block
    @staticmethod
    def getpctagfromelam(prettyelam):
        '''
        Given an elam block, return the src pcTag and dst pcTag if present
        else return None
        Sample elam block below, where src pcTag is 5638 and dst pcTag is 13

        Contract Lookup Key
        ------------------------------------------------------------------------------------------------------------------------------------------------------
        IP Protocol                             : undefined( 0x3D )             
        L4 Src Port                             : 21602( 0x5462 )               
        L4 Dst Port                             : 27090( 0x69D2 )               
        sclass (src pcTag)                      : 5638( 0x1606 )                
        dclass (dst pcTag)                      : 13( 0xD )                     
        src pcTag is from local table           : yes                           
        derived from a local table on this node by the lookup of src IP or MAC
        Unknown Unicast / Flood Packet          : no                            
        If yes, Contract is not applied here because it is flooded

        '''

        text = FTRIAGE.printReturnElamBlock(start_line='Contract Lookup Key',end_line='Contract Result',prettyelam=prettyelam)
        lines = text.strip().split('\n')
        src_pcTag = None
        dst_pcTag = None
        for line in lines:
            # Check if the current line contains start_line
            if 'sclass (src pcTag)' in line:
                src_pcTag = line.split(':')[1].strip().split('(')[0].strip()
            if 'dclass (dst pcTag)' in line:
                dst_pcTag = line.split(':')[1].strip().split('(')[0].strip()
        return src_pcTag, dst_pcTag


    @staticmethod
    def getAclqosStatsIdfromelam(prettyelam):
        '''
        Given an elam block, return the Aclqos Stats Index if present
        else return None
        Sample elam block below, where Aclqos Stats Index is 81871

        ------------------------------------------------------------------------------------------------------------------------------------------------------
        Contract Result
        ------------------------------------------------------------------------------------------------------------------------------------------------------
        Contract Drop                           : yes                           
        Contract Logging                        : no                            
        Contract Applied                        : no                            
        Contract Hit                            : yes                           
        Contract Aclqos Stats Index             : 81871                         
        ( show sys int aclqos zoning-rules | grep -B 9 "Idx: 81871" )

        ======================================================================================================================================================
                                                                Look Up Blocks Information


        '''
        text = FTRIAGE.printReturnElamBlock(start_line='Contract Result',end_line='Look Up Blocks Information',prettyelam=prettyelam)
        lines = text.strip().split('\n')
        aclqos_stats_id = None
        for line in lines:
            # Check if the current line contains start_line
            if 'Contract Aclqos Stats Index' in line:
                aclqos_stats_id = line.split(':')[1].strip()
        return aclqos_stats_id


    @staticmethod
    def getLeafPrefix(src_leaf:str, dst_leaf:str):
        if not src_leaf and not dst_leaf:
            return ''
        elif not src_leaf:
            return f'-ei {FTRIAGE.getLeaftype(dst_leaf)}:{dst_leaf}'
        elif not dst_leaf:
            return f'-ii {FTRIAGE.getLeaftype(src_leaf)}:{src_leaf}'
        else:
            return f'-ii {FTRIAGE.getLeaftype(src_leaf)}:{src_leaf} -ei {FTRIAGE.getLeaftype(dst_leaf)}:{dst_leaf}'
    @staticmethod
    def getLeaftype(leafName:str):
        '''
        Given a leafName, return the leaf type leaf/VPC
        '''
        try:
            int(leafName)
            return 'LEAF'
        except ValueError:
            return 'VPC'   
    @staticmethod
    def route(src_ip:str, dst_ip:str, src_leaf: str=None, dst_leaf: str=None):
        '''
        Given a source and destination IP address, run ftriage route between them
        '''
        cmd = f'{FTRIAGE.prefix()} route {FTRIAGE.getLeafPrefix(src_leaf=src_leaf,dst_leaf=dst_leaf)} -sip {src_ip} -dip {dst_ip}'
        FTRIAGE.run(cmd)


    @staticmethod
    def bridge(src_mac:str=None, dst_mac:str=None, src_ip:str=None, dst_ip:str=None, src_leaf: str=None, dst_leaf: str=None):
        '''
        Given a source and destination MAC/IP address, run ftriage bridge between them
        '''
        if (bool(src_mac),bool(dst_mac),bool(src_ip),bool(dst_ip)) not in (
            (True,True,False,False), 
            (False,False,True,True)):
            typer.BadParameter(f'Please provide either src_mac and dst_mac or src_ip and dst_ip')

        bridge_prefix = f'{FTRIAGE.prefix()} bridge {FTRIAGE.getLeafPrefix(src_leaf=src_leaf,dst_leaf=dst_leaf)}'
        if src_mac and dst_mac:
            cmd = f'{bridge_prefix} -smac {src_mac} -dmac {dst_mac}'
        else:
            cmd = f'{bridge_prefix} -sip {src_ip} -dip {dst_ip}'
        
        FTRIAGE.run(cmd)

    @staticmethod
    def run(cmd:str):
        '''
        Given a command, run ftriage command
        '''
        def return_filename_with_recent_date(files: list):
            '''
            Given a list of files with a time stamp in the name, return the file with the most recent time stamp
            All files would be in this format: data_2023-08-02-14-43-09-833.json
            '''
            file_dict = {}
            for file in files:
                try:
                    file_dict[file] = datetime.datetime.strptime(re.search(r'\d{4}-\d{2}-\d{2}-\d{2}-\d{2}-\d{2}-\d{3}',file).group(),'%Y-%m-%d-%H-%M-%S-%f')
                except AttributeError:
                    msg = f'File {file} does not have a date in the name'
                    print(msg)
                    continue
            return max(file_dict, key=file_dict.get)
        
        try:
            timeout = 1200
            msg = richWrapper.highlight(f'Running ftriage command: {cmd}.')
            richWrapper.console.print(msg)
            msg =f'##### This could take anywhere between 5 and 20 minutes #####'
            richWrapper.console.warning(msg)
            with Progress() as progress:
                task = progress.add_task("[magenta bold]CmdExecutionWait...", total=timeout/5)
                
                while not progress.finished:
                    if FTRIAGE.passwordRequired:
                        output = sendCmdApic(cmd,interactivecommand=handles.apic_ssh_handle.password,timeout=timeout,progress=progress,task=task)
                        progress.update(task, advance=timeout/5,description='CmdExecutionWait: Completed')
                    else:
                        output = sendCmdApic(cmd,timeout=timeout,progress=progress,task=task)
                        progress.update(task, advance=timeout/5,description='CmdExecutionWait: Completed')
            richWrapper.console.print('Ftriage completed. Please see the output above')
        except Exception as e:
            richWrapper.console.print(f'Ftriage failed with Exception:{e}')
            raise typer.Abort()
        
        # extract the log file name from the multiline ouput.
        # The line with the log file name will have the following pattern: Log file name for the current run is: ftlog_2023-08-09-13-33-59-398.txt
        try:
            logFileName = re.search(r'Log file name for the current run is: (.*)',output).group(1)
            richWrapper.console.print(f'Ftriage file is {logFileName}')
            try:
                remote_path = f'/home/admin/{logFileName}'
                local_path = '/root/'
                local_filename = f'{local_path}{logFileName}'
                handles.apic_ssh_handle.scp_remote_to_local(remote_path=remote_path,local_path=local_path)
                #replace ftlog with data and .txt with .json
                datalogFileName = logFileName.replace('ftlog','data').replace('.txt','.json')
                
                remote_path = f'/home/admin/{datalogFileName}'
                local_path = '/root/'
                local_data_filename = f'{local_path}{datalogFileName}'
                handles.apic_ssh_handle.scp_remote_to_local(remote_path=remote_path,local_path=local_path)
            except Exception as e:
                richWrapper.console.error(f'Ftriage failed: Could not scp ftriage Log File, Exception:{e}')
                raise typer.Abort()
            richWrapper.console.print(f'Ftriage log file location:{local_filename}')
            richWrapper.console.print(f'Ftriage json data file location:{local_data_filename}')
        except AttributeError:
            richWrapper.console.error('Ftriage failed: output does not have a log file name')
            raise typer.Abort()
        except Exception as e:
            richWrapper.console.error(f'Ftriage failed: Could not scp ftriage Log File, Exception:{e}')
            richWrapper.console.error('Please check for the following posibilities:')
            msg = '''
1. The data log file or the ft log file was not generated
2. The data log file and the ft log filke may not have the same extensions for example 
    ftlog_2023-10-10-15-01-25-155.txt
    data_2023-10-10-15-01-25-156.json
    In this case you probably have to rerun. The #2 is a rare case that happens when the timing of the file write spans two separate minutes
    Currently there is no fix to address this issue
'''
            raise typer.Abort()
        
        try:
            FTI = FTRIAGE.updateFT(local_filename,local_data_filename)
            #richWrapper.console.print(FT.nodes)
        except Exception as e:
            richWrapper.console.error(f'Ftriage failed: Could not update FT object, Exception:{e}')
            raise typer.Abort()
        if 'Ftriage Completed with: Only one instance of fTriage is supported at a time.' in FT.errors:
            richWrapper.console.error(f'Ftriage failed with another session in progress: {FT.errors}')
            raise typer.Abort()
        #Update the upload file list
        from ..infra.globals import dingolfyGlobal
        dingolfyGlobal.FilesToUpload.append(local_filename)
        dingolfyGlobal.FilesToUpload.append(local_data_filename)
        