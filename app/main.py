from __future__ import annotations

import os
import enum
import subprocess
from sys import (stdout, stderr)
from typing import (NoReturn, Callable, Optional)

__old_pwd__ : str = None

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

def do_exit(*args) -> int: return -1

def do_echo(_ : str, *args : list[str]) -> int:
    stdout.write(
        " ".join(args) + "\n"
    )
    return 0

def do_type(_ : str, *args : list[str]) -> int:
    if len(args) > 0:
        type_of : str = args[0]
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

def do_pwd(*args : list[str]) -> int:
    stdout.write(
        os.getcwd() + "\n"
    )
    return 0

def do_cd(_ : str, *args : list[str]) -> int:
    global __old_pwd__
    ...
    new_dir : str = None
    if len(args) == 0 or args[0] == "~":
        new_dir = os.environ["HOME"]
    elif args[0] == "-":
        new_dir = __old_pwd__
        if new_dir is None:
            stderr.write("Old PWD not set\n" )
            return 0
    else:
        new_dir = args[0]
    try:
        tmp = os.getcwd()
        os.chdir(new_dir)
        __old_pwd__ = tmp
    except FileNotFoundError as _:
        stderr.write("%s: No such file or directory\n" % args[0])
    return 0

def do_run(cmd : str, *args : list[str]) -> int:
    if look_up(cmd) is not None:
        subprocess.run(args)
    else:
        stderr.write("%s: command not found\n" % cmd)
    return 0


def do_(request : BuiltIn) -> Callable[[str], int]:
    return {
        BuiltIn.EXIT : do_exit,
        BuiltIn.ECHO : do_echo,
        BuiltIn.TYPE : do_type,
        BuiltIn.PWD  : do_pwd,
        BuiltIn.CD   : do_cd,

    }.get(request, do_run)

def split_args(line : str) -> list[str]:
    # uses an algorithm similar to Dijkistra's two stacks
    args : list[str] = []
    current = ""
    quoted, mark = False, None
    for c in line.rstrip():
        if not quoted:
            if (c == '"' or c == "'"):
                quoted, mark = True, c
                continue
            if c == " " and len(current) > 0:
                args.append(current)
                current = ""
                continue
            ...
        elif quoted and c == mark:
            quoted, mark = False, None
            continue
        current += c
        ...
    args.append(current)
    print(args)
    return args

def read() -> int:
    stdout.write("$ ")
    try:
        line : str = input()
        args = split_args(line)
        return\
            do_(args[0])(*args) if len(args) != 0 else 0
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
