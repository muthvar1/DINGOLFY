import typer
from .infra.typer_wrapper import echo_log
typer.echo = echo_log
from .infra import richWrapper
from .components.L3_Forwarding import cli_factory as L3_Forwarding
from .components.L2_Forwarding import cli_factory as L2_Forwarding
from .components.SwitchPlatform import cli_factory as SwitchPlatform
from .components.ApicPlatform import cli_factory as ApicPlatform
from .components.Contracts import cli_factory as Contracts
from .components.MULTICAST import cli_factory as MULTICAST
from .components.AAA import cli_factory as AAA
from .components.BARNEY import cli_factory as BARNEY

from requests_oauthlib import OAuth1, OAuth1Session
import time
import re
import os
import datetime
bugFilingGudielines = 'For any issues seen please file CDETS defect under the following components\n\tProject:CSC.autons\n\tProduct:aci\n\tComponent:aci-qa-dashboard\n\tPlease include Dingolfy version in the description'
startTimer = datetime.datetime.now()

def cdetsUpload(ddts: str, cec_id: str,outputFile: str,filename: str)->None:
    from .infra.globals import dingolfyGlobal
    with open(outputFile, 'r') as file:
        content = file.read()
        content = content.encode('utf-8')
    cdets_url = "https://cdetsng.cisco.com/wsapi/latest/api"
    session = OAuth1Session(dingolfyGlobal.coar_key, client_secret=dingolfyGlobal.coar_secret, resource_owner_key=cec_id, resource_owner_secret=dingolfyGlobal.coar_secret)
    url = cdets_url+'/bug/'+ddts+'/file/'+filename
    response = session.post(url,data=content,headers={'Content-Type': 'application/octet-stream'})
    if response.status_code not in [200,201]:
        if response.status_code == 401:
            raise Exception(f'Could not update cdets with attachment, status code:{response.status_code} error:Unauthorized,{response.reason} \nPlease check if you have the correct coar_key')
        raise Exception(f'Could not update cdets with attachment, status code:{response.status_code} error:{response.text}')
    msg = f'\n{outputFile} file uploaded to cdets: {ddts}'
    print(msg)


def handles_callback(cdets_id: str=None,#str = typer.Option(default="",prompt="Please provide cdets_id if required"), 
                     cec_id: str=None):#str = typer.Option(default="",prompt="Please provide cec_id if required")):
#def handles_callback(cdets_id: str = None, cec_id: str = None):
    
    print(f'cdets_id:{cdets_id},cec_id:{cec_id}')
    msg = f'''
______  _                       _   __                                                                      
|  _  \(_)                     | | / _|        _                                                            
| | | | _  _ __    __ _   ___  | || |_  _   _ (_)                                                           
| | | || || '_ \  / _` | / _ \ | ||  _|| | | |                                                              
| |/ / | || | | || (_| || (_) || || |  | |_| | _                                                            
|___/  |_||_| |_| \__, | \___/ |_||_|   \__, |(_)                                                           
                   __/ |                 __/ |                                                              
                  |___/                 |___/                                                               
______       _                           _                                                                  
|  _  \     | |                         (_)                                                                 
| | | | ___ | |__   _   _   __ _   __ _  _  _ __    __ _                                                    
| | | |/ _ \| '_ \ | | | | / _` | / _` || || '_ \  / _` |                                                   
| |/ /|  __/| |_) || |_| || (_| || (_| || || | | || (_| |                                                   
|___/  \___||_.__/  \__,_| \__, | \__, ||_||_| |_| \__, |                                                   
  ___                       __/ |  __/ |            __/ |                                                   
 ( _ )                     |___/  |___/            |___/                                                    
 / _ \/\                                                                                                    
| (_>  <                                                                                                    
 \___/\/                                                                                                    
 _____         _  _                _                                 _  _              _    _               
|  _  |       | |(_)              | |                               | || |            | |  (_)              
| | | | _ __  | | _  _ __    ___  | |      ___    __ _    ___  ___  | || |  ___   ___ | |_  _   ___   _ __  
| | | || '_ \ | || || '_ \  / _ \ | |     / _ \  / _` |  / __|/ _ \ | || | / _ \ / __|| __|| | / _ \ | '_ \ 
\ \_/ /| | | || || || | | ||  __/ | |____| (_) || (_| | | (__| (_) || || ||  __/| (__ | |_ | || (_) || | | |
 \___/ |_| |_||_||_||_| |_| \___| \_____/ \___/  \__, |  \___|\___/ |_||_| \___| \___| \__||_| \___/ |_| |_|
______            _  _  _  _ __   __              __/ |                                                     
|  ___|          (_)| |(_)| |\ \ / /             |___/                                                      
| |_  __ _   ___  _ | | _ | |_\ V /                                                                         
|  _|/ _` | / __|| || || || __|\ /                                                                          
| | | (_| || (__ | || || || |_ | |                                                                          
\_|  \__,_| \___||_||_||_| \__|\_/                                                                          
                                                                                                            
*** Dingolfy: Debugging and Online Log collection Facility ***

{bugFilingGudielines}
'''
    msg = richWrapper.dingolfyLogo(msg)
    richWrapper.console.print(msg)
    #print('*** Dingolfy: Debugging and Online Log collection Facility ***') # we could ideally initialize at this point. But it will slow everything down
    # msg = richWrapper.dingolfyLogo(bugFilingGudielines)
    # richWrapper.console.print(msg)
def end_callback(executed_command_result,cdets_id,cec_id):
    endTimer = datetime.datetime.now()
    print(f'Time taken for Utility in minutes is: {(endTimer-startTimer).total_seconds()/60}')
    from .infra.globals import dingolfyGlobal
    def upload_to_cdets(cdets_id,cec_id):
        version = dingolfyGlobal.version.replace('.','_')
        Base_Date_String = str(re.sub('\s|\:', '_', time.asctime()))
        dateString = '_' + re.sub(':', '_', Base_Date_String)
        extension = typer.prompt('Pleas provide a custom extension to the fileName if required? eg: ifav21-leaf1',default="None")
        if extension not in ['None','none','NONE', '', None]:
            Logfile_Filename = 'Dingolfy_cli_output' + '_' + extension + '_v_' + version + dateString + '.txt'
        else:
            Logfile_Filename = 'Dingolfy_cli_output' + '_v_' + version + dateString + '.txt'
        Logfile_Filename = re.sub(':', '_', Logfile_Filename)
        cdetsUpload(ddts=cdets_id,cec_id=cec_id,outputFile=dingolfyGlobal.cliOutput,filename=Logfile_Filename)
        if dingolfyGlobal.FilesToUpload:
            for logFile in dingolfyGlobal.FilesToUpload:
                try:
                    Logfile_Filename = logFile.split('/')[-1]
                    cdetsUpload(ddts=cdets_id,cec_id=cec_id,outputFile=logFile,filename=Logfile_Filename)
                except Exception as e:
                    richWrapper.console.error(f'Could not upload file: {logFile} to cdets, error:{e}')

    if dingolfyGlobal.cdetsUploaded:
        typer.echo('Files have already been uploaded to cdets')
        
    elif cdets_id and cec_id:
        upload_to_cdets(cdets_id,cec_id)
    elif cdets_id == 'NA':
        typer.echo('cdets_id is NA, not uploading to cdets')
    else:
        #Prompt the user one more time if he wants to upload to cdets
        #If yes, then prompt for cdets_id and cec_id
        #If no, then exit
        #If no response, then exit
        choice = typer.confirm('Do you want to upload the output and files to cdets?')
        if choice:
            cdets_id = typer.prompt('Please provide cdets_id')
            cec_id = typer.prompt('Please provide cec_id')
            upload_to_cdets(cdets_id,cec_id)
        else:
            typer.echo('Exiting without uploading to cdets')
            
    
    from .infra.globals import dingolfyGlobal
    msg = f'''
CLI Output Located at: {dingolfyGlobal.cliOutput}
Dingolfy version: {dingolfyGlobal.version}

    '''
    print(msg)
    msg = richWrapper.dingolfyLogo(bugFilingGudielines)
    richWrapper.console.print(msg)
    
    raise typer.Exit()


app = typer.Typer(callback=handles_callback, result_callback=end_callback)
app.add_typer(L3_Forwarding.app, name="l3_forwarding",help='Helps users collect log/debug L3_Forwarding issues')
app.add_typer(L2_Forwarding.app, name="l2_forwarding",help='Helps users collect log/debug L2_Forwarding issues')
app.add_typer(SwitchPlatform.app, name="switch_platform",help='Helps users collect log/debug SwitchPlatform issues')
app.add_typer(ApicPlatform.app, name="apic_platform",help='Helps users collect log/debug ApicPlatform issues')
app.add_typer(Contracts.app, name="contracts",help='Helps users collect log/debug Contracts issues')
app.add_typer(MULTICAST.app, name="multicast",help='Helps users collect log/debug MULTICAST issues')
app.add_typer(AAA.app, name="aaa",help='Helps users collect log/debug AAA issues')
app.add_typer(BARNEY.app, name="barney",help='a cli plugin for TREX traffic generator')

@app.command()
def cdets_file_upload(files: str = typer.Option(default=False,help='Please provide files to upload to cdets in a comma separated string, eg: /home/user/1.txt,/home/user/2.txt'),
                      cdets_id: str = typer.Option(default=False,help='Please provide cdets_id'),
                      cec_id: str = typer.Option(default=False,help='Please provide cec_id')):
    '''
    Upload files to cdets
    '''
    from .infra.globals import dingolfyGlobal
    if not files:
        files = typer.prompt('Please provide files to upload to cdets in a comma separated string, eg: /home/user/1.txt,/home/user/2.txt',default=False)
        if not files:
            richWrapper.console.error('No files provided to upload to cdets')
            raise typer.Exit()
    if not cdets_id:
        cdets_id = typer.prompt('Please provide cdets_id',default=False)
        if not cdets_id:
            richWrapper.console.error('No cdets_id provided')
            raise typer.Exit()
    if not cec_id:
        cec_id = typer.prompt('Please provide cec_id',default=False)
        if not cec_id:
            richWrapper.console.error('No cec_id provided')
            raise typer.Exit()
    if ',' in files:
        files = [file.strip() for file in files.split(',')]
    else:
        files = [files]
    for file in files:
        if not os.path.isfile(file):
            richWrapper.console.error(f'{file} is not a valid file')
            raise typer.Exit()
        #get the filename from the file path
        filename = file.split('/')[-1]
        cdetsUpload(ddts=cdets_id,cec_id=cec_id,outputFile=file,filename=filename)
    
    dingolfyGlobal.cdetsUploaded = True

@app.command()
def version():
    '''
    Print the version of dingolfy
    '''
    from .infra.globals import dingolfyGlobal
    typer.echo(f'Dingolfy version: {dingolfyGlobal.version}')

if __name__ == "__main__":
    app()
    
    

