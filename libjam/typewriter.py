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
  def print_progress(
    self,
    status: str,
    done: int,
    todo: int,
    max_bar_width: int = 50,
    symbols: str = '[=]',
  ):
    # Getting maximum bar width
    min_width = len(f' 000% {symbols[0]}{symbols[2]} {status}: {todo}/{todo}')
    end_padding = 2
    bar_width = self.get_terminal_size()[0] - min_width - end_padding
    if bar_width > max_bar_width:
      bar_width = max_bar_width
    # Calculating stuffs
    progress_float = done / todo
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
    self.print_status(result)

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
