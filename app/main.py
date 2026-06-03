from __future__ import annotations
import sys

from typing import (NoReturn)
from sys import (stdout, stderr)

def main() -> NoReturn:
    stdout.write("$ ")

    line : str = input()
    
    stderr.write("%s: command not found" % line)
    pass


if __name__ == "__main__":
    main()
