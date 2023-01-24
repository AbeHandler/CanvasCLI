from enum import Enum



class LetterGrade(Enum):
    A = 4.0
    A_MINUS = 3.7
    B_PLUS = 3.3
    B = 3.0
    B_MINUS = 2.7
    C_PLUS = 2.3
    C = 2.0
    C_MINUS = 1.7
    D_PLUS = 1.3
    D = 1.0
    D_MINUS = 0.0
    F = 0.0

if __name__ == "__main__":
    assert LetterGrade.A.value == 4.0