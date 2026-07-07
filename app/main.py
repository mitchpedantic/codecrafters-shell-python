from __future__ import annotations

import io
import os
import subprocess
from sys import (stdout, stderr)
from typing import (NoReturn, Callable, Optional)
from .module import (Expansion, SyntaxError, DirectoryError, GNUComplete, BuiltIn, JobHandler)
from .module import (get_expansion, readline_setup)

class Shell(object):
    def run(self) -> NoReturn:
        readline_setup(
            complete_callback = self._complete_cmd.search
        )
        while (0 == self._input()): ...
    ...
    def _input(self) -> int:
        try:
            for msg in self._job_handler.routine():
                stdout.write(msg)
            expansions : list[Expansion] = get_expansion(
                input("$ ")
            )
            returncode = 0
            if len(expansions) > 1:
                returncode = self._pipe(expansions)
            else :
                returncode : int = 0
                expanse = expansions[0]
                returncode = self._do_(expanse.command)(expanse)
                if expanse.command in BuiltIn:
                    self._write_message(expanse)
                    self._error_message(expanse)
            return returncode
        except (SyntaxError, DirectoryError) as parsex:
            stderr.write(str(parsex))
        except (EOFError, KeyboardInterrupt) as _:
            stdout.write("\n")
            return -1
        ...
    def _pipe(self, expansions : list[Expansion]) -> int:
        """
        TODO to be merged with run function. Consider creating a new module .py
        """ 
        def call_subprocess(inp : Optional[io.FileIO], out : Optional[io.FileIO], err : Optional[io.FileIO], args) -> subprocess.Popen:
            if last_built_in:
                proc = subprocess.Popen(args, stdin=subprocess.PIPE, stdout=out, stderr=err)
                proc.communicate(bytes(self._message, "utf-8"))
                return proc
            else:
                return subprocess.Popen(args, stdin=inp, stdout=out, stderr=err)
        ...
        last_built_in = False
        processes_num = len(expansions)
        processes_list = [None]*processes_num
        ...
        for i in range(0, processes_num - 1):
            exp = expansions[i]
            if exp.command in BuiltIn:
                last_built_in = True
                self._do_(exp.command)(exp)
                ...
            else:
                stdin = processes_list[i-1].stdout if i > 0 and processes_list[i-1] else None
                processes_list[i] = call_subprocess(stdin, subprocess.PIPE, None, [exp.command, *exp.arguments])
                last_built_in = False
            ...
        exp = expansions[-1]
        if exp.command in BuiltIn:
            returncode = self._do_(exp.command)(exp)
            self._write_message(exp)
            self._error_message(exp)
            return returncode
        else:
            stdin = processes_list[-2].stdout if processes_list[-2] else None
            if exp.stdout_to:
                with open(exp.stdout_to, exp.access) as fd:
                    last = call_subprocess(stdin, fd, None, [exp.command, *exp.arguments])
            elif exp.stderr_to:
                with open(exp.stderr_to, exp.access) as fd:
                    last = call_subprocess(stdin, None, fd, [exp.command, *exp.arguments])
            else:
                last = call_subprocess(stdin, None, None, [exp.command, *exp.arguments])
            last.wait()
        return 0
    ...
    def __init__(self):
        self._message : str = ""
        self._emessage : str = ""
        self._old_pwd : str = None
        self._complete_cmd = GNUComplete()
        self._job_handler = JobHandler()
        pass
    ...
    def _write_message(self,
                        exp : Expansion = None) -> NoReturn:
        if exp and exp.stdout_to:
            with open(exp.stdout_to, exp.access) as f: f.write(self._message)
        else:
            stdout.write(self._message)
        self._message = ""
        pass
    ...
    def _error_message(self,
                        exp : Expansion = None) -> NoReturn:
        if exp and exp.stderr_to:
            with open(exp.stderr_to, exp.access) as f: f.write(self._emessage)
        else:
            stderr.write(self._emessage)
        self._emessage = ""
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
        self._message = " ".join(exp.arguments) + "\n"
        self._emessage = ""
        return 0
    ...
    def _do_type(self,
                 exp : Expansion) -> int:
        if len(exp.arguments) > 0:
            type_of : str = exp.arguments[0]
            if type_of in BuiltIn.__members__.values():
                self._message = "%s is a shell builtin\n" % type_of
            else:
                location : str = self._look_up(type_of) 
                if location:
                    self._message = "%s is %s\n" % (type_of, location)
                else:
                    self._emessage = "%s: not found\n" % type_of
                ...
            ...
        return 0
    ...
    def _do_jobs(self,
                 exp : Expansion) -> int:
        for message in self._job_handler.iterate():
            self._message += message
        return 0
    ...
    def _do_pwd(self,
                 exp : Expansion) -> int:
        self._message += os.getcwd() + "\n"
        return 0
    ...
    def _do_complete(self,
                     exp : Expansion) -> int:
        self._complete_cmd.complete(exp)
        self._message = self._complete_cmd.message
        self._emessage = self._complete_cmd.emessage
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
                self._emessage = "Old PWD not set\n"
                return 0
        else:
            new_dir = exp.arguments[0]
        try:
            tmp = os.getcwd()
            os.chdir(new_dir)
            self._old_pwd = tmp
        except FileNotFoundError as _:
            self._emessage = "%s: No such file or directory\n" % exp.arguments[0]
        return 0
    ...
    def _do_history(self,
                    exp : Expansion) -> int:
        return 0
    ...
    def _do_run(self,
                exp : Expansion) -> int:
        cmd : str = exp.command
        if self._look_up(cmd) is not None:
            self._handler_run(exp)
        else:
            self._emessage = "%s: command not found\n" % cmd
            self._error_message(exp)
        return 0
    ...
    def _handler_run(self,
                     exp : Expansion) -> NoReturn:
        if exp.background:
            index, pid = self._job_handler.add(
                subprocess.Popen(
                    [exp.command, *exp.arguments]
                )
            )
            self._message = f"[{index}] {pid}\n"
            self._write_message(exp)
        elif exp.stdout_to:
            with open(exp.stdout_to, exp.access) as fd:
                subprocess.run([exp.command, *exp.arguments], stdout = fd)
        elif exp.stderr_to:
            with open(exp.stderr_to, exp.access) as fd:
                subprocess.run([exp.command, *exp.arguments], stderr = fd)
        else:
            subprocess.run([exp.command, *exp.arguments])
        pass
    ...
    def _do_(self,
             request : BuiltIn) -> Callable[[Expansion], int]:
        return {
            BuiltIn.COMPLETE : self._do_complete,
            BuiltIn.HISTORY : self._do_history,
            BuiltIn.EXIT : self._do_exit,
            BuiltIn.ECHO : self._do_echo,
            BuiltIn.TYPE : self._do_type,
            BuiltIn.JOBS : self._do_jobs,
            BuiltIn.PWD  : self._do_pwd,
            BuiltIn.CD   : self._do_cd,

        }.get(request, self._do_run)

def main() -> NoReturn:
    Shell().run()
    ...
    pass

if __name__ == "__main__":
    main()