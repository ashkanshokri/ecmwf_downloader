import argparse

from ecmwf_downloader.logger_setup import setup_logger

from ecmwf_downloader.config.config import load_config
from ecmwf_downloader.download import get_data
from ecmwf_downloader import helpers as h

# Initialize logger
logger = setup_logger(__name__)


def main(config_path: str) -> None:
    """
    Main function that loads the configuration and initiates the data retrieval and processing.

    Args:
        config_path (str): Path to the configuration file.
    """
    config_path = h.resolve_config_path(config_path)
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
# example: python -m ecmwf_downloader.run test_config.yaml
# example: python -m ecmwf_downloader.run test_config
