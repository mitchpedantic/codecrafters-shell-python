from __future__ import annotations
from typing import (NoReturn, Final, Optional, Iterator)

import subprocess

#MAX_JOBS : Final[int] = 8192
MESSAGE : Final[callable[[int, int, bool, str], str]] =\
    lambda index, delta, reap, command : "[%d]%s  %-21s%s\n" % ( index,
                                                                "+" if delta == 0 else "-" if delta == 1 else " ",
                                                                "Done" if reap else "Running",
                                                                command + ("" if reap else " &"))
class JobHandler:
    @property
    def registered(self) -> int: return self._registered
    ...
    def routine(self) -> Iterator[str]:
        if self._registered:
            for reap, msg in self._poll_all():
                if reap: yield msg
    ...
    def iterate(self) -> Iterator[str]:
        """
        iterates over the jobs, when a job is done, reaps it
        """
        for _, msg in self._poll_all(): yield msg
    ...
    def add(self, job : subprocess.Popen) -> tuple[int, int]:
        index : int = 0
        queue : int = self._registered + 1
        for p in self._processes:
            if not p:
                break
            index += 1
        ...
        if index >= self._registered:
            self._processes.append(job)
            self._indexes.append(queue)
        else:
            self._processes[index] = job
            self._indexes[index] = queue
        self._registered += 1
        return queue, job.pid
    ...
    def __init__(self):
        self._registered : int = 0
        self._indexes : list[int] = []
        self._processes : list[subprocess.Popen] = []
        pass
    ...
    def _poll_all(self) -> Iterator[tuple[bool, str]]:
        index : int = 0
        removed : int = 0
        for i in range(len(self._processes)):
            if self._processes[i] is None: continue
            reap : bool = self._processes[i].poll() is not None
            delta : int = self.registered - index - 1
            yield reap, MESSAGE(self._indexes[i], delta, reap, " ".join(self._processes[i].args))
            ...
            if reap:
                self._processes[i] = None
                removed += 1
            index += 1
            ...
        self._registered -= removed