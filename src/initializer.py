'''
Handles initialization for a course
'''
from pathlib import Path
from src.config import Config
from src.api import get_api
from canvasapi.canvas import Canvas
from src.calendar import get_dates_for_course
from src.calendar import get_weeks2dates
from src.calendar import STANDARDDATE
from jinja2 import Template
from collections import defaultdict


class Initializer(object):

    def __init__(self, config: Config, api: Canvas):
        self.config = config
        self.api = api
        self.course = api.get_course(config.canvas_no)

    def makeHTMLforSemester(self):
        html = self._build_html()
        lecture_page = self.course.get_page(config.course_name)
        lecture_page.edit(wiki_page={"body": html})

    def init_wiki_page(self):

        # create the front page and set it as home on Canvas
        
        self.course.create_page(
            wiki_page={
                "title": config.course_name,
                "published": True,
                "front_page": True,
                "body": "Welcome!",
            }
        )
        self.course.update(course={"default_view": "wiki"})


    '''
    This code was ported over from canvas_cli.py but does not work yet



    def init_quizzes(course):
        """
        Initialize weekly quizzes for a course

        The day of the week will be determined by the initial value of the now variable
        """
        now = datetime(2020, 9, 11)
        for week in range(1, 17):
            title = "Week {} ".format(str(week).zfill(2)) + "Quiz"
            time_limit = 10
            due_at = now.strftime("%Y-%m-%d") + "T11:20:00"
            unlock_at = now.strftime("%Y-%m-%d") + "T11:00:00"
            points_possible = 10
            now = now + timedelta(days=7)
            course.create_quiz(
                {
                    "title": title,
                    "published": False,
                    "time_limit": time_limit,
                    "points_possible": points_possible,
                    "unlock_at": unlock_at,
                    "due_at": due_at,
                }
            )
    '''

    def init_groups(self):

        for name, weight in self.config.group2weight.items():
            self.course.create_assignment_group(name=name, group_weight=weight)


    def init(self):
        self.init_wiki_page()
        self.makeHTMLforSemester()
        self.init_groups()

    def _build_html(self) -> str:

        dates_for_course = get_dates_for_course(self.config)

        weeks2dates = get_weeks2dates(dates_for_course)

        weeks = list(weeks2dates.keys())

        template = Template(
            """<h3 data-date="{{week_start_date}}" style='display:none'> Week {{ week }}</h3>{% for row in dates %}\n<h4 data-date="{{row.strftime("%Y%m%d")}}" style='display:none'>{{row.strftime("%a %b %d")}}</h4>\n<ul data-date="{{row.strftime("%Y%m%d")}}" style='display:none'>\n{% for item in items %}<li style='display:none' data-date="{{row.strftime("%Y%m%d")}}" data-bullet="{{item | replace(" ", "-") }}">{{item}}</li>\n{% endfor %}</ul>{% endfor %}\n
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
            )

        return out


if __name__ == "__main__":

    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    initializer = Initializer(config=config, api=api)
    initializer.init()

