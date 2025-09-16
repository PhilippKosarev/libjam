# Imports
import tomllib
import configparser
import json

# Internal imports
from .drawer import Drawer

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

  # Reads INI file and returns its contents in the form of a dict.
  # allow_duplicates is only to be used as a last resort due to the performance
  # impact and inaccuracy in results.
  def read_ini(self, ini_file: str) -> dict:
    data = drawer.read_file(ini_file)
    parser = configparser.ConfigParser(
      inline_comment_prefixes=('#', ';'),
      strict=False,
    )
    parser.read_string(data)
    return dict(parser)

  # Writes an INI file from a given dict to a given path.
  def write_ini(self, ini_file: str, contents: dict):
    parser = configparser.ConfigParser()
    for section in contents:
      for var_name in contents.get(section):
        value = contents.get(section).get(var_name)
        if section not in parser:
          parser[section] = {}
        parser[section][var_name] = value
    with open(ini_file, 'w') as file:
      parser.write(file)

  # Reads a given json file as a dictionary.
  def read_json(self, json_file: str) -> dict:
    json_string = drawer.read_file(json_file)
    data = json.loads(json_string, strict=False)
    return data
