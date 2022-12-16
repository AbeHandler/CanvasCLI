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
from collections import defaultdict
from datetime import datetime
from datetime import timedelta
from datetime import date
import pandas as pd
from bs4 import BeautifulSoup, Tag

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


def get_student_names2_ids(course_no):
    """
    courseno = a canvas course number
    Returns a dictionary of names 2 student ids for this course
    note that maps student names to *canvas* student IDs
    """
    out = {}
    course = canvas.get_course(course_no)
    for student in course.get_recent_students():
        out[student.name] = student.id
    return out



def comment_and_grade_no_submission(assignment_id, student):
    """
    Give 0 + comment "no submission" to student on assignment

    e.g.
    for student in get_no_submissions(course, assignment):
        comment_and_grade_no_submission(assignment_id=880992, student_id=student)
    """
    assignment = course.get_assignment(assignment=assignment_id)
    submission = assignment.get_submission(student.id)  # student id
    # print("- Setting {} score to zero".format(student))

    submission.edit(
        submission={"posted_grade": 0},
        comment={"text_comment": "no submission"},
    )



def show_before_date(course, main_page, in_date="20210315"):
    """update a page to show elements w/ data-date before some input date"""

    def isb4Eq(input_date):
        """
        Returns a function, f: date -> bool
        that is true if its input is less than or equal to input_date
        Used for a lambda in bs4
        """
        input_date = datetime.strptime(input_date, "%Y%m%d")

        def hidden(t):
            if "data-date" not in t.attrs:
                return False
            if datetime.strptime(t.attrs["data-date"], "%Y%m%d") <= input_date:
                return True
            else:
                return False

        return hidden

    canvas_page = course.get_page(main_page)

    html = canvas_page.body
    soup = BeautifulSoup(html, features="html.parser")

    for header in soup.findAll(isb4Eq(in_date)):
        if header.name == "li":
            header["style"] = "display:list-item"
        else:
            header["style"] = "display:block"

    html = str(soup)

    print("\t - Updating {} page to show before {}".format(main_page, in_date))

    canvas_page.edit(wiki_page={"body": html})


def comment_and_grade_participation(assignment_id, student, course):
    """
    Give 0 + comment "no submission" to student on assignment

    e.g.
    for student in get_no_submissions(course, assignment):
        comment_and_grade_no_submission(assignment_id=880992, student_id=student)
    """
    assignment = course.get_assignment(assignment=assignment_id)
    submission = assignment.get_submission(student.id)  # student id

    if submission.submitted_at is None:
        print("\t - No submission yet for {}".format(student))
        submission.edit(
            submission={"posted_grade": 0, "comment": "no submission"}
        )
    else:
        print("\t - Setting {} score to full".format(student))
        submission.edit(submission={"posted_grade": assignment.points_possible})


def get_in_class_assignment_group(course):
    """Get the in-class assignment group for the course"""
    id_ = None
    for i in course.get_assignment_groups():
        if "In-class assignments" in str(i):
            id_ = i.id

    if id_ is None:
        print("Can't find a group called 'In-class assignments'.")
        import os

        os._exit(0)
    return course.get_assignment_group(id_)


def get_in_class_assignments_for_course(course):
    """return the in-class assignments for a course"""
    gp = get_in_class_assignment_group(course)
    assignments = []
    for assignment in course.get_assignments_for_group(gp.id):
        assignments.append(assignment)
    return assignments


def get_ungraded_in_class_assignments_for_course(course):
    """
    Return the in-class assignments for a course if no grades have
    been assigned yet for the whole class
    """
    ids = set()
    for j in get_in_class_assignments_for_course(course):
        any_graded = False
        for user in course.get_users(enrollment_type=["student"]):
            sub = j.get_submission(user=user.id)
            if sub.graded_at != None:
                any_graded = True
        if not any_graded:
            ids.add(j.id)
    return ids


def grade_in_class_assignments(course):
    """Grade ungraded in-class assignments (for participation)"""
    for assignment_id in get_ungraded_in_class_assignments_for_course(course):
        assignment = course.get_assignment(assignment_id)
        gradable_students = assignment.get_gradeable_students()
        if type(gradable_students) == PaginatedList:
            grade = True
        else:
            if len(gradable_students) > 0:
                grade = True

        if grade is True:
            print("\t Scoring {}".format(assignment.name))
            for student in gradable_students:
                comment_and_grade_participation(
                    assignment.id, student, course=course
                )


def get_day(args_date, tomorrow, day_after_tomorrow=False):
    """
    A helper method for --visible
    """
    day = date.today()
    assert (tomorrow and day_after_tomorrow) == False

    if tomorrow:
        day += timedelta(days=1)
    elif day_after_tomorrow:
        day += timedelta(days=2)
    elif args_date != "None":
        day = datetime.strptime(args_date, "%Y%m%d")
    return day.strftime("%Y%m%d")


def get_names2ids(CUnum2canvasnum):
    names2ids = {}
    for coursename, courseno in CUnum2canvasnum.items():
        names2ids[coursename] = get_student_names2_ids(
            CUnum2canvasnum[coursename]
        )
    return names2ids


def make_course_visible(args, configs, course_no):
    CUnum2canvasnum = configs["CUnum2canvasnum"]
    Canvasno2mainpage = configs["Canvasno2mainpage"]
    canvas_num = CUnum2canvasnum[course_no]
    day = get_day(args.date, args.tomorrow)
    canvas_course = canvas.get_course(CUnum2canvasnum[course_no])
    show_before_date(
        course=canvas_course,
        main_page=Canvasno2mainpage[canvas_num],
        in_date=day,
    )


def run_all_visible(args, configs):
    for course_no in CUnum2canvasnum.values():
        make_course_visible(args, configs, course_no)


def get_due_from_args(args) -> str:
    if args.due is None:

        if args.tomorrow is False:
            print("[*] No due date, assuming it's for today")
            return date.today().strftime("%Y%m%d")
        else:
            print("[*] Assignment is for tomorrow")
            return (date.today() + timedelta(days=1)).strftime("%Y%m%d")
    elif args.due is not None:
        try:
            if args.due is not None:
                return datetime.strptime(args.due, "%Y%m%d").strftime("%Y%m%d")
        except ValueError:
            print(
                "[*] The argument inClass needs to match the format YYYYMMDD. Won't make assignment."
            )


def get_tomorrow():
    day = date.today()
    day += timedelta(days=1)
    return day.strftime("%Y%m%d")



if __name__ == "__main__":

    parser = argparse.ArgumentParser()

    parser.add_argument(
        "-init",
        "--init",
        dest="init",
        default=False,
        action="store_true",
        help="Use this flag to init the course files on Canvas",
    )

    args = parser.parse_args()
    if args.init:
        path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
        config = Config(path)
        api = get_api()
        initializer = Initializer(config=config, api=api)

    import os

    os._exit(0)
    # rest is old code and suspect

    # TODO alphabetize
    parser.add_argument(
        "-a",
        "-assignment",
        "--assignment",
        dest="assignment",
        default=False,
        action="store_true",
        help="Use this flag to create an assignment",
    )

    parser.add_argument(
        "-all_visible",
        "--all_visible",
        dest="all_visible",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-attendance",
        "--attendance",
        dest="attendance",
        default=False,
        action="store_true",
        help="Take attendance",
    )

    parser.add_argument(
        "-assignment_id",
        "--assignment_id",
        dest="assignment_id",
        help="Assignment ID for no submission",
    )

    parser.add_argument(
        "-c",
        "-course",
        "--course",
        default=None,
        help="INFO course number, e.g. 4604",
    )

    parser.add_argument(
        "-cron",
        "--cron",
        action="store_true",
        help="run maintence jobs",
        dest="cron",
        default=False,
    )

    parser.add_argument(
        "-d",
        "-due",
        "--due",
        help="pass a date in YYYYMMDD for the due date, e.g. 20200824",
    )

    parser.add_argument(
        "-date",
        dest="date",
        default="None",
        help="pass a date in YYYYMMDD for the date, e.g. 20200824",
    )

    parser.add_argument(
        "-e",
        "-export",
        "--export",
        dest="export",
        help="Export all",
        default=False,
        action="store_true",
    )

    parser.add_argument(
        "-html",
        action="store_true",
        help="print HTML for semester",
        dest="html",
        default=False,
    )

    parser.add_argument(
        "-n", "-name", "--name", help="the name of the quiz or assignment"
    )

    parser.add_argument(
        "-p", "-points", "--points", dest="points", default=3, type=int
    )

    parser.add_argument(
        "--participation",
        action="store_true",
        help="assigns full points to students who submitted",
        dest="participation",
        default=False,
    )

    parser.add_argument(
        "--publish",
        dest="publish",
        default=False,
        action="store_true",
        help="Use this flag to immediately publish the assignment",
    )

    parser.add_argument(
        "-q",
        "-quiz",
        "--quiz",
        dest="quiz",
        default=False,
        action="store_true",
        help="Use this flag to create a quiz",
    )

    parser.add_argument(
        "-set_extra_time_on_quizzes",
        dest="set_extra_time_on_quizzes",
        default=False,
        action="store_true",
        help="Use this flag to set extra time on all quizzes for students w/ accomodations",
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

    parser.add_argument("-w", "-week", "--week", dest="week", type=int)

    parser.add_argument(
        "-v",
        "-visible",
        "--visible",
        dest="visible",
        default=False,
        action="store_true",
        help="Make html visible",
    )

    parser.add_argument(
        "-z",
        "-zeros",
        "--zeros",
        action="store_true",
        help="assigns zeros to students who have not submitted",
        dest="zeros",
        default=False,
    )

    SEMESTER = "S2023"

    configs = read_configs(INI_DIR, SEMESTER)
    CUnum2canvasnum = configs["CUnum2canvasnum"]
    Canvasno2mainpage = configs["Canvasno2mainpage"]
    CUno2Classtime = configs["CUno2Classtime"]

    # don't need to specify a course if args are visible
    if args.course is None and not args.all_visible and not args.cron:
        print(
            "[*] You must specify a course using the --course flag, unless you are doing all_visible"
        )
        os._exit(0)

    if args.cron and args.course is not None:

        print("[*] Setting visible")
        make_course_visible(args, configs, args.course)

        print("[*] Running participation points")

        print("[*] checking {}".format(args.course))
        course = canvas.get_course(CUnum2canvasnum[args.course])
        grade_in_class_assignments(course)


    if args.visible:
        day = get_day(args.date, args.tomorrow, args.day_after_tomorrow)
        canvas_no = CUnum2canvasnum[args.course]
        course = canvas.get_course(CUnum2canvasnum[args.course])

        show_before_date(
            course=course, main_page=Canvasno2mainpage[canvas_no], in_date=day
        )

    if args.all_visible:
        run_all_visible(args, configs)

    # mostly used for 3402
    if args.participation and args.assignment_id is not None:
        course = canvas.get_course(CUnum2canvasnum[args.course])
        for student in assignment.get_gradeable_students():
            comment_and_grade_participation(args.assignment_id, student, course)
        os._exit(0)

    if args.zeros and args.assignment_id is not None:
        # py canvas_cli.py -c 2301 -zeros --assignmentid 871212
        course = canvas.get_course(CUnum2canvasnum[args.course])
        for student in get_no_submissions(course, args.assignment_id):
            comment_and_grade_no_submission(args.assignment_id, student)
        os._exit(0)

    if args.set_extra_time_on_quizzes:
        names2ids = get_names2ids(CUnum2canvasnum)
        course = canvas.get_course(CUnum2canvasnum[args.course])
        names = [
            o.replace("\n", "")
            for o in open("accomodations{}.txt".format(args.course))
        ]
        names2ids_course = names2ids[args.course]
        set_extra_time_on_quizzes(course, names, names2ids_course)
        os._exit(0)

    if args.export:
        export_all(CUnum2canvasnum)
        os._exit(0)

    if args.quiz:

        create_quiz(
            due=args.due,
            tomorrow=args.tomorrow,
            course=args.course,
            publish=args.publish,
            points=args.points,
        )

    if args.assignment:

        course = canvas.get_course(CUnum2canvasnum[args.course])

        due = get_due_from_args(args)
        assert type(due) == str

        assignment = create_in_class_assignment(
            courseNo=args.course,
            due=due,
            name=args.name,
            published=True,
            points=args.points,
        )

        canvas_no = CUnum2canvasnum[args.course]
        main_page = Canvasno2mainpage[canvas_no]
        link_url_for_in_class_assignment(
            assignment=assignment, main_page=main_page, due=due, course=course
        )

        os._exit(0)

    if args.init:
        """
        Initialize a single course
        """
        ini_loc = INI_DIR + "/" + args.course + SEMESTER + ".ini"
        init_course(
            CUnum2canvasnum,
            course_no=args.course,
            config=configs,
            ini_loc=ini_loc,
        )
