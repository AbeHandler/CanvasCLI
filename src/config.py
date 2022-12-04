from pathlib import Path
import configparser
from datetime import datetime
import os


class Config(object):
    def _str2date(self, str_):
        """
        format = YYYYMMDD
        """
        STANDARDDATE = "%Y%m%d"
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


if __name__ == "__main__":

    config = Config(Path("/Users/abe/CanvasCLI/3220S2023.ini"))
    print(config.days_of_week)
