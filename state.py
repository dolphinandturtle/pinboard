from enum import Enum, auto


class Action(Enum):
    IDLE = auto()
    CREATE = auto()
    REMOVE = auto()
    EDIT = auto()
    MOVE = auto()

class Environment(Enum):
    GLOBAL = auto()
    CARD = auto()
    ARROW = auto()

class StateCard(Enum):
    ISOLATED = auto()
    AXIOM = auto()
    THEOREM = auto()
    THESIS = auto()

class FlowArrow(Enum):
    UNI = auto()
    BI = auto()
