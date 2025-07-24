# Imports
import os, sys, shutil, send2trash, platform, tempfile, pathlib
import zipfile, patoolib, rarfile, subprocess
from .typewriter import Typewriter
from .clipboard import Clipboard
typewriter = Typewriter()
clipboard = Clipboard()

PLATFORM = platform.system()

# Internal functions
joinpath = os.path.join

def outpath(path: str or list) -> str or list:
  if type(path) == str:
    return path.replace(os.sep, '/')
  elif type(path) == list:
    result_list = []
    for item in path:
      result_list.append(item.replace(os.sep, '/'))
    return result_list

HOME = str(pathlib.Path.home())

def realpath(path: str) -> str:
  path_prefixes = ['/', '~']
  first_char = path[0]
  if first_char in path_prefixes:
    path = path.replace('~', HOME)
    return os.path.normpath(path)
  else:
    return path

def realpaths(path: list) -> list:
  result_list = []
  for item in path:
    result_list.append(realpath(item))
  return result_list

# Deals with files
class Drawer:

  # Converts the given path to absolute
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

  # Returns the extension of a given file (a string)
  def get_filetype(self, path: str) -> str:
    if self.is_folder(path):
      return "folder"
    basename = self.basename(path)
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

  # Sends given file(s)/folder(s) to trash.
  def trash(self, path: str or list) -> str or list:
    if type(path) == str:
      path = realpath(path)
      try:
        send2trash.send2trash(path)
      except FileNotFoundError:
        print(f"File '{path}' wasn't found, skipping sending it to trash.")
    elif type(path) == list:
      path = realpaths(path)
      for item in path:
        try:
          send2trash.send2trash(item)
        except FileNotFoundError:
          print(f"File '{path}' wasn't found, skipping sending it to trash.")
    else:
      return None
    return outpath(path)

  # Deletes a given file.
  def delete_file(self, path: str or list) -> str or list:
    if type(path) == str:
      path = realpath(path)
      if self.is_file(path):
        os.remove(path)
    elif type(path) == list:
      path = realpaths(path)
      for item in path:
        if self.is_file(path):
          os.remove(item)
    return outpath(path)

  # Deletes a given folder.
  def delete_folder(self, path: str) -> str:
    path = realpath(path)
    try:
      if self.is_folder(path):
        shutil.rmtree(path)
      else:
        return None
    except KeyboardInterrupt:
      typewriter.print("Folder deletion cancelled.")
      shutil.rmtree(path)
      sys.exit(-1)
    except PermissionError:
      typewriter.print(f"Failed to delete folder '{path}', due to insufficient permissions.")
      sys.exit(1)
    return outpath(path)

  # Returns the parent folder of given file/folder.
  def get_parent(self, path: str or list) -> str or list:
    if type(path) == str:
      path = realpath(path)
      basename = self.basename(path)
      parent = path.removesuffix(basename)
      parent = parent.removesuffix(os.sep)
      return outpath(parent)
    elif type(path) == list:
      path = realpaths(path)
      result_list = []
      for file in path:
        basename = self.basename(file)
        parent = file.removesuffix(basename)
        parent = parent.removesuffix(os.sep)
        result_list.append(parent)
      return outpath(result_list)

  # Returns depth of given file/folder.
  def get_depth(self, path: str) -> int:
    depth = len(path.split('/'))
    return depth

  # Returns the basename of file(s)/folder(s).
  def basename(self, path: str or list) -> str or list:
    if type(path) == str:
      path = realpath(path)
      if self.is_folder(path):
        path = os.path.basename(os.path.normpath(path))
      else:
        path = path.rsplit(os.sep,1)[-1]
      return outpath(path)
    elif type(path) == list:
      path = realpaths(path)
      return_list = []
      for file in path:
        if self.is_file(file):
          file = os.path.basename(file)
        elif self.is_folder(file):
          file = os.path.basename(os.path.normpath(file))
        return_list.append(file)
      return outpath(return_list)

  # Searches for string in list of basenames.
  def search_for_files(self, search_term: str, path: list) -> list:
    path = realpaths(path)
    result_list = []
    files = self.get_files_recursive(path)
    for file in files:
      basename = self.basename(file)
      if search_term.lower() in basename.lower():
        result_list.append(file)
    return outpath(result_list)

  def search_for_folder(self, search_term: str, path: str or list) -> list:
    result_list = []
    if type(path) == str:
      path = realpath(path)
      subfolders = self.get_folders(path)
      for item in subfolders:
        basename = self.basename(item)
        if basename == search_term:
          result_list.append(item)
    elif type(path) == list:
      path = realpaths(path)
      for subfolder in path:
        subfolders = self.get_folders(subfolder)
        for item in subfolders:
          basename = self.basename(item)
          if basename == search_term:
            result_list.append(item)
    return outpath(result_list)

  def search_for_folders(self, search_term: str, path: str or list) -> list:
    result_list = []
    def search(search_term: str, path: str):
      folders = self.get_folders_recursive(path)
      for folder in folders:
        basename = self.basename(folder)
        if search_term.lower() in basename.lower():
          result_list.append(folder)
    if type(path) == str:
      path = realpath(path)
      search(search_term, path)
    elif type(path) == list:
      path = realpaths(path)
      for subfolder in path:
        search(search_term, subfolder)
    return outpath(result_list)

  # Finds a folder with specified files
  def find_folders_with_files(self, path: str, required_files: list) -> list:
    path = realpath(path)
    matches = []
    for req in required_files:
      matched_files = self.get_parent(self.search(req, path))
      matched_files = Clipboard().deduplicate(matched_files)
      if matched_files != []:
        matches += matched_files
    return outpath(matches)

  # Checks if a given file is an archive
  archive_types = ['zip', 'rar', '7z']
  def is_archive(self, path: str) -> bool:
    path = realpath(path)
    filetype = self.get_filetype(path)
    if clipboard.is_string_in_list(self.archive_types, filetype):
      return True
    else:
      return False

  # Extracts a given archive.
  # progress_function is called every time a file is extracted from the archive,
  # it passes number of extracted files and number of files that need to be extracted (done, total).
  # Example definition of progress_function:
  # def progress_function(done: int, total: int):
  #   print(f"Extracted {done} files out of {total} files total")
  def extract_archive(self, archive: str, extract_location: str, progress_function=None) -> str:
    archive = realpath(archive)
    extract_location = realpath(extract_location)
    archive_type = self.get_filetype(archive)
    archive_basename = self.basename(archive).removesuffix(f".{archive_type}")
    extract_location = joinpath(extract_location, archive_basename)
    try:
      if archive_type == 'zip': archive_function = zipfile.ZipFile
      elif archive_type == 'rar': archive_function = rarfile.RarFile
      elif archive_type == '7z':
        try:
          patoolib.extract_archive(archive, outdir=extract_location, verbosity=-1)
          return extract_location
        except PatoolError:
          print("Please install the 'p7zip' package to process 7zip archives.")
          return None
      else:
        return None
      if archive_type == 'zip' or archive_type == 'rar':
        archive_obj = archive_function(archive)
        archived_files = archive_obj.namelist()
        to_extract = len(archived_files)
        extracted = 0
        for archived_file in archived_files:
          archive_obj.extract(archived_file, path=extract_location)
          extracted += 1
          if progress_function is not None:
            progress_function(extracted, to_extract)
    except KeyboardInterrupt:
      typewriter.print("Archive extraction cancelled.")
      self.delete_folder(extract_location)
      exit()
    return outpath(extract_location)

  # Returns the home folder.
  def get_home(self) -> str:
    return outpath(HOME)

  # Returns the temporary folder.
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
    if PLATFORM == 'Linux':
      command = 'xdg-open'
    elif PLATFORM == 'Windows':
      command = 'start'
    elif PLATFORM == 'Darwin':
      command = 'open'
    else:
      return 1
    return subprocess.run([command, path])

  # Returns host OS name.
  # Possible values: 'Linux', 'Windows', 'Darwin'.
  def get_platform(self) -> str:
    return PLATFORM
