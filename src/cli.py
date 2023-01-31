#! /opt/anaconda3/bin/python
# replace shebang w/ your local Python version

"""
An opinionated command-line interface to the canvas API.
- This will modify your canvas courses
- Start with your sandbox course when learning
- Mostly just a wrapper over https://github.com/ucfopen/canvasapi

Setup for CU users:
1. Go to https://canvas.colorado.edu/profile/settings
    and click "+ New Access Token"
2. in your local shell, run export CANVAS_TOKEN="my_secret_token"
3. Install the python client $pip install canvasapi

Questions and contact:
abram.handler@gmail.com
www.abehandler.com

To make an API call when logged into canvas do this

https://canvas.colorado.edu/api/v1/courses/62535/assignment_groups

On my local machine, I "install" by symlinking to this script
and aliasing it as "canvas"
    - ln -s /Users/abramhandler/CanvasCLI/canvas_cli.py ~/bin/canvas_cli.py
    - In zshrc => alias canvas="canvas_cli.py"


"""

import argparse
import glob
import os
from src.api import get_api
from src.parser import get_args
from src.parser import get_day
from src.quiz_manager import QuizManager
from src.config import Config
from pathlib import Path
from src.course import Course
from src.front_page import FrontPage
from collections import defaultdict
from datetime import datetime
from datetime import date
from src.nb_grader_manager import NBGraderManager
from src.assignment import Assignment
from canvasapi.exceptions import CanvasException
from canvasapi.paginated_list import PaginatedList



def get_course_from_ini(path_to_ini: str = "/Users/abe/CanvasCLI/3220S2023.ini"):
    '''
    A convenience function which creates a course object
    from an ini file
    '''
    path = Path(path_to_ini)
    config = Config(path)
    api = get_api()

    course = Course(config=config,
                    api=api)

    return course


if __name__ == "__main__":

    args = get_args()

    PATH_TO_INI = "/Users/abe/CanvasCLI/3220S2023.ini"

    course = get_course_from_ini(PATH_TO_INI)

    if args.init:
        initializer = Initializer(config=config, api=api)
        os._exit(0)

    if args.visible:
        fp = FrontPage(course)
        day = get_day(args)
        fp.show_before_date(day)
        os._exit(0)

    if args.quiz:
        quiz_group = course.get_assignment_group("Quizzes")
        due = get_day(args)
        manager = QuizManager(quiz_group, course)
        manager.create(due)
        os._exit(0)

    if args.export:
        course.export()

    if args.download_assignment:
        id_ = course.lookup_assignment_id(args.group, args.canvas_name)
        assignment = Assignment(course=course.course, assignment_id=id_)
        students = course.get_students()

        assignment.download_submissions(students, 
                                        download_location=course.config.submitted_location,
                                        assignment_name=args.nb_grader_name)
        if args.autograde_assignment:
            nb_grader = NBGraderManager(course.config)
            nb_grader.run()
        os._exit(0)

    if args.export:
        id_ = course.lookup_assignment_id("Exercises", 'Week 01 Assignment')
        assignment = Assignment(course=course, assignment_id=id_)
        students = course.get_students()
        assignment.download_submissions(students, 
                                        download_location='',
                                        assignment_name="one")