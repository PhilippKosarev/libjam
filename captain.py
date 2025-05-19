# Imports
import sys, re, inspect
from .typewriter import Typewriter
from .clipboard import Clipboard
typewriter = Typewriter()
clipboard = Clipboard()

# Processes command line arguments
class Captain:

  # Returns a generated a help page based on provided inputs
  def generate_help(self, app, description, commands, options):
    offset = 2; offset_string = "".ljust(offset)
    commands_list = []
    for command in commands:
      command_desc = commands.get(command).get('description')
      commands_list.append(f"{command}")
      commands_list.append(f"- {command_desc}")
    commands_list.append("help")
    commands_list.append("- Prints this page")
    commands_string = typewriter.list_to_columns(commands_list, 2, offset)
    options_list = []
    for option in options:
      option_desc = options.get(option).get('description')
      long = ', --'.join(options.get(option).get('long'))
      short = ', -'.join(options.get(option).get('short'))
      options_list.append(f"-{short}, --{long}")
      options_list.append(f"- {option_desc}")
    options_string = typewriter.list_to_columns(options_list, 2, offset)
    help = f'''{typewriter.bolden('Description:')}
{offset_string}{description}
{typewriter.bolden('Synopsis:')}
{offset_string}{app} [OPTIONS] [COMMAND]
{typewriter.bolden('Commands:')}
{commands_string.rstrip()}
{typewriter.bolden('Options:')}
{options_string.rstrip()}'''
    return help


  # Interprets input arguments
  def interpret(self, app, help, commands, arguments, options):
    # Class vars
    self.command = None
    self.function = None
    self.arbitrary_args = False
    self.required_args = 0
    self.command_args = []

    # Creating option bools
    self.option_values = {}
    for option in options:
      name = options.get(option).get('option')
      self.option_values[name] = False

    # Parsing arguments
    for argument in arguments:
      if argument.startswith("-"):
        self.arg_found = False
        # Long options
        if argument.startswith("--"):
          argument = argument.removeprefix("--")
          for option in options:
            strings = options.get(option).get('long')
            if clipboard.is_string_in_list(strings, argument):
              option_dict = options.get(option).get('option')
              option_value = self.option_values[option_dict] = True
              self.arg_found = True
          if self.arg_found is False:
            print(f"Option '{argument}' unrecognized. Try {app} help")
            sys.exit(-1)

        # Short options
        else:
          argument = argument.removeprefix("-")
          arguments = list(argument)
          for argument in arguments:
            command_found = False
            for option in options:
              strings = options.get(option).get('short')
              if clipboard.is_string_in_list(strings, argument):
                option_dict = options.get(option).get('option')
                option_value = self.option_values[option_dict] = True
                command_found = True
          if command_found is False:
            print(f"Option '{argument}' unrecognized. Try {app} help")
            sys.exit(-1)

      # Commands
      else:
        if self.command is None:
          for command in commands:
            if command == argument:
              self.command = command
              command_function = commands.get(command).get('function')
              command_args = inspect.signature(command_function)
              command_args = command_args.format().replace('(', '').replace(')', '').replace(' ', '')
              command_args = command_args.split(',')
              if clipboard.is_string_in_list(command_args, '*args'):
                command_args.remove('*args')
                self.arbitrary_args = True
              if command_args == ['']:
                command_args = []
              self.required_args = len(command_args)
            elif argument == 'help':
              print(help)
              sys.exit(0)
          if self.command is None:
            print(f"Command '{argument}' unrecognized. Try {app} help")
            sys.exit(-1)

        # Command arguments
        else:
          if self.arbitrary_args is False:
            if self.required_args == 0:
              print(f"Command '{self.command}' does not take arguments.")
              sys.exit(-1)
            elif len(self.command_args) >= self.required_args:
              s = ''
              if self.required_args > 1: s = 's'
              print(f"Command '{self.command}' requires only {self.required_args} argument{s}.")
              sys.exit(-1)
          self.command_args.append(argument)
    if self.arbitrary_args is False and self.required_args > len(self.command_args):
      print(f"Command '{self.command}' requires {self.required_args} arguments.")
      sys.exit(-1)

    # Checking if command is specified
    if self.command is None:
        print(f"No command specified. Try {app} help")
        sys.exit(0)

    function = commands.get(self.command).get('function')
    function = function(*self.command_args)

    return {'function': function, 'options': self.option_values}
