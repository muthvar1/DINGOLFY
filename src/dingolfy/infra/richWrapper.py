from rich.console import Console
from rich.traceback import install
from rich.text import Text
from rich.markup import escape
from rich.style import Style
from rich.align import Align
from rich.padding import Padding
from rich.panel import Panel

install(show_locals=True)

class StyleGuide:
    command_style = "bold white on #049fd9"#"bold white on blue"
    title_style = "bold white on #049fd9"#"bold white on blue"
    device_style = "bold"
    warning_style = Style(color="#e8a425", bold=True)#"bold yellow"
    error_style = "bold red"
    highlight_style = "bold white on #049fd9"#"bold white on green"
    pageSeparator = "bold yellow on #049fd9"#"bold yellow on cyan"
    pageSeparatorborder = "black on #049fd9"#"black on cyan"
    dingolfyLogo = "bold white on #049fd9"

_console=Console(highlight=False)
_console.print('\n')
_err_console = Console(stderr=True,highlight=False)
_err_console.print('\n')

def highlight(text):
    return f'[{StyleGuide.highlight_style}]{text}[/{StyleGuide.highlight_style}]'
def dingolfyLogo(text):
    return f'[{StyleGuide.dingolfyLogo}]{text}[/{StyleGuide.dingolfyLogo}]'
def pageSeparator(text,title="",subtitle=""):
    text = Align.center(text)
    pnl = Panel(Padding(text, style=StyleGuide.pageSeparator),title=title, subtitle=subtitle, border_style=StyleGuide.pageSeparatorborder)
    console.print('\n')
    console.print(pnl)
    console.print('\n')
    
def style_command(devicename, text):
    return f'[{StyleGuide.device_style}]{devicename}[/{StyleGuide.device_style}]: [{StyleGuide.command_style}]{escape(text)}[/{StyleGuide.command_style}]'
    


class console:
    
    @staticmethod
    def print(*args,**kwargs):
        '''
        Uses rich to print to stdout
        Also prints all the output to the cli output file, unless specified otherwise
        '''
        def capture_to_text(*args,**kwargs):
            '''
            Takes a rich object and returns the text
            '''
            with _console.capture() as capture:
                _console.print(*args,**kwargs)
            return Text.from_ansi(capture.get()).plain
        
        _console.print(*args,**kwargs)
        text = capture_to_text(*args,**kwargs)
        from .globals import dingolfyGlobal
        with open(dingolfyGlobal.cliOutput,'a') as f:
            f.write(text)
            f.write('\n')
        
        
    
    @staticmethod
    def log(*args,**kwargs):
        '''
        Uses rich to log to stdout and also includes the traceback with local variables
        Also prints all the output to the cli output file, unless specified otherwise
        '''
        def capture_to_text(*args,**kwargs):
            '''
            Takes a rich object and returns the text
            '''
            with _console.capture() as capture:
                _console.log(*args,**kwargs)
            return Text.from_ansi(capture.get()).plain
        
        _console.log(*args,**kwargs)
        text = capture_to_text(*args,**kwargs)
        from .globals import dingolfyGlobal
        with open(dingolfyGlobal.cliOutput,'a') as f:
            f.write(text)
            f.write('\n')
    
    @staticmethod
    def error(*args,**kwargs):
        '''
        Uses rich to print to stderr
        Also prints all the output to the cli output file, unless specified otherwise
        '''
        def capture_to_text(*args,**kwargs):
            '''
            Takes a rich object and returns the text
            '''
            with _err_console.capture() as capture:
                _err_console.print('ERROR: ',style=StyleGuide.error_style,end=' ')
                _err_console.print(*args,**kwargs)
            return Text.from_ansi(capture.get()).plain
        
        _err_console.print('ERROR: ',style=StyleGuide.error_style,end=' ')
        _err_console.print(*args,**kwargs)
        text = capture_to_text(*args,**kwargs)
        from .globals import dingolfyGlobal
        with open(dingolfyGlobal.cliOutput,'a') as f:
            f.write(text)
            f.write('\n')
    
    @staticmethod
    def warning(*args,**kwargs):
        '''
        Uses rich to print to stderr
        Also prints all the output to the cli output file, unless specified otherwise
        '''
        def capture_to_text(*args,**kwargs):
            '''
            Takes a rich object and returns the text
            '''
            with _console.capture() as capture:
                _console.print('WARNING: ',style=StyleGuide.warning_style,end=' ')
                _console.print(*args,**kwargs)
            return Text.from_ansi(capture.get()).plain
        
        _console.print('WARNING: ',style=StyleGuide.warning_style,end=' ')
        _console.print(*args,**kwargs)
        text = capture_to_text(*args,**kwargs)
        from .globals import dingolfyGlobal
        with open(dingolfyGlobal.cliOutput,'a') as f:
            f.write(text)
            f.write('\n')