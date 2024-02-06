import paramiko
import time
import subprocess
from rich.progress import Progress

reconnectDelay = 5


    

class paramikoSSHClient():

    def __init__(self, host, username, password, proxy=False, invoke_shell=False, look_for_keys=False, allow_agent=False):
        from .globals import dingolfyGlobal
        self.logger = dingolfyGlobal.logger
        self.host = host
        self.username = username
        self.password = password
        self.proxy = proxy
        msg = 'Log into {0}, with username {1} and password {2} with proxy {3} and invoke shell {4}'.format(host, username, password, proxy, invoke_shell)
        self.logger.info(msg, To_Screen=False)
        self.client = self.ssh_connect(host, username, password, proxy=proxy, look_for_keys=look_for_keys, allow_agent=allow_agent)
        self.invoke_shell = invoke_shell

        if self.invoke_shell:
            self.channel = self.client.invoke_shell()
            buff = ''
            # Covers prompts for azure ubuntu VMs and DMZ linux VM
            count = 0
            # check if buff ends with any of the below prompts [':~$ ', ':~$', '~]# ', '#', '# ']
            while not buff.endswith((':~$ ', ':~$', '~]# ', '#', '# ')):
            #while not buff.endswith(':~$ ') and not buff.endswith(':~$') and not buff.endswith('~]# ') and not buff.endswith('#') and not buff.endswith('# '):
                resp = self.channel.recv(9999).decode('utf-8')
                buff += resp
                msg = resp
                self.logger.info(msg, To_Screen=True)
                if count >= 1:screen = True
                else:screen = False
                msg = 'logger prompt not seen'
                self.logger.info(msg, To_Screen=screen)
                count += 1

        else:
            self.channel = None

    def scp_remote_to_local(self, remote_path, local_path='/root/',local_filename=None):
        msg = None
        try:
            # Create an SSH client
            ssh_client = paramiko.SSHClient()
            ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())

            # Connect to the remote host
            ssh_client.connect(self.host, username=self.username, password=self.password)

            # Create an SFTP client on top of the SSH connection
            sftp = ssh_client.open_sftp()

            # Download the remote file to the local path
            remote_filename = remote_path.split('/')[-1]
            remote_dir = '/'.join(remote_path.split('/')[:-1])
            remote_file_path = remote_path
            if not local_filename: 
                local_file_path = f"{local_path}/{remote_filename}"
            else:
                local_file_path = f"{local_path}/{local_filename}"

            sftp.get(remote_file_path, local_file_path)

            msg = f"File downloaded from {remote_file_path} to {local_file_path}"
            self.logger.info(msg, To_Screen=True)

        except Exception as e:
            msg = f"An error occurred: {e}"
            self.logger.info(msg, To_Screen=True)
            raise Exception(msg)
        else:
            if sftp:
                sftp.close()
            if ssh_client:
                ssh_client.close()
            return msg

    def is_alive(self):
        return self.client.get_transport().is_active()
    
    def disconnect(self):
        self.client.close()

    def close(self):
        self.client.close()

    def ssh_connect(self, host, username, password, proxy=False, look_for_keys=False, allow_agent=False):
        retryMax = 1
        for retry in range(1,retryMax+1):
            try:
                client = paramiko.SSHClient()
                client.load_system_host_keys()
                client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                if proxy:
                    proxy = paramiko.proxy.ProxyCommand('/usr/bin/ncat --proxy proxy.esl.cisco.com:8080 %s %d' % (host, 22))
                    client.connect(hostname=host, username=username, password=password, look_for_keys=look_for_keys, allow_agent=allow_agent, sock=proxy)
                else:
                    client.connect(hostname=host, username=username, password=password, look_for_keys=look_for_keys, allow_agent=allow_agent)
                
                return client
            except paramiko.AuthenticationException as e:
                self.logger.info("Authentication failed when connecting to %s, %s" % (host, str(e)))

                if retry > 3:
                    self.logger.info("Authentication failed when connecting to %s, %s after 3 tries. will retry again" % (host, str(e)))
                    break

                else:
                    timeout = reconnectDelay
                    msg = "Authentication failed when connecting to %s, %s. Will try again after %d seconds" % (host, str(e), timeout)
                    self.logger.info(msg, To_Screen=True)
                    retry += 1
                    time.sleep(timeout)

            except:
                timeout = reconnectDelay
                msg = f"Could not SSH to %{host}, waiting for it to start. Will try again after {timeout} seconds, sshConn Retry: {retry} of {retryMax}"
                self.logger.info(msg, To_Screen=True)
                retry += 1
                time.sleep(timeout)
        raise Exception('Could not Connect to host - %s' % host)
    @property
    def send_command(self):
        return self.execute_cmd

    def execute_cmd(self, cmd, interactivecommand=None, noexitcode=False, timeout=60,progress=None,task=None):
        def execute_cmd_noshell(cmd, interactivecommand=None, noexitcode=False, count=60):
            try:
                # self.logger.info(cmd, client)
                msg = cmd
                # # hard coded by else while is infinite loop for fail cases
                count = count
                self.logger.info(msg, To_Screen=False)
                ssh_stdin, ssh_stdout, ssh_stderr = self.client.exec_command(cmd)
                if noexitcode: return None
                if interactivecommand:
                    msg = "User requested to send interactive command - %s" % interactivecommand
                    self.logger.info(msg, To_Screen=True)
                    time.sleep(20)
                    ssh_stdin.write(interactivecommand + '\n')
                    ssh_stdin.flush()
                time.sleep(0.25)
                while not ssh_stdout.channel.exit_status_ready():
                    msg = "waiting for command completion exist ready status - %s" % ssh_stdout.channel.exit_status_ready()
                    self.logger.info(msg, To_Screen=False)
                    if progress: progress.update(task, advance=1,description=msg)
                    time.sleep(time_delay)
                    count -= 1
                    if count < 0:
                        raise Exception("time limit exceeded when executing command!!")

                output = ssh_stdout.readlines()
                output = "".join(output)
                if 'ArgumentUsageError' in output:
                    msg = output
                    self.logger.info(msg, To_Screen=True)
                    raise Exception('Command execution failed')
#                 self.logger.info "output Varghese is %s" % output
                return output

            except Exception as  e:
                msg = "Could not execute command , error {}".format(str(e))
                self.logger.info(msg, To_Screen=True)
                raise Exception(msg)

            msg = 'Nothing to return'
            self.logger.info(msg, To_Screen=True)
            return None

        def execute_cmd_invoke_shell(cmd, count=60):
            try:
                # self.logger.info(cmd, client)
                msg = cmd
                # # hard coded by cyarlaga, else while is infinite loop for fail cases
                count = count
                self.logger.info(msg, To_Screen=True)

                self.channel.send(cmd + '\n')
                time.sleep(0.25)
                while not self.channel.recv_ready():
                    msg = "waiting for command completion exist ready status - %s" % self.channel.recv_ready()
                    self.logger.info(msg, To_Screen=True)
                    if progress: progress.update(task, advance=1,description=msg)
                    time.sleep(5)
                    count -= 1
                    if count < 0:
                        raise Exception("time limit exceeded when executing command!!")
                output = self.channel.recv(9999)
                return output
            except Exception as  e:
                msg = "Could not execute command , error {}".format(str(e))
                self.logger.info(msg, To_Screen=True)
                raise Exception(msg)
            msg = "Could not execute command , error {}".format(str(e))
            self.logger.info(msg, To_Screen=True)
            raise Exception('Could not execute command')
        
        time_delay = 5
        count = int(timeout / time_delay)
        if self.invoke_shell:
            op = execute_cmd_invoke_shell(cmd, count=count)
            if type(op)==bytes:
                op = op.decode('utf-8')
            return op
        else:
            op = execute_cmd_noshell(cmd, interactivecommand=interactivecommand, noexitcode=noexitcode, count=count)
            if type(op)==bytes:
                op = op.decode('utf-8')
            return op
        

