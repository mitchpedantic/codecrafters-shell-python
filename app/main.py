from __future__ import annotations
import sys

import enum
from string import (whitespace)
from sys import (stdout, stderr)
from typing import (NoReturn, Callable)

class BuiltIn(str, enum.Enum):
    EXIT = "exit"
    ECHO = "echo"

def do_echo(line : str) -> int:
    stdout.write(
        " ".join(line.split()[1:]) + "\n"
    )
    return 0

def do_run(line : str) -> int:
    stderr.write("%s: command not found\n" % line)
    return 0

def do_exit(_ : str) -> int: return -1

def do_(request : BuiltIn) -> Callable[[str], int]:
    return {
        BuiltIn.EXIT : do_exit,
        BuiltIn.ECHO : do_echo,
    }.get(request, do_run)

def read() -> int:
    stdout.write("$ ")
    try:
        line : str = input()
        return do_(line.split(' ')[0])(line)
    except (EOFError, KeyboardInterrupt) as _:
        stdout.write("\n")
        return -1
    ...

def main() -> NoReturn:
    while (0 == read()):
        ...
    pass

if __name__ == "__main__":
    main()
