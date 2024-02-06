from . import ding
from ....infra.utils import leafTable
from ....infra import richWrapper
import typer
app = typer.Typer()


@app.command()
def collect_logs(leafName: str = typer.Option(default=False,help='LINK: Please provide leafName in format ifav21-leaf1'),
                 interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 ")
                 
                  ):
    '''
    Collect all necessary LINK/port logs
    '''
    if not leafName: leafName = leafTable(messagePrefix='LINKS:')
    ding.collect_logs(interface=interface, leafName=leafName)


@app.command()
def show_module(leafName: str = typer.Option(default=False,help='LINK: Please provide leafName in format ifav21-leaf1')):
    '''
    show module
    '''
    if not leafName: leafName = leafTable(messagePrefix='LINKS:')
    ding.show_module(leafName=leafName)

#Show interface commands
@app.command()
def show_interface(leafName: str = typer.Option(default=False,help='LINK: Please provide leafName in format ifav21-leaf1'), 
                    interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16 "),
                    viewOptions: str = typer.Option(default="",prompt="Please provide an option from following List \n-all\n-brief\n-transciver\n-status\n-flap\n:")
                     ):
    '''
    show interface on leaf with different view options
    '''
    if not leafName: leafName = leafTable(messagePrefix='LINKS:')
    if viewOptions not in ['all','brief','transciver','status','flap']:
        print('Please provide a valid view option')
        viewOptions = typer.prompt("Please provide an option from following List -all\n-brief\n-transciver\n-status\n-flap\n:")
        if viewOptions not in ['all','brief','transciver','status','flap']:
            richWrapper.console.error('Please provide a valid view option')
            typer.Abort()
    ding.show_interface(leafName=leafName, interface=interface, viewOptions=viewOptions)

#USD info commands
@app.command()
def show_usd_info(leafName: str = typer.Option(default=False,help='LINK: Please provide leafName in format ifav21-leaf1'), 
                    interface: str = typer.Option(default="",prompt="Please provide interface id , eg: Eth1/16"),
                    viewOptions: str = typer.Option(default="",prompt="Please provide an option from following List -all\n-event-history\n-link-event\n-dfe\n-xcvr:")
                     ):
    '''
    show usd info on port
    '''
    if not leafName: leafName = leafTable(messagePrefix='LINKS:')
    if viewOptions not in ['all','event-history','link-event','dfe','xcvr']:
        print('Please provide a valid view option')
        viewOptions = typer.prompt("Please provide an option from following List -all\n-event-history\n-link-event\n-dfe\n-xcvr:")
        if viewOptions not in ['all','event-history','link-event','dfe','xcvr']:
            richWrapper.console.error('Please provide a valid view option')
            typer.Abort()
    ding.show_usd_info(leafName=leafName, interface=interface, viewOptions=viewOptions)

    

if __name__ == "__main__":
    app()