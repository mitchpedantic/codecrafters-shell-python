from __future__ import annotations
import sys

import enum

from sys import (stdout, stderr)
from typing import (NoReturn, Callable)

class BuiltIn(str, enum.Enum):
    EXIT = "exit"

def do_run(line : str) -> int:
    stderr.write("%s: command not found\n" % line)
    return 0

def do_exit(_ : str) -> int: return -1

def do_(request : BuiltIn) -> Callable[[str], int]:
    return {
        BuiltIn.EXIT : do_exit,        
    }.get(request, do_run)

def read() -> int:
    stdout.write("$ ")

    try:
        line : str = input()
        return do_(line.split(' ')[0])(line)
    except EOFError as _:
        return -1
    ...

def main() -> NoReturn:
    while (0 == read()):
        ...
    pass

if __name__ == "__main__":
    main()
