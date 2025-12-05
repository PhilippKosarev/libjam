# libjam
A library jam for Python.

## Installing
libjam is available on [PyPI](https://pypi.org/project/libjam/), and can be installed using pip.
```
pip install libjam
```
To install the latest bleeding edge:
```
pip install git+https://github.com/philippkosarev/libjam.git
```

## Modules

### Captain
Makes creating command line interfaces easy.

### Drawer
Responsible for file operations. Accepts the '/' as the file separator, regardless the OS.

### Typewriter
Transforms text and prints to the terminal.

### Clipboard
Provides some useful and commonly used list operations.

### Notebook
Simplifies and standardises reading and writing configuration files.

### Flashcard
Useful for getting user input from the command line.

## Example CLI project
example.py:
```python
from libjam import Captain

class CLI:
  'An example CLI for the libjam library'
  def shout(self, *text):
    'Shouts the given text back'
    text = ' '.join(text)
    if options.get('world'):
      text += ' world'
    print(text + '!')

cli = CLI()
captain = Captain(cli)
captain.add_option(
  'world', ['world', 'w'],
  "Adds ' world' before the exclamation mark",
)
global options
function, args, options = captain.parse()
function(*args)
```

Output:
```sh
$ ./example.py
example.py: No command specified.
Try 'example.py --help' for more information.

$ ./example.py shout Hello
Hello!

$ ./example.py shout Hello --world
Hello world!

$ ./example.py --help
Usage:
  example.py shout [TEXT]...
Synopsis:
  example.py [OPTION]... COMMAND [ARGS]...
Description:
  An example CLI for the libjam library.
Commands:
  shout - Shouts the given text back.
Options:
  -w, --world - Adds ' world' before the exclamation mark.
  -h, --help  - Prints this page.
```