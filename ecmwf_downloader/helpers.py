import warnings
from datetime import datetime, timedelta
from typing import List, Union


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


def adjust_date(date: Union[int, float, str],
                offset: int,
                date_format: str = '%Y%m%d') -> Union[int, float, str]:
    """
    Adjusts the given date by the specified offset. If the date is numeric, the offset is added directly.
    If the date is a string, it is converted to a datetime object, the offset is added, and the new date is returned
    as a string in the same format.

    Args:
        date (Union[int, float, str]): The date to adjust. Can be numeric (int/float) or a string.
        offset (int): The number of days to offset the date by.
        date_format (str): The format of the input date string. Default is '%Y-%m-%d'.

    Returns:
        Union[int, float, str]: The adjusted date. Returns a numeric date if the input was numeric,
                                or a string in the same format if the input was a string.
    """
    if isinstance(date, (int, float)):
        return date + offset
    elif isinstance(date, str):
        try:
            parsed_date = datetime.strptime(date, date_format)
            new_date = parsed_date + timedelta(days=offset)
            return new_date.strftime(date_format)
        except ValueError as e:
            raise ValueError(
                f"Invalid date format: {date}. Expected format is '{date_format}'."
            ) from e
    else:
        raise TypeError(
            f"Date must be either numeric (int/float) or a string in '{date_format}' format."
        )
