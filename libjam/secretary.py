# Imports
from copy import deepcopy
import os
import sys
import toml
import collections
import platformdirs


def _merge_dicts(src: dict, dst: dict) -> dict:
  """Overlays the `dst` dict on top of the `src` dict."""
  for key, value in src.items():
    if isinstance(value, dict):
      node = dst.setdefault(key, {})
      _merge_dicts(value, node)
    else:
      dst[key] = value
  return dst


class File(collections.UserDict):
  """A program's configuration class, works like a dictionary."""

  def __init__(
    self,
    file: str,
    template: str,
    defaults: dict,
    ensure_exists: bool,
    exit_on_error: bool,
  ):
    self.file = file
    self.template = template
    self.defaults = defaults
    self.ensure_exists = ensure_exists
    self.exit_on_error = exit_on_error
    self.load()

  def load(self):
    """Updates the config."""
    if self.exit_on_error:
      try:
        data = self._load()
      except OSError as e:
        self.on_error(e.args[1] + '.')
      except toml.TomlDecodeError as e:
        self.on_error(str(e) + '.')
    else:
      data = self._load()
    self.data = _merge_dicts(data, deepcopy(self.defaults))

  def _load(self) -> dict:
    if self.ensure_exists:
      if not os.path.isfile(self.file):
        with open(self.file, 'w') as fp:
          fp.write(self.template)
    if os.path.isfile(self.file):
      return toml.load(self.file)
    else:
      return {}

  def on_error(self, *lines: str):
    """Prints the error to `sys.stderr` and calls `sys.exit` with the
    appropriate exit code.
    """
    message = '\n'.join(lines)
    print(
      f'Configuration error in {self.file}:\n{message}',
      file=sys.stderr,
    )
    exit_code = getattr(os, 'EX_CONFIG', 78)
    sys.exit(exit_code)


class Secretary:
  """A program's configuration manager.

  This is basically a wrapper around the `platformdirs.user_config_dir`
  function, but with the addition of the `file` method.

  The `ensure_exists` option is passed down to `File`s created
  by the `file` method, if not specified otherwise.
  """

  def __init__(
    self,
    program: str,
    author: str = None,
    version: str = None,
    roaming: bool = False,
    ensure_exists: bool = False,
  ):
    self.directory = platformdirs.user_config_dir(
      program, author, version, roaming, ensure_exists,
    )
    self.ensure_exists = ensure_exists
    self.program = program

  def file(
    self,
    name: str,
    defaults: dict = {},
    template: str = '',
    ensure_exists: bool = None,
    exit_on_error: bool = True,
  ) -> File:
    """Files a configuration."""
    file = os.path.join(self.directory, name + '.toml')
    if ensure_exists is None:
      ensure_exists = self.ensure_exists
    file = File(file, template, defaults, ensure_exists, exit_on_error)
    return file
