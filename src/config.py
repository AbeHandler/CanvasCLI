'''
An object to store the configurations for a course, which are loaded from an ini
'''
from pathlib import Path
import configparser
from datetime import datetime
import os

STANDARDDATE = "%Y%m%d"


class Config(object):
    def _str2date(self, str_):
        """
        format = YYYYMMDD
        """
        data_date = datetime.strptime(str_, STANDARDDATE)
        return data_date

    def __init__(self, path_to_file: Path) -> None:
        assert (
            path_to_file.is_file()
        ), "Config file not found. Do you have the wrong semester?"
        config = configparser.ConfigParser()
        config.read(path_to_file.as_posix())

        self.start_date = self._str2date(config["dates"]["start_date"])
        self.end_date = self._str2date(config["dates"]["end_date"])

        self.canvas_no = config["course_info"]["canvas_no"]
        self.course_name = config["course_info"]["course_name"]
        self.start_time = config["course_info"]["start_time"]
        self.end_time = config["course_info"]["end_time"]
        self.weeks = config["course_info"]["weeks"]
        self.main_page = config["course_info"]["main_page"]
        self.days_of_week = config["course_info"]["days_of_week"].split(",")
        self.daily_bullets = config["course_info"]["daily_bullets"].split(",")
        self.submitted_location = Path(config["nbgrader"]["base_dir"]) / "submitted"
        self.path_to_autograded = Path(config["nbgrader"]['base_dir']) / "autograded"
        self.path_to_feedback = Path(config["nbgrader"]["base_dir"]) / "feedback"
        self.path_to_autograde_script = Path(config["nbgrader"]["base_dir"]) / config["nbgrader"]["path_to_autograde_script"]
        self.path_to_grades = Path(config["nbgrader"]["base_dir"]) / config["nbgrader"]["path_to_grades"]
        self.front_page_date_tag_in_html = config["course_info"]["front_page_date_tag_in_html"]
        self.data_bullet_tag_in_html = config['course_info']["data_bullet_tag_in_html"]
        self.max_score = float(config['assignment_configs']['max_score'])
        groups = config['assignment_configs']['groups'].split(",")
        weights = config['assignment_configs']['weights'].split(",")
        self.group2weight = {k: v for k, v in zip(groups, weights)}



if __name__ == "__main__":

    config = Config(Path("/Users/abe/CanvasCLI/3220F2023.ini"))
    print(config.days_of_week)
