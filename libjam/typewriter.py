# Imports
import shutil


# Responsible for formatting, modification and printing of strings.
class Typewriter:
  # Shorthand vars
  BOLD = '\033[1m'
  NORMAL = '\033[0m'
  CLEAR = '\x1b[2K'
  CURSOR_UP = '\033[1A'

  # Gets a string, makes it bold, returns the string.
  def bolden(self, *args):
    args = [f'{self.BOLD}{text}{self.NORMAL}' for text in args]
    n_args = len(args)
    if n_args == 0:
      return ''
    elif n_args == 1:
      return args[0]
    else:
      return tuple(args)

  # Returns current terminal width and height (columns and lines) as a tuple.
  def get_terminal_size(self) -> tuple:
    size = shutil.get_terminal_size()
    return (size[0], size[1])

  # Clears a given number of lines in the terminal.
  # If the specified number of lines is 0 then the current line will be erased.
  def clear_lines(self, lines: int):
    if lines == 0:
      print('\r' + self.CLEAR, end='')
      return
    for line in range(lines):
      print(self.CLEAR, end=self.CURSOR_UP)

  # Clears current line to print a new one.
  # Common usecase: after typewriter.print_status()
  def print(self, *args, **kwargs):
    self.clear_lines(0)
    print(*args, **kwargs)

  # Prints on the same line.
  def print_status(self, *args, **kwargs):
    if 'end' in kwargs:
      kwargs['end'] += '\r'
    else:
      kwargs['end'] = '\r'
    self.clear_lines(0)
    print('', *args, **kwargs)

  # Clears the current line and prints the progress bar on the same line.
  def print_progress(self, status: str, current: int, total: int):
    width = 25
    progress_float = current / total
    percent = int(round((progress_float * 100), 0))
    percent_string = str(percent)
    if percent < 100:
      percent_string = ' ' + percent_string
    if percent < 10:
      percent_string = ' ' + percent_string
    progress_width = int(progress_float * width)
    progress_bar = '=' * progress_width + ' ' * (width - progress_width)
    self.print_status(
      f'{percent_string}% [{progress_bar}] {status}: {current}/{total}'
    )

  # Given a list, it returns a string with the elements of the given list
  # arranged in in columns.
  def list_to_columns(
    self,
    text_list: list,
    num_of_columns: int = 0,
    offset: int = 2,
  ) -> str:
    if len(text_list) == 0:
      return ''
    column_width = len(max(text_list, key=len))
    # Automatically set num of columns if not specified otherwise
    if num_of_columns == 0:
      terminal_width = shutil.get_terminal_size()[0] - 1
      num_of_columns = int(terminal_width / (column_width + offset))
      if num_of_columns < 1:
        num_of_columns = 1
    # Creating a list of columns
    columns = []
    iteration = 0
    for item in text_list:
      current_column = iteration % num_of_columns
      if len(columns) <= current_column:
        columns.append([])
      columns[current_column].append(item)
      iteration += 1
    # Equalising width of columns
    current_column = 0
    for column in columns:
      column_width = 0
      # Getting column width
      for text in column:
        if len(text) > column_width:
          column_width = len(text)
      # Adding spaces
      current_text = 0
      for text in column:
        if current_column == len(columns) - 1:
          spaces = ''
        else:
          spaces = ' ' * ((column_width - len(text)) + 1)
        columns[current_column][current_text] = text + spaces
        current_text += 1
      current_column += 1
    # Adding offset
    iteration = 0
    for text in columns[0]:
      columns[0][iteration] = ' ' * offset + text
      iteration += 1
    # Adding newlines
    last_column = len(columns) - 1
    iteration = 0
    for text in columns[last_column]:
      columns[last_column][iteration] = text
      iteration += 1
    # Creating list of rows
    rows = []
    for row in range(len(columns[0])):
      rows.append([])
    current_row = 0
    for row in rows:
      current_column = 0
      for column in columns:
        try:
          text = columns[current_column][current_row]
        except IndexError:
          continue
        rows[current_row].append(text)
        current_column += 1
      current_row += 1
    # Adding rows' text to output
    output = ''
    for row in rows:
      text = ' '.join(row)
      if text.count('\n') > 0:
        text = text.replace('\n', '\n' + (' ' * offset * 2))
      output += text + '\n'
    # Returning string
    return output.rstrip()
