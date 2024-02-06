from .ARP_ND import cli_factory as ARP_ND_cli_factory
from .OSPF import cli_factory as OSPF_cli_factory
from .BGP import cli_factory as BGP_cli_factory
from .STATIC_ROUTE import cli_factory as STATIC_ROUTE_cli_factory
from .L3_Traffic_Loss import cli_factory as L3_Traffic_Loss_cli_factory
from .BD_ROUTES import cli_factory as BD_ROUTES_cli_factory
from .BFD import cli_factory as BFD_cli_factory
from .utils import L3
from ...infra.utils import ipValidation, vrfTable, getLeafIdfromLeaName, getLeafNamefromLeafId
from ...infra import richWrapper

import typer
app = typer.Typer()
app.add_typer(ARP_ND_cli_factory.app, name="arp_nd",help='Helps user collect relevant info for ARP/ND Debugging')
app.add_typer(OSPF_cli_factory.app, name='ospf', help='Helps user collect relevant info for OSPF Debugging')
app.add_typer(BGP_cli_factory.app, name='bgp', help='Helps user collect relevant info for BGP Debugging')
app.add_typer(STATIC_ROUTE_cli_factory.app, name='static_route', help='Helps user collect relevant info for STATIC ROUTE Debugging')
app.add_typer(L3_Traffic_Loss_cli_factory.app, name='l3_traffic_loss', help='Helps user collect relevant info for L3 Traffic Loss Debugging')
app.add_typer(BD_ROUTES_cli_factory.app, name='bd_routes', help='Helps user collect relevant info for BD routes not going out L3-out Debugging')
app.add_typer(BFD_cli_factory.app, name='bfd', help='Helps user collect relevant info for BFD Debugging')

@app.command()
def locate_ip(ip:str = typer.Option(default=...,prompt="Please provide interested ipv4/ipv6address",callback=ipValidation),
                       vrf: str = typer.Option(default=None,help='L3_TLOSS: Please provide vrf name in format tn1:ctx1 or all'),
                       leafName: str = typer.Option(default=None,help='L3_TLOSS: Please provide leaf name: eg: ifav21-leaf1')):
    '''
    Locate an externally learnt ip address.
    '''
    if not vrf: vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if vrf=='all':
        vrf = None
    if leafName:
        leafId = getLeafIdfromLeaName(leafName=leafName)
    else:
        leafId = None
    extInfo = L3.locate_ip(externalIp=ip,l3ctxName=vrf,leafId=leafId)


@app.command()
def ftriage_route(src_ip:str = typer.Option(default=...,prompt="Please provide source ip address",callback=ipValidation),
                  dst_ip:str = typer.Option(default=...,prompt="Please provide destination ip address",callback=ipValidation),
                  src_leaf:str = typer.Option(default=None,help="Please provide source leaf , eg:101"),
                  dst_leaf:str = typer.Option(default=None,help="Please provide destination leaf , eg:101"),
                  src_vrf: str = typer.Option(default=None,help='L3_TLOSS: Please provide src_vrf name in format tn1:ctx1 or all'),
                  dst_vrf: str = typer.Option(default=None,help='L3_TLOSS: Please provide dst_vrf name in format tn1:ctx1 or all')):
    '''
    Run ftriage route between two leafs
    '''
    def validateLeafId(leafId:str):
        try:
            int(leafId)
            return True
        except ValueError:
            return False
    if not src_vrf: src_vrf = vrfTable(messagePrefix='L3_TLOSS: For src_vrf:')
    if src_vrf=='all': src_vrf = None
    if not dst_vrf: dst_vrf = vrfTable(messagePrefix='L3_TLOSS: For dst_vrf:')
    if dst_vrf=='all': dst_vrf = None
    if src_leaf and not validateLeafId(src_leaf): src_leaf = getLeafIdfromLeaName(leafName=src_leaf)
    if dst_leaf and not validateLeafId(dst_leaf): dst_leaf = getLeafIdfromLeaName(leafName=dst_leaf)

    L3.ftriage_route(src_ip=src_ip,dst_ip=dst_ip,src_leaf=src_leaf,dst_leaf=dst_leaf,src_vrf=src_vrf,dst_vrf=dst_vrf)

@app.command()
def flow_debug(src_ip: str = typer.Option(default=...,prompt="Please provide source ip , eg:1.1.1.1,",callback=ipValidation),
            dst_ip: str = typer.Option(default=...,prompt="Please provide destination ip , eg:1.1.1",callback=ipValidation),
            src_leaf: str = typer.Option(default=None,help="Please provide source leaf , eg:101"),
            dst_leaf: str = typer.Option(default=None,help="Please provide destination leaf , eg:101"),
            src_vrf: str = typer.Option(default=None,help="Please provide source vrf , eg:tn2:ctx1"),
            dst_vrf: str = typer.Option(default=None,help="Please provide destination vrf , eg:tn2:ctx1"),
            ):
    

    '''
    Given the src ip and dst ip, verify the forwarding path by running 
    ftriage on the fabric and verify the path on the leaf and spine.
    Also, validate and provide information on the following:
    - Policy drops
    - Hardware drops
    - Path drops
    - Path drops on the leaf
    - Path drops on the spine
    
    Subsequently provide the src EP and dst EP information.
    as per the wiki below
    https://wiki.cisco.com/display/ACIQA/End-End+info+based+on+flow

    '''
    def validateLeafId(leafId:str):
        try:
            int(leafId)
            return True
        except ValueError:
            return False
    
    # if not src_vrf: src_vrf = vrfTable(messagePrefix='L3_TLOSS: ')
    if src_vrf=='all': src_vrf = None
    # if not dst_vrf: dst_vrf = vrfTable(messagePrefix='L3_TLOSS:')
    if dst_vrf=='all': dst_vrf = None
    if src_leaf and not validateLeafId(src_leaf): src_leaf = getLeafIdfromLeaName(leafName=src_leaf)
    if dst_leaf and not validateLeafId(dst_leaf): dst_leaf = getLeafIdfromLeaName(leafName=dst_leaf)
    srcL3Info, dstL3Info = L3.ftriage_route(src_ip=src_ip,dst_ip=dst_ip,src_leaf=src_leaf,dst_leaf=dst_leaf,src_vrf=src_vrf,dst_vrf=dst_vrf)
    if not srcL3Info or not dstL3Info:
        richWrapper.console.error("Src/Dst Ip not present in fabric. Please debug route/fabricEndpoint")
        raise typer.Exit()
    from ...infra.ftriage import FT
    if FT.errors:
        if srcL3Info and dstL3Info:
            L3.ftriageResolution(srcL3Info, dstL3Info)
        
    


if __name__ == "__main__":
    app()