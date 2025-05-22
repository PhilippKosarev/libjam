# Imports
import shutil

# Responsible for formatting, modification and printing of strings
class Typewriter:
  def __init__(self):
    # Shorthand vars
    self.BOLD = '\033[1m'
    self.NORMAL = '\033[0m'
    self.CLEAR = '\x1b[2K'
    self.CURSOR_UP = '\033[1A'

  # Gets a string, makes it bold, returns the string
  def bolden(self, text: str):
    text = f'{self.BOLD}{text}{self.NORMAL}'
    return text

  # Clears a given number of lines in the terminal
  # if given 0 the current line will be erased
  def clear_lines(self, lines: int):
    if lines == 0:
      print("\r" + self.CLEAR, end='')
      return
    for line in range(lines):
      print(self.CURSOR_UP + self.CLEAR, end='')

  # Clears current line to print a new one.
  # Usecase: after typewriter.print_status()
  def print(self, text: str):
    self.clear_lines(0)
    print(text)

  # Prints on the same line
  def print_status(self, status: str):
    self.clear_lines(0)
    print(f" {status}", end='\r')

  # Prints on the same line
  def print_progress(self, status: str, current: int, total: int):
    width = 25
    progress_float= (current / total)
    percent = int(round((progress_float* 100), 0))
    percent_string = str(percent)
    if percent < 100:
      percent_string = ' ' + percent_string
    if percent < 10:
      percent_string = ' ' + percent_string
    progress_width = int(progress_float * width)
    progress_bar = '=' * progress_width + ' ' * (width - progress_width)
    self.print_status(f"{percent_string}% [{progress_bar}] {status}: {current}/{total}")

  # Given a list, it returns a string with the elements of the given list
  # arranged in in columns
  def list_to_columns(self, text_list: list, columns = None, offset = 2):
    column_width = len(max(text_list, key=len))
    # Automatically set num of columns if not specified otherwise
    if columns is None:
      terminal_width = shutil.get_terminal_size()[0] - 1
      columns = int(terminal_width / (column_width + offset))
      if columns < 1: columns = 1
    output = ""
    iteration = 1
    for item in text_list:
      spaces = column_width - len(item)
      end = "".ljust(spaces)
      offset_string = "".ljust(offset)
      if iteration % columns == 0 or iteration == len(text_list):
        end = "\n"
      output += f"{offset_string}{item}{end}"
      iteration += 1
    return output

    columns = []
