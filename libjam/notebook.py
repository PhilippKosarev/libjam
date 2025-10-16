# Imports
import tomllib
import configparser
import json
import io

# Internal imports
from .drawer import Drawer

# Shorthand vars
drawer = Drawer()


# Deals with configs and reading/writing files
class Notebook:
  # Checking if config exists, and creating one if it does not
  def check_config(self, config_template_file: str, config_file: str):
    # Checking folder
    config_folder = drawer.get_parent(config_file)
    if not drawer.is_folder(config_folder):
      drawer.make_folder(config_folder)
    # Checking file
    if not drawer.is_file(config_file):
      drawer.make_file(config_file)
      config_template = drawer.read_file(config_template_file)
      drawer.write_file(config_template, config_file)
    # Returning path
    return config_file

  # Returns a toml file parsed to a dict.
  def read_toml(self, file: str) -> dict:
    data = drawer.read_file(file)
    data = tomllib.loads(data)
    return data

  # Returns an ini file parsed to a dict.
  def read_ini(self, ini_file: str) -> dict:
    data = drawer.read_file(ini_file)
    parser = configparser.ConfigParser(
      inline_comment_prefixes=('#', ';'),
      strict=False,
    )
    parser.read_string(data)
    return parser._sections

  # Writes a ini file parsed from a dict.
  def write_ini(self, path: str, contents: dict, overwrite: bool = False):
    parser = configparser.ConfigParser(
      inline_comment_prefixes=('#', ';'),
      strict=False,
    )
    parser.read_dict(contents)
    output = io.StringIO()
    parser.write(output)
    drawer.write_file(path, output.getvalue(), overwrite)

  # Returns a json file parsed to a dict.
  def read_json(self, path: str) -> dict:
    data = drawer.read_file(path)
    return json.loads(data, strict=False)
