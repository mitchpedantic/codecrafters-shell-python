from __future__ import annotations

import os
import enum
import subprocess
from sys import (stdout, stderr)
from typing import (NoReturn, Callable, Optional)

class BuiltIn(str, enum.Enum):
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"
    PWD = "pwd"
    CD = "cd"

def look_up(executable : str) -> Optional[str]:
    for directory in os.environ['PATH'].split(':'):
        if not os.path.exists(directory) : continue
        for item in os.listdir(directory):
            full_path : str = os.path.join(directory, item)
            if os.access(full_path, os.X_OK) and item == executable:
                return full_path
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
                    "%s is %s" % (type_of, location)
                )
            else:
                stdout.write(
                     "%s: not found" % type_of
                )
    stdout.write("\n")
    return 0

def do_pwd(_ : str) -> int:
    stdout.write(
        os.curdir
    )
    return 0

def do_run(line : str) -> int:
    args = line.split()
    if look_up(args[0]) is not None:
        subprocess.run(args)
    else:
        stderr.write("%s: command not found\n" % line)
    return 0


def do_(request : BuiltIn) -> Callable[[str], int]:
    return {
        BuiltIn.EXIT : do_exit,
        BuiltIn.ECHO : do_echo,
        BuiltIn.TYPE : do_type,
        BuiltIn.PWD  : do_pwd,
        BuiltIn.CD   : do_cd,

    }.get(request, do_run)

def read() -> int:
    stdout.write("$ ")
    try:
        line : str = input()
        return\
            do_(line.split()[0])(line) if len(line) != 0 else 0
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
