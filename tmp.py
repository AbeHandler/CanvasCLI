import argparse
import glob
import os
from src.api import get_api
from src.parser import get_args
from src.parser import get_day
from src.quiz_manager import QuizManager
from src.config import Config
from pathlib import Path
from src.course import Course
from src.front_page import FrontPage
from collections import defaultdict
from datetime import datetime
from datetime import date

from canvasapi.exceptions import CanvasException
from canvasapi.paginated_list import PaginatedList
from src.cli import get_course_from_ini

PATH_TO_INI = "/Users/abe/CanvasCLI/3220S2023.ini"

course = get_course_from_ini(PATH_TO_INI)

assignment = course.get_assignments_in_group("Exercises")
assignment_one = assignment[0]
from src.assignment import Assignment
from src.graders.one_off import Grader
students = course.get_students()
submissions = assignment_one.get_submissions(students)
type(submissions[0])