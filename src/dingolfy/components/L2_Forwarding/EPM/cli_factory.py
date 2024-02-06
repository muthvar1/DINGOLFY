from . import ding
from ....infra.utils import vrfTable, leafTable, ipValidation,versionValidation
from ..utils import EP
import typer
app = typer.Typer()


@app.command()
def collect_logs(vrf: str = typer.Option(default=False,help='EPM: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='EPM: Please provide leafName in format ifav21-leaf1'),
                 ip: str = typer.Option(default="",prompt="Please provide epm ip , eg: 1.1.1.1",callback=ipValidation),
                 mac: str = typer.Option(default="",prompt="Please provide epm mac , eg: 00:00:01:00:d2:38"),
                 tunnel_id: str = typer.Option(default="",prompt='Please provide tunnel id'),
                 ):
    '''
    Collect all necessary L2 Forwarding CONFIG DEPLOYMENT logs
    '''
    if not vrf: vrf = vrfTable(messagePrefix='EPM:')
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.collect_logs(vrf=vrf, ip=ip, mac=mac,leafName=leafName)




@app.command()
def epm_ip(ip: str = typer.Option(default="",prompt="Please provide epm ip , eg: 1.1.1.1",callback=ipValidation),
           leafName: str = typer.Option(default=False,help='EPM: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    verify the EPM o/p of the source EP for correct mapping of below entities in source TOR for the given ip
    VRF vnid, BD vnid, port of learning, SCLASS
    '''
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.epm_ip(ip=ip,leafName=leafName)

@app.command()
def epm_mac(mac: str = typer.Option(default="",prompt="Please provide epm mac , eg: 00:00:01:00:d2:38"),
           leafName: str = typer.Option(default=False,help='EPM: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    verify the EPM o/p of the source EP for correct mapping of below entities in source TOR for the given mac
    VRF vnid, BD vnid, port of learning, SCLASS
    '''
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.epm_mac(mac=mac,leafName=leafName)

@app.command()
def epm_vrf(vrf: str = typer.Option(default=False,help='EPM: Please provide vrf name in format tn1:ctx1 or all'),
                leafName: str = typer.Option(default=False,help='EPM: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    verify the EPM o/p of the source EP for correct mapping of below entities in source TOR for the given vrf
    VRF vnid, BD vnid, port of learning, SCLASS
    '''
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.epm_vrf(vrf=vrf,leafName=leafName)


@app.command()
def epm_summary(leafName: str = typer.Option(default=False,help='EPM: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    verify the EPM summary on TOR
    '''
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.epm_summary(leafName=leafName)

@app.command()
def epm_tunnel(tunnel_id: str = typer.Option(default=...,prompt='Please provide tunnel id'),
           leafName: str = typer.Option(default=False,help='EPM: Please provide leafName in format ifav21-leaf1')
           ):
    '''
    verify the tunnel destination is same as the destination TOR dtep or the vpc tep based on the location of EP
    show system internal epm interface tunnel <tunnel_id>
    '''
    if not leafName: leafName = leafTable(messagePrefix='EPM:')
    ding.epm_tunnel(tunnel_id=tunnel_id,leafName=leafName)

@app.command()
def locate_ip(ip:str = typer.Option(default="",prompt="Please provide ip to locate , eg:1.1.1.1",callback=ipValidation)):
           
    '''
    verify the location of the given ip
    '''
    
    EP.ip_location(ip=ip,comprehensive=True)
    
@app.command()
def locate_mac(mac:str = typer.Option(default="",prompt="Please provide mac to locate , eg:00:00:01:00:d2:38")):
           
    '''
    verify the location of the given mac
    '''
    EP.mac_location(mac=mac)
    
               
@app.command()
def ftriage(src_ip:str = typer.Option(default="",prompt="Please provide source ip , eg:1.1.1.1,",callback=ipValidation),
            dst_ip:str = typer.Option(default="",prompt="Please provide destination ip , eg:1.1.1",callback=ipValidation)
):
    '''
    Given the src ip and dst ip, verify the forwarding path by running 
    ftriage on the fabric and verify the path on the leaf and spine.
    Also, validate and provide information on the following:
    - Policy drops
    - Hardware drops
    - EPM drops
    - Path drops
    - Path drops on the leaf
    - Path drops on the spine
    

    '''
    ding.ftriage(src_ip=src_ip,dst_ip=dst_ip)
    


if __name__ == "__main__":
    app()
