"""Provides functionality for making fancy terminal output."""

# Imports
import os

# Constants
ESC = '\x1B['


# General control codes (C0)
class ControlCode(str):
  """A string that prints itself when called."""
  def __call__(self, file=None, flush=False):
    print(self, end='', file=file, flush=flush)


bell = ControlCode('\a')
back = ControlCode('\b')
home = ControlCode('\r')
tab = ControlCode('\t')


# Navigation sequences (CSI commands)
class NavigationSequence(str):
  def __new__(cls, char: str):
    new = str.__new__(cls, f'{ESC}1{char}')
    new._char = char
    return new

  def __call__(self, n: int = 1, file=None, flush=False) -> str:
    print(f'{ESC}{n}{self._char}', end='', file=file, flush=flush)


up = NavigationSequence('A')
down = NavigationSequence('B')
right = NavigationSequence('C')
left = NavigationSequence('D')
next_line = NavigationSequence('E')
prev_line = NavigationSequence('F')
view_up = NavigationSequence('S')
view_down = NavigationSequence('T')


# Clear sequences (CSI commands)
class ClearSequence(ControlCode):
  """A string that clears some part of the screen."""
  def __new__(cls, char: str, n: int):
    return str.__new__(cls, f'{ESC}{n}{char}')

  def __call__(self, file=None, flush=False):
    print(self, end='', file=file, flush=flush)


clear_page_after_cursor = ClearSequence('J', 0)
clear_page_before_cursor = ClearSequence('J', 1)
clear_page = ClearSequence('J', 2)
clear_history = ClearSequence('J', 3)
clear_line_after_cursor = ClearSequence('K', 0)
clear_line_before_cursor = ClearSequence('K', 1)
clear_line = ClearSequence('K', 2)


# Style sequences (SGR)
class Style(str):
  def __new__(cls, start, end = ''):
    start = f'{ESC}{start}m'
    if end:
      end = f'{ESC}{end}m'
    new = str.__new__(cls, start)
    new._end = end
    return new

  def __add__(self, seq: Style) -> Style:
    start = f"{self}{seq}"
    end = f"{self._end}{seq}"
    new = str.__new__(Style, start)
    new._end = end
    return new

  def __call__(self, s) -> str:
    return f'{self}{s}{self._end}'


# Typographic styles
reset = Style(0, 0)
bold = Style(1, 22)
dim = Style(2, 22)
italic = Style(3, 23)
underline = Style(4, 24)
blink = Style(5, 25)
invert = Style(7, 27)
hide = Style(8, 28)
strike = Style(9, 29)
# Regular colours
default = Style(39, 39)
black = Style(30, 39)
red = Style(31, 39)
green = Style(32, 39)
yellow = Style(33, 39)
blue = Style(34, 39)
purple = Style(35, 39)
cyan = Style(36, 39)
white = Style(37, 39)
# Regular background colours
on_default = Style(49, 49)
on_black = Style(40, 49)
on_red = Style(41, 49)
on_green = Style(42, 49)
on_yellow = Style(43, 49)
on_blue = Style(44, 49)
on_purple = Style(45, 49)
on_cyan = Style(46, 49)
on_white = Style(47, 49)
# Bright colours
bright_black = Style(90, 39)
bright_red = Style(91, 39)
bright_green = Style(92, 39)
bright_yellow = Style(93, 39)
bright_blue = Style(94, 39)
bright_purple = Style(95, 39)
bright_cyan = Style(96, 39)
bright_white = Style(97, 39)
# Bright background colours
on_bright_black = Style(100, 49)
on_bright_red = Style(101, 49)
on_bright_green = Style(102, 49)
on_bright_yellow = Style(103, 49)
on_bright_blue = Style(104, 49)
on_bright_purple = Style(105, 49)
on_bright_cyan = Style(106, 49)
on_bright_white = Style(107, 49)


def rgb(r: int, g: int, b: int) -> Style:
  """Creates a colour Style for given rgb values."""
  return Style(f'38;2;{r};{g};{b}', 39)


def on_rgb(r: int, g: int, b: int) -> Style:
  """Creates a background colour Style for given rgb values."""
  return Style(f'48;2;{r};{g};{b}', 49)


# Clears a given number of lines in the terminal.
def clear_lines(n_lines: int, file=None, flush=False):
  buff = [clear_line for _ in range(n_lines)]
  buff = up.join(buff)
  print(buff, end='', file=file, flush=flush)


# Prints on the same line.
def print_status(status: str, file=None, flush=False):
  print(f'{clear_line} {status}\r', end='', file=file, flush=flush)


# Clears the current line and prints the progress bar on the same line.
def print_progress(
  status: str,
  done: int,
  todo: int,
  max_bar_width: int = 50,
  symbols: str = '[=]',
):
  # Getting maximum bar width
  min_width = len(f' 000% {symbols[0]}{symbols[2]} {status}: {todo}/{todo}')
  end_padding = 5
  bar_width = os.get_terminal_size()[0] - min_width - end_padding
  if bar_width > max_bar_width:
    bar_width = max_bar_width
  # Calculating stuffs
  progress_float = done / todo
  if progress_float > 1:
    progress_float = 1
  percentage = str(int(progress_float * 100))
  percentage = percentage + '%' + (' ' * (3 - len(percentage)))
  # Outputting
  result = f' {percentage}'
  if bar_width > 5:
    bar = symbols[1] * int(progress_float * bar_width)
    bar += ' ' * (bar_width - len(bar))
    bar = symbols[0] + bar + symbols[2]
    result += f' {bar}'
  result += f' {status}:'
  todo, done = str(todo), str(done)
  done = done + (' ' * (len(todo) - len(done)))
  result += f' {done}/{todo}'
  print_status(result)


# Returns a string with elements of the list arranged in in columns.
def list_to_columns(
  text_list: list,
  n_columns: int = 0,
  offset: int = 2,
  spacing: int = 1,
) -> str:
  text_list_len = len(text_list)
  if text_list_len == 0:
    return ''
  text_list = [str(text) for text in text_list]
  sorted_text_list = sorted(text_list, key=len, reverse=True)
  # Getting n_columns
  if n_columns == 0:
    available_width = os.get_terminal_size()[0] - offset
    counter = 0
    while True:
      texts = sorted_text_list[:counter]
      if counter == text_list_len:
        n_columns = counter
        break
      if len((' ' * spacing).join(texts)) > available_width:
        n_columns = counter - 1
        break
      counter += 1
    if n_columns < 1:
      n_columns = 1
  columns_range = range(n_columns)
  # Getting columns
  columns = [[] for i in columns_range]
  for i in columns_range:
    columns[i] += text_list[i::n_columns]
  columns = [column for column in columns if len(column) > 0]
  # Getting column widths
  column_widths = []
  for column in columns:
    column_widths.append(len(sorted(column, key=len, reverse=True)[0]))
  # Combining rows to string
  n_rows = len(columns[0])
  strings = []
  for i in range(n_rows):
    start = n_columns * i
    end = start + n_columns
    row = text_list[start:end]
    # Equalising row width
    for i in range(len(row)):
      row[i] += ' ' * (column_widths[i] - len(row[i]))
    strings.append(' ' * offset + (' ' * spacing).join(row))
  return '\n'.join(strings)
