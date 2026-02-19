"""Provides a few missing pieces for file management."""

# Imports
import os
import io
import sys
import math
import shutil
import filetype
import subprocess


# An internal function.
def _get_extract_functions() -> dict[str:callable]:
  """Returns a dict where the file extension points to a function."""
  from .extract_functions import (
    extract_zip,
    extract_rar,
    extract_tar,
    extract_tar_gz,
    extract_tar_xz,
    extract_7z,
  )

  extract_functions = {
    'zip': extract_zip,
    'rar': extract_rar,
    'tar': extract_tar,
    'gz': extract_tar_gz,
    'xz': extract_tar_xz,
    '7z': extract_7z,
  }
  return extract_functions


# An internal function.
def _statdir(directory) -> tuple[list[tuple[os.DirEntry, bool, int]], int]:
  total_size = 0
  items = []
  for entry in os.scandir(directory):
    size = entry.stat().st_size
    total_size += size
    is_dir = entry.is_dir()
    info = entry, is_dir, size
    items.append(info)
    if is_dir:
      pair = _statdir(entry)
      items.extend(pair[0])
      total_size += pair[1]
  return items, total_size


def copy_file_with_progress(src, dst, progress_callback: callable):
  """Copies given file while providing current progress."""
  buffer_size = shutil.COPY_BUFSIZE
  filesize = os.stat(src).st_size
  n_buffers = math.ceil(filesize / buffer_size)
  approximated_filesize = buffer_size * n_buffers
  with open(src, 'rb') as src_fp, open(dst, 'wb') as dst_fp:
    for i in range(n_buffers):
      progress_callback(i * buffer_size, approximated_filesize)
      dst_fp.write(src_fp.read(buffer_size))
    progress_callback(approximated_filesize, approximated_filesize)


def copy_dir_with_progress(src, dst, progress_callback: callable):
  """Copies given directory while providing current progress."""
  queue, total_size = _statdir(src)
  bytes_copied = 0

  def subprogress_callback(done, todo):
    progress_callback(done + bytes_copied, total_size)

  os.mkdir(dst)
  for entry, is_dir, size in queue:
    progress_callback(bytes_copied, total_size)
    entry_dst = os.path.join(dst, os.path.relpath(entry, src))
    if is_dir:
      os.mkdir(entry_dst)
    else:
      copy_file_with_progress(entry, entry_dst, subprogress_callback)
    bytes_copied += size
  progress_callback(bytes_copied, total_size)


def unlink_dir_with_progress(directory, progress_callback: callable):
  """Deletes a given directory while providing current progress."""
  bytes_deleted = 0
  queue, total_size = _statdir(directory)
  queue.reverse()
  for entry, is_dir, size in queue:
    progress_callback(bytes_deleted, total_size)
    if is_dir:
      os.rmdir(entry)
    else:
      os.unlink(entry)
    bytes_deleted += size
  os.rmdir(directory)
  progress_callback(bytes_deleted, total_size)


def get_dir_size(directory) -> int:
  """Returns the size of a given directory in bytes."""
  total_size = 0
  for entry in os.scandir(directory):
    total_size += entry.stat().st_size
    if entry.is_dir():
      total_size += get_dir_size(entry)
  return total_size


def get_readable_filesize(
  size: int,
  ndigits: int or None = 1,
) -> tuple[float, str, str]:
  """Given a number of bytes, returns a human readable filesize, as a tuple.

  Tuple format: (value, short unit name, long unit name)
  Example output: (6.9, 'MB', 'MegaBytes')
  """
  orders = [
    ('B', 'Bytes'),
    ('KB', 'KiloBytes'),
    ('MB', 'MegaBytes'),
    ('GB', 'GigaBytes'),
    ('TB', 'TeraBytes'),
    ('PB', 'PetaBytes'),
    ('EB', 'ExaBytes'),
    ('ZB', 'ZettaBytes'),
    ('YB', 'YottaBytes'),
    ('RB', 'RonnaBytes'),
    ('QB', 'QuettaBytes'),
  ]
  n_orders = len(orders)
  if size > 0:
    order = math.floor(math.log(size, 1000))
    if order >= n_orders:
      order = n_orders - 1
    size = size / (1000**order)
    size = round(size, ndigits)
  else:
    order = 0
  units = orders[order]
  return (size,) + units


def is_archive_supported(archive) -> bool:
  """Checks whether extraction of the given archive is supported.

  The `archive` can be a path to file, bytes, bytesarray or a file-like object.
  """
  extension = filetype.guess_extension(archive)
  supported = list(_get_extract_functions().keys())
  return extension in supported


def extract_archive(src, dst, progress_callback: callable = None):
  """Extracts the given archive to a specified destination.

  The `src` can be a path to file, bytes, bytesarray or a file-like object.
  The `dst` has to be a path that leads to a directory.
  """
  extension = filetype.guess_extension(src)
  functions = _get_extract_functions()
  function = functions.get(extension)
  if not function:
    raise NotImplementedError(f"Unsupported archive type '{extension}'")
  src_type = type(src)
  if hasattr(src, '__fspath__') or src_type is str:
    with open(src, 'rb') as fp:
      function(fp, dst, progress_callback)
  elif src_type in (bytes, bytearray):
    with io.BytesIO(src) as fp:
      function(fp, dst, progress_callback)
  elif hasattr(src, 'read'):
    function(src, dst, progress_callback)
  else:
    raise TypeError('Invalid `archive` type')


def start(*args) -> int:
  """Like xdg-open, but platform-aware."""
  commands = {
    'linux': 'xdg-open',
    'darwin': 'open',
    'win32': 'start',
    'cygwin': 'start',
  }
  command = commands.get(sys.platform)
  if not command:
    raise NotImplementedError(f"Unsupported platform '{sys.platform}'")
  process = subprocess.run([command, *args], check=True)
  return process.returncode
