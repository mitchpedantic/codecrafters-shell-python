from __future__ import annotations

import enum

from typing import (NoReturn, Callable, Optional)
from .parse_handler import Expansion

class Flags(str, enum.Enum):
    LOWER_C = "-c"
    UPPER_C = "-C"
    LOWER_P = "-p"

class GNUComplete:
    @property
    def message(self) -> str: return self._message
    @property
    def emessage(self) -> str: return self._emessage
    ...
    def __init__(self):
        self._message : str = ""
        self._emessage : str = ""
        self._gnu_complete = dict()
        ...
    ...
    def search(self,
               key : str) -> Optional[str]:
        return self._gnu_complete.get(key, None)
    ...
    def complete(self,
                 exp : Expansion = None) -> NoReturn:
        self._message : str = ""
        self._emessage : str = ""
        return self._on_call_(exp)(exp)
    ...
    def _on_call_(self,
                  exp : Expansion) -> Callable[[Expansion], int]:
        if len(exp.arguments) < 1:
            return self._do_display_all
        ...
        flag, *_ = exp.arguments
        ...
        return {
            Flags.LOWER_C : self._do_register_wout_path,
            Flags.UPPER_C : self._do_register_with_path,
            Flags.LOWER_P : self._do_display,
        }.get(flag, self._invalid)
    ...
    def _do_display(self,
                    exp : Expansion) -> int:
        if len(exp.arguments) == 1:
            return self._do_display_all(exp)
        ...
        _, exe, *_ = exp.arguments
        ...
        #completions : list[str] = self._gnu_complete.get(exe, list())
        #if not len(completions):
        #    self._emessage = "complete: %s: no completion specification\n" % exe
        #for c in completions:
        #    self._message += "complete %s %s\n" % ("-C '%s'" % c if len(c) else "-c", exe)
        completion : list[str] = self._gnu_complete.get(exe, None)
        if not completion:
            self._emessage = "complete: %s: no completion specification\n" % exe
        else:
            self._message += "complete %s %s\n" % ("-C '%s'" % completion if len(completion) else "-c", exe)
        ...
    ...
    def _do_register_wout_path(self,
                               exp : Expansion) -> int:
        if len(exp.arguments) == 1:
            return self._invalid(exp)
        ...
        _, exe, *_ = exp.arguments
        #self._gnu_complete[exe] = self._gnu_complete.get(exe, set()) | set([""])
        self._gnu_complete[exe] = ""
        ...
        return 0
    ...
    def _do_register_with_path(self,
                               exp : Expansion) -> int:
        if len(exp.arguments) == 1:
            return self._invalid(exp)
        if len(exp.arguments) == 2:
            return self._help()
        ...
        _, path, exe, *_ = exp.arguments
        #self._gnu_complete[exe] = self._gnu_complete.get(exe, set()) | set([path])
        self._gnu_complete[exe] = path
        ...
        return 0
    ...
    def _do_display_all(self,
                        exp : Expansion) -> int:
        for k, vs in self._gnu_complete.items():
            #for v in vs:
            #    self._message += "complete %s %s\n" % ("-C '%s'" % v if len(v) else "-c", k)
            self._message += "complete %s %s\n" % ("-C '%s'" % vs if len(vs) else "-c", k)
        ...
    ...
    def _invalid(self,
                 exp : Expansion) -> int:
        flag, *_ = exp.arguments
        self._emessage : str = ("bash: complete: %s: invalid option\n" if flag not in Flags else "bash: complete: %s: option requires an argument\n") % flag
        return self._help()
    ...
    def _help(self) -> int:
        self._emessage += "complete: usage: complete [-abcdefgjksuv] [-pr] [-DEI] [-o option] [-A action] [-G globpat] [-W wordlist] [-F function] [-C command] [-X filterpat] [-P prefix] [-S suffix] [name ...]\n"
        return 0
    ...