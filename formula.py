from typing import *
from copy import copy


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
    rev: Dict[Clause, bool]  # role(+-) of its occurrences in each clause
    # number of negatively and/or positively occurrences
    stat: List[int]
    n_: int

    def __init__(self, n: int):
        self.n_ = n
        self.stat = [0, 0]
        self.rev = {}


class Formula:
    # the following members are managed by push & pop, used in the recursive process
    raw : List[List[int]]
    cnf: Dict[int, Clause]
    var: List[VarInfo]
    var_value: Dict[int, Tuple[bool,  # value
                                int,  # depth
                                Optional[Set[int]] ] ]  # any edge table
    model: Optional[List[int]]
    changes: List[Tuple[int, bool]]
    frame: List[int]
    depth: int

    one: Set[Clause] # guaranteed to be size 0 after bcp exits
    zero: Optional[List[int]] #not None during the inflating process(backjumping)

    def get_var(self, x) -> VarInfo: return self.var[abs(x) - 1]

    def assign(self, _var: int, value: bool,
               cause: Optional[Set[int]] = None) -> None:
        self.var_value[_var] = (value, self.depth,
                                None if cause is None else copy(cause))
        for cl, val in self.get_var(_var).rev.items():
            x = cl.def_(_var * (-1 + 2 * val))
            if val == value:
                self.before_unmount(cl)
                del self.cnf[cl.i_]
            else:
                if x == 0:
                    self.one.remove(cl)
                    self.zero = list(cl.defined)
                elif x == 1:
                    self.one.add(cl)
        self.changes.append((_var, value))

    def unassign(self, _var: int, value: bool) -> None:
        for cl, val in self.get_var(_var).rev.items(): # FIXME rev是不可靠的，因为会新产生从句，导致rev变大
            #TODO 新开一个list真的记一下这些修改，这是容易办到的事情
            if val == value:
                self.cnf[cl.i_] = cl
                self.after_mounted(cl)
            cl.undef_(_var * (-1 + 2 * val))
        del self.var_value[_var]

    def push(self) -> None:
        self.depth += 1
        self.frame.append(len(self.changes))

    def pop(self) -> None:
        last = self.frame.pop() # throws IndexError indicating unsat
        while len(self.changes) > last:
            x, y = self.changes.pop()
            self.unassign(x, y)
        self.depth -= 1

    def after_mounted(self, cl: Clause) -> None:
        for x in cl.undef:
            self.get_var(x).rev[cl] = x > 0
            self.get_var(x).stat[x > 0] += 1
            assert self.get_var(x).stat[x > 0] <= 2 #TODO 这个数据调完删掉

    def before_unmount(self, cl: Clause) -> None:
        for x in cl.undef:
            self.get_var(x).stat[x > 0] -= 1
            assert self.get_var(x).stat[x > 0] >= 0
            del self.get_var(x).rev[cl]

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
        self.after_mounted(tp)


    def __init__(self, n: int, cnf1: List[List[int]]):
        self.var = [VarInfo(1 + i) for i in range(n)]
        self.raw = cnf1
        self.depth = 0
        self.cnf = {}
        self.var_value = {}
        self.model= None
        self.changes = []
        self.frame  = []
        self.one = set()
        self.zero = None
        for cl in cnf1: self.add_clause(cl)

    def validate(self) -> None:
        n = len(self.var)
        self.model = { (i + 1) : False for i in range(n)}
        for x, (y, p1, p2) in self.var_value.items():
            self.model[x] = y
        assert all([any([self.model[abs(j)] == (j > 0) for j in i]) for i in self.raw])


