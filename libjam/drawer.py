# Imports
import io
import os
import sys
import math
import shutil
import filetype
import tempfile
import zipfile
import rarfile
import tarfile
import py7zr
import platform
import platformdirs
import subprocess

# Shorthand vars
PLATFORM = platform.system()
joinpath = os.path.join


# Internal functions
def realpath(path: str) -> str:
  return os.path.abspath(os.path.expanduser(os.path.normpath(path)))


def realpaths(path: list) -> list:
  result_list = []
  for item in path:
    result_list.append(realpath(item))
  return result_list


def outpath(path: str or list) -> str or list:
  if type(path) is str:
    return path.replace(os.sep, '/')
  elif type(path) is list:
    result_list = []
    for item in path:
      result_list.append(item.replace(os.sep, '/'))
    return result_list


# Internal classes
class JamTarFile:
  def __init__(self, tar: tarfile.TarFile):
    self.tar = tar
    self.members = self.tar.getmembers()
    self.n_members = len(self.members)
    self.extracted = 0
    self.archive_basename = None

  @classmethod
  def open(cls, *args, **kwargs):
    tar = tarfile.open(*args, **kwargs)
    self = cls(tar)
    return self

  def extractall(self, path: str, progress_function: callable = None):
    self.extract_location = path
    self.progress_function = progress_function
    self.tar.extractall(path, filter=self.filter)

  def filter(
    self, member: tarfile.TarInfo, path: str, /
  ) -> tarfile.TarInfo | None:
    if self.progress_function:
      self.progress_function(self.extracted, self.n_members)
    self.extracted += 1
    member = tarfile.data_filter(member, path)
    if member:
      if not self.archive_basename:
        self.archive_basename = os.path.basename(member.name)
      member.name = member.name.removeprefix(self.archive_basename)
      member.name = self.extract_location + member.name
    return member


class SevenZipCallbacks(py7zr.callbacks.ExtractCallback):
  def __init__(self, to_extract: int, progress_function: callable = None):
    self.extracted = 0
    self.to_extract = to_extract
    self.progress_function = progress_function

  def report_start_preparation(self):
    pass

  def report_start(self, file, size):
    if self.progress_function is not None:
      self.progress_function(self.extracted, self.to_extract)
    self.extracted += 1

  def report_end(self, file, size):
    pass

  def report_postprocess(self):
    pass

  def report_update(self, size):
    pass

  def report_warning(self, message):
    pass


# Extract functions
def generic_extract(
  archive_object: zipfile.ZipFile or rarfile.RarFile,
  extract_location: str,
  progress_function: callable = None,
):
  archived_files = archive_object.namelist()
  to_extract = len(archived_files)
  extracted = 0
  for archived_file in archived_files:
    if progress_function:
      progress_function(extracted, to_extract)
    extracted += 1
    archive_object.extract(archived_file, path=realpath(extract_location))


def extract_zip(
  archive: str or bytes,
  extract_location: str,
  progress_function: callable = None,
):
  if type(archive) is str:
    archive = open(realpath(archive), 'rb').read()
  archive_object = zipfile.ZipFile(io.BytesIO(archive))
  generic_extract(archive_object, extract_location, progress_function)


def extract_rar(
  archive: str or bytes,
  extract_location: str,
  progress_function: callable = None,
):
  if type(archive) is str:
    archive = open(realpath(archive), 'rb').read()
  archive_object = rarfile.RarFile(io.BytesIO(archive))
  generic_extract(archive_object, extract_location, progress_function)


def generic_tar_extract(
  archive: str or bytes,
  archive_type: str,  # 'gz', 'xz' or ''
  extract_location: str,
  progress_function: callable = None,
):
  if type(archive) is str:
    archive = open(realpath(archive), 'rb').read()
  if archive_type:
    archive_object = JamTarFile.open(
      mode=f'r:{archive_type}',
      fileobj=io.BytesIO(archive),
    )
  else:
    archive_object = JamTarFile.open(
      mode='r',
      fileobj=io.BytesIO(archive),
    )
  archive_object.extractall(realpath(extract_location), progress_function)


def extract_tar(
  archive: str or bytes,
  extract_location: str,
  progress_function: callable = None,
):
  generic_tar_extract(archive, '', extract_location, progress_function)


def extract_tar_gz(
  archive: str or bytes,
  extract_location: str,
  progress_function: callable = None,
):
  generic_tar_extract(archive, 'gz', extract_location, progress_function)


def extract_tar_xz(
  archive: str or bytes,
  extract_location: str,
  progress_function: callable = None,
):
  generic_tar_extract(archive, 'xz', extract_location, progress_function)


def extract_7z(
  archive: str or bytes,
  extract_location: str,
  progress_function: callable = None,
):
  if type(archive) is str:
    archive = open(realpath(archive), 'rb').read()
  archive_object = py7zr.SevenZipFile(io.BytesIO(archive))
  archived_files = archive_object.namelist()
  to_extract = len(archived_files)
  seven_zip_callbacks = SevenZipCallbacks(to_extract, progress_function)
  archive_object.extract(
    realpath(extract_location),
    recursive=True,
    callback=seven_zip_callbacks,
  )


# Deals with files.
class Drawer:
  # General:

  # Converts the given path to an absolute path.
  def absolute_path(self, path: str) -> str:
    path = realpath(path)
    return outpath(path)

  # Reads a given file.
  def read_file(
    self,
    path: str,
    strict: bool = False,
    binary: bool = False,
  ) -> str or bytes:
    path = realpath(path)
    strictness = {True: 'strict', False: 'replace'}
    if binary:
      with open(path, 'rb') as f:
        data = f.read()
    else:
      with open(path, 'r', errors=strictness.get(strict)) as f:
        data = f.read()
    return data

  # Writes given string/bytes to a file.
  def write_file(
    self,
    path: str,
    content: str or bytes,
    overwrite: bool = False,
  ) -> str:
    if not overwrite:
      if self.exists(path):
        raise FileExistsError(f"File '{path}' already exists.")
    path = realpath(path)
    if type(content) is bytes:
      with open(path, 'wb') as f:
        f.write(content)
    else:
      with open(path, 'w') as f:
        f.write(content)
    return outpath(path)

  # Variable getters:

  # Returns the user's home folder.
  def get_home(self) -> str:
    return outpath(os.path.expanduser('~'))

  # Returns the user's config folder.
  def get_config(self) -> str:
    return outpath(platformdirs.user_config_dir())

  # Returns the system's temporary folder.
  def get_temp(self) -> str:
    return outpath(str(tempfile.gettempdir()))

  # Returns host OS name.
  # Common values: 'Linux', 'Windows', 'Darwin'.
  def get_platform(self) -> str:
    return PLATFORM

  # File checking:

  # Returns True if path exists.
  def exists(self, path: str) -> bool:
    path = realpath(path)
    return os.path.exists(path)

  # Returns True if given a path to a file.
  def is_file(self, path: str) -> bool:
    path = realpath(path)
    return os.path.isfile(path)

  # Returns True if given a path to a folder.
  def is_folder(self, path: str) -> bool:
    if path == '':
      return False
    path = realpath(path)
    return os.path.isdir(path)

  # File gathering:

  # Returns a list of files and folders in a given path.
  def get_all(self, path: str) -> list:
    path = realpath(path)
    relative_files = os.listdir(path)
    absolute_files = []
    for file in relative_files:
      file = joinpath(path, file)
      absolute_files.append(file)
    return outpath(absolute_files)

  # Returns a list of files in a given folder.
  def get_files(self, path: str) -> list:
    everything = self.get_all(path)
    files = []
    for item in everything:
      if self.is_file(item):
        files.append(item)
    return files

  # Returns a list of folders in a given folder.
  def get_folders(self, path: str) -> list:
    folders = []
    for item in self.get_all(path):
      if self.is_folder(item):
        folders.append(item)
    return outpath(folders)

  # Returns a list of all files in a given folder.
  def get_files_recursive(self, path: str) -> list:
    path = realpath(path)
    files = []
    for folder in os.walk(path, topdown=True):
      for file in folder[2]:
        file = joinpath(folder[0], file)
        files.append(file)
    return outpath(files)

  # Returns a list of all folders in a given folder.
  def get_folders_recursive(self, path: str) -> list:
    path = realpath(path)
    folders = []
    for folder in os.walk(path, topdown=True):
      for subfolder in folder[1]:
        subfolder = joinpath(folder[0], subfolder)
        folders.append(subfolder)
    return outpath(folders)

  # File creation:

  # Creates a new file.
  def make_file(self, path: str) -> str:
    path = realpath(path)
    new = open(path, 'w')
    new.close()
    return outpath(path)

  # Creates a new folder.
  def make_folder(self, path: str) -> str:
    path = realpath(path)
    path = os.mkdir(path)
    return outpath(path)

  # Non-destructive file operations:

  # Copies given file/folder.
  # Copying with progress_function is always slower.
  def copy(
    self,
    source: str,
    destination: str,
    overwrite: bool = False,
    progress_function: callable = None,
  ) -> str:
    if self.is_file(source):
      return self.copy_file(source, destination, overwrite, progress_function)
    elif self.is_folder(source):
      return self.copy_folder(source, destination, overwrite, progress_function)
    else:
      raise FileNotFoundError(f"File at '{source}' does not exist.")

  # Copies the given file.
  # Copying with a progress_function is about 20% slower.
  def copy_file(
    self,
    source: str,
    destination: str,
    overwrite: bool = False,
    progress_function: callable = None,
  ) -> str:
    if self.is_folder(source):
      raise IsADirectoryError(f"Path '{source}' leads to a directory.")
    if self.is_folder(destination):
      destination += '/' + self.get_basename(source)
    if self.exists(destination):
      if overwrite:
        self.delete_path(destination)
      else:
        raise FileExistsError(f"File at '{destination}' already exists.")
    if progress_function is not None:
      todo = self.get_filesize(source)
    source, destination = realpath(source), realpath(destination)
    if progress_function is None:
      shutil.copy2(source, destination)
    else:
      buffer_size = 1024 * 100
      done = 0
      with (
        open(source, 'rb') as source_file,
        open(destination, 'wb') as destination_file,
      ):
        while True:
          buffer = source_file.read(buffer_size)
          if not buffer:
            break
          destination_file.write(buffer)
          done += len(buffer)
          progress_function(done, todo)
    return outpath(destination)

  # Copies the given folder.
  # Copying with progress_function can be up to 50% slower.
  def copy_folder(
    self,
    source: str,
    destination: str,
    overwrite: bool = False,
    progress_function: callable = None,
  ) -> str:
    # Processing info
    source = self.absolute_path(source)
    destination = self.absolute_path(destination)
    # Getting relative paths
    source_folders = [
      folder.removeprefix(source)
      for folder in self.get_folders_recursive(source)
    ]
    source_files = [
      file.removeprefix(source) for file in self.get_files_recursive(source)
    ]
    destination_folders = [
      folder.removeprefix(destination)
      for folder in self.get_folders_recursive(destination)
    ]
    destination_files = [
      file.removeprefix(destination)
      for file in self.get_files_recursive(destination)
    ]
    # Checking if any files are about to be overwritten
    if not overwrite:
      if self.exists(destination):
        raise FileExistsError(f"File at '{destination}' already exists.")
      sources = source_folders + source_files
      destinations = destination_folders + destination_files
      for path in sources:
        if path in destinations:
          raise FileExistsError(
            f"File at '{destination + path}' already exists."
          )
    # Letting shutil do the heavy lifting
    if progress_function is None:
      source, destination = realpath(source), realpath(destination)
      shutil.copytree(source, destination, dirs_exist_ok=overwrite)
      return outpath(destination)
    # Doing it ourselves
    else:
      # Creating destination folder
      if self.is_file(destination):
        self.delete_file(destination)
      elif not self.is_folder(destination):
        self.make_folder(destination)
      # Creating folder structure in destination
      for folder in source_folders:
        destination_folder = destination + folder
        if self.is_file(destination_folder):
          self.delete_file(destination_folder)
        elif not self.is_folder(destination_folder):
          self.make_folder(destination_folder)
      # Copying files
      done, todo = 0, len(source_files)
      for file in source_files:
        source_file = source + file
        destination_file = destination + file
        self.copy_file(source_file, destination_file, overwrite)
        done += 1
        progress_function(done, todo)
      return outpath(realpath(destination))

  # Renames a given file in a given path.
  def rename(self, folder: str, old_filename: str, new_filename: str) -> str:
    if not folder.endswith('/'):
      folder = folder + '/'
    old_file, new_file = folder + old_filename, folder + new_filename
    old_file, new_file = realpath(old_file), realpath(new_file)
    os.rename(old_file, new_file)
    return outpath(new_file)

  # File removal:

  # Deletes a given file/folder.
  def delete_path(self, path: str) -> str:
    if self.is_file(path):
      remove_function = os.remove
    elif self.is_folder(path):
      remove_function = shutil.rmtree
    path = realpath(path)
    remove_function(path)
    return outpath(path)

  # Deletes given files/folders.
  def delete_paths(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.delete_path(path))
    return return_list

  # Deletes a given file.
  def delete_file(self, file: str) -> str:
    file = realpath(file)
    if self.is_file(file):
      os.remove(file)
      return outpath(file)
    else:
      raise IsADirectoryError(f"Attempted to delete a folder at '{file}'.")

  # Deletes given files.
  def delete_files(self, files: list) -> list:
    return_list = []
    for file in files:
      return_list.append(self.delete_file(file))
    return return_list

  # Deletes a given folder.
  def delete_folder(self, folder: str) -> str:
    if self.is_folder(folder):
      folder = realpath(folder)
      shutil.rmtree(folder)
    else:
      raise NotADirectoryError(f"Attempted to delete file at '{folder}'.")
    return outpath(folder)

  # Deletes given folders.
  def delete_folders(self, folders: list) -> list:
    return_list = []
    for folder in folders:
      return_list.append(self.delete_folder(folder))
    return return_list

  # Sends given file/folder to trash.
  def trash_path(self, path: str) -> str:
    # Need to check the file ourselves because send2trash raises an OSError
    # instead of a FileNotFoundError
    if not self.exists(path):
      raise FileNotFoundError(f"File at '{path}' does not exist.")
    # Send2Trash can take a long time to import on systems that use GIO due
    # to how long it takes to import GObject and GIO, so doing it on-demand
    # is generally better
    if 'send2trash' not in sys.modules:
      import send2trash
    send2trash = sys.modules.get('send2trash')
    path = realpath(path)
    try:
      send2trash.send2trash(path)
    except send2trash.exceptions.TrashPermissionError:
      raise PermissionError(
        f"Attempted to trash path '{path}' with insufficient permissions."
      )
    return outpath(path)

  # Sends given files/folders to trash.
  def trash_paths(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.trash_path(path))
    return return_list

  # Path parts:

  # Returns a given file's/folder's basename.
  def get_basename(self, path: str) -> str:
    path = realpath(path)
    if self.is_folder(path):
      path = os.path.basename(os.path.normpath(path))
    else:
      path = path.rsplit(os.sep, 1)[-1]
    return outpath(path)

  # Given a list of paths, returns a list of their basenames.
  def get_basenames(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.get_basename(path))
    return return_list

  # Returns the parent folder of given file/folder.
  def get_parent(self, path: str) -> str:
    basename = self.get_basename(path)
    parent = path.removesuffix(basename)
    parent = parent.removesuffix('/')
    return parent

  def get_parents(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append(self.get_parent(path))
    return return_list

  # Path parameters:

  # Returns depth of given file/folder.
  def get_depth(self, path: str) -> int:
    depth = len(path.split('/'))
    return depth

  # Returns the extension of a given file.
  def get_extension(self, path: str) -> str:
    if self.is_folder(path):
      return 'folder'
    basename = self.get_basename(path)
    filetype = os.path.splitext(basename)[1].removeprefix('.')
    return filetype

  # Returns the filetype of a given file.
  def get_filetype(self, file: str or bytes) -> str:
    if type(file) is str:
      file = realpath(file)
    return filetype.guess_extension(file)

  # File statistics:

  # Returns the weight of a given file/folder, in bytes.
  def get_filesize(self, path: str) -> int:
    path = realpath(path)
    if self.is_file(path):
      size = os.path.getsize(path)
    elif self.is_folder(path):
      size = 0
      subfiles = self.get_files_recursive(path)
      for file in subfiles:
        size += os.path.getsize(file)
    return size

  # Given a number of bytes, returns a human readable filesize, as a tuple.
  # Tuple format: (value: float, short_unit_name: str, long_unit_name: str)
  # Example tuple: (6.986356, 'mb', 'megabytes')
  def get_readable_filesize(self, filesize: int) -> tuple:
    filesize_orders = [
      ('b', 'bytes'),
      ('kb', 'kilobytes'),
      ('mb', 'megabytes'),
      ('gb', 'gigabytes'),
      ('tb', 'terabytes'),
      ('eb', 'exabytes'),
      ('zb', 'zettabytes'),
      ('yb', 'yottabytes'),
      ('rb', 'ronnabytes'),
      ('qb', 'quettabytes'),
    ]
    if filesize > 0:
      filesize_order = math.floor(math.log(filesize, 1000))
      filesize = filesize / (1000**filesize_order)
    else:
      filesize_order = 0
    return (filesize,) + filesize_orders[filesize_order]

  # Archive extraction:

  # Given a path to an archive, returns whether archive's extraction is supported.
  def is_archive_supported(self, path: str) -> bool:
    supported_archive_types = ['zip', 'rar', '7z']
    filetype = self.get_filetype(path)
    return filetype in supported_archive_types

  # Extracts a given archive to a specified location.
  # progress_function is called every time a file is extracted from the archive.
  # Example progress_function:
  # def progress_function(extracted: int, to_extract: int):
  #   print(f"Extracted {extracted} files out of {to_extract} files total")
  def extract_archive(
    self,
    archive: str or bytes,
    extract_location: str,
    progress_function: callable = None,
  ):
    extract_functions = {
      'zip': extract_zip,
      'rar': extract_rar,
      'tar': extract_tar,
      'gz': extract_tar_gz,
      'xz': extract_tar_xz,
      '7z': extract_7z,
    }
    archive_type = self.get_filetype(archive)
    function = extract_functions.get(archive_type)
    if function is None:
      raise NotImplementedError(
        f"Archive type '{archive_type}' is not supported."
      )
    function(archive, extract_location, progress_function)

  # Same as xdg-open, but platform-independent.
  def open(self, argument: str, is_path: bool = True) -> int:
    if is_path:
      argument = realpath(argument)
    open_by_platform = {
      'Linux': 'xdg-open',
      'Windows': 'start',
      'Darwin': 'open',
    }
    if PLATFORM not in open_by_platform:
      raise NotImplementedError(f"Platform '{platform}' is not supported.")
    open_command = open_by_platform.get(PLATFORM)
    process = subprocess.run([open_command, argument], check=True)
    return process.returncode
