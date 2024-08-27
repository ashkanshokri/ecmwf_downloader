# pylint: disable=W1203,W0718

import json
import os
import shutil
from pathlib import Path
from typing import Dict, Union

import ecmwf.data as ecdata
import pandas as pd
import xarray as xr

from ecmwf_downloader import helpers as h
from ecmwf_downloader.logger_setup import setup_logger

# Initialize logger
logger = setup_logger(__name__)


def update_downloaded_dates(date: str, json_file: Path) -> None:
    """
    Updates the JSON file with the new date if it's not already present.

    Args:
        date (str): The date to add to the JSON file.
        json_file (Path): Path to the JSON file where dates are recorded.
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


def get_save_dir(config: Dict[str, Union[str, Path]]) -> Path:
    """
    Creates and returns the directory where files will be saved.

    Args:
        config (Dict[str, Union[str, Path]]): Configuration dictionary containing 'save_dir' and 'name'.

    Returns:
        Path: The directory where files will be saved.
    """
    save_dir = Path(config['save_dir']) / config['name']
    save_dir.mkdir(exist_ok=True, parents=True)
    return save_dir


def convert_and_crop_grib_to_netcdf(
        config: Dict[str, Union[str, Path, bool, list]]) -> str:
    """
    Converts GRIB data to NetCDF format, crops the data based on the specified area, 
    and saves the resulting NetCDF file with compression.

    Args:
        config (Dict[str, Union[str, Path, bool, list]]): Configuration dictionary containing necessary parameters.

    Returns:
        str: The processed date in 'YYYYMMDD' format.
    """
    save_dir = get_save_dir(config)
    temp_filename = config['temp_filename']

    for data_type in config['type']:
        ds = xr.open_dataset(temp_filename,
                             engine="cfgrib",
                             filter_by_keys={'dataType': data_type})

        # Crop data using config['area'] (-5.0/110.0/-45.0/155.0)
        ds = h.crop_data(ds, config['area'])

        # Ensure all variables are single precision (float32)
        ds = ds.astype({var: 'float32' for var in ds.data_vars})

        date = pd.to_datetime(ds.time.values).strftime(config['date_format'])

        try:
            # Save to NetCDF with compression using the netcdf4 engine
            comp = dict(zlib=True,
                        complevel=5)  # Adjust complevel (0-9) for compression
            encoding = {var: comp for var in ds.data_vars}

            if not isinstance(date, str):
                date = date[0]
            out_filename = f'{data_type}_{date}.nc'

            ds.to_netcdf(save_dir / out_filename,
                         encoding=encoding,
                         engine='netcdf4')
            logger.info(f"Saving NetCDF using netcdf4: {out_filename}")
        except Exception as e:
            logger.exception(
                f"Failed to save NetCDF for {data_type} on {date}: {e}")
            ds.to_netcdf(save_dir / out_filename, engine='scipy')
            logger.info(f"Saving NetCDF using scipy: {out_filename}")

    return date


def save_grib(config: Dict[str, Union[str, Path]]) -> str:
    """
    Saves the GRIB file to the specified directory after processing.

    Args:
        config (Dict[str, Union[str, Path]]): Configuration dictionary containing necessary parameters.

    Returns:
        str: The processed date in 'YYYYMMDD' format.
    """
    temp_filename = config['temp_filename']
    save_dir = get_save_dir(config)
    data = ecdata.read(temp_filename)  # pylint: disable=E1101
    date = h.get_grib_date(data).strftime('%Y%m%d')

    shutil.copy(temp_filename, save_dir / f'{date}.grib')

    logger.info(
        f"Successfully processed and saved data for {date} to {save_dir}")
    return date


def get_date(config: Dict[str, Union[str, Path]]) -> str:
    """
    Retrieves the date from the GRIB file.

    Args:
        config (Dict[str, Union[str, Path]]): Configuration dictionary containing the 'temp_filename' key.

    Returns:
        str: The date in 'YYYYMMDD' format.
    """
    temp_filename = config['temp_filename']
    data = ecdata.read(temp_filename)  # pylint: disable=E1101
    return h.get_grib_date(data).strftime('%Y%m%d')


def postprocess(config: Dict[str, Union[str, Path, bool]]) -> None:
    """
    Processes the raw ECMWF data and saves it to the specified directory with a date-based filename.
    Updates the JSON file with the processed date.

    Args:
        config (Dict[str, Union[str, Path, bool]]): Configuration dictionary containing necessary parameters.
    """
    try:
        date = None
        if config.get('save_netcdf', False):
            date = convert_and_crop_grib_to_netcdf(config)
        if config.get('save_grib', False):
            date = save_grib(config)

        date = date or get_date(config)
        update_downloaded_dates(date, config.date_log_file)
        os.remove(config['temp_filename'])

    except Exception as e:
        logger.exception(
            f"Failed to process data for {config.get('date', 'unknown date')}: {e}"
        )
