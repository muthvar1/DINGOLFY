from . import trexLib
from . import stats
from . import globals
import time
import typer
from ...infra import richWrapper
app = typer.Typer()


@app.command()
def start_traffic(trex_server:str = typer.Option(default=...,prompt="Please provide the trex server ip address"),
                  stream_name:str = typer.Option(default=None,help="Please provide the stream_name that you would like to start traffic for"),
                  stream_id:str = typer.Option(default=None,help="Please provide the stream_id that you would like to start traffic for"),
                  port_handle:str = typer.Option(default='all',help="Please provide the port_handle that you would like to start traffic for"),
                  reset:bool = typer.Option(default=False,help="Please provide the reset option. If set to True, all config will be lost and reset"),
                  break_locks:bool = typer.Option(default=True,help="Please provide the break_locks option. If set to True, all port locks will be broken"),):
    '''
    Start traffic
    '''
    richWrapper.console.print(f"Connecting to trex Server: {trex_server}")
    connectkwargs = {'device': trex_server,
                    'username': 'trex',
                    'reset':reset,
                    'break_locks':break_locks,
                    'port_list': 'all'
                    }
    trex = trexLib.TrexSession(**connectkwargs)
    globals.trexGlobal.trex = trex
    richWrapper.console.print(f"Connected to trex Server: {trex_server}")

    richWrapper.console.print(f"Starting traffic on port: {port_handle}")
    kwargs = {'action': 'run', 'port_handle':port_handle}
    trex.traffic_control(**kwargs)
    richWrapper.console.print(f"Started traffic on port: {port_handle}")
    time.sleep(5)
    richWrapper.console.print(f"Stop traffic for port: {port_handle}")
    kwargs = {'action': 'stop', 'port_handle':port_handle}
    trex.traffic_control(**kwargs)



if __name__ == "__main__":
    app()