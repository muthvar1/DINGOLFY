from . import ding
from ....infra.utils import leafTable
from ....infra import richWrapper
import typer
app = typer.Typer()


@app.command()
def collect_logs(leafName: str = typer.Option(default=False,help='MACSEC: Please provide leafName in format ifav21-leaf1'),
                 ):
    '''
    Collect all necessary MACSEC logs
    '''
    if not leafName: leafName = leafTable(messagePrefix='MACSEC:')
    ding.collect_logs(leafName=leafName)



    

    

if __name__ == "__main__":
    app()