# DINGOLFY

A CLI-based utility to debug the ACI Fabric and collect component-level logs.


## Installation

Use the package manager [pip](https://pip.pypa.io/en/stable/) to install Dingolfy.

```bash
python3 -m pip install --upgrade git+https://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@wwwin-github.cisco.com/ACI-QA/DINGOLFY.git
```

## Usage

```bash
Dingolfy

# returns a list of options and commands
Options:
  --cdets-id TEXT
  --cec-id TEXT
  --install-completion  Install completion for the current shell.
  --show-completion     Show completion for the current shell, to copy it or
                        customize the installation.

  --help                Show this message and exit.

Commands:
  aaa                Helps users collect log/debug AAA issues
  apic_platform      Helps users collect log/debug ApicPlatform issues
  cdets-file-upload  Upload files to cdets
  contracts          Helps users collect log/debug Contracts issues
  l2_forwarding      Helps users collect log/debug L2_Forwarding issues
  l3_forwarding      Helps users collect log/debug L3_Forwarding issues
  multicast          Helps users collect log/debug MULTICAST issues
  switch_platform    Helps users collect log/debug SwitchPlatform issues
  version            Print the version of dingolfy


```

## Contributing

Pull requests are welcome. For changes, please open a CDETS defect first
to discuss what you would like to change. All commits have to be code-reviewed and unit-tested.

Please make sure to update tests as appropriate.
Important notes on adding code:
  - Please optimize your code and do not load large data stuctures into memory. Specifically lookups that result in large data sets should be avoided. The utility is built to run in light weight environments with stringent memory requirements. Running into OOM situation is quite common and would need a redesign of your code.
  - Do not raise Exceptions as "raise Exception(msg)". Instead use the richconsole error wrapper to print out your exception and subsequently use typer.Exit() to exit.
```python
    try:
        something
    except Exception as e:
        richWrapper.console.error(f'Exception: {e}')
        raise typer.Exit() #Please be aware that if you raise typer.Exit() then the end callback method does not get called which includes logfile location and cdets uploads
```

## License


