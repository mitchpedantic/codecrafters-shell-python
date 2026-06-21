from __future__ import annotations
import os
import enum
import pathlib as plib
from typing import (Optional, NoReturn, override)

class SyntaxError(Exception): ...
class DirectoryError(Exception): ...

def get_expansion(line : str) -> Expansion:
    splitter : Ctx = Ctx()
    ...
    for c in line + ' ':
        splitter.handle(c)
        ...
    ...
    if splitter.file_redir:
        validate(splitter.file_redir)
    ...
    expansion = Expansion(
        splitter.args,
        splitter.policy_redir,
        splitter.file_redir
    )
    ...
    return expansion

def validate(path : str) -> NoReturn:
    p, _ = os.path.split(path)
    if not os.path.exists(p):
        plib.Path(p).mkdir(parents=True, exist_ok=True)
        plib.Path(path).touch(exist_ok=True)
        #raise DirectoryError(f"{path}: No such file or directory\n")
    ...

class Expansion:
    @property
    def command(self) -> Optional[str]: return self._command
    @property
    def arguments(self) -> list[str]: return self._arguments
    @property
    def stdout_to(self) -> str: return self._stdout_to
    @property
    def stderr_to(self) -> str: return self._stderr_to
    @property
    def access(self) -> str: return self._access
    ...
    def __init__(self,
                 args : list[str],
                 redirection : Optional[RedirectionPolicy],
                 destination : Optional[str]):
        self._command : Optional[str] = args[0] if len(args) > 0 else None
        self._arguments : list[str] = args[1:]
        self._access : Optional[str] = None
        if redirection is RedirectionPolicy.STDOUT_APPEND or\
            redirection is RedirectionPolicy.STDERR_APPEND:
            self._access = "a"
        elif redirection is RedirectionPolicy.STDERR_WRITE or\
             redirection is RedirectionPolicy.STDOUT_WRITE:
            self._access = "w+"
        self._stderr_to : Optional[str] = None
        self._stdout_to : Optional[str] = None
        if redirection is RedirectionPolicy.STDERR_WRITE or\
            redirection is RedirectionPolicy.STDERR_APPEND:
            self._stderr_to = destination
        else:
            self._stdout_to = destination
        pass

class RedirectionPolicy(enum.Enum):
    STDOUT_WRITE = enum.auto()
    STDOUT_APPEND = enum.auto()
    STDERR_WRITE = enum.auto()
    STDERR_APPEND = enum.auto()
    ...

class Ctx:
    _handler : Handler = None
    ...
    @property
    def args(self) -> list[str]: return self._args 
    @property
    def policy_redir(self) -> Optional[RedirectionPolicy]: return self._policy_redir 
    @property
    def file_redir(self) -> Optional[str]: return self._file_redir
    ...
    def __init__(self):
        self._args : list[str] = []
        self._policy_redir : Optional[RedirectionPolicy] = None
        self._file_redir : Optional[str] = None
        self.to(BaseHandler())
        pass
    ...
    def to(self,
           handler: Handler) -> NoReturn:
        self._handler = handler
        self._handler.ctx = self
    ...
    def handle(self, c : str) -> NoReturn:
        self._handler.do(c)

class Handler:
    """
    Handler class prototype. Gathers all the properties shared between implementations
    """
    def do(self) -> NoReturn: ...
    ...
    @property
    def ctx(self) -> Ctx: return self._ctx
    @ctx.setter
    def ctx(self, ctx : Ctx) -> NoReturn: self._ctx = ctx
    ...
    @property
    def last(self) -> str: return self._last
    @last.setter
    def last(self, last : str) -> NoReturn: self._last = last
    ...
    @property

    def arg(self) -> str: return self._arg
    @arg.setter
    def arg(self, arg : str) -> NoReturn: self._arg = arg
    ...
    def __init__(self, underway : str = ''):
        self._arg : str = underway
        self._ctx : Optional[Ctx] = None
        self._last : Optional[str] = None

class BaseHandler(Handler):
    """
    Implementation of the Handler for the base case (unquoted sentence).
    """
    @override
    def do(self, c : str) -> NoReturn:
        """
        The base case handler shall:
         - check the last character
         - if the last character was a \\:
            - copy the current character to the growing string, as is
         - if the last character was not a \\:
            - when a \' is found, attach the single quote handler to the context
            - when a \" is found, attach the double quote handler to the context
            - when a \\ is found, pass
            - when a blank is found, move the current string to the parsed arguments and reset the current string
         - save the last character found
        """
        def _do() -> NoReturn:
            if self.last != '\\':
                if c == '\'': return self.ctx.to(SingleQuoteHandler(self.arg))
                if c == '\"': return self.ctx.to(DoubleQuoteHandler(self.arg))
                if c == '\\': return
                ...
                if c == '>' and self.last == '>':
                    if self.ctx._policy_redir is RedirectionPolicy.STDOUT_WRITE:
                        self.ctx._policy_redir = RedirectionPolicy.STDOUT_APPEND
                    else:
                        self.ctx._policy_redir = RedirectionPolicy.STDERR_APPEND
                    return
                    ... # redirection
                elif c == '>':
                    self.arg = '' # necessary to handle the case of '1>'
                    if self._last == ' ' or self._last == '1':
                        self.ctx._policy_redir = RedirectionPolicy.STDOUT_WRITE
                    elif self._last == '2':
                        self.ctx._policy_redir = RedirectionPolicy.STDERR_WRITE
                    else:
                        raise SyntaxError("syntax error near unexpected token `newline`\n")
                    return
                    ... # redirection
                ...
                if c == ' ':
                    if len(self.arg) > 0:
                        if self.ctx.policy_redir and not self.ctx.file_redir:
                            self.ctx._file_redir = self.arg
                        else:
                            self.ctx.args.append(self.arg)
                        self.arg = ''
                    return
                ...
            self.arg += c
            ...
        _do()
        self.last = c
        return
    ...

class SingleQuoteHandler(Handler):
    """
    Implementation of the Handler for the single quote case .
    """
    @override
    def do(self, c : str) -> NoReturn:
        def _do() -> NoReturn:
            if c == '\'': return self.ctx.to(BaseHandler(self.arg))
            self.arg += c
            ...
        _do()
        return
    ...


class DoubleQuoteHandler(Handler):
    """
    Implementation of the Handler for the double quote case .
    """
    @override
    def do(self, c : str) -> NoReturn:
        def _do() -> NoReturn:
            if self.last == '\\':
                if c == '\"' or c == '\\':
                    self.arg += c
                else:
                    self.arg += (self.last + c)
                return
                ...
            if c == '\"':
                return self.ctx.to(BaseHandler(self.arg))
            if c == '\\': return
            self.arg += c
            ...
        _do()
        # poor bug fix
        self.last = c if self.last != '\\' else '\"'
        return
    ...
