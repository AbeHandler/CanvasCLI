'''
Handles logic for reasoning about dates, which is very common
'''

from enum import Enum
from pathlib import Path
from src.config import Config
from datetime import datetime
from datetime import timedelta
from copy import copy
from typing import List
from typing import Dict
from collections import defaultdict
from src.config import STANDARDDATE


# class syntax
class Week(Enum):
    MON = 0
    TUES = 1
    WED = 2
    THRS = 3
    FRI = 4
    SAT = 5
    SUN = 6


def isb4(input_date):
    """
    Returns a function, f: date -> bool
    that is true if its input is less than or equal to input_date
    Used for a lambda in bs4
    """
    input_date = datetime.strptime(input_date, STANDARDDATE)

    def hidden(t):
        if "data-date" not in t.attrs:
            return False
        if datetime.strptime(t.attrs["data-date"], "%Y%m%d") <= input_date:
            return True
        else:
            return False

    return hidden

def get_tomorrow():
    day = date.today()
    day += timedelta(days=1)
    return day.strftime("%Y%m%d")


def get_weeks2dates(dates_for_course):

    weeks2dates = defaultdict(list)

    for d in dates_for_course:
        weeks2dates[d["week"]].append(d["date"])

    return weeks2dates


def get_dates_for_course(config: Config) -> List[Dict]:
    """
    return dates of all class meetings
    """
    assert type(config) == Config
    start = config.start_date
    end = config.end_date

    counter = start
    delta = timedelta(days=1)

    dates_for_course = []

    week = 1 # weeks start at 1, b/c it is for people (and is displayed in HTML)

    days_of_week = [Week[i].value for i in config.days_of_week]

    while counter < end:
        if counter.weekday() == Week.MON.value and counter != start:
            week += 1
        if counter.weekday() in days_of_week:
            dates_for_course.append({"date": copy(counter), "week": week})
        counter += delta
    return dates_for_course

if __name__ == "__main__":
    config = Config(Path("/Users/abe/CanvasCLI/3220S2023.ini"))
    print(get_dates_for_course(config))
    print(config.days_of_week)