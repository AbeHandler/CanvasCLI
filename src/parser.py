'''
Functions for parsing command-line inpue
'''

import argparse
import datetime

from datetime import timedelta
from datetime import date


def get_day(args):

    day = date.today()

    if args.tomorrow or args.day_after_tomorrow:
        assert args.date is None, "You can't specify a date if you use the -t or -tt flag"
    else:
        assert args.date != None, "You must specify a date if you don't use the -t or -tt flag"


    assert (args.tomorrow and args.day_after_tomorrow) == False, "You must either use the -t or -tt flag"

    if args.tomorrow:
        day += timedelta(days=1)
    elif args.day_after_tomorrow:
        day += timedelta(days=2)
    elif args.date != None:
        day = args.date
    return day.strftime("%Y%m%d")

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


    args = parser.parse_args()

    if args.date is not None:
        args.date = datetime.strptime(args_date, "%Y%m%d")

    return args