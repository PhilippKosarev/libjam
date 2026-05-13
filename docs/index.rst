https://github.com/philippkosarev/libjam

libjam
======

A Python library that makes it easier to create better CLIs and provides some missing pieces for file management.

Here is a quick overview of what each module/class does:

- The :doc:`captain` class provides a boilerplate-free way of creating CLIs.
- The :doc:`secretary` class is just another program configuration system.
- The :doc:`writer` module makes it easy to format and style your terminal output.
- The :doc:`flashcard` module has a few functions for getting user input in the terminal.
- The :doc:`drawer` module provides some missing file-management pieces.
- The :doc:`path` class is an extension of ``pathlib.Path`` with :doc:`drawer`'s functionality.


Installing
----------

libjam is available on `PyPi <https://pypi.org/project/libjam/>`_ and can be installed using pip:

.. code-block:: sh

  pip install libjam


API Overview
------------
.. toctree::

  captain
  secretary
  writer
  flashcard
  drawer
  path
