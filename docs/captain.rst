Captain
=======

API
---

.. autoclass:: libjam.Captain


Simple example
--------------

``example.py`` file:

.. code-block::

  from libjam import Captain

  def shout(text: str):
    'Shouts the given text back'
    if opts.get('world'):
      text += ' world'
    print(text + '!')

  captain = Captain(shout, program='shout')
  captain.add_option(
    'world', ['world', 'w'],
    "Adds ' world' before the exclamation mark",
  )
  global opts
  args, opts = captain.parse()
  shout(*args)


Here is what the user will see when running this CLI:

.. code-block::

  $ ./example.py
  shout: missing argument <TEXT>

  $ ./example.py Hello
  Hello!

  $ ./example.py Hello --world
  Hello world!

  $ ./example.py --help
  Usage:
    shout [OPTION]... <TEXT>
  Description:
    Shouts the given text back
  Options:
    -w, --world - Adds ' world' before the exclamation mark
    -h, --help  - Prints this page
