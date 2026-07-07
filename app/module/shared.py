from __future__ import annotations

import enum

class BuiltIn(str, enum.Enum):
    COMPLETE = "complete"
    HISTORY = "history"
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"
    JOBS = "jobs"
    PWD = "pwd"
    CD = "cd"