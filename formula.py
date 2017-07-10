from typing import *
from enum import IntEnum


class Clause:
    __slots__ = ('undef', 'defined', 'i_')
    undef: Set[int]
    defined: Set[int]
    i_: int

    def __init__(self, v: Iterable, i_: int):
        self.undef = set(v)
        self.defined = set()
        self.i_ = i_

    def def_(self, other: int) -> int:
        self.undef.remove(other)
        self.defined.add(other)
        return len(self.undef)

    def undef_(self, other: int) -> None:
        self.defined.remove(other)
        self.undef.add(other)


class VarInfo:
    rev: Dict[Clause, bool] = {}  # role(+-) of its occurrences in each clause
    # number of negatively and/or positively occurrences
    stat: List[int] = [0, 0]
    n_: int

    def __init__(self, n: int):
        self.n_ = n


class Formula:
    # the following members are managed by push & pop, used in the recursive process
    cnf: Dict[int, Clause] = {}
    var: List[VarInfo]
    assignment: Dict[int, Tuple[bool, # value
                                int,  # depth
                                Set[int]  # any edge table
    ] ] = {}
    changes: List[Tuple[int, bool]]
    frame: List[int]
    depth = 0

    one: Set[Clause] # guaranteed to be size 0 after bcp exits FIXME: 递归函数里面使用全局变量小心不同层被改写！
    zero: Optional[List[int]] = None #not None during the inflating process(backjumping)

    def assign(self, var: int, value: bool,
               cause: Optional[Set[int]] = None) -> None:
        for cl, val in self.var[var].rev:
            if val == value:
                self.before_cl_removed(cl)
                del self.cnf[cl.i_]
            else:
                x = cl.def_( val)
                if x == 0:
                    self.one.remove(cl)
                    self.zero = list(cl.undef)
                elif x == 1:
                    self.one.add(cl)
        self.assignment[var] = (value, self.depth, cause)
        self.changes.append((var, value))

    def unassign(self, var: int, value: bool) -> None:
        del self.assignment[var]
        for cl, val in reversed(self.var[var].rev):
            if val == value:
                self.cnf[cl.i_] = cl
                self.after_cl_born(cl)
            else: cl.undef_(val)

    def push(self) -> None:
        self.depth += 1
        self.frame.append(len(self.changes))

    def pop(self) -> None:
        last = self.frame.pop() # throws IndexError indicating unsat
        while len(self.changes) > last:
            x, y = self.changes.pop()
            self.unassign(x, y)
        self.depth -= 1

    def after_cl_born(self, cl: Clause) -> None:
        for x in cl.undef:
            self.var[abs(x)].rev[cl] = x > 0
            self.var[abs(x)].stat[x > 0] += 1

    def before_cl_removed(self, cl: Clause) -> None:
        for x in cl.undef:
            self.var[abs(x)].stat[x > 0] -= 1
            del self.var[abs(x)].rev[cl]

    def bcp(self) -> bool:
        while (self.zero is not None) or len(self.one):
            if self.zero is not None:
                self.one.clear()
                return False
            y = self.one.pop()
            assert(len(y.undef) == 1)
            m = next(iter(y.undef))
            self.assign(abs(m), m > 0, y.defined)
        return True

    def add_clause(self, cl) -> None:
        i = len(self.cnf)
        tp = self.cnf[i] = Clause(cl, i)
        self.after_cl_born(tp)

    def __init__(self, n: int, cnf1: List[List[int]]):
        self.var = [VarInfo(i) for i in range(n)]
        for cl in cnf1: self.add_clause(cl)

