
#! /opt/anaconda3/bin/python
# replace shebang w/ your local Python version

'''
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


'''

import glob
import os
import argparse
import configparser
from copy import copy
from jinja2 import Template
from canvasapi import Canvas
from datetime import datetime
from datetime import date
from datetime import timedelta
from collections import defaultdict
from bs4 import BeautifulSoup
import pandas as pd

from canvasapi.exceptions import CanvasException

STANDARDDATE = "%Y%m%d"


def str2date(str_):
    '''
    format = YYYYMMDD
    '''
    data_date = datetime.strptime(str_, STANDARDDATE)
    return data_date


def get_dates_for_course(ini_loc='3402S2021.ini', days_of_week=[0, 2, 4]):
    '''
    return all dates

    Days_of_week = [MON = 0, WED = 2, FRI = 4]
    '''
    MON = 0
    WED = 2
    FRI = 4
    config = configparser.ConfigParser()

    config.read(ini_loc)

    start = str2date(config['dates']["start"])
    end = str2date(config["dates"]["end"])

    counter = start
    delta = timedelta(days=1)

    dates_for_course = []

    week = 1

    while counter < end:
        if counter.weekday() in days_of_week:
            if counter.weekday() == MON and counter != start:
                week += 1
            dates_for_course.append({"date": copy(counter), "week": week})
        counter += delta
    return dates_for_course


def get_weeks2dates(dates_for_course):

    weeks2dates = defaultdict(list)

    for d in dates_for_course:
        weeks2dates[d["week"]].append(d['date'])

    return weeks2dates


'''
suspected dead code 9/2/21
def get_dates2weeks(dates_for_course):

    dates2weeks = {}

    for d in dates_for_course:
        dates2weeks[d['date'].strftime(STANDARDDATE)] = d["week"]

    return dates2weeks
'''


def makeHTMLforSemester(ini_loc="2301S2021.ini", course_no_canvas=70073, course_no_cu=2301):
    '''
    print out HTML for a whole course to copy/paste into Canvas Pages

    py canvas_cli.py -html -ini "2301S2021.ini" | pbcopy
    '''

    dates_for_course = get_dates_for_course(ini_loc=ini_loc)

    weeks2dates = get_weeks2dates(dates_for_course)

    weeks = list(weeks2dates.keys())

    template = Template('''<h3 data-date="{{week_start_date}}" style='display:none'> Week {{ week }}</h3>{% for row in dates %}\n<h4 data-date="{{row.strftime("%Y%m%d")}}" style='display:none'>{{row.strftime("%a %b %d")}}</h4>\n<ul data-date="{{row.strftime("%Y%m%d")}}" style='display:none'>\n{% for item in items %}<li style='display:none' data-date="{{row.strftime("%Y%m%d")}}" data-bullet="{{item | replace(" ", "-") }}">{{item}}</li>\n{% endfor %}</ul>{% endfor %}\n
                        ''')
    weeks.sort(reverse=True)

    out = ""

    for week in weeks:
        dates = weeks2dates[week]
        dates.sort(reverse=True)
        dates = [d for d in dates]
        bullets = ["in-class code", "whiteboards",
                   "recording", "in-class assignment", "quiz"]

        week_start_date = dates[-1].strftime(STANDARDDATE)
        out = out + template.render(week=week, dates=dates, items=bullets,
                                    week_start_date=week_start_date)

    course = canvas.get_course(course_no_canvas)

    lecture_page = course.get_page(course_no_cu)

    print("[*] Setting up {} page".format(course_no_cu))
    lecture_page.edit(wiki_page={"body": out})


def get_api():

    # Canvas API URL
    API_URL = "https://canvas.colorado.edu"
    # Canvas API key
    API_KEY = os.environ['CANVAS_TOKEN']

    # Initialize a new Canvas object
    return Canvas(API_URL, API_KEY)


def create_in_class_assignment(courseNo, due, name=None, points=3, published=False, group_id=166877):

    # to find assignment groups ids do: https://canvas.colorado.edu/api/v1/courses/70073/assignment_groups

    course = canvas.get_course(CUno2canvasno[courseNo])

    due = datetime.strptime(due, '%Y%m%d')

    print("[*] Creating in-class assignment {} for {}".format(courseNo, due))

    if name is None:
        name = due.strftime("%b %d") + " : in-class"

    description = "Use this link to turn in your in-class work. You will be graded based on participation. You are NOT expected to work on this outside of class."

    course.create_assignment({
        'name': name,
        'published': published,
        'due_at': due.strftime('%Y-%m-%d') + "T23:59:00",
        "points_possible": points,
        "description": description,
        "submission_types": ["online_upload", "online_text_entry"],
        "assignment_group_id": str(group_id),
    })

    print("   - Added assignment to {}".format(course.name))


def init_course_files(course_number):
    # See https://github.com/ucfopen/canvasapi/issues/415

    course = canvas.get_course(course_number)

    # Create a folder in canvas
    for week in range(1, 17):
        print("[*] Init folders week {}".format(week))
        parent = "/week{}/".format(week)
        for folder in FOLDERS:
            course.create_folder(name=folder, parent_folder_path=parent)


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

    The day of the week will be determined by the initial value of the now variable
    '''
    now = datetime(2020, 9, 11)
    for week in range(1, 17):
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
    course = canvas.get_course(CUno2canvasno["3401"])
    names = [o.replace('\n', "") for o in open("accomodations3401.txt")]
    names2ids_course = names2ids["3401"]

    To see this in the Canvas UI click "Moderate this quiz"
    https://community.canvaslms.com/t5/Instructor-Guide/Once-I-publish-a-quiz-how-can-I-give-my-students-extra-attempts/ta-p/1242
    $ canvas -set_extra_time_on_quizzes -c 3401
    '''
    ids = [names2ids_course[i] for i in names]

    for quiz in course.get_quizzes():
        print("[*] Setting accomodation for {}".format(quiz.title))
        for id_ in ids:
            print("-", id_)
            quiz.set_extensions(
                [{'user_id': id_, 'extra_time': extra_minutes}])


def export_all(CUno2canvasno):
    '''This will backup all courses on Canvas'''
    for course in CUno2canvasno:
        print("[*] Exporting {} from Canvas".format(course))
        course = canvas.get_course(CUno2canvasno[course])
        course.export_content(export_type="common_cartridge")


def get_lecture_page_body(lecture_page):
    '''
    Take the page of recorded lectures and add to it
    '''

    str_ = lecture_page.body
    body_start = str_.index("<ul>")
    body_end = str_.index("\r\n\r\n")

    return(str_[body_start:body_end])


def get_no_submissions(course, assignment):
    '''Get students who did not submit'''
    assignment = course.get_assignment(assignment)
    non_submitting_students = []
    for student in assignment.get_gradeable_students():
        id_ = student.id
        submission = assignment.get_submission(id_)
        if submission.submitted_at is None:
            non_submitting_students.append(student)
    return non_submitting_students


def update_roll_call(course, roll_call_attendance_no, canvas_student_name, canvas_student_id, excused):
    '''
    - Canvas has a built in roll call attendance feature
    - Each student automatically is submitted to roll call attendance
    - Write their history to your_attendance.csv and upload to justify attendance
    '''

    # print(canvas_student_name)
    attendance_csv = get_student_attendance(canvas_student_name)
    assignment = course.get_assignment(assignment=roll_call_attendance_no)
    submission = assignment.get_submission(canvas_student_id)  # student id

    # 5 free excused absences
    score = (sum(attendance_csv["present"]) +
             excused[canvas_student_id])/len(attendance_csv["present"])

    score = 1.0 if score > 1.0 else score

    print(canvas_student_name, score * 100)

    submission.edit(submission={'posted_grade': int(
        score * 100)}, comment={'present'})

    '''
    Not used
    attendance_csv.to_csv("your_attendance.csv", index=False)
    try:
        submission.edit(submission={'posted_grade': int(score * 100)}, comment={'present'})
        # write student's attendance history to a csv called history.csv
        submission.upload_comment("your_attendance.csv") # reference
    except CanvasException:
        print("error on {}".format(canvas_student_name))
    '''


def get_student_attendance(name, folder="3402"):
    '''
    Input: a CU email
    Output: a dataframe saying when they were present or not
    Assumes you run py atttendence.py to fill folder (e.g. 3402)

    Matches based on last name lower case. If that is not unique matches on first 3 of first
    This is sufficient for 3402
    '''
    name = name.replace("'", "")

    # print(name)

    all_ = pd.concat(pd.read_csv(fn) for fn in glob.glob(folder + "/pro*"))

    #import ipdb;ipdb.set_trace()

    all_["last"] = all_["name"].apply(
        lambda x: x.split()[-1].lower().replace("'", ""))
    all_["first3"] = all_["name"].apply(lambda x: x.split()[0].lower()[0:3])

    all_["date"] = all_["date"].apply(lambda x: str(x))

    dates = pd.DataFrame(all_["date"].unique())
    dates.columns = ["date"]

    dates["date"] = dates["date"].apply(
        lambda x: datetime.strptime(str(x), "%Y%m%d"))

    dates.sort_values(by='date', inplace=True)

    dates["date"] = dates["date"].apply(
        lambda x: datetime.strftime(x, "%Y%m%d"))

    # get student values
    stu = all_[all_['last'] == name.split()[-1].lower()]

    # merge on all dates
    stu = pd.merge(dates, stu, how="outer", on=["date"])

    stu = stu.fillna(0)

    unique_names = [j for j in stu.name.unique().tolist() if type(j) == str]
    if len(unique_names) > 1:

        # additional matching on first 3 chars of first name
        stu = stu[stu['first3'] == name.split()[0].lower()[0:3]]

    stu = stu[["date", 'present', 'name']]
    stu["name"] = name

    return stu


def comment_and_grade_no_submission(assignment_id, student):
    '''
    Give 0 + comment "no submission" to student on assignment

    e.g.
    for student in get_no_submissions(course, assignment):
        comment_and_grade_no_submission(assignment_id=880992, student_id=student)
    '''
    assignment = course.get_assignment(assignment=assignment_id)
    submission = assignment.get_submission(student.id)  # student id
    #print("- Setting {} score to zero".format(student))

    submission.edit(submission={'posted_grade': 0}, comment={
                    'text_comment': 'no submission'})


def make_link(title="D19-5414.pdf",
              link_text="in-class code",
              href="https://canvas.colorado.edu/courses/62535/files/27550350/preview"):
    '''make a link to a file that can be pasted into Canvas'''
    css_class = "instructure_file_link instructure_scribd_file"
    endpoint = "/".join(href.split("/")[0:-1])

    # needs to be 1 line?
    t = Template(
        '''<a class="{{css_class}}" title="{{title}}" href="{{href}}" target="_blank"  rel="noopener" data-api-endpoint="{{endpoint}}" data-api-returntype="File">{{link_text}}</a>''')
    return t.render(css_class=css_class, link_text=link_text,
                    title=title, href=href, endpoint=endpoint)


def show_before_date(course, main_page, in_date='20210315'):
    '''update a page to show elements w/ data-date before some input date'''

    def isb4Eq(input_date):
        '''
        Returns a function, f: date -> bool
        that is true if its input is less than or equal to input_date
        Used for a lambda in bs4
        '''
        input_date = datetime.strptime(input_date, '%Y%m%d')

        def hidden(t):
            if 'data-date' not in t.attrs:
                return False
            if datetime.strptime(t.attrs['data-date'], '%Y%m%d') <= input_date:
                return True
            else:
                return False
        return hidden

    canvas_page = course.get_page(main_page)

    html = canvas_page.body
    soup = BeautifulSoup(html, features="html.parser")

    for header in soup.findAll(isb4Eq(in_date)):
        if(header.name == "li"):
            header['style'] = "display:list-item"
        else:
            header['style'] = "display:block"

    html = str(soup)

    print("[*] Updating {} page to show before {}".format(main_page, in_date))

    canvas_page.edit(wiki_page={"body": html})


def comment_and_grade_participation(assignment_id, student, course):
    '''
    Give 0 + comment "no submission" to student on assignment

    e.g.
    for student in get_no_submissions(course, assignment):
        comment_and_grade_no_submission(assignment_id=880992, student_id=student)
    '''
    assignment = course.get_assignment(assignment=assignment_id)
    submission = assignment.get_submission(student.id)  # student id

    if submission.submitted_at is None:
        print('- No submission yet for {}'.format(student))
        submission.edit(
            submission={'posted_grade': 0, 'comment': "no submission"})
    else:
        print("- Setting {} score to full".format(student))
        submission.edit(
            submission={'posted_grade': assignment.points_possible})


def get_peer_reviews(course, assignment_id):
    '''
    Get the peer review scores for an assignment_id for a course

    thanks to Brian Keegan for this code

    '''

    _assignment = course.get_assignment(assignment_id)

    # Get peer reviews
    _pr_l = [{'submitter_user_id': _pr.user_id,
              'assessor_user_id': _pr.assessor_id,
              'asset_id': _pr.asset_id,
              'state': _pr.workflow_state}
             for _pr in _assignment.get_peer_reviews()]

    # Get peer review assessments
    _assignment_rubric = _assignment.rubric_settings['id']
    _ra_l = [{'asset_id': _a['artifact_id'],
              'assessor_user_id':_a['assessor_id'],
              'score':_a['score']}
             for _a in course.get_rubric(_assignment_rubric, include='peer_assessments', style='full').assessments]

    # Combine
    _assignment_pr_assessment_df = pd.merge(
        left=pd.DataFrame(_pr_l),
        right=pd.DataFrame(_ra_l),
        left_on=['assessor_user_id', 'asset_id'],
        right_on=['assessor_user_id', 'asset_id'],
        how='outer'
    )

    return _assignment_pr_assessment_df


def assign_grades_if_peer_review_exists(course, assignment_id):
    '''
    Assign a student's grade based on peer review, if it exists

    thanks to Brian Keegan for this code
    '''
    _assignment = course.get_assignment(assignment_id)
    _assignment_pr_assessment_df = get_peer_reviews(course, assignment_id)
    for r in _assignment_pr_assessment_df.to_dict('records'):
        if r['state'] == 'completed':
            _assignment.get_submission(r['submitter_user_id']).edit(submission={
                'posted_grade': r['score']}, comment={'text_comment': "Peer review grade"})
        else:
            print("[*] Warning no review {}".format(r))


def find_missing_peer_reviews(course, assignment_id):
    '''
    Assign a student's grade based on peer review, if it exists

    thanks to Brian Keegan for this code
    '''
    _assignment_pr_assessment_df = get_peer_reviews(course, assignment_id)
    out = []
    for r in _assignment_pr_assessment_df.to_dict('records'):
        if r['state'] != 'completed':
            out.append(r)
    return out


def get_in_class_assignment_group(course):
    '''Get the in-class assignment group for the course'''
    for i in course.get_assignment_groups():
        if "In-class assignments" in str(i):
            id_ = i.id

    return course.get_assignment_group(id_)


def get_in_class_assignments_for_course(course):
    '''return the in-class assignments for a course'''
    gp = get_in_class_assignment_group(course)
    assignments = []
    for assignment in course.get_assignments_for_group(gp.id):
        assignments.append(assignment)
    return assignments


def get_ungraded_in_class_assignments_for_course(course):
    '''
    Return the in-class assignments for a course if no grades have
    been assigned yet for the whole class
    '''
    ids = set()
    for j in get_in_class_assignments_for_course(course):
        any_graded = False
        for user in course.get_users(enrollment_type=['student']):
            sub = j.get_submission(user=user.id)
            if sub.graded_at != None:
                any_graded = True
        if not any_graded:
            ids.add(j.id)
    return ids


def grade_in_class_assignments(course):
    '''Grade ungraded in-class assignments (for participation)'''
    for assignment_id in get_ungraded_in_class_assignments_for_course(course):
        assignment = course.get_assignment(assignment_id)
        gradable_students = assignment.get_gradeable_students()
        if len(gradable_students) > 0:
            print(assignment.name)
            for student in gradable_students:
                comment_and_grade_participation(
                    assignment.id, student, course=course)


def deduct_for_missing_reviews(course, assignment_id):
    '''
    Assign a student's grade based on peer review, if it exists

    thanks to Brian Keegan for this code
    '''

    missing = find_missing_peer_reviews(course, assignment_id)

    _assignment = course.get_assignment(assignment_id)

    # Deduct points from submissions missing peer reviews
    for r in missing:
        try:
            _current_score = _assignment.get_submission(
                r['assessor_user_id']).score
            _penalty = round(_assignment.points_possible * .1)
            _penalty_score = _current_score - _penalty
            if _penalty_score < 0:
                _penalty_score = 0

            _assignment.get_submission(r['assessor_user_id']).edit(submission={'posted_grade': _penalty_score},
                                                                   comment={'text_comment': "Incomplete peer review, grade dropped by 10%"})
            print("[*] deducted", r)
        except TypeError:
            print(r, _assignment.get_submission(r['assessor_user_id']))
            print(
                "Assessor {0}'s assignment has not been submitted/graded".format(r['assessor_user_id']))
            pass


def init_groups(course, config):

    course = canvas.get_course(CUno2canvasno[args.course])
    groups = config["assignment_configs"]
    names = groups["groups"].split(",")
    weights = groups["weights"].split(",")
    assert len(names) == len(weights)
    for name, weight in zip(names, weights):
        course.create_assignment_group(name=name, group_weight=weight)


def get_day(args_date, tomorrow):
    '''
    A helper method for --visible
    '''
    day = date.today()
    if tomorrow:
        day += timedelta(days=1)
    elif args_date != "None":
        day = datetime.strptime(args_date, '%Y%m%d')
    return day.strftime("%Y%m%d")


def read_configs():
    CUno2canvasno = {}
    Canvasno2mainpage = {}
    CUno2Classtime = {}
    CUno2_dates_for_course = {}

    with open(INI_DIR + "/" + "semester.txt", "r") as inf:
        for course in inf:

            course = course.replace("\n", "")
            INI_LOC = INI_DIR + "/" + course + SEMESTER + ".ini"
            dates_for_course = get_dates_for_course(INI_LOC)
            assert os.path.isfile(
                INI_LOC), "Config file not found. Do you have the wrong semester?"
            config = configparser.ConfigParser()
            config.read(INI_LOC)
            CUno2canvasno[config["course_info"]["course_name"]] = int(
                config["course_info"]["canvas_no"])
            Canvasno2mainpage[int(config["course_info"]["canvas_no"]
                                  )] = config["course_info"]["main_page"]

            CUno2Classtime[course] = config["course_info"]["end_time"]

    return {"CUno2canvasno": CUno2canvasno,
            "CUno2Classtime": CUno2Classtime,
            "CUno2datesforcourse": CUno2_dates_for_course,
            "Canvasno2mainpage": Canvasno2mainpage}


def get_names2ids(CUno2canvasno):
    names2ids = {}
    for coursename, courseno in CUno2canvasno.items():
        names2ids[coursename] = get_student_names2_ids(
            CUno2canvasno[coursename])
    return names2ids


def run_all_visible(args, configs):
    CUno2canvasno = configs["CUno2canvasno"]
    Canvasno2mainpage = configs["Canvasno2mainpage"]
    day = get_day(args.date, args.tomorrow)
    for course_no in CUno2canvasno.values():
        course = canvas.get_course(course_no)
        show_before_date(course=course,
                         main_page=Canvasno2mainpage[course_no],
                         in_date=day)


if __name__ == "__main__":

    # TODO this is a global variable. Fix.
    canvas = get_api()

    INI_DIR = "/Users/abramhandler/CanvasCLI"

    FOLDERS = ['assignment_files', 'in-class-code',
               'other_files', 'quiz_files', 'whiteboards']

    parser = argparse.ArgumentParser()

    # TODO alphabetize
    parser.add_argument('-a', '-assignment', '--assignment', dest='assignment',
                        default=False, action='store_true', help='Use this flag to create an assignment')

    parser.add_argument('-all_visible', '--all_visible', dest='all_visible',
                        default=False, action='store_true')

    parser.add_argument('-attendance', '--attendance', dest='attendance',
                        default=False, action='store_true', help='Take attendance')

    parser.add_argument('--assignment_id', dest="assignment_id",
                        help='Assignment ID for no submission')

    parser.add_argument('-c', '-course', '--course',
                        default=None, help='INFO course number, e.g. 4604')

    parser.add_argument('-cron', '--cron', action='store_true',
                        help='run maintence jobs', dest='cron', default=False)

    parser.add_argument('-d', '-due', '--due',
                        help='pass a date in YYYYMMDD for the due date, e.g. 20200824')

    parser.add_argument('-date', dest='date', default="None",
                        help='pass a date in YYYYMMDD for the date, e.g. 20200824')

    parser.add_argument('-e', '-export', '--export', dest='export',
                        help='Export all', default=False, action='store_true')

    parser.add_argument('-html', action='store_true',
                        help='print HTML for semester', dest='html', default=False)

    parser.add_argument('-init', '--init', dest='init', default=False,
                        action='store_true', help='Use this flag to init the course files on Canvas')

    parser.add_argument('-n', '-name', '--name',
                        help='the name of the quiz or assignment')

    parser.add_argument('-p', '-points', '--points',
                        dest='points', default=3, type=int)

    parser.add_argument('--participation', action='store_true',
                        help='assigns full points to students who submitted', dest='participation', default=False)

    parser.add_argument('--publish', dest='publish', default=False, action='store_true',
                        help='Use this flag to immediately publish the assignment')

    parser.add_argument('--peer_review', dest='peer_review', default=False,
                        action='store_true', help='Use this flag to run peer reviews')

    parser.add_argument('-q', '-quiz', '--quiz', dest='quiz', default=False,
                        action='store_true', help='Use this flag to create a quiz')

    parser.add_argument('-set_extra_time_on_quizzes', dest='set_extra_time_on_quizzes', default=False,
                        action='store_true', help='Use this flag to set extra time on all quizzes for students w/ accomodations')

    parser.add_argument('-t', '-tomorrow', '--tomorrow', action='store_true',
                        help='syncs a directory to canvas', dest='tomorrow', default=False)

    parser.add_argument('-w', '-week', '--week', dest='week', type=int)

    parser.add_argument('-v', '-visible', '--visible', dest='visible',
                        default=False, action='store_true', help='Make html visible')

    parser.add_argument('-z', '-zeros', '--zeros', action='store_true',
                        help='assigns zeros to students who have not submitted', dest='zeros', default=False)

    args = parser.parse_args()

    if args.course is None and not args.all_visible and not args.cron:  # don't need to specify a course if args are visible
        print("[*] You must specify a course using the --course flag, unless you are doing all_visible")
        os._exit(0)

    SEMESTER = "F2021"

    configs = read_configs()
    CUno2canvasno = configs["CUno2canvasno"]
    Canvasno2mainpage = configs["Canvasno2mainpage"]
    CUno2Classtime = configs["CUno2Classtime"]

    names2ids = get_names2ids(CUno2canvasno)

    if args.cron:
        print("[*] Setting visible")
        run_all_visible(args, configs)

        print("[*] Running autograde")
        for course in ["2301"]: #CUno2canvasno:
            print("[*] checking {}".format(course))
            course = canvas.get_course(CUno2canvasno[course])
            grade_in_class_assignments(course)
        

    if args.attendance:
        # first run $py attendance.py
        course = canvas.get_course(CUno2canvasno[args.course])
        roll_call_attendance_no = config["course_info"]["roll_call_attendance_no"]

        # read in excused absences
        excused = config["attendance_info"]["excused"]
        excused = defaultdict(lambda: int(
            config["attendance_info"]["excused"]))

        for alt in config["attendance_info"].keys():
            if alt[0:7] == "student":
                student_no = int(alt.split("_")[1])
                excused[student_no] = int(config["attendance_info"][alt])

        canvasID2email = {}

        for u in course.get_users(enrollment_type=['student']):
            canvasID2email[u.id] = u.email
            try:
                update_roll_call(course=course,
                                 roll_call_attendance_no=roll_call_attendance_no,
                                 canvas_student_name=u.name,
                                 canvas_student_id=u.id,
                                 excused=excused)
            except AttributeError:
                print("-", "error on student ", u)

        os._exit(0)

    if args.visible:
        day = get_day(args.date, args.tomorrow)
        canvas_no = CUno2canvasno[args.course]
        course = canvas.get_course(CUno2canvasno[args.course])

        show_before_date(course=course,
                         main_page=Canvasno2mainpage[canvas_no],
                         in_date=day)

    if args.all_visible:
        run_all_visible(args, configs)

    # mostly used for 3402
    if args.participation and args.assignment_id is not None:
        course = canvas.get_course(CUno2canvasno[args.course])
        for student in assignment.get_gradeable_students():
            comment_and_grade_participation(
                args.assignment_id, student, course)
        os._exit(0)

    if args.zeros and args.assignment_id is not None:
        # py canvas_cli.py -c 2301 -zeros --assignmentid 871212
        course = canvas.get_course(CUno2canvasno[args.course])
        for student in get_no_submissions(course, args.assignmentid):
            comment_and_grade_no_submission(args.assignmentid, student)
        os._exit(0)

    if(args.set_extra_time_on_quizzes):
        course = canvas.get_course(CUno2canvasno[args.course])
        names = [o.replace('\n', "") for o in open(
            "accomodations{}.txt".format(args.course))]
        names2ids_course = names2ids[args.course]
        set_extra_time_on_quizzes(course, names, names2ids_course)
        os._exit(0)

    if(args.export):
        export_all(CUno2canvasno)
        os._exit(0)

    if(args.quiz):
        if args.due is None and args.tomorrow is None:
            print("[*] You must set a due date")
            os._exit(0)
        if args.due is None and args.tomorrow is not None:
            day = date.today()
            day += timedelta(days=1)
            args.due = day.strftime('%Y%m%d')
        course = canvas.get_course(CUno2canvasno[args.course])
        due = datetime.strptime(args.due, '%Y%m%d')
        if args.name is None:
            name = due.strftime("%b %d") + " quiz"
        else:
            name = args.name
        course.create_quiz({'title': name,
                            'published': args.publish,
                            'time_limit': 5,
                            "points_possible": args.points,
                            "due_at": args.due + "T" + CUno2Classtime[args.course]})
        print("[*] created quiz for {}".format(args.course))
        os._exit(0)

    if(args.assignment):

        # TODO auto link w/ HTML in Canvas
        # TODO put in the in-class assignment group. There is code for
        # that if you follow args.cron
        course = canvas.get_course(CUno2canvasno[args.course])

        if args.due is None:

            if args.tomorrow is False:
                print("[*] No due date, assuming it's for today")
                args.due = date.today().strftime('%Y%m%d')
            else:
                print("[*] Assignment is for tomorrow")
                args.due = (date.today() + timedelta(days=1)
                            ).strftime('%Y%m%d')
        elif args.due is not None:
            try:
                if args.due is not None:
                    datetime.strptime(args.due, '%Y%m%d')
            except ValueError:
                print(
                    "[*] The argument inClass needs to match the format YYYYMMDD. Won't make assignment.")

        create_in_class_assignment(
            courseNo=args.course, due=args.due, name=args.name, points=args.points)
        os._exit(0)

    if(args.init):
        '''
        Initialize course locally and on canvas
        Assumes ~/everything/teaching/courseno[S|F]year, e.g. 2301S2021
        '''
        print("- Init a course Canvas")

        # create the front page and set it as home on Canvas
        course = canvas.get_course(CUno2canvasno[args.course])
        course.create_page(wiki_page={"title": args.course,
                                      "published": True,
                                      "front_page": True,
                                      "body": "Welcome!"})
        course.update(course={"default_view": "wiki"})

        print("- Init files on Canvas")
        init_course_files(CUno2canvasno[args.course])

        #print("- Init local files")
        print("- Init HTML")
        makeHTMLforSemester(ini_loc=INI_LOC,
                            course_no_canvas=CUno2canvasno[args.course],
                            course_no_cu=args.course)
        init_groups(course=course, config=config)
        os._exit(0)

    if(args.peer_review):
        if args.assignment_id is None:
            print("[*] You must enter an assignment_id")
        else:
            course = canvas.get_course(CUno2canvasno[args.course])
            assign_grades_if_peer_review_exists(course, args.assignment_id)
            deduct_for_missing_reviews(course, args.assignment_id)
