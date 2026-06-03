from __future__ import annotations
import sys

from typing import (NoReturn)
from sys import (stdout, stderr)

def body() -> int:
    stdout.write("$ ")

    try:
        line : str = input()
    except EOFError as _:
        return -1
    
    stderr.write("%s: command not found\n" % line)
    return 0

def main() -> NoReturn:
    while (0 == body()):
        ...
    pass

if __name__ == "__main__":
    main()
