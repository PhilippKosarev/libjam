# Imports
from zipfile import ZipFile
from tarfile import TarFile, TarInfo, data_filter as tar_data_filter
from rarfile import RarFile
from py7zr import SevenZipFile
from py7zr.callbacks import ExtractCallback as SevenZipExtractCallback


# Internal classes
class JamTarFile:
  def __init__(self, tar: TarFile):
    self.tar = tar
    self.members = self.tar.getmembers()
    self.n_members = len(self.members)
    self.extracted = 0
    self.archive_basename = None

  @classmethod
  def open(cls, *args, **kwargs):
    tar = TarFile.open(*args, **kwargs)
    return cls(tar)

  def extractall(self, dst, progress_function: callable = None):
    self.progress_function = progress_function
    self.tar.extractall(dst, filter=self.filter)

  def filter(self, member: TarInfo, dst) -> TarInfo | None:
    if self.progress_function:
      self.progress_function(self.extracted, self.n_members)
    self.extracted += 1
    return tar_data_filter(member, dst)


class SevenZipJamCallback(SevenZipExtractCallback):
  def __init__(self, to_extract: int, progress_function: callable):
    self.extracted = 0
    self.to_extract = to_extract
    self.progress_function = progress_function

  def report_start_preparation(self):
    self.progress_function(self.extracted, self.to_extract)

  def report_start(self, file, size):
    self.progress_function(self.extracted, self.to_extract)
    self.extracted += 1

  def report_end(self, file, size):
    self.progress_function(self.extracted, self.to_extract)

  def report_postprocess(self):
    pass

  def report_update(self, size):
    pass

  def report_warning(self, message):
    pass


# Extract functions
def generic_extract(
  archive_object: ZipFile or RarFile,
  dst,
  progress_function: callable = None,
):
  archived_files = archive_object.namelist()
  to_extract = len(archived_files)
  extracted = 0
  for archived_file in archived_files:
    if progress_function:
      progress_function(extracted, to_extract)
    extracted += 1
    archive_object.extract(archived_file, path=dst)
  if progress_function:
    progress_function(extracted, to_extract)


def extract_zip(fp, dst, progress_function: callable = None):
  archive_object = ZipFile(fp)
  generic_extract(archive_object, dst, progress_function)


def extract_rar(fp, dst, progress_function: callable = None):
  archive_object = RarFile(fp)
  generic_extract(archive_object, dst, progress_function)


def generic_tar_extract(
  fp,
  dst,
  compression: str,  # should be 'gz', 'xz' or '',
  progress_function: callable = None,
):
  if compression:
    archive_object = JamTarFile.open(
      mode=f'r:{compression}',
      fileobj=fp,
    )
  else:
    archive_object = JamTarFile.open(mode='r', fileobj=fp)
  archive_object.extractall(dst, progress_function)


def extract_tar(fp, dst, progress_function: callable = None):
  generic_tar_extract(fp, dst, '', progress_function)


def extract_tar_gz(fp, dst, progress_function: callable = None):
  generic_tar_extract(fp, dst, 'gz', progress_function)


def extract_tar_xz(fp, dst, progress_function: callable = None):
  generic_tar_extract(fp, dst, 'xz', progress_function)


def extract_7z(fp, dst, progress_function: callable = None):
  archive_object = SevenZipFile(fp)
  archived_files = archive_object.namelist()
  to_extract = len(archived_files)
  if progress_function:
    callback = SevenZipJamCallback(to_extract, progress_function)
  else:
    callback = None
  archive_object.extract(
    dst,
    recursive=True,
    callback=callback,
  )
