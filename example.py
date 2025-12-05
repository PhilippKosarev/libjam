#!/usr/bin/env python3

from libjam import Captain

class CLI:
  'An example CLI for the libjam library'
  def shout(self, *text):
    'Shouts the given text back'
    text = ' '.join(text)
    if options.get('world'):
      text += ' world'
    print(text + '!')

cli = CLI()
captain = Captain(cli)
captain.add_option(
  'world', ['world', 'w'],
  "Adds ' world' before the exclamation mark",
)
global options
function, args, options = captain.parse()
function(*args)
