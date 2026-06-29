from __future__ import annotations

import os
import readline
import functools
import subprocess

from .shared import BuiltIn
from typing import (NoReturn, Callable, Optional)


def readline_setup(complete_callback : Callable[[object], Optional[str]]) -> NoReturn:
    _setup_delims()
    ...
    readline.set_completer(
        Completer(complete_callback)._completer_logic
    )
    readline.parse_and_bind("tab: complete")
    ...

def _setup_delims() -> NoReturn:
    delim = readline.get_completer_delims()
    readline.set_completer_delims(delim[:delim.find("-")] + delim[delim.find("-")+1:])
    ...

def set_environ(func):
    @functools.wraps(func)
    def wrapoper_set_environ(instance : Completer, buffer : str) -> list[str]:
        os.environ["COMP_LINE"] = buffer
        os.environ["COMP_POINT"] = f"{len(buffer)}"
        ...
        return_list = func(instance, buffer)
        ...
        os.environ["COMP_LINE"] = ""
        os.environ["COMP_POINT"] = ""
        return return_list
    return wrapoper_set_environ

class Completer:
    def __init__(self,
                 complete_callback : Callable[[object], Optional[str]]):
        self._complete_callback = complete_callback
        pass
    ...
    def _completer_logic(self, text : str, state : int) -> Optional[str]:
        completed : str = self._try_run(readline.get_line_buffer())
        if completed: # non empty
            return [*completed, None][state]
        return ([c + (" " if not c.endswith("/") else "") for c in _general_lookups() if c.startswith(text)] + [None])[state]
    ...
    @set_environ
    def _try_run(self, buffer : str) -> list[str]:
        candidates = []
        args = buffer.split()
        nargs = len(args)
        if nargs <= 3:
            if nargs < 3:
                args.extend([""]*(3 - nargs))
            else:
                args[1:] = args[:0:-1]
            script : Optional[str] = self._complete_callback(args[0])
            if script and os.path.isfile(script) and os.access(script, os.X_OK):
                candidates : list[str] = subprocess.run([script] + args, capture_output = True, text = True).stdout.splitlines()
                candidates = map(lambda c: c + ("" if c.endswith("/") else " "), candidates)
        return candidates

def _general_lookups() -> list[str]:
    to_completer = []
    buffer = readline.get_line_buffer()
    head, _ = os.path.split(buffer.split()[-1])
    if (not buffer.endswith(" ")) and len(head) > 0:
        _, dir, files = next(os.walk(head))
        ...
    else:
        if len(buffer.split()) <= 1 and not buffer.endswith(" "):
            to_completer.extend(_get_executables())
            to_completer.extend(list(BuiltIn))
        _, dir, files = next(os.walk(os.path.curdir))
        ...
    dir = list(map(lambda d: d+"/", dir))
    to_completer.extend([*dir, *files])
    return to_completer

def _get_executables() -> list[str]:
    executables = []
    for directory in os.environ['PATH'].split(':'):
        if not os.path.exists(directory) : continue
        for item in os.listdir(directory):
            full_path : str = os.path.join(directory, item)
            if os.access(full_path, os.X_OK):
                executables.append(item)
    return executables