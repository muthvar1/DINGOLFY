from ...infra.utils import sendCmd, sendCmdApic
from ...infra.globals import handles
from typing import Optional
import typer
from .utils import Contracts


def collect_logs(vrf:str=None,leafName:str=None,srcEpg:str=None,dstEpg:str=None):
    '''
    Collect all the logs for contracts
    '''
    zoning_rules(vrf=vrf,leafName=leafName,srcEpg=srcEpg,dstEpg=dstEpg)


def zoning_rules(vrf:str=None,leafName:str=None,srcEpg:str=None,dstEpg:str=None):
    '''
    get Zoning rules from leaf using the command "show zoning-rule"
    Also derive the actrl rule from the object store
    If srcEpg is provided, then derive the pcTag from the srcEpg and the scope id of the vrf
    If the dstEpg is provided, then derive the pcTag from the dstEpg and the scope id of the vrf
    If the vrf is provided, then derive the scope id of the vrf
    If the filterName is provided, then derive the filterId from the filterName, assuming srcEpg is provided
    If the filterId id is provided, then use that to derive zoning rules for that filterId
    '''
    Contracts.zoning_rule(vrf=vrf,leafName=leafName,srcEpg=srcEpg,dstEpg=dstEpg)

