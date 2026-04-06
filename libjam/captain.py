# Imports
import os
import sys

# Internal imports
from . import typewriter


# Exceptions
class ParsingError(Exception):
  pass


def get_class_commands(cls) -> dict[str: callable]:
  """Returns a dictionary where a command name points to a function."""
  commands = {}
  for key, value in cls.__dict__.items():
    if key.startswith('_'):
      continue
    if not callable(value):
      continue
    key = key.replace('_', '-').lower()
    commands[key] = value
  return commands


def get_function_args(
  function: callable,
) -> tuple[list[str], list[str], str|None]:
  """Returns parameters a given function accepts.

  Return tuple format: `(required, optional, arbitary)`.
  """
  code = function.__code__
  if code.co_kwonlyargcount:
    raise NotImplementedError(
      'Keyword-only function arguments are not supported.'
    )
  varnames = list(code.co_varnames)
  argcount = code.co_argcount
  n_optional_args = len(function.__defaults__ or [])
  n_required_args = argcount - n_optional_args
  required_args = varnames[:n_required_args]
  optional_args = varnames[n_required_args:n_optional_args + 1]
  if code.co_flags & 0x04:
    arbitrary_arg = varnames[argcount]
  else:
    arbitrary_arg = None
  return required_args, optional_args, arbitrary_arg


def _to_posix_arg(arg: str) -> str:
  return arg.replace('_', ' ').upper()


def to_posix_args(
  required_args: list,
  optional_args: list = [],
  arbitrary_arg: str = None,
) -> str:
  """Returns the POSIX-style representation of given arguments."""
  required_args = [_to_posix_arg(arg) for arg in required_args]
  optional_args = [_to_posix_arg(arg) for arg in optional_args]
  required_args = [f'<{arg}>' for arg in required_args]
  optional_args = [f'[{arg}]' for arg in optional_args]
  all_args = required_args + optional_args
  if arbitrary_arg:
    arbitrary_arg = _to_posix_arg(arbitrary_arg)
    arbitrary_arg = f'[{arbitrary_arg}]...'
    all_args.append(arbitrary_arg)
  return ' '.join(all_args)


def _dict_to_table(d: dict[str: str|None]) -> str:
  """Creates a help page table from the given dictionary."""
  items = []
  for key, value in d.items():
    value = ' - ' + value if value else ''
    items += [key, value]
  return typewriter.to_columns(items, 2, '', '')


# Captain is a tool for making CLIs quickly. It works by constructing a CLI
# based on the specified `ship` which can be either an initialised object or
# a function. If the `ship` is an initialised object then it's functions
# will be mapped to the CLI's commands. The function's parameters will be
# mapped to command-line arguments.
class Captain:
  # If the `program` keyword is not specified, then it use the basename of
  # `sys.argv[0]`.
  def __init__(
    self,
    ship: object or callable,
    program: str = None,
    *,
    add_help: bool = True,
    compact_help: bool = None,
  ):
    if type(ship) is type:
      raise ParsingError(f"Specified ship '{ship.__name__}' is not initialised")
    self.ship = ship
    self.add_help = add_help
    self.compact_help = compact_help
    if program is None:
      program = os.path.basename(sys.argv[0])
    self.program = program
    self.options = []

  def add_option(self, key: str, flags: list = [], desc: str = ''):
    """Adds an option to the CLI.

    If the `flags` param is not specified then it will use the `key` as
    a flag.

    After parsing you will get an options dictionary where the provided
    `key` will lead to either True (if one of the flags was provided by
    the user) or False (if the user did not specify the option's flag).
    """
    if not flags:
      flags = [key]
    long_flags = []
    short_flags = []
    for flag in flags:
      if len(flag) == 1:
        short_flags.append(flag)
      else:
        long_flags.append(flag)
    option = {
      'key': key,
      'long': long_flags,
      'short': short_flags,
      'desc': desc,
    }
    self.options.append(option)

  @staticmethod
  def _classify_args(args: list[str]) -> tuple[list, list, list]:
    """Categorises arguments.

    Return tuple format: (positional args, long options, short options)
    """
    # Vars
    pos_args = []
    long_opts = []
    short_opts = []
    # Categorising
    for arg in args:
      if arg.startswith('--'):
        long_opts.append(arg.removeprefix('--'))
      if arg.startswith('-'):
        short_opts += list(arg.removeprefix('-')) or ['']
      else:
        pos_args.append(arg)
    # Returning
    return pos_args, long_opts, short_opts

  def _parse_options(
    self,
    long_opts: list[str],
    short_opts: list[str],
  ) -> dict[str: bool]:
    parsed_options = {}
    for option in self.options:
      parsed_options[option.get('key')] = False
    for prefix, flag_type, given_opts in (
      ('--', 'long', long_opts),
      ('-', 'short', short_opts),
    ):
      for given_opt in given_opts:
        found = None
        for option in self.options:
          flags = option.get(flag_type)
          if given_opt in flags:
            found = option
            break
        if found is None:
          self.on_usage_error(f"unrecognised option '{prefix}{given_opt}'")
        else:
          parsed_options[found.get('key')] = True
    return parsed_options

  def parse(self, args: list[str] = sys.argv[1:]) -> tuple:
    """Parses `args`, or sys.argv if `args` is not specified.

    The function's return tuple dependends on the specified `ship` and whether
    any options were added.

    If the specified `ship` was a function then the returned tuple will look
    like `(funtion_args: list,)`. If, however, any options were added, then
    return tuple will be `(funtion_args: list, options: dict)`.

    If the specified `ship` was an initialised object, then the output will
    be `(function: callable, funtion_args: list)`. And, naturally, if any
    options were added then the tuple will look like this
    `(function: callable, funtion_args: list, options: dict)`.
    """
    # Categorising args
    args, long_opts, short_opts = self._classify_args(args)
    # Parsing options and printing help if needed
    if self.add_help:
      self.add_option('help', ['help', 'h'], 'Prints this page')
    parsed_options = self._parse_options(long_opts, short_opts)
    if self.add_help:
      if parsed_options.get('help'):
        self.print_help()
        exit_code = getattr(os, 'EX_OK', 0)
        sys.exit(exit_code)
      parsed_options.pop('help')
    # Getting chosen command
    ship_callable = callable(self.ship)
    if ship_callable:
      function = self.ship
      command = None
    else:
      if not args:
        self.on_usage_error(
          'no command specified.\n'
          f"Try '{self.program} --help' to view available commands."
        )
      commands = get_class_commands(type(self.ship))
      command = args.pop(0)
      function = commands.get(command)
      if not function:
        available_commands = ', '.join(commands.keys())
        self.on_usage_error(
          f"command '{command}' not recognised.\n"
          f'Available commands: {available_commands}'
        )
    # Checking arguments
    required_args, optional_args, arbitrary_arg = get_function_args(function)
    n_required_args = len(required_args)
    n_optional_args = len(optional_args)
    if not ship_callable:
      if not required_args:
        function_name = function.__name__
        class_name = type(self.ship).__name__
        raise ParsingError(
          f"Function '{function_name}' of '{class_name}' is missing "
          "the `self` parameter"
        )
      args.insert(0, self.ship)
    n_args = len(args)
    if n_args < n_required_args:
      self.on_missing_arguments(required_args[n_args:])
    if n_args > n_required_args + n_optional_args and not arbitrary_arg:
      self.on_usage_error('too many arguments.', command)
    # Returning
    return_list = []
    if not ship_callable:
      return_list += [function, args]
    else:
      return_list.append(args)
    if parsed_options:
      return_list.append(parsed_options)
    if len(return_list) == 1:
      return return_list[0]
    return tuple(return_list)

  def print_help(self):
    """Prints the help page."""
    compact = self.compact_help
    ship_callable = callable(self.ship)
    if compact is None:
      compact = True if ship_callable else False
    section_separator = '\n' if compact else '\n\n'
    sections: list[tuple[str|None, str]] = []
    description = self.ship.__doc__
    if ship_callable:
      # Adding usage
      usage = self.program + ' [OPTION]...'
      args = to_posix_args(*get_function_args(self.ship))
      if args:
        usage += ' ' + args
      sections.append(('Usage', usage))
      # Adding description
      sections.append(('Description', description))
    else:
      # Adding description
      sections.append((None, description))
      # Adding synopsis
      synopsys = self.program + ' [OPTION]... COMMAND [ARGS]...'
      sections.append(('Synopsis', synopsys))
      # Adding commands
      commands = get_class_commands(type(self.ship))
      commands_table = {}
      for command, function in commands.items():
        commands_table[command] = function.__doc__
      commands_table = _dict_to_table(commands_table)
      sections.append(('Commands', commands_table))
      # Adding usage
      usage = []
      for command, function in commands.items():
        args = get_function_args(function)
        args[0].pop(0) # Removing the `self` argument
        if not any(args):
          continue
        args = to_posix_args(*args)
        usage.append(f'{self.program} {command} {args}')
      usage = '\n'.join(usage)
      sections.append(('Usage', usage))
    # Adding options
    options = {}
    for option in self.options:
      long_flags = ['--' + flag for flag in option.get('long')]
      short_flags = ['-' + flag for flag in option.get('short')]
      flags = ', '.join(short_flags + long_flags)
      options[flags] = option.get('desc')
    options = _dict_to_table(options)
    sections.append(('Options', options))
    # Assembling sections
    sections = [
      f"{title}:\n  {body.replace('\n', '\n  ')}" if title else body
      for title, body in sections if body
    ]
    # Printing
    print(section_separator.join(sections))

  def on_usage_error(self, message: str, command: str = None):
    """Prints the error message and calls sys.exit with the appropriate exit code."""
    items = [f'{self.program}:']
    if command:
      items.append(f'{command}:')
    items.append(message)
    message = ' '.join(items)
    print(message, file=sys.stderr)
    exit_code = getattr(os, 'EX_USAGE', 64)
    sys.exit(exit_code)

  def on_missing_arguments(self, args: list, command: str = None):
    """Prints the missing arguments and returns the appropriate exit code."""
    n_args = len(args)
    args = to_posix_args(args)
    message = 'missing argument'
    if n_args != 1:
      message += 's'
    message += ': ' + args
    return self.on_usage_error(message, command)
