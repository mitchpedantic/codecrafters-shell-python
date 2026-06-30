from __future__ import annotations
from typing import (NoReturn, Final, Optional, Iterator)

import subprocess

#MAX_JOBS : Final[int] = 8192

class JobHandler:
    @property
    def registered(self) -> int: return self._registered
    ...
    def iterate(self) -> Iterator[str]:
        """
        iterates over the jobs, when a job is done, reaps it
        """
        index : int = 0
        actual : int = 0
        removed : int = 0
        for i in range(len(self._processes)):
            index += 1
            if self._processes[i] is None: continue
            actual += 1
            reap : bool = self._processes[i].poll() is not None
            delta : int = self.registered - actual
            yield "[%d]%s  %-21s%s\n" % (
                        index,
                        "+" if delta == 0 else "-" if delta == 1 else " ",
                        "Done" if reap else "Running",
                        " ".join(self._processes[i].args) + ("" if reap else " &"))
            ...
            if reap:
                self._processes[i] = None
                removed += 1
            ...
        self._registered -= removed
        pass
    ...
    def add(self, job : subprocess.Popen) -> tuple[int, int]:
        index : int = 1
        for p in self._processes:
            if not p:
                break
            index += 1
        ...
        if index > self._registered:
            self._processes.append(job)
        else:
            self._processes[index - 1] = job
        self._registered += 1
        return index, job.pid
    ...
    def __init__(self):
        self._registered : int = 0
        self._processes : list[subprocess.Popen] = []
        pass
