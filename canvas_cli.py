#! /opt/anaconda3/bin/python 
# replace shebang w/ your local python version 

'''
An opinionated command-line interface to the canvas API.
- This will modify your canvas courses
- Start with your sandbox course when learning
- Mostly just a wrapper over https://github.com/ucfopen/canvasapi

Setup for CU users:
1. Go to https://canvas.colorado.edu/profile/settings and click "+ New Access Token"
2. in your local shell, run export CANVAS_TOKEN="my_secret_token"
3. Install the python client $pip install canvasapi

Questions and contact:
abram.handler@gmail.com
www.abehandler.com

To make an API call when logged into canvas do this 

https://canvas.colorado.edu/api/v1/courses/62535/assignment_groups

On my local machine, I "install" by symlinking to this script and aliasing it as "canvas"
    - In zshrc => alias canvas="canvas_cli.py"

'''

import glob
import time
import os
import argparse
from datetime import datetime
from canvasapi import Canvas
from datetime import datetime
from datetime import timedelta


def get_api():

    # Canvas API URL
    API_URL = "https://canvas.colorado.edu"
    # Canvas API key
    API_KEY = os.environ['CANVAS_TOKEN']

    # Initialize a new Canvas object
    return Canvas(API_URL, API_KEY)

# update an assignment
# https://canvas.instructure.com/doc/api/assignments.html#method.assignments_api.update


def create_in_class_assignment(courseNo, due, name, published=False):

    course = canvas.get_course(CU2Canvas[courseNo])

    due = datetime.strptime(due, '%Y%m%d')

    print("[*] Creating in-class assignment {} for {}".format(courseNo, due))

    course.create_assignment({
        'name': name,
        'published': published,
        'due_at': due.strftime('%Y-%m-%d') + "T23:59:00",
        "points_possible": 3
    })

    print("   - Added assignment to {}".format(course.name))


def init_course_files(course_number):
    # See https://github.com/ucfopen/canvasapi/issues/415

    course = canvas.get_course(course_number)

    # Create a folder in canvas
    for week in range(1, 17):
        print("[*] Init folders week {}".format(week))
        parent = "/week{}/".format(week)
        course.create_folder(name='quiz_files', parent_folder_path=parent)
        course.create_folder(name='assignment_files', parent_folder_path=parent)
        course.create_folder(name='other_files', parent_folder_path=parent)


def get_student_names2_ids(course_no):
    '''
    courseno = a canvas course number
    Returns a dictionary of names 2 student ids for this course
    note that maps student names to *canvas* student IDs
    '''
    out = {}
    course = canvas.get_course(course_no)
    for student in course.get_recent_students():
        out[student.name] = student.id
    return out


def init_quizzes(course):
    '''
    Initialize weekly quizzes for a course

    This code starts on week 3 b/c Brian already made the first 2 weeks of quizzes

    The day of the week will be determined by the initial value of the now variable
    '''
    now = datetime(2020, 9, 11)
    for week in range(3, 17):
        title = "Week {} ".format(str(week).zfill(2)) + "Quiz"
        time_limit = 10
        due_at = now.strftime('%Y-%m-%d') + "T11:20:00"
        unlock_at = now.strftime('%Y-%m-%d') + "T11:00:00"
        points_possible = 10
        now = now + timedelta(days=7)
        course.create_quiz({'title': title,
                            'published': False,
                            'time_limit': time_limit,
                            "points_possible": points_possible,
                            "unlock_at": unlock_at,
                            "due_at": due_at})


def set_extra_time_on_quizzes(course, names, names2ids_course, extra_minutes=10):
    '''
    course = canvas.get_course(CU2Canvas["3401"])
    names = [o.replace('\n', "") for o in open("accomodations3401.txt")]
    names2ids_course = names2ids["3401"]

    To see this in the Canvas UI click "Moderate this quiz"
    https://community.canvaslms.com/t5/Instructor-Guide/Once-I-publish-a-quiz-how-can-I-give-my-students-extra-attempts/ta-p/1242
    '''
    ids = [names2ids_course[i] for i in names]

    for quiz in course.get_quizzes():
        print("[*] Setting accomodation for {}".format(quiz.title))
        for id_ in ids:
            print("-", id_)
            quiz.set_extensions([{'user_id': id_, 'extra_time': extra_minutes}])


def export_all(CU2Canvas):
    for course in CU2Canvas:
        print("[*] Exporting {} from Canvas".format(course))
        course = canvas.get_course(CU2Canvas[course])
        course.export_content(export_type="common_cartridge")


if __name__ == "__main__":
    canvas = get_api()

    # Map CU course names to Canvas course names
    CU2Canvas = {"4604": 62561, "sandbox": 62535, "2301": 62559, "3401": 62560}

    # map course to in-class assignment groups
    COURSE2INCLASS = {"4604": "149100"}

    Course2Classtime = {"4604": "T12:40:00", "sandbox": "T12:40:00"}

    names2ids = {}
    for coursename, courseno in CU2Canvas.items():
        names2ids[coursename] = get_student_names2_ids(CU2Canvas[coursename])

    # TODO exports

    parser = argparse.ArgumentParser()

    parser.add_argument('-c', '-course', '--course', default='sandbox', help='INFO course number, e.g. 4604')

    parser.add_argument('-init_files', '--init_files', dest='init_files', default=False, action='store_true', help='Use this flag to init the course files on Canvas')

    parser.add_argument('-q', '-quiz', '--quiz', dest='quiz', default=False, action='store_true', help='Use this flag to create a quiz')

    parser.add_argument('-set_extra_time_on_quizzes', dest='set_extra_time_on_quizzes', default=False, action='store_true', help='Use this flag to set extra time on all quizzes for students w/ accomodations')

    parser.add_argument('-a', '-assignment', '--assignment', dest='assignment', default=False, action='store_true', help='Use this flag to create an assignment')

    parser.add_argument('-attachments', '--attachments', nargs='+', help='Input a list of globs; matching files will be uploaded', required=False)

    parser.add_argument('-d', '-due', '--due', help='pass a date in YYYYMMDD for the due date, e.g. 20200824')

    parser.add_argument('-n', '-name', '--name', help='the name of the quiz or assignment')

    parser.add_argument('-w', '-week', '--week', dest='week', type=int)

    parser.add_argument('-e', '-export', '--export', dest='export', help='Export all', default=False, action='store_true')

    parser.add_argument('-p', '-points', '--points', dest='points', default=10, type=int)

    parser.add_argument('-u', '-upload', '--upload', help='Uploads all files in this folder to canvas.', dest='upload', type=str)

    parser.add_argument('-s', '-sync', '--sync', action='store_true', help='syncs a directory to canvas', dest='sync', default=False)

    parser.add_argument('-time_limit', '--time_limit', default=10, help='time limit, in minutes')

    parser.add_argument('--publish', dest='publish', default='false', action='store_true', help='Use this flag to immediately publish the assignment')

    args = parser.parse_args()

    # test out overrides

    print(args)

    if(args.set_extra_time_on_quizzes):
        course = canvas.get_course(CU2Canvas[args.course])
        names = [o.replace('\n', "") for o in open("accomodations{}.txt".format(args.course))]
        names2ids_course = names2ids[args.course]
        set_extra_time_on_quizzes(course, names, names2ids_course)
        import os; os._exit(0)

    if(args.export):
        export_all(CU2Canvas)
        import os; os._exit(0)

    if(args.quiz):
        course = canvas.get_course(CU2Canvas[args.course])
        course.create_quiz({'title': args.name,
                            'published': args.publish,
                            'time_limit': args.time_limit,
                            "points_possible": args.points,
                            "due_at": args.due + "T" + Course2Classtime[args.course]})

    if(args.assignment):
        try:
            datetime.strptime(args.due, '%Y%m%d')
            create_in_class_assignment(courseNo=args.course, due=args.due, name=args.name)
        except ValueError:
            print("[*] The argument inClass needs to match the format YYYYMMDD. Won't make assignment.")

    if(args.init_files):
        init_course_files(CU2Canvas[args.course])

    if args.upload is not None and args.sync is False:
        # py canvas_cli.py -u ../2301fall2020/week2/assignment_files/ -c 2301 -w 2
        print("*uploading")

        def get_week_folder(course_no, week_no):
            course = canvas.get_course(CU2Canvas[args.course])
            for f in course.get_folders():
                if f.name == "week{}".format(args.week):
                    return f

        folder = get_week_folder(CU2Canvas[args.course], args.week)

        for fn in glob.glob(args.upload + "/*"):
            folder.upload(fn)

    if args.sync and args.week is not None:

        # $ canvas -w 3 -sync -c 2301

        def get_week_folder(course_no, week_no):
            course = canvas.get_course(CU2Canvas[args.course])
            for f in course.get_folders():
                if f.name == "week{}".format(args.week):
                    return f

        folder = get_week_folder(CU2Canvas[args.course], args.week)

        for subfolder in folder.get_folders():
            name = subfolder.name
            glb =  os.environ["ROOT"] +  "/everything/teaching/{}fall2020/week{}/{}/*".format(args.course, args.week, name)
            print(glb)
            for fn in glob.glob(glb):
                print("fn=", fn)
                print("[*] Uploading {} to {}".format(fn, name))
                subfolder.upload(fn, on_duplicate="overwrite")
