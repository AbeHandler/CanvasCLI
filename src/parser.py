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
    subparsers = parser.add_subparsers(help='sub-command help', dest='command')

    parser.add_argument(
        "-date",
        dest="date",
        default=None,
        help="pass a date in YYYYMMDD for the date, e.g. 20200824",
    )

    parser.add_argument("-export", 
                         action="store_true",
                         default=False)

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


    parser.add_argument(
        "-checkin",
        "-c",
        dest="checkin",
        default=False,
        action="store_true",
        help="Do a check in for the class"
    )

    parser.add_argument(
        "-curve",default=False,action="store_true"
    )

    parser_a = subparsers.add_parser('grade', help='a help')
    parser_a.add_argument("-participation", action="store_true", default=False, dest="grade_participation")
    parser_a.add_argument("-assignment_id", dest="assignment_id", type=int)



    parser_a = subparsers.add_parser('assignment', help='a help')
    parser_a.add_argument("-download", action="store_true", default=False, dest="download_assignment", help="Download assignment files")
    parser_a.add_argument("-canvas_name", '-cn', help="Canvas name for assignment")
    parser_a.add_argument("-nb_grader_name", '-nbn',  dest="nb_grader_name", help="Name in nb_grader")
    parser_a.add_argument("-g", '-group', "--group", default="Exercises", help="Canvas group")
    parser_a.add_argument("-sync",  action="store_true", default=False, dest="assignment_sync", help="Assign grades on Canvas")
    parser_a.add_argument("-autograde", action="store_true", default=False, dest="assignment_autograde", help="Run the nb_grader autograder")
    parser_a.add_argument("-participation",  action="store_true", default=False, dest="participation_assignment")
    parser_a.add_argument('-perfects', action="store_true", default=False, dest="assignment_grade_perfects")
    parser_a.add_argument('-reports', action="store_true", default=False, dest="assignment_reports")



    args = parser.parse_args()

    if args.date is not None:
        args.date = datetime.strptime(args_date, "%Y%m%d")

    return args