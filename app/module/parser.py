from __future__ import annotations
from typing import (Optional, NoReturn, override)

class SyntaxError(Exception): ...

def get_expansion(line : str) -> Expansion:
    splitter : Ctx = Ctx()
    ...
    for c in line + ' ':
        splitter.handle(c)
        ...
    ...
    expansion = Expansion(
        splitter.args,
        splitter.access_redir,
        splitter.file_redir
    )
    ...
    return expansion

class Expansion:
    @property
    def command(self) -> Optional[str]: return self._command
    @property
    def arguments(self) -> list[str]: return self._arguments
    @property
    def file(self) -> str: return self._file
    @property
    def access(self) -> str: return self._access
    ...
    def __init__(self,
                 args : list[str],
                 redirection : Optional[str],
                 destination : Optional[str]):
        self._command : Optional[str] = args[0] if len(args) > 0 else None
        self._arguments : list[str] = args[1:]
        self._access = redirection
        self._file = destination
        pass

class Ctx:
    _handler : Handler = None
    ...
    @property
    def args(self) -> list[str]: return self._args 
    @property
    def access_redir(self) -> Optional[str]: return self._access_redir 
    @property
    def file_redir(self) -> Optional[str]: return self._file_redir
    ...
    def __init__(self):
        self._args : list[str] = []
        self._access_redir : Optional[str] = None
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
                    self.ctx._access_redir = "a"
                    return
                    ... # redirection
                elif c == '>':
                    if self._last != ' ' and\
                        self._last != '1':
                        raise SyntaxError("syntax error near unexpected token `newline`\n")
                    self.arg = ''
                    self.ctx._access_redir = "w+"
                    return
                    ... # redirection
                ...
                if c == ' ':
                    if len(self.arg) > 0:
                        if self.ctx.access_redir and not self.ctx.file_redir:
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
            if self.last == '\\':
                if c == '\'':
                    self.arg += c
                else:
                    self.arg += (self.last + c)
                return
                ...
            if c == '\'': return self.ctx.to(BaseHandler(self.arg))
            if c == '\\': return
            self.arg += c
            ...
        _do()
        self.last = c
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
        self.last = c
        return
    ...
