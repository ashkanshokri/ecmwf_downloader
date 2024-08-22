from pathlib import Path
from typing import Any, Dict, Optional, Union

import yaml
import os


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
        DEFAULT_DICT = {
            'time': [0],  # 0,6,12,18
            'type': ["cf"],  # "pf",
            'step': [0, 24, 48, 72],
            'param': ["tp"],
            'date': -1,  # '20220125',
            "stream": "enfo",
            'source': "ecmwf",
            'temp_filename': './temp.grib',
            'save_dir': None,
            'look_back': 2,
            'date_format': '%Y%m%d',
            'name': 'data',
            'area': [-5.0, 110.0, -45.0, 155.0],
            'save_grib': False,
            'save_netcdf': True,
        }
        default_config: Dict[str, Any] = DEFAULT_DICT
        default_config.update(kwargs)
        self.update(default_config)

        # get save_dir
        #self.set_save_dir()

    def set_save_dir(self):
        """
        Determines and sets the 'save_dir' attribute from the environment variable 
        or the default provided in the config. Validates the path and ensures it exists.
        """
        save_dir = self.get('save_dir', None)

        if not save_dir:
            save_dir = os.getenv('SAVE_DIR', None)
            if save_dir is None:
                raise ValueError(
                    "The 'save_dir' is not set in the config and 'SAVE_DIR' environment variable is not defined."
                )

        save_dir = Path(save_dir).expanduser().resolve()
        save_dir.mkdir(parents=True, exist_ok=True)
        self.__dict__['save_dir'] = str(save_dir)

    @property
    def date_log_file(self) -> str:
        """
        Returns the file path for logging the dates which are already downloaded.
        """
        return str(
            Path(self.__dict__['save_dir']) / self['name'] /
            'downloaded_dates.json')

    @property
    def request(self) -> Dict[str, Any]:
        """
        Returns a dictionary of configuration parameters relevant for requests.
        """
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
