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
from src.graders.nbgrader import NBGrader
from src.api import get_api
from src.parser import get_args
from src.parser import get_day
from src.quiz_manager import QuizManager
from src.config import Config
from pathlib import Path
from src.assignment_manager import AssignmentManager
from src.course import Course
from src.front_page import FrontPage
from collections import defaultdict
from datetime import datetime
from datetime import date
from src.graders.participation_grader import ParticipationGrader
from src.nb_grader_manager import NBGraderManager
from src.assignment import Assignment
from canvasapi.exceptions import CanvasException
from canvasapi.paginated_list import PaginatedList



def get_course_from_ini(path_to_ini: str = "/Users/abe/CanvasCLI/3220F2023.ini"):
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

    PATH_TO_INI = "/Users/abe/CanvasCLI/3220F2023.ini"

    course = get_course_from_ini(PATH_TO_INI)

    if args.command == "grade" and args.grade_participation:
        assert args.assignment_id is not None, "You must supply an assignment id to grade participation"
        assignment = Assignment(course=course, assignment_id=args.assignment_id)
        grader = ParticipationGrader(assignment=assignment, course=course)
        grader.grade_based_on_participation()

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
        os._exit(0)

    if args.command == "assignment" and args.participation_assignment:
        manager = AssignmentManager(course)
        day = get_day(args)

        day = datetime.strptime(day, config.STANDARDDATE)
        manager.create_assignment(day, group = "In-class coding", points_possible = 1)
        dt = day.strftime('%B %d')
        print(f"[*] Created assignment {dt}")
        os._exit(0)

    if args.command == "assignment" and args.assignment_reports:
        id_ = course.lookup_assignment_id(args.group, args.canvas_name)
        grader = NBGrader(course=course,
                          grades_location="/Users/abe/everything/teaching/S2023/3220/3220/grades.jsonl",
                          assignment_id=id_,
                          nbgrader_name=args.nb_grader_name,
                          autograded_location="/Users/abe/everything/teaching/S2023/3220/3220/autograded",
                          feedback_location="/Users/abe/everything/teaching/S2023/3220/3220/feedback")
        grader.upload_reports(assignment=args.nb_grader_name)
        os._exit(0)

    if args.command == "assignment" and args.assignment_sync:
        
        id_ = course.lookup_assignment_id(args.group, args.canvas_name)
        grader = NBGrader(course=course,
                          grades_location="/Users/abe/everything/teaching/S2023/3220/3220/grades.jsonl",
                          assignment_id=id_,
                          nbgrader_name=args.nb_grader_name,
                          autograded_location="/Users/abe/everything/teaching/S2023/3220/3220/autograded",
                          feedback_location="/Users/abe/everything/teaching/S2023/3220/3220/feedback")

        if args.assignment_grade_perfects:
            grader.grade_perfect_scores(assignment=args.nb_grader_name)

        if args.assignment_grade_skipped:
            grader.grade_skipped(assignment=args.nb_grader_name, dryrun=args.dryrun)
        
        if args.assignment_missed_challenge:
            grader.grade_missed_challenge(assignment=args.nb_grader_name, dryrun=args.dryrun)

        os._exit(0)

    if args.command == "assignment" and args.assignment_autograde:
        id_ = course.lookup_assignment_id(args.group, args.canvas_name)
        assignment = Assignment(course=course, assignment_id=id_)
        students = course.get_students()

        assignment.download_submissions(students, 
                                        download_location=course.config.submitted_location,
                                        assignment_name=args.nb_grader_name)

        nb_grader = NBGraderManager(course.config, args.nb_grader_name)
        nb_grader.run()
        os._exit(0)

    if args.students:
        for i in course.get_students():
            print(i)

    if args.curve:
        print(course.get_average_grade())

    if args.checkin:
        avg = course.get_average_grade()
        print("Average grade {:.2f}".format(avg))
        assignments = course.get_ungraded_assignments_in_group("In-class coding")
        for _ in assignments:
            print(_)