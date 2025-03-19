from datetime import datetime, timedelta
from pathlib import Path
import pandas as pd
from typing import List, Set

def get_filtered_dates(save_dir: Path, param: str, total_types: int) -> List[datetime]:
    """
    Retrieves and filters dates based on NetCDF files in a directory.
    
    :param save_dir: The root directory where parameter-specific files are stored.
    :param param: The parameter name used to locate relevant files.
    :param total_types: The minimum number of occurrences required for a date to be considered complete.
    :return: A sorted list of filtered datetime objects.
    """
    file_paths = (Path(save_dir) / param).glob("*.nc")
    
    date_strings = [p.stem.split('_')[1] for p in file_paths]
    
    # Find the dates that appear fewer than total_types times
    filtered_dates: Set[str] = {date for date in date_strings if date_strings.count(date) >= total_types}
    
    # Convert to datetime objects and sort
    return sorted(datetime.strptime(date, "%Y%m%d") for date in filtered_dates)

def get_missing_dates_df(dates: List[datetime]) -> pd.DataFrame:
    """
    Identifies missing dates and returns a DataFrame summarizing missing counts per month and year.
    
    :param dates: A sorted list of datetime objects.
    :return: A DataFrame with months as rows and years as columns, showing missing date counts.
    """
    missing_dates: List[datetime] = []
    for i in range(len(dates) - 1):
        next_day = dates[i] + timedelta(days=1)
        while next_day < dates[i + 1]:
            missing_dates.append(next_day)
            next_day += timedelta(days=1)
    
    # Create DataFrame with months as index and years as columns
    df = pd.DataFrame(index=range(1, 13), columns=range(2024, 2026))
    df[:] = 0
    
    for m, y in [(x.month, x.year) for x in missing_dates]:
        df.loc[m, y] += 1
    
    return df