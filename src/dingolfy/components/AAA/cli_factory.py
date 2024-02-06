from . import ding
from ...infra.utils import leafTable
from ...infra import richWrapper
import typer
app = typer.Typer()


@app.command()
def collect_logs(leafName: str = typer.Option(default=False,help='AAA: Please provide leafName in format ifav21-leaf1',)):
    '''
    Collect all necessary AAA related log
    '''
    if not leafName: leafName = leafTable(messagePrefix='AAA:')
    ding.collect_logs(leafName)
   

if __name__ == "__main__":
    app()