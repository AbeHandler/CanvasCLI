'''
Handles logic for the front page of the class
'''
from src.config import Config
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api
from src.course import Course
from bs4 import BeautifulSoup, Tag
from datetime import datetime
from datetime import date
from src.calendar import isb4
from src.config import STANDARDDATE

class FrontPage(object):
    '''
    Represents the front page on Canvas including
        - The HTML
        - The datetime parse
    '''

    def __init__(self, course):
        self.course = course
        self.canvas_page = self.course.course.get_page(self.course.course_name)
        self.html = self.canvas_page.body
        self.soup = BeautifulSoup(self.html, features="html.parser")
        self.front_page_date_tag_in_html = course.config.front_page_date_tag_in_html
        self.data_bullet_tag_in_html = course.config.data_bullet_tag_in_html


    def get_data_bullet(self, date, bullet_text="in-class-assignment"):

        '''date is in format STANDARDATE'''
        results = self.soup.find_all("li",
                                    attrs={self.front_page_date_tag_in_html: date,  
                                           self.data_bullet_tag_in_html: bullet_text})

        assert len(results) != 0, "no bullet selected"
        assert len(results) == 1, "there should only be one bullet selected"
        return results[0]


    def update_link(self, date, bullet_text, assignment_url):

        a = self.get_data_bullet(date, bullet_text)
        a.string = ""
        p = self.soup.new_tag("a", href=assignment_url)
        p.string = bullet_text
        a.append(p)
        html = str(self.soup)
        self.canvas_page.edit(wiki_page={"body": html})


    def show_before_date(self, threshold: str="20210315"):
        """update a page to show elements w/ data-date before some input date"""

        for header in self.soup.findAll(isb4(threshold)):
            if header.name == "li":
                header["style"] = "display:list-item"
            else:
                header["style"] = "display:block"

        html = str(self.soup)

        print("- Updating {} page to show before {}".format(self.course.course_name, threshold))

        self.canvas_page.edit(wiki_page={"body": html})


if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    course = Course(config=config, api=api)
    fp = FrontPage(course)
    fp.update_link(date="20230131",
                   bullet_text="interview", 
                   assignment_url="https://www.nytimes.com/")