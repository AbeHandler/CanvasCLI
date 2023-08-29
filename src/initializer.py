'''
Handles initialization for a course
'''
import time
import datetime
import pytz
from pathlib import Path
from src.config import Config
from src.api import get_api
from canvasapi.canvas import Canvas
from src.calendar import get_dates_for_course
from src.calendar import get_weeks2dates
from jinja2 import Template
from collections import defaultdict
from datetime import datetime, timedelta
from src.config import STANDARDDATE
from src.course import Course
from src.quiz_manager import QuizManager
from src.assignment_manager import AssignmentManager
from src.front_page import FrontPage

class Initializer(object):

    def __init__(self, course: Course, config: Config):
        self.course = course
        self.config = config

    def makeHTMLforSemester(self):
        html = self._build_html()
        lecture_page = self.course.get_front_page()
        lecture_page.edit(wiki_page={"body": html})

    def init_wiki_page(self):

        # create the front page and set it as home on Canvas
        self.course.course.create_page(
            wiki_page={
                "title": config.course_name,
                "published": True,
                "front_page": True,
                "body": "Welcome!",
            }
        )
        self.course.course.update(course={"default_view": "wiki"})


    def init_groups(self):

        for name, weight in self.config.group2weight.items():
            self.course.course.create_assignment_group(name=name, group_weight=weight)


    def init(self):
        self.init_groups()
        self.init_wiki_page()
        self.makeHTMLforSemester()
        print("[-] sleeping to let canvas catch up")
        time.sleep(30)

    def _build_html(self) -> str:

        dates_for_course = get_dates_for_course(self.config)

        weeks2dates = get_weeks2dates(dates_for_course)

        weeks = list(weeks2dates.keys())

        template = Template(
            """<h3 data-date="{{week_start_date}}" style='display:none'> Week {{ week }}</h3>{% for row in dates %}
            <h4 data-date="{{row.strftime(STANDARDDATE)}}" style='display:none'>{{row.strftime("%a %b %d")}}</h4>
            <ul data-date="{{row.strftime(STANDARDDATE)}}" style='display:none'>
            {% for item in items %}<li style='display:none' data-date="{{row.strftime(STANDARDDATE)}}" data-bullet="{{item | replace(" ", "-") }}">{{item}}</li>
            {% endfor %}</ul>{% endfor %}
            """
        )
        weeks.sort(reverse=True)

        out = ""

        for week in weeks:
            dates = weeks2dates[week]
            dates.sort(reverse=True)
            dates = [d for d in dates]
            bullets = config.daily_bullets

            week_start_date = dates[-1].strftime(STANDARDDATE)
            out = out + template.render(
                week=week,
                dates=dates,
                items=bullets,
                week_start_date=week_start_date,
                STANDARDDATE=STANDARDDATE,
            )

        return out

    def init_quizzes(self):
        dates_for_course = get_dates_for_course(self.config)

        quiz_group = self.course.get_assignment_group("Quizzes")
        for _ in dates_for_course:
            for section in [1, 2, 3]:
                day = _["date"]
                manager = QuizManager(quiz_group, self.course)
                manager.create(day,
                               time_limit=2, 
                               points=8,
                               section=section)

    def init_assignments(self, group = "Interview grading", points=1.5):
        dates_for_course = get_dates_for_course(self.config)

        dates_for_course = [o for o in dates_for_course] # if o["date"] >= datetime.today()]
        
        quiz_group = self.course.get_assignment_group(group)
        for no, _ in enumerate(dates_for_course):

            if _["date"].weekday() == 0:
                day = _["date"]
                one_week = timedelta(weeks=1)
                due = day + one_week

                manager = AssignmentManager(course=self.course)
                num = no + 1
                manager.create(due=due, group=group, points=points, title=f"Exercize #{num}")



    def update_quiz_links(self, course):

        quizzes = [o for o in course.course.get_quizzes()]
        fp = FrontPage(course)

        def title2text(title):
            if "section 3" in quiz.title:
                return "quiz3"
            if "section 2" in quiz.title:
                return "quiz2"
            if "section 1" in quiz.title:
                return "quiz1"

        for quiz in quizzes:
            due = assignment.due_at_date.astimezone(pytz.timezone('US/Mountain')).strftime(STANDARDDATE)
            text = title2text(quiz.title)
            db = fp.get_data_bullet(due, text)
            url = quiz.html_url
            
            fp.update_link(date=due,
                           bullet_text=text, 
                           assignment_url=url)


    def update_participation_links(self, course):

        fp = FrontPage(course)
        assignments = course.course.get_assignments_for_group(course.assigment_groups['Participation'])
        assignments = [o for o in assignments]

        for assignment in assignments:

            # these come back in UTX
            due = assignment.due_at_date.astimezone(pytz.timezone('US/Mountain')).strftime(STANDARDDATE)
            text = "participation"
            db = fp.get_data_bullet(due, text)
            url = assignment.html_url
            fp.update_link(date=due,
                           bullet_text=text, 
                           assignment_url=url)

if __name__ == "__main__":

    path = Path("/Users/abe/CanvasCLI/3220F2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(api=api, config=config)
    initializer = Initializer(course=course, config=config)

    #uncomment and run this
    #initializer.init()
    #import os; os._exit(0)

    # then uncomment and run this
    #initializer.init_assignments(group = "Participation")
    #initializer.init_quizzes()
    #import os; os._exit(0)
    
    # then uncomment and run this
    #initializer.update_participation_links(course)

    initializer.init_assignments(group = "Exercises", points=25)

