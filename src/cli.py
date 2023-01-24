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


def link_url_for_in_class_assignment(assignment, course, main_page, due):

    assignment_id = assignment.id
    course_id = course.id
    template = "https://canvas.colorado.edu/courses/{}/assignments/{}"
    assignment_url = template.format(course_id, assignment_id)

    canvas_page = course.get_page(main_page)
    html = canvas_page.body
    soup = BeautifulSoup(html, features="html.parser")

    # data-date="20210924"

    results = soup.findAll(
        "li", {"data-date": due, "data-bullet": "in-class-assignment"}
    )

    assert len(results) == 1

    for a in results:
        a.string = ""
        p = soup.new_tag("a", href=assignment_url)
        p.string = "in-class assignment"
        a.append(p)

    html = str(soup)
    canvas_page.edit(wiki_page={"body": html})


def create_in_class_assignment(
    courseNo, due, name=None, points=3, published=False, group_id=166877
):

    # to find assignment groups ids do: https://canvas.colorado.edu/api/v1/courses/70073/assignment_groups

    course = canvas.get_course(CUnum2canvasnum[courseNo])

    due = datetime.strptime(due, "%Y%m%d")

    print("[*] Creating in-class assignment {} for {}".format(courseNo, due))

    if name is None:
        name = due.strftime("%b %d") + " : in-class"

    description = "Use this link to turn in your in-class work. You will be graded based on participation. You are NOT expected to work on this outside of class."

    group_id = get_in_class_assignment_group(course)

    new_assignment = course.create_assignment(
        {
            "name": name,
            "published": published,
            "due_at": due.strftime("%Y-%m-%d") + "T23:59:00",
            "points_possible": points,
            "description": description,
            "assignment_group_id": group_id.id,
            "submission_types": ["online_upload", "online_text_entry"],
        }
    )

    print("   - Added assignment to {}".format(course.name))
    print("   - {} ".format(name))

    return new_assignment



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

    print(args)

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

    if args.assignment:
        id_ = course.lookup_assignment_id(args.group, args.canvas_name)
        assignment = Assignment(course=course, assignment_id=id_)
        students = course.get_students()

        if args.download:
            assignment.download_submissions(students, 
                                            download_location=course.config.submitted_location,
                                            assignment_name=args.nb_grader_name)
        if args.autograde:
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