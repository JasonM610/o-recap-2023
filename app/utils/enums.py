from enum import Enum


class Mode(Enum):
    OSU = "osu"
    TAIKO = "taiko"
    CATCH = "fruits"
    MANIA = "mania"


class Status(Enum):
    GRAVEYARD = "graveyard"
    WIP = "wip"
    PENDING = "pending"
    RANKED = "ranked"
    APPROVED = "approved"
    QUALIFIED = "qualified"
    LOVED = "loved"


class Grade(Enum):
    SSH = "XH"
    SH = "SH"
    SS = "X"
    S = "S"
    A = "A"
    B = "B"
    C = "C"
    D = "D"
    F = "F"
