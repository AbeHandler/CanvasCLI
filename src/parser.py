'''
Functions for parsing command-line inpue
'''

import argparse
import datetime

from datetime import timedelta
from datetime import date
from src.vars import DATE_FORMAT


def get_day(args) -> str:
    '''
    Returns a date in {today, tomorrow, dayaftertomorrow}

    In theory I guess you would want some other day line next 
    Wednesday but I never end up doing that. Maybe 
    another method like get_day_precise if args.date is not none
    '''

    if args.tomorrow or args.day_after_tomorrow:
        assert args.date is None, "You can't specify a date if you use the -t or -tt flag"

    if args.tomorrow and args.day_after_tomorrow:
        raise ValueError("You can't use the -t and -tt flag together")

    day = date.today()
    if args.tomorrow:
        day += timedelta(days=1)
    elif args.day_after_tomorrow:
        day += timedelta(days=2)
    else:
        day = day # the default, just adding for clarity

    return day.strftime(DATE_FORMAT)

def get_args():

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-date",
        dest="date",
        default=None,
        help="pass a date in YYYYMMDD for the date, e.g. 20200824",
    )

    parser.add_argument(
        "-init",
        "--init",
        dest="init",
        default=False,
        action="store_true",
        help="Use this flag to init the course files on Canvas",
    )

    parser.add_argument(
        "-t",
        "-tomorrow",
        "--tomorrow",
        action="store_true",
        help="syncs a directory to canvas",
        dest="tomorrow",
        default=False,
    )

    parser.add_argument(
        "-tt",
        action="store_true",
        help="syncs a directory to canvas",
        dest="day_after_tomorrow",
        default=False,
    )

    parser.add_argument(
        "-v",
        "--visible",
        dest="visible",
        default=False,
        action="store_true",
        help="Make html visible"
    )

    parser.add_argument(
        "-q",
        "-quiz",
        "--quiz",
        dest="quiz",
        default=False,
        action="store_true",
        help="Use to make a quiz"
    )

    args = parser.parse_args()

    if args.date is not None:
        args.date = datetime.strptime(args_date, "%Y%m%d")

    return args