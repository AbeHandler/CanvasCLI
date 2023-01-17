'''
Handles logic for the front page of the class wiki
'''
from src.config import Config
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.course import Course
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from datetime import date

class FrontPage(object):


    def __init__(self, course):
        self.course = course

    def _isb4(self, input_date):
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

    def show_before_date(self, threshold: str="20210315"):
        """update a page to show elements w/ data-date before some input date"""

        canvas_page = self.course.get_front_page()

        html = canvas_page.body
        soup = BeautifulSoup(html, features="html.parser")

        for header in soup.findAll(self._isb4(threshold)):
            if header.name == "li":
                header["style"] = "display:list-item"
            else:
                header["style"] = "display:block"

        html = str(soup)

        print("- Updating {} page to show before {}".format(self.course.course_name, threshold))

        canvas_page.edit(wiki_page={"body": html})


if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    fp = FrontPage(course)