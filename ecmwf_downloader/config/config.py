import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml

DEFAULT_DICT = {
    'time': [0],  #0,6,12,18
    'type': ["cf"],  #"pf", 
    'step': [0, 24, 48, 72],
    'param': ["tp"],
    'date': -1,  #'20220125',
    "stream": "enfo",
    'source': "ecmwf",
    'temp_filename': './temp.grib',
    'save_dir': './downloads'
}


def get_current_timestamp() -> str:
    """
    Returns the current timestamp formatted as 'YYMMDDHHMMSS'.
    
    :return: A string representing the current timestamp.
    """
    return datetime.datetime.now().strftime('%y%m%d%H%M%S')


def load_config(path: Union[str, Path]) -> 'Config':
    """
    Loads a configuration from a YAML file.
    
    :param path: The path to the YAML file.
    :return: A Config object populated with data from the YAML file.
    """
    config = Config()
    config.load_from_yaml(path)
    return config


class Config:
    """
    A class for managing configuration data. Configurations can be loaded from
    or saved to a YAML file, and accessed like a dictionary.
    """

    def __init__(self, **kwargs: Any):
        """
        Initializes the Config object with default values and any additional 
        keyword arguments provided.
        
        :param kwargs: Additional configuration parameters.
        """
        default_config: Dict[str, Any] = DEFAULT_DICT
        default_config.update(kwargs)
        self.update(default_config)

    @property
    def request(self):
        return {
            k: v
            for k, v in self.__dict__.items() if k in [
                'type',
                'stream',
                'date',
                'time',
                'step',
                'param',
                'levtype',
                'levelist',
                'number',
            ]
        }

    def __setitem__(self, key: str, value: Any) -> None:
        """
        Sets a configuration parameter.
        
        :param key: The key of the configuration parameter.
        :param value: The value of the configuration parameter.
        """
        self.__dict__[key] = value

    def __getitem__(self, key: str) -> Any:
        """
        Gets a configuration parameter.
        
        :param key: The key of the configuration parameter.
        :return: The value of the configuration parameter.
        """
        return self.__dict__[key]

    def __repr__(self) -> str:
        """
        Returns a string representation of the configuration.
        
        :return: A string representing the configuration.
        """
        return repr(self.__dict__)

    def keys(self) -> list:
        """
        Returns a list of configuration keys.
        
        :return: A list of keys in the configuration.
        """
        return list(self.__dict__.keys())

    def save_to_yaml(self, filepath: Union[str, Path]) -> None:
        """
        Saves the current configuration to a YAML file.
        
        :param filepath: The path to the YAML file where the configuration 
                         should be saved.
        """
        Path(filepath).parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w', encoding='utf-8') as file:
            yaml.dump(self.__dict__, file)

    def load_from_yaml(self, filepath: Union[str, Path]) -> None:
        """
        Loads configuration from a YAML file and updates the current 
        configuration.
        
        :param filepath: The path to the YAML file to load.
        """
        with open(filepath, 'r', encoding='utf-8') as file:
            config_data = yaml.safe_load(file)
            self.__dict__.update(config_data)

    def get(self, key: str, default: Optional[Any] = None) -> Optional[Any]:
        """
        Gets a configuration value with an optional default if the key does 
        not exist.
        
        :param key: The key of the configuration parameter.
        :param default: The default value to return if the key does not exist.
        :return: The value of the configuration parameter, or the default if 
                 the key is not found.
        """
        return self.__dict__.get(key, default)

    def update(self, data: Dict[str, Any]) -> None:
        """
        Updates the current configuration with the provided dictionary.
        
        :param data: A dictionary with configuration data to update.
        """
        self.__dict__.update(data)
