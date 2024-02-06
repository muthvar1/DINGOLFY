from . import ding
from ....infra.utils import leaf_options
from ....infra import richWrapper
import typer
app = typer.Typer()


@app.command()
def collect_logs():
    '''
    Collect all necessary APIC UPGRADE/DOWNGRADE logs
    '''
    ding.collect_logs()
   

if __name__ == "__main__":
    app()