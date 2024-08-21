import argparse

from ecmwf_downloader.logger_setup import setup_logger

from ecmwf_downloader.config.config import load_config
from ecmwf_downloader.download import get_data
from ecmwf_downloader import helpers as h

# Initialize logger
logger = setup_logger(__name__)


def main(config_path: str, save_dir=None) -> None:
    """
    Main function that loads the configuration and initiates the data retrieval and processing.

    Args:
        config_path (str): Path to the configuration file.
    """
    config_path = h.resolve_config_path(config_path)
    config = load_config(config_path)

    if save_dir is not None:
        config['save_dir'] = save_dir

    get_data(config)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Download and process ECMWF data.")

    # Argument for the configuration file path
    parser.add_argument("config_path",
                        type=str,
                        help="Path to the configuration file.")

    # Argument for the save directory
    parser.add_argument(
        "--save_dir",
        type=str,
        default=None,
        help=
        "Directory where the data will be saved. Overrides the save_dir in the config if provided."
    )

    args = parser.parse_args()

    # Pass both arguments to the main function
    main(args.config_path, save_dir=args.save_dir)

# example: python -m ecmwf_downloader.run /Users/sho108/projects/ecmwf_downloader/ecmwf_downloader/configs/test_config.yaml --save_dir /path/to/save/dir
# example: python -m ecmwf_downloader.run test_config.yaml --save_dir /path/to/save/dir
