import argparse
import os
import shutil
from pathlib import Path
from typing import Dict

import ecmwf.data as ecdata
from ecmwf.opendata import Client

from ecmwf_downloader import helpers as h
from ecmwf_downloader.config.config import load_config


def get_raw_data(config: Dict[str, str]) -> None:
    """
    Retrieves raw ECMWF data based on the provided configuration and saves it to a temporary file.

    Args:
        config (Dict[str, str]): Configuration dictionary containing necessary parameters.
    """
    temp_filename = Path(config['temp_filename'])
    temp_filename.parent.mkdir(exist_ok=True)
    client = Client(source=config['source'])
    client.retrieve(config.request, temp_filename)


def postprocess(config: Dict[str, str]) -> None:
    """
    Processes the raw ECMWF data and saves it to the specified directory with a date-based filename.

    Args:
        config (Dict[str, str]): Configuration dictionary containing necessary parameters.
    """
    temp_filename = config['temp_filename']
    save_dir = Path(config['save_dir'])
    save_dir.mkdir(exist_ok=True, parents=True)

    data = ecdata.read(temp_filename)  # pylint: disable=E1101
    date = h.get_grib_date(data).strftime('%Y%m%d')

    shutil.copy(temp_filename, save_dir / f'{date}.grib')
    os.remove(temp_filename)


def get_data(config: Dict[str, str]) -> None:
    """
    Coordinates the process of downloading and post-processing ECMWF data.

    Args:
        config (Dict[str, str]): Configuration dictionary containing necessary parameters.
    """
    get_raw_data(config)
    postprocess(config)


def main(config_path: str) -> None:
    """
    Main function that loads the configuration and initiates the data retrieval and processing.

    Args:
        config_path (str): Path to the configuration file.
    """
    config = load_config(config_path)

    get_data(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and process ECMWF data.")
    parser.add_argument("config_path",
                        type=str,
                        help="Path to the configuration file.")

    args = parser.parse_args()
    main(args.config_path)

# example: python -m ecmwf_downloader.run /Users/sho108/projects/ecmwf_downloader/ecmwf_downloader/configs/test_config.yaml
