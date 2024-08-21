# pylint: disable=W1203,W0718

import os
import shutil
import json
from pathlib import Path
from typing import Dict

import ecmwf.data as ecdata
from ecmwf_downloader.logger_setup import setup_logger

from ecmwf_downloader import helpers as h

# Initialize logger
logger = setup_logger(__name__)


def update_downloaded_dates(date: str, json_file: Path) -> None:
    """
    Updates the JSON file with the new date.

    Args:
        date (str): The date to add to the JSON file.
        json_file (Path): Path to the JSON file.
    """
    if Path(json_file).exists():
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
    else:
        data = []

    if date not in data:
        data.append(date)
        with open(json_file, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4)
        logger.info(f"Added {date} to {json_file}")
    else:
        logger.info(f"Date {date} already in {json_file}")


def postprocess(config: Dict[str, str]) -> None:
    """
    Processes the raw ECMWF data and saves it to the specified directory with a date-based filename.
    Updates the JSON file with the processed date.

    Args:
        config (Dict[str, str]): Configuration dictionary containing necessary parameters.
    """
    try:
        temp_filename = config['temp_filename']
        save_dir = Path(config['save_dir'])
        save_dir.mkdir(exist_ok=True, parents=True)

        data = ecdata.read(temp_filename)  # pylint: disable=E1101
        date = h.get_grib_date(data).strftime('%Y%m%d')

        shutil.copy(temp_filename, save_dir / config['name'] / f'{date}.grib')
        os.remove(temp_filename)
        logger.info(
            f"Successfully processed and saved data for {date} to {save_dir}")

        # Update the JSON file with the processed date
        update_downloaded_dates(date, config.date_log_file)

    except Exception as e:
        logger.error(f"Failed to process data for {config['date']}: {e}")
