from dataclasses import dataclass
from typing import List
from src.student import Student


@dataclass
class Grade:
    """A student's grade"""
    score: int
    comments: List[str]