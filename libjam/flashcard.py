"""Used for getting user input inside the terminal."""

# Importing readline if available for a better input() experience
try:
  import readline as readline
except ModuleNotFoundError:
  pass

# Internal imports
from . import typewriter


def yn_prompt(prompt: str, prompt_style: typewriter.Style or callable = None) -> bool:
  prompt = '{prompt} [y/n]: '
  if prompt_style:
    prompt = prompt_style(prompt)
  while True:
    user_input = input(prompt).strip().lower()
    if user_input in ('y', 'yes'):
      return True
    elif user_input in ('n', 'no'):
      return False


def choose(
  prompt: str,
  items: list[str],
  prompt_style: typewriter.Style or callable = typewriter.bold,
) -> str or None:
  # Creating the prompt
  n_items = len(items)
  prompt = '{prompt} (1-{n_items}, 0 to abort): '
  if prompt_style:
    prompt_style(prompt)
  # Printing available items
  items = [f'{i}) {item}' for i, item in enumerate(items, start=1)]
  items = typewriter.to_columns(items)
  print(items + '\n')
  # Getting user input
  while True:
    choice = input(prompt).strip()
    if choice == '0':
      return None
    elif choice in [str(n) for n in range(1, n_items + 1)]:
      return items[int(choice) - 1]
    elif choice in items:
      return choice
