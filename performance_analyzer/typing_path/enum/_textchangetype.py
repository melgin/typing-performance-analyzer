from enum import Enum

class TextChangeType(Enum):
    ENTRY = 1
    DELETE = 2
    AUTO_CORRECT = 3
    AUTO_COMPLETE = 4
    NO_CHANGE = 5
