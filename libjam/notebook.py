"""Provides functions for reading and writing configuration files as well as
per-program configuration management via Ledger.
"""

# Imports
from configparser import ConfigParser
from pathlib import Path
import os
import sys
import copy
import toml
import json
import platformdirs

# Internal imports
from . import typewriter


# An internal function.
def _merge_dicts(src: dict, dst: dict) -> dict:
  """Ovverides the values of the `dst` dict with the values of the `src` dict."""
  for key, value in src.items():
    if isinstance(value, dict):
      node = dst.setdefault(key, {})
      _merge_dicts(value, node)
    else:
      dst[key] = value
  return dst


def read_toml(file) -> dict:
  """Returns a toml file parsed to a dict."""
  with open(file, 'r') as fp:
    return toml.load(fp)


def write_toml(file, data: dict):
  """Writes a toml file parsed from a dict."""
  with open(file, 'w') as fp:
    toml.dump(data, fp)


# An internal function.
def _get_ini_parser() -> ConfigParser:
  """Returns a ConfigParser."""
  parser = ConfigParser(
    inline_comment_prefixes=('#', ';'),
    strict=False,
  )
  return parser


def read_ini(file) -> dict:
  """Returns an ini file parsed to a dict."""
  with open(file, 'r') as fp:
    data = fp.read()
  parser = _get_ini_parser()
  parser.read_string(data)
  return parser._sections


def write_ini(file, data: dict):
  """Writes a ini file parsed from a dict."""
  parser = _get_ini_parser()
  parser.read_dict(data)
  with open(file, 'w') as fp:
    parser.write(fp)


def read_json(file) -> dict:
  """Returns a json file parsed to a dict."""
  with open(file, 'r') as fp:
    return json.load(fp, strict=False)


def write_json(file, data: dict):
  """Writes a json file parsed from a dict."""
  with open(file, 'w') as fp:
    data = json.dump(data, fp, indent=2)


def get_read_write_functions(file) -> tuple[callable, callable]:
  """Given a path to a configuration file, returns a pair of (read, write) functions"""
  functions = {
    'toml': (read_toml, write_toml),
    'ini': (read_ini, write_ini),
    'json': (read_json, write_json),
  }
  extension = os.path.splitext(file)[1].removeprefix('.')
  pair = functions.get(extension)
  if not pair:
    raise NotImplementedError(f"Unsupported format '{extension}'")
  return pair


class Config:
  """A config object, meant to be created by the Ledger.

  On initialisation, if the `file` does not exist it writes the file using the
  'template' string. Then it checks the config for any errors with the config
  file, if it encounters an issue it prints what the issue is and then exits.
  In other words, if you have initialised the config object, you can be sure
  that it does not contain any errors.

  The `defaults` dict is used to fill in any values that are missing in the
  config file itself.
  """

  def __init__(self, file, defaults: dict, template: str):
    # Ensuring file exists
    file = Path(file)
    if not file.is_file():
      file.write_text(template)
    # Setting vars to self
    self.file = file
    self.defaults = defaults
    # Checking config contents
    self.check()

  def check(self):
    """Checks the config file for any errors, if any are present then it prints
    the error and exits using the appropriate exit code.
    """
    try:
      self.read()
    except Exception as e:
      self.on_error(str(e))

  def on_error(self, error: str or list[str]):
    error_type = type(error)
    if error_type not in (str, list):
      raise TypeError(f"Invalid error type '{error_type}'")
    if error_type is str:
      title = f"Configuration error in '{self.file}':"
      error = [error]
    title = typewriter.stylise(
      typewriter.Colour.BRIGHT_RED,
      'Configuration error(s):',
    )
    title = typewriter.bolden(title)
    errors = [f'- {e}' for e in error]
    errors = typewriter.list_to_columns(errors, n_columns=1)
    print(f'{title}\n{self.file}:\n{errors}', file=sys.stderr)
    exit_code = getattr(os, 'EX_CONFIG', None)
    if exit_code is None:
      exit_code = 78
    sys.exit(exit_code)

  def read(self) -> dict:
    """Reads the config and fills any missing values with the 'defaults' provided
    during initialisation.
    """
    read_func, _ = get_read_write_functions(self.file)
    data = read_func(self.file)
    defaults = copy.deepcopy(self.defaults)
    data = _merge_dicts(data, defaults)
    return data

  def write(self, data: dict):
    """Writes the given dict to the config file.
    Note that using this function will erase all the comments and custom
    formatting from the file.
    """
    _, write_func = get_read_write_functions(self.file)
    return write_func(self.file, data)


# Ensures that the program's configuration directory exists on initialisation
# and simplifies the creation of Config objects.
class Ledger:
  def __init__(
    self,
    program: str,
    author: str = None,
    version: str = None,
    roaming: bool = False,
  ):
    configs_dir = platformdirs.user_config_path()
    configs_dir.mkdir(exist_ok=True)
    self.config_dir = platformdirs.user_config_path(
      program,
      author,
      version,
      roaming,
    )

  def init_config(
    self,
    name: str,
    defaults: dict,
    template: str,
    extension: str = 'toml',
  ) -> Config:
    """Initialises a Config.

    The `extension` can be 'toml', 'ini' or 'json'
    """
    if extension not in ('toml', 'ini', 'json'):
      raise ValueError(f"Invalid extension '{extension}'")
    self.config_dir.mkdir(exist_ok=True)
    file = name + '.' + extension
    file = self.config_dir / file
    config = Config(file, defaults, template)
    return config
