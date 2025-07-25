# Imports
import os, sys, shutil, pathlib
import subprocess, send2trash, platform, tempfile
import zipfile, rarfile, patoolib

# Internal functions
joinpath = os.path.join

def realpath(path: str) -> str:
  home = str(pathlib.Path.home())
  path_prefixes = ['/', '~']
  first_char = path[0]
  if first_char in path_prefixes:
    path = path.replace('~', home)
    return os.path.normpath(path)
  else:
    return path

def realpaths(path: list) -> list:
  result_list = []
  for item in path:
    result_list.append(realpath(item))
  return result_list

def outpath(path: str or list) -> str or list:
  if type(path) == str:
    return path.replace(os.sep, '/')
  elif type(path) == list:
    result_list = []
    for item in path:
      result_list.append(item.replace(os.sep, '/'))
    return result_list

# Deals with files
class Drawer:

  # Converts the given path to absolute.
  def absolute_path(self, path) -> str:
    path = realpath(path)
    return outpath(path)

  # Returns True if given a path to a folder.
  def is_folder(self, path: str) -> bool:
    if path == '':
      return False
    path = realpath(path)
    return os.path.isdir(path)

  # Returns True if given a path to a file.
  def is_file(self, path: str) -> bool:
    path = realpath(path)
    return os.path.isfile(path)

  # Returns True if path exists.
  def exists(self, path: str) -> bool:
    path = realpath(path)
    return os.path.exists(path)

  # Returns the extension of a given file.
  def get_filetype(self, path: str) -> str:
    if self.is_folder(path):
      return 'folder'
    basename = self.get_basename(path)
    filetype = os.path.splitext(basename)[1].removeprefix('.')
    return filetype

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

  # Renames a given file in a given path. Returns path to renamed file/folder.
  def rename(self, folder: str, old_filename: str, new_filename: str) -> str:
    if not folder.endswith('/'):
      folder = folder = '/'
    folder = realpath(folder)
    os.rename(folder + old_filename, folder + new_filename)
    return outpath(folder + new_filename)

  # Creates a new folder.
  def make_folder(self, path: str) -> str:
    path = realpath(path)
    path = os.mkdir(path)
    return outpath(path)

  # Creates a new file.
  def make_file(self, path: str) -> str:
    path = realpath(path)
    new = open(path, 'w')
    new.close()
    return outpath(path)

  # Copies given file(s)/folder(s).
  def copy(self, source: str, destination: str, overwrite=False) -> str:
    source = realpath(source)
    destination = realpath(destination)
    if self.is_file(source):
      shutil.copy(source, destination)
    elif self.is_folder(source):
      shutil.copytree(source, destination, dirs_exist_ok=overwrite)
    return outpath(destination)

  # Sends given file/folder to trash.
  def trash_path(self, path: str) -> str:
    path = realpath(path)
    try:
      return send2trash.send2trash(path)
    except FileNotFoundError:
      raise FileNotFoundError(f"Error sending '{path}' to trash.")
    return outpath(path)

  # Sends given files/folders to trash.
  def trash_paths(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append( self.trash_path(path) )
    return return_list

  # Deletes a given file.
  def delete_file(self, file: str) -> str:
    file = realpath(file)
    if self.is_file(file):
      os.remove(file)
      return outpath(file)
    else:
      raise IsADirectoryError(f"Attempted to delete a folder '{path}'.")

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
      raise NotADirectoryError(f"Error deleting '{folder}'.")
    return outpath(folder)

  def delete_folders(self, folders: list) -> list:
    return_list = []
    for folder in folders:
      return_list.append(self.delete_folder(folder))
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
      return_list.append( self.get_parent(path) )
    return return_list

  # Returns depth of given file/folder.
  def get_depth(self, path: str) -> int:
    depth = len(path.split('/'))
    return depth

  # Returns a given file's/folder's basename.
  def get_basename(self, path: str) -> str:
    path = realpath(path)
    if self.is_folder(path):
      path = os.path.basename(os.path.normpath(path))
    else:
      path = path.rsplit(os.sep,1)[-1]
    return outpath(path)

  # Given a list of paths, returns a list of basenames.
  def get_basenames(self, paths: list) -> list:
    return_list = []
    for path in paths:
      return_list.append( self.get_basename(path) )
    return return_list

  # Given a path to an archive, returns whether archive's extraction is supported.
  def is_archive_supported(self, path: str) -> bool:
    supported_archive_types = ['zip', 'rar', '7z']
    filetype = self.get_filetype(path)
    return filetype in supported_archive_types

  # Extracts a given archive to a specified location.
  # progress_function is called every time a file is extracted from the archive.
  # progress_function is only supported for ZIP and RAR archives.
  # Example definition of a progress_function:
  # def progress_function(done: int, total: int):
  #   print(f"Extracted {done} files out of {total} files total")
  def extract_archive(
    self, archive: str, extract_location: str, progress_function=None,
  ) -> str:
    if not self.is_archive_supported(archive):
      raise NotImplementedError(f"Extracting archive at '{archive}' is not supported.")
    archive_type = self.get_filetype(archive)
    archive_basename = self.get_basename(archive).removesuffix(f".{archive_type}")
    extract_location = f"{extract_location}/{archive_basename}"
    archive, extract_location = realpath(archive), realpath(extract_location)
    if archive_type == '7z':
      try:
        patoolib.extract_archive(archive, outdir=extract_location, verbosity=-1)
      except PatoolError:
        raise RuntimeError("It appears that 7Zip is not installed on this system.")
    elif archive_type in ('zip', 'rar'):
      if archive_type == 'zip':
        archive_object = zipfile.ZipFile(archive)
      elif archive_type == 'rar':
        archive_object = rarfile.RarFile(archive)
      archived_files = archive_object.namelist()
      to_extract = len(archived_files)
      extracted = 0
      for archived_file in archived_files:
        archive_object.extract(archived_file, path=extract_location)
        extracted += 1
        if progress_function is not None:
          progress_function(extracted, to_extract)
    return outpath(extract_location)

  # Returns the user's home folder.
  def get_home(self) -> str:
    return outpath(str(pathlib.Path.home()))

  # Returns the system's temporary folder.
  def get_temp(self) -> str:
    temp = str(tempfile.gettempdir())
    return outpath(temp)

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
    if filesize > 1000 ** 7:
      value = filesize / 1000 ** 7
      return (value, 'zb', 'zettabytes')
    elif filesize > 1000 ** 6:
      value = filesize / 1000 ** 6
      return (value, 'eb', 'exabytes')
    elif filesize > 1000 ** 5:
      value = filesize / 1000 ** 5
      return (value, 'pb', 'petabytes')
    elif filesize > 1000 ** 4:
      value = filesize / 1000 ** 4
      return (value, 'tb', 'terabytes')
    elif filesize > 1000 ** 3:
      value = filesize / 1000 ** 3
      return (value, 'gb', 'gigabytes')
    elif filesize > 1000 ** 2:
      value = filesize / 1000 ** 2
      return (value, 'mb', 'megabytes')
    elif filesize > 1000:
      value = filesize / 1000 ** 1
      return (value, 'kb', 'kilobytes')
    else:
      return (filesize, 'b', 'bytes')

  # Same as xdg-open, but platform-independent.
  def open(self, path: str) -> subprocess.CompletedProcess:
    path = realpath(path)
    platform = self.get_platform()
    if platform == 'Linux':
      command = 'xdg-open'
    elif platform == 'Windows':
      command = 'start'
    elif platform == 'Darwin':
      command = 'open'
    else:
      raise NotImplementedError(f"Platform '{platform}' is not supported.")
    return subprocess.run([command, path])

  # Returns host OS name.
  # Common values: 'Linux', 'Windows', 'Darwin'.
  def get_platform(self) -> str:
    return platform.system()
