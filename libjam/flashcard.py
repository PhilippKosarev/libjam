"""Used for getting user input inside the terminal."""

# Importing readline if available for a better input() experience
try:
  import readline as readline
except ModuleNotFoundError:
  pass

# Internal imports
from . import typewriter


def yn_prompt(question: str) -> bool:
  while True:
    user_input = input(f'{question} [y/n]: ')
    user_input = user_input.strip().lower()
    if user_input in ('y', 'yes'):
      return True
    elif user_input in ('n', 'no'):
      return False


def choose(
  prompt: str,
  items: list[str],
  *prompt_styles: typewriter.Style
  or typewriter.Colour
  or typewriter.BackgroundColour,
) -> str:
  n_items = len(items)
  # Creating the prompt
  prompt = f'{prompt} (1-{n_items}, 0 to abort):'
  for style in prompt_styles:
    prompt = typewriter.stylise(style, prompt)
  prompt += ' '
  # Printing available items
  printable_items = []
  for i, item in enumerate(items, start=1):
    printable_items.append(f'{i}) {item}')
  printable_items = typewriter.list_to_columns(printable_items, spacing=2)
  print(printable_items + '\n')
  # Getting user input
  while True:
    choice = input(prompt).strip()
    if choice == '0':
      return None
    elif choice in [str(n) for n in range(1, n_items + 1)]:
      return items[int(choice) - 1]
    elif choice in items:
      return choice
