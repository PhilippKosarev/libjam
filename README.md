# libjam
A library jam for Python.

## Installing
libjam is available on [PyPI](https://pypi.org/project/libjam/), and can be installed using pip.
```sh
pip install libjam
```sh
To install the latest bleeding edge:
```sh
pip install git+https://github.com/philippkosarev/libjam.git
```

## Submodules

### Captain
Provides an easy, intuitive and boilerplate-free way of creating command line interfaces.

#### A simple CLI script:
example.py:
```python
#! /usr/bin/env python3

from libjam import Captain

def shout(text: str):
  'Shouts the given text back'
  if options.get('world'):
    text += ' world'
  print(text + '!')

captain = Captain(shout, program='shout')
captain.add_option(
  'world', ['world', 'w'],
  "Adds ' world' before the exclamation mark",
)
global options
args, options = captain.parse()
shout(*args)
```

Usage:
```sh
$ ./example.py
shout: missing argument <TEXT>

$ ./example.py Hello
Hello!

$ ./example.py Hello --world
Hello world!

$ ./example.py --help
Usage:
  shout [OPTION]... <TEXT>
Description:
  Shouts the given text back.
Options:
  -w, --world - Adds ' world' before the exclamation mark.
  -h, --help  - Prints this page.
```

### Drawer
Provides a few missing pieces for file management.

#### Example CLI for extracting any archive:
extract.py:
```python
#! /usr/bin/env python3

# Imports
from libjam import Captain, drawer, typewriter
import os, sys

# Helper functions
def eprint(*args, **kwargs):
  print(*args, **kwargs, file=sys.stderr)

# Main function
def extract(archive: str, out_directory: str):
  # Checking for errors
  if not os.path.exists(archive):
    captain.on_usage_error('file not found.')
  if os.path.isdir(archive):
    captain.on_usage_error('given archive is a directory.')
  if not drawer.is_archive_supported(archive):
    captain.on_usage_error('unsupported archive type.')
  # Extracting
  basename = os.path.basename(archive)
  def progress_function(done: int, todo: int):
    typewriter.print_progress(f"Extracting '{basename}'", done, todo)
  drawer.extract_archive(archive, out_directory, progress_function)
  typewriter.clear_lines(0)

# Running
def main():
  captain = Captain(extract)
  args = captain.parse()
  return extract(*args)

if __name__ == '__main__':
  sys.exit(main())
```

### Typewriter
Provides functions for formatting and printing text.

### Notebook
Allows reading and writing toml, ini and json configuration files. Also provides a configuration management system via the `Notebook.Ledger` class.

#### Example configuration for a program:
config.py:
```py
# Imports
from pathlib import Path
from libjam import notebook

# Defining default values
default_downloads_dir = Path.home() / 'Downloads'
if not default_downloads_dir.is_dir():
  default_downloads_dir = None
default_values = {
  'downloads-directory': default_downloads_dir,
}

# Config template
template = '''\
# An override for the default downloads directory
# downloads-directory = ''
'''

# Initialising config
ledger = notebook.Ledger('download-manager')
config_obj = ledger.init_config('config', default_values, template)
config_dict = config_obj.read()

# Checking values
downloads_dir = config_dict.get('downloads-directory')
if downloads_dir is None:
    config_obj.on_error(
      "Could not automatically find an existing Downloads directory. "
      "Please specify the 'downloads-directory' manually."
  )
downloads_dir = Path(downloads_dir)
if not downloads_dir.is_dir():
  config_obj.on_error("The specified 'downloads-directory' does not exist.")
```

cli.py:
```py
#! /usr/bin/env python3

# Internal imports
from .download_manager import DownloadManager
from .config impxort downloads_dir

download_manager = DownloadManager(downloads_dir)

# The rest of the program...
```

Example error:
```sh
$ ./cli.py
Configuration error(s):
/home/philipp/.config/download-manager/config.toml:
  - Could not automatically find an existing Downloads directory. Please specify 'downloads-directory' in the configuration manually.
```

### Flashcard
Used for getting user input inside the terminal.

### Cloud
Provides the `download` function.
