# Imports
import sys

# Internal imports
from .drawer import Drawer
from .typewriter import Typewriter

drawer = Drawer()
typewriter = Typewriter()


# Custom exceptions
class EmptyShortFlagError(Exception):
  pass


class EmptyLongFlagError(Exception):
  pass


# Helper functions
def get_input_args() -> list:
  args = sys.argv.copy()
  script = drawer.get_basename(args[0])
  args.pop(0)
  return script, args


def parse_args(raw_args: list) -> tuple:
  # Initialising vars
  command = None
  command_args = []
  long_flags = []
  short_flags = []
  # Categorising args
  for arg in raw_args:
    if arg.startswith('--'):
      arg = arg.removeprefix('--')
      if arg == '':
        raise EmptyLongFlagError()
      long_flags += arg.split()
    elif arg.startswith('-'):
      arg = arg.removeprefix('-')
      if arg == '':
        raise EmptyShortFlagError()
      short_flags += arg.split()
    else:
      if command is None:
        command = arg
      else:
        command_args.append(arg)
  return (command, command_args, long_flags, short_flags)


# Generates the help pages.
class Helper:
  @classmethod
  def get_help_section(cls, title: str, content: str or list) -> str:
    offset = 2
    offset_string = ' ' * offset
    section = f'{typewriter.bolden(title + ":")}\n'
    if type(content) is str:
      content = content.replace('\n', '\n' + offset_string)
      section += f'{offset_string}{content}\n'
    elif type(content) is list:
      columns = 2
      section += typewriter.list_to_columns(content, columns, offset) + '\n'
    else:
      raise NotImplementedError()
    return section

  @classmethod
  def sections_to_help(cls, sections: list) -> str:
    help = ''
    for title, content in sections:
      help += cls.get_help_section(title, content)
    help = help.rstrip()
    return help

  # Prints the help page for a specific command.
  @classmethod
  def print_command_help(
    cls,
    script: str,
    command: str,
    command_info: dict,
  ):
    sections = [
      ('Synopsis', f'{script} {command} [OPTIONS]'),
      ('Description', command_info.get('description')),
    ]
    print(cls.sections_to_help(sections))

  # Returns a help page for a CLI program.
  @classmethod
  def generate_help(
    cls, description: str, commands: dict, options: dict = None
  ) -> str:
    # Getting info
    script, _ = get_input_args()
    commands_list = []
    for command in commands:
      command_desc = commands.get(command).get('description')
      commands_list.append(f'{command}')
      commands_list.append(f'- {command_desc}')
    commands_list.append('help')
    commands_list.append('- Prints this page.')
    # Sections
    sections = [
      ('Synopsis', f'{script} [OPTIONS] [COMMAND]'),
      ('Description', description),
      ('Commands', commands_list),
    ]
    # Adding options
    if options is not None:
      options_list = []
      for option in options:
        option_desc = options.get(option).get('description')
        long = ', --'.join(options.get(option).get('long'))
        short = ', -'.join(options.get(option).get('short'))
        options_list.append(f'-{short}, --{long}')
        options_list.append(f'- {option_desc}')
      option_section = ('Options', options_list)
      sections.append(option_section)
    # Returning
    return cls.sections_to_help(sections)


# Processes command line arguments.
class Captain:
  # See the example in the readme for proper info.
  @staticmethod
  def sail(
    description: str,
    commands: dict,
    options: dict = None,
    arguments: list = None,
  ) -> dict:
    # Processing arguments
    if arguments is None:
      script, arguments = get_input_args()
    try:
      command, command_args, long_flags, short_flags = parse_args(arguments)
    except EmptyLongFlagError:
      print(f"Invalid option '--'. Try {script} help")
      sys.exit(-1)
    except EmptyShortFlagError:
      print(f"Invalid option '-'. Try {script} help")
      sys.exit(-1)
    # Processing command
    if command is None:
      print(f'No command specified. Try {script} help')
      sys.exit(0)
    elif command == 'help':
      help = Helper.generate_help(description, commands, options)
      print(help)
      sys.exit(0)
    elif command not in commands:
      print(f"""\
Command '{command}' not recognised.
Available commands: {', '.join(commands)}\
      """)
      sys.exit(-1)
    command_info = commands.get(command)
    # Creating options
    if options is not None:
      processed_options = {}
      for option in options:
        processed_options[option] = False
    # Processing flags
    ## Long flags
    for flag in long_flags:
      if options is None:
        print(f"Option '--{flag}' not recognised. Try {script} help")
        sys.exit(-1)
      for option in options:
        option_flags = options.get(option).get('long')
        if flag == 'help':
          Helper.print_command_help(script, command, command_info)
          sys.exit(0)
        elif flag not in option_flags:
          print(f"Option '--{flag}' not recognised. Try {script} help")
          sys.exit(-1)
        processed_options[option] = True
    ## Short flags
    for flag in short_flags:
      if options is None:
        print(f"Option '-{flag}' not recognised. Try {script} help")
        sys.exit(-1)
      for option in options:
        option_flags = options.get(option).get('short')
        if flag == 'h':
          Helper.print_command_help(script, command, command_info)
          sys.exit(0)
        elif flag not in option_flags:
          print(f"Option '-{flag}' not recognised. Try {script} help")
          sys.exit(-1)
        processed_options[option] = True
    # Returning
    command_function = command_info.get('function')
    if options is None:
      return command_function, command_args
    else:
      return command_function, command_args, processed_options
