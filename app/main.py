from __future__ import annotations

import os
import enum
from sys import (stdout, stderr)
from typing import (NoReturn, Callable, Optional)

class BuiltIn(str, enum.Enum):
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"

def look_up(executable : str) -> Optional[str]:
    for directory in os.environ['PATH'].split(':'):
        if not os.path.exists(directory) : continue
        for item in os.listdir(directory):
            if os.path.isfile(item) and item == executable:
                return directory
            ...
        ...
    return None

def do_exit(_ : str) -> int: return -1

def do_echo(line : str) -> int:
    stdout.write(
        " ".join(line.split()[1:]) + "\n"
    )
    return 0

def do_type(line : str) -> int:
    if len(line.split()) > 1:
        type_of : str = line.split()[1]
        if type_of in BuiltIn.__members__.values():
            stdout.write(
                 "%s is a shell builtin" % type_of
            )
        else:
            location : str = look_up(type_of) 
            if location:
                stdout.write(
                    "%s is %s" % type_of, location
                )
            else:
                stdout.write(
                     "%s: not found" % type_of
                )
    stdout.write("\n")
    return 0
    
def do_run(line : str) -> int:
    stderr.write("%s: command not found\n" % line)
    return 0


def do_(request : BuiltIn) -> Callable[[str], int]:
    return {
        BuiltIn.EXIT : do_exit,
        BuiltIn.ECHO : do_echo,
        BuiltIn.TYPE : do_type,
    }.get(request, do_run)

def read() -> int:
    stdout.write("$ ")
    try:
        line : str = input()
        return do_(line.split()[0])(line)
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
