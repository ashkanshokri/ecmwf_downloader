from datetime import datetime
from typing import List
import warnings


def get_grib_date(data) -> datetime:
    """
    Retrieves the base date from the given data and checks if all dates are the same.

    Args:
        data: An object that contains a method `base_date` which returns a list of datetime objects.

    Returns:
        datetime: The common datetime object if all are the same.
                  If not, returns the first datetime object and raises a warning.
    """
    base_dates = data.base_date()
    return check_all_same(base_dates)


def check_all_same(values: List[datetime]) -> datetime:
    """
    Checks if all datetime values in a list are the same.

    Args:
        values (List[datetime]): A list of datetime objects.

    Returns:
        datetime: The common datetime object if all are the same.
                  If not, returns the first datetime object and raises a warning.
    """
    if len(values) == 0:
        raise ValueError("The list of datetime values is empty.")

    first_value = values[0]

    if all(value == first_value for value in values):
        return first_value

    warnings.warn(
        "Not all datetime values in the list are the same. Returning the first value.",
        UserWarning)
    return first_value
