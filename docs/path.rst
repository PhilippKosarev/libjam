Path
====

API
---

.. autoclass:: libjam.Path


Example CLI for extracting archives
-----------------------------------

``extract.py`` file:

.. code-block::

  #! /usr/bin/env python3

  # Imports
  from libjam import Captain, writer, Path
  import sys

  # Main function
  def extract(archive: str, out_directory: str):
    archive = Path(archive)
    out_directory = Path(out_directory)
    # Validating input
    if not archive.exists():
      captain.on_usage_error('file not found.')
    if not archive.is_file():
      captain.on_usage_error('given archive is not a file.')
    if not archive.can_unpack():
      captain.on_usage_error('unsupported archive type.')
    # Extracting
    with writer.ProgressBar(f"Extracting '{archive.name}'") as bar:
      archive.unpack_with_progress(out_directory, bar.update)

  # Running
  def main():
    captain = Captain(extract)
    args = captain.parse()
    return extract(*args)

  if __name__ == '__main__':
    sys.exit(main())
