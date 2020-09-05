from datetime import datetime, timedelta
from dateutil.parser import parse
from nba_api.stats.library.parameters import Season


def date_to_str(date):
    return date.strftime('%m/%d/%Y')


def str_to_date(date_str):
    return parse(date_str)


# given a date string, returns the date string for the previous day
def yesterday(date_str):
    return date_to_str(str_to_date(date_str) - timedelta(1))

def start_year_to_season(start_year):
    return '{}-{}'.format(start_year, str(start_year + 1)[2:])


def get_season_start_and_end_dates(season_start_year):
    # october of start year to september of the next year
    return date_to_str(datetime(season_start_year, 10, 1)), date_to_str(datetime(season_start_year+1, 9, 1))


def get_season_for_date(date_str):
    if not date_str:
        return Season.default
    date = str_to_date(date_str)
    # if before October, the season is the last year to the current year
    # otherwise, the season is the current year to the next year
    # ex. 05/02/2020 -> 2019-20 season
    #     11/02/2020 -> 2020-21 season
    start_year = date.year
    if date.month < 10:
        start_year -= 1
    return start_year_to_season(start_year)
