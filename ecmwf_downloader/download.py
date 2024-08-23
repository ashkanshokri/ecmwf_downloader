# pylint: disable=W1203,W0718

from pathlib import Path
from typing import Dict

from ecmwf.opendata import Client
from ecmwf_downloader.logger_setup import setup_logger

from ecmwf_downloader import helpers as h
from ecmwf_downloader.postprocess import postprocess
from datetime import datetime, timedelta
import json
from uuid import uuid4

# Initialize logger
logger = setup_logger(__name__)


def ensure_date_format(date, config):
    """
    Ensures that the date is in the correct format as specified in the config.
    
    Args:
        date: The date to be formatted, which can be a datetime object, string, or an offset (int, float).
        config (dict): Configuration dictionary that contains 'date_format'.
    
    Returns:
        str: The date formatted as a string according to the specified 'date_format'.
    """

    if isinstance(date, (int, float)):
        # If date is a number, treat it as an offset (e.g., number of days from today)
        date = datetime.now() + timedelta(days=date)

    if isinstance(date, datetime):
        # If it's already a datetime object, format it to string
        date = date.strftime(config['date_format'])

    return date


def check_exists(date: str, config) -> bool:
    """
    Checks if the data for a specific date has already been downloaded.

    Args:
        date (str): The date to check.
        json_filename (str): The name of the JSON file to store the dates.

    Returns:
        bool: True if the date exists in the JSON file, False otherwise.
    """
    if isinstance(date, (int, float)):
        date = ensure_date_format(date, config)

    json_file = Path(config.date_log_file)
    if json_file.exists():
        with json_file.open("r", encoding='utf-8') as file:
            data = json.load(file)
            if date in data:
                logger.info(
                    f"Data for {date} already exists in {config.date_log_file}"
                )
                return True

    return False


def get_raw_data(config: Dict[str, str]) -> None:
    """
    Retrieves raw ECMWF data based on the provided configuration and saves it to a temporary file.

    Args:
        config (Dict[str, str]): Configuration dictionary containing necessary parameters.
    """

    config['temp_filename'] = str(uuid4())
    temp_filename = Path(config['temp_filename'])
    temp_filename.parent.mkdir(exist_ok=True)
    if not isinstance(config['source'], list):
        config['source'] = [config['source']]

    for source in config['source']:
        try:
            client = Client(source=source)
            client.retrieve(config.request, temp_filename)
            logger.info(
                f"Successfully retrieved data for {config['date']} and saved to {temp_filename}"
            )
            break

        except Exception:
            logger.error(
                f"Failed to retrieve data for {config['date']} from {source}.")


def get_data(config: Dict[str, str]) -> None:
    """
    Coordinates the process of downloading and post-processing ECMWF data.

    Args:
        config (Dict[str, str]): Configuration dictionary containing necessary parameters.
    """
    initial_date = config['date']

    if not config.get('save_dir'):
        raise ValueError("save_dir is not defined")

    for offset in range(config['look_back'] * -1, 1):
        date = h.adjust_date(initial_date, offset)
        config['date'] = date

        if not check_exists(date, config):
            logger.info(f"Downloading and processing data for {date}")
            get_raw_data(config)
            postprocess(config)
