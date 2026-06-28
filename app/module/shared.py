from __future__ import annotations

import enum

class BuiltIn(str, enum.Enum):
    COMPLETE = "complete"
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"
    PWD = "pwd"
    CD = "cd"