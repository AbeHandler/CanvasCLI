from src.config import Config
from canvasapi.canvas import Canvas
from pathlib import Path
from src.api import get_api

class Course(object):

    def __init__(self, config: Config, api: Canvas):
        self.config = config
        self.course = api.get_course(config.canvas_no)
        self.course_name = config.course_name


    def export(self):
        """This will create a course backup on Canvas"""
        self.course.export_content(export_type="common_cartridge")

    def print_assignment_groups(self):
        for i in self.course.get_assignment_groups():
            print(i)

if __name__ == "__main__":
    path = Path("/Users/abe/CanvasCLI/3220S2023.ini")
    config = Config(path)
    api = get_api()
    initializer = Course(config=config, api=api)
    initializer.print_assignment_groups()