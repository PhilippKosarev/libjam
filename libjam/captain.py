# Imports
import sys
import os


# Exceptions
class ParsingError(Exception):
  pass


# Internal functions
def categorise_args(all_args: list) -> tuple:
  # Vars
  args = []
  long_opts = []
  short_opts = []
  # Categorising
  for arg in all_args:
    if arg.startswith('--'):
      long_opts.append(arg.removeprefix('--'))
    elif arg.startswith('-'):
      short_opts += list(arg.removeprefix('-'))
    else:
      args.append(arg)
  # Returning
  return args, long_opts, short_opts


def parse_options(
  self,
  long_opts: list,
  short_opts: list,
) -> dict:
  parsed_options = {}
  for option in self.options:
    parsed_options[option.get('key')] = False
  for prefix, key, given_opts in (
    ('--', 'long', long_opts),
    ('-', 'short', short_opts),
  ):
    for given_opt in given_opts:
      found = None
      for option in self.options:
        flags = option.get(key)
        if given_opt in flags:
          found = option
          break
      if found is None:
        self.on_usage_error(f"unrecognised option '{prefix}{given_opt}'")
      else:
        parsed_options[found.get('key')] = True
  return parsed_options


# Returns a list of function parameters.
def get_function_args(function: callable) -> list:
  code = function.__code__
  if code.co_kwonlyargcount:
    raise NotImplementedError(
      'Keyword-only function arguments are not supported.'
    )
  argcount = code.co_argcount
  varnames = list(code.co_varnames)
  args = varnames[:argcount]
  flags = code.co_flags
  if flags & 0x04:
    args.append(varnames[len(args)])
  if argcount < len(args):
    args[argcount] = '*' + args[argcount]
  return args


def function_args_to_posix(input_args: list) -> list:
  output_args = []
  for arg in input_args:
    arg = arg.upper().replace('_', ' ')
    if arg.startswith('*'):
      arg = arg.removeprefix('*')
      arg = f'[{arg}]...'
    else:
      arg = f'<{arg}>'
    output_args.append(arg)
  return output_args


def get_object_methods(obj: object) -> dict:
  commands = {}
  class_dict = obj.__class__.__dict__
  for key in class_dict:
    if key.startswith('_'):
      continue
    function = class_dict.get(key)
    key = key.replace('_', '-')
    commands[key] = function
  return commands


def get_section(title: str, body: str or list or None) -> str:
  if not body:
    return ''
  if type(body) is list:
    body = ['' if i is None else i for i in body]
    if len(body) > 1:
      for i in range(1, len(body), 2):
        if body[i]:
          body[i] = '- ' + body[i]
    body = typewriter.list_to_columns(body, n_columns=2)
  else:
    body = typewriter.list_to_columns([body], n_columns=2)
  return typewriter.bolden(title + ':') + '\n' + body


class Captain:
  def __init__(self, ship: object or callable, *, program: str = None):
    if type(ship) is type:
      raise ParsingError(
        f"Specified object '{ship.__name__}' is not initialised"
      )
    self.ship = ship
    if program is None:
      program = os.path.basename(sys.argv[0])
    self.program = program
    self.options = []

  def add_option(
    self,
    key: str,
    flags: list = None,
    description: str = '',
  ):
    if flags is None:
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
      'description': description,
    }
    self.options.append(option)

  def on_usage_error(self, text: str, command: str = None):
    prefix = self.program + ':'
    if command:
      prefix += ' ' + command + ':'
    print(prefix + ' ' + text, file=sys.stderr)
    sys.exit(os.EX_USAGE)

  def on_missing_arguments(self, missing_args: str, command: str = None):
    missing_args = function_args_to_posix(missing_args)
    if len(missing_args) == 1:
      self.on_usage_error(f'missing argument {missing_args[0]}', command)
    missing_args = ' '.join(missing_args)
    self.on_usage_error(f'missing arguments {missing_args}', command)

  def print_help(self):
    # Initialising typewriter
    from .typewriter import Typewriter

    global typewriter
    typewriter = Typewriter()
    # Sections
    sections = []
    ship_callable = callable(self.ship)
    # Usage
    if not ship_callable:
      commands = get_object_methods(self.ship)
      usage_body = []
      for command in commands:
        command_args = get_function_args(commands.get(command))[1:]
        command_args = ' '.join(function_args_to_posix(command_args))
        usage_body.append(f'{self.program} {command} {command_args}')
      sections.append(get_section('Usage', '\n  '.join(usage_body)))
    # Synopsys
    if ship_callable:
      function_args = get_function_args(self.ship)
      posix_args = ' '.join(function_args_to_posix(function_args))
      sections.append(
        get_section('Synopsis', f'{self.program} [OPTION]... {posix_args}')
      )
    else:
      sections.append(
        get_section('Synopsis', f'{self.program} [OPTION]... COMMAND [ARGS]...')
      )
    doc = self.ship.__doc__
    if doc:
      sections.append(get_section('Description', doc + '.'))
    # Commands
    if not ship_callable:
      commands_body = []
      for key in commands:
        commands_body.append(key)
        commands_body.append(commands.get(key).__doc__ + '.')
      sections.append(
        get_section('Commands', commands_body),
      )
    # Options
    options_body = []
    for option in self.options:
      long = ['--' + string for string in option.get('long')]
      short = ['-' + string for string in option.get('short')]
      flags = ', '.join(short + long)
      options_body.append(flags)
      options_body.append(option.get('description') + '.')
    sections.append(
      get_section('Options', options_body),
    )
    # Removing empty sections
    sections = [section for section in sections if section]
    # Printing
    print('\n'.join(sections))

  def parse(
    self,
    args: list = None,
    *,
    add_help: bool = True,
  ) -> tuple:
    # Retrieving args
    if args is None:
      args = sys.argv[1:]
    # Categorising args
    given_args, long_opts, short_opts = categorise_args(args)
    # Parsing options and printing help if needed
    if add_help:
      self.add_option(
        'help',
        ['help', 'h'],
        'Prints this page',
      )
    parsed_options = parse_options(self, long_opts, short_opts)
    if add_help:
      if parsed_options.get('help'):
        self.print_help()
        sys.exit(os.EX_OK)
      parsed_options.pop('help')
    # Getting chosen function
    ship_callable = callable(self.ship)
    if ship_callable:
      function = self.ship
      command = None
    else:
      if not given_args:
        self.on_usage_error(
          'No command specified.\n'
          f"Try '{self.program} --help' for more information."
        )
      available_commands = get_object_methods(self.ship)
      command = given_args.pop(0)
      function = available_commands.get(command)
      available_commands = ', '.join(available_commands.keys())
      if function is None:
        self.on_usage_error(
          f"command '{command}' not recognised.\n"
          f'Available commands: {available_commands}'
        )
    # Checking arguments
    required_args = get_function_args(function)
    n_required_args = len(required_args)
    if not ship_callable:
      if n_required_args == 0:
        function_name = function.__name__
        class_name = self.ship.__class__.__name__
        raise ParsingError(
          f"Function '{function_name}' of '{class_name}' is missing the 'self' parameter"
        )
      given_args.insert(0, self.ship)
    n_given_args = len(given_args)
    if n_required_args > 0:
      arbitrary_args = required_args[-1][0] == '*'
    else:
      arbitrary_args = False
    if not arbitrary_args:
      if n_given_args != n_required_args:
        if n_given_args > n_required_args:
          self.on_usage_error('too many arguments.', command)
        elif n_given_args < n_required_args:
          self.on_missing_arguments(required_args[n_given_args:])
    # Returning
    return_list = []
    if not ship_callable:
      return_list += [function, given_args]
    else:
      return_list.append(given_args)
    if parsed_options:
      return_list.append(parsed_options)
    if len(return_list) == 1:
      return return_list[0]
    return tuple(return_list)
