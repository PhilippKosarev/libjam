# Imports
import tomllib
import configparser
import json
import re

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
  def read_ini(self, ini_file: str, allow_duplicates=False) -> dict:
    data = drawer.read_file(ini_file)
    parser = configparser.ConfigParser(inline_comment_prefixes=('#', ';'))
    try:
      parser.read_string(data)
    except (
      configparser.DuplicateSectionError,
      configparser.DuplicateOptionError,
    ):
      if allow_duplicates is True:
        ini_string = open(ini_file, 'r').read()
        ini_string = re.sub(';.*', '', ini_string)  # Removing comments
        ini_sections = ini_string.replace(' =', '=').replace('= ', '=')
        ini_sections = ini_sections.replace('\n', ';')
        ini_sections = ini_sections.replace('[', '\n[')
        ini_sections = ini_sections.removeprefix('\n')
        ini_sections = ini_sections.split('\n')
        ini_dict = {}
        for section in ini_sections:
          section_name = re.sub('];.*', '', section).replace('[', '')
          section_name = section_name.upper()
          ini_dict[section_name] = {}
          declarations = section.removeprefix(f'[{section_name}];')
          declarations = declarations.split(';')
          for declaration in declarations:
            if declaration == '':
              continue
            info = declaration.split('=')
            name = info[0].lower()
            value = info[1]
            ini_dict[section_name][name] = value
        return ini_dict
      else:
        return None
    except configparser.ParsingError:
      return None
    sections = parser.sections()
    data = {}
    for section in sections:
      keys = {}
      for key in parser[section]:
        value = parser[section][key]
        keys[key] = value
      data[section] = keys
    return data

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
    json_string = json_string.replace('null', 'None')
    data = json.loads(json_string, strict=False)
    return data
