'''
A wrapper for typer to override some of the typer functionalities, for example, typer.echo
'''
from .globals import handles, dingolfyGlobal
import typer
import re


def echo_log(*args, **kw):
    '''
    Override typer.echo append to a file and also send to stdout
    '''
    
    with open(dingolfyGlobal.cliOutput, 'a') as f:
        if 'message' in kw:
            msg = kw['message']
        else:
            msg = args[0]
        print(msg)
        f.writelines(msg)
        f.writelines('\n')





