"""Provides useful formatting and printing functions."""

# Imports
from __future__ import annotations
from enum import Enum
import os

# Shorthand vars
CLEAR = '\x1b[2K'
CURSOR_UP = '\033[1A'


# Helper functions
def escape_seq(text: str):
  return f'\033[{text}m'


class Style(Enum):
  RESET = escape_seq(0)
  INVERT = escape_seq(7)
  BOLD = escape_seq(1)
  UNDERLINE = escape_seq(4)
  OVERLINE = escape_seq(53)
  BLINKING = escape_seq(5)
  HIDDEN = escape_seq(8)
  THROUGHLINE = escape_seq(9)


class Colour(Enum):
  DEFAULT = escape_seq(39)
  WHITE = escape_seq(37)
  BLACK = escape_seq(30)
  RED = escape_seq(31)
  GREEN = escape_seq(32)
  BLUE = escape_seq(34)
  MAGENTA = escape_seq(35)
  YELLOW = escape_seq(33)
  CYAN = escape_seq(36)
  BRIGHT_WHITE = escape_seq(97)
  BRIGHT_BLACK = escape_seq(90)
  BRIGHT_RED = escape_seq(91)
  BRIGHT_GREEN = escape_seq(92)
  BRIGHT_BLUE = escape_seq(94)
  BRIGHT_MAGENTA = escape_seq(95)
  BRIGHT_YELLOW = escape_seq(93)
  BRIGHT_CYAN = escape_seq(96)


class BackgroundColour(Enum):
  DEFAULT = escape_seq(49)
  WHITE = escape_seq(47)
  BLACK = escape_seq(40)
  RED = escape_seq(41)
  GREEN = escape_seq(42)
  BLUE = escape_seq(44)
  MAGENTA = escape_seq(45)
  YELLOW = escape_seq(43)
  CYAN = escape_seq(46)
  BRIGHT_WHITE = escape_seq(107)
  BRIGHT_BLACK = escape_seq(100)
  BRIGHT_RED = escape_seq(101)
  BRIGHT_GREEN = escape_seq(102)
  BRIGHT_BLUE = escape_seq(104)
  BRIGHT_MAGENTA = escape_seq(105)
  BRIGHT_YELLOW = escape_seq(103)
  BRIGHT_CYAN = escape_seq(106)


# Applies a specified style to a string(s).
def stylise(
  style: Style or Colour or BackgroundColour,
  *text,
):
  if len(text) == 0:
    return ''
  text = [f'{style.value}{text}{Style.RESET.value}' for text in text]
  n_texts = len(text)
  if n_texts == 1:
    return text[0]
  else:
    return tuple(text)


# Gets a string, makes it bold, returns the string.
def bolden(*text):
  return stylise(Style.BOLD, *text)


# # Gets a string, underlines it, returns the string.
def underline(*text):
  return stylise(Style.UNDERLINE, *text)


# Gets RGB values, returns escape sequence to print with that colour in the terminal.
def rgb_to_escape_sequence(red: int, green: int, blue: int) -> str:
  return escape_seq(f'38;2;{red};{green};{blue}')


# Clears a given number of lines in the terminal.
# If the specified number of lines is 0 then the current line will be erased.
def clear_lines(lines: int):
  if lines == 0:
    print('\r' + CLEAR, end='')
    return
  for line in range(lines):
    print(CLEAR, end=CURSOR_UP)


# Prints on the same line.
def print_status(*args, **kwargs):
  kwargs.setdefault('end', '\r')
  clear_lines(0)
  print('', *args, **kwargs)


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
