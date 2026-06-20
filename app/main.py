from __future__ import annotations

import os
import enum
import subprocess
from sys import (stdout, stderr)
from typing import (NoReturn, Callable, Optional)
from .module import (get_expansion, Expansion, SyntaxError)

class BuiltIn(str, enum.Enum):
    EXIT = "exit"
    ECHO = "echo"
    TYPE = "type"
    PWD = "pwd"
    CD = "cd"

class Shell:
    def input(self) -> int:
        self._write("$ ")
        try:
            expanse : Expansion = get_expansion(
                input()
            )
            return\
                self._do_(expanse.command)(expanse) if expanse.command else 0
        except SyntaxError as syn:
            self._error(syn)
        except (EOFError, KeyboardInterrupt) as _:
            self._write("\n")
            return -1
        ...
    def __init__(self):
        self._old_pwd : str = None
        pass
    ...
    def _write(self,
               message : str,
               exp : Expansion = None) -> NoReturn:
        if exp and exp.file:
            with open(exp.file, exp.access) as f: f.write(message)
        else:
            stdout.write(message)
        pass
    ...
    def _error(self,
               message : str) -> NoReturn:
        stderr.write(message)
        pass
    ...
    def _look_up(self,
                 executable : str) -> Optional[str]:
        for directory in os.environ['PATH'].split(':'):
            if not os.path.exists(directory) : continue
            for item in os.listdir(directory):
                full_path : str = os.path.join(directory, item)
                if os.access(full_path, os.X_OK) and item == executable:
                    return full_path
                ...
            ...
        return None
    ...
    def _do_exit(self, _) -> int: return -1
    ...
    def _do_echo(self,
                 exp : Expansion) -> int:
        self._write(
            " ".join(exp.arguments) + "\n",
            exp
        )
        return 0
    ...
    def _do_type(self,
                 exp : Expansion) -> int:
        message : str = ""
        if len(exp.arguments) > 0:
            type_of : str = exp.arguments[0]
            if type_of in BuiltIn.__members__.values():
                message = "%s is a shell builtin" % type_of
            else:
                location : str = self._look_up(type_of) 
                if location:
                    message = "%s is %s" % (type_of, location)
                else:
                    message = "%s: not found" % type_of
                ...
            ...
        self._write(message + "\n", exp)
        return 0
    ...
    def _do_pwd(self,
                 exp : Expansion) -> int:
        self._write(
            os.getcwd() + "\n",
            exp
        )
        return 0
    ...
    def _do_cd(self,
               exp : Expansion) -> int:
        new_dir : str = None
        if len(exp.arguments) == 0 or exp.arguments[0] == "~":
            new_dir = os.environ["HOME"]
        elif exp.arguments[0] == "-":
            new_dir = self._old_pwd
            if new_dir is None:
                self._error("Old PWD not set\n" )
                return 0
        else:
            new_dir = exp.arguments[0]
        try:
            tmp = os.getcwd()
            os.chdir(new_dir)
            self._old_pwd = tmp
        except FileNotFoundError as _:
            self._error("%s: No such file or directory\n" % exp.arguments[0])
        return 0
    ...
    def _do_run(self,
                exp : Expansion) -> int:
        cmd : str = exp.command
        if self._look_up(cmd) is not None:
            if exp.file:
                with open(exp.file, exp.access) as fd:
                    subprocess.run([exp.command, *exp.arguments], stdout = fd)
            else:
                subprocess.run([exp.command, *exp.arguments])
        else:
            self._error("%s: command not found\n" % cmd)
        return 0
    ...
    def _do_(self,
             request : BuiltIn) -> Callable[[Expansion], int]:
        return {
            BuiltIn.EXIT : self._do_exit,
            BuiltIn.ECHO : self._do_echo,
            BuiltIn.TYPE : self._do_type,
            BuiltIn.PWD  : self._do_pwd,
            BuiltIn.CD   : self._do_cd,

        }.get(request, self._do_run)

def main() -> NoReturn:
    sh = Shell() 
    while (0 == sh.input()):
        ...
    pass

if __name__ == "__main__":
    main()