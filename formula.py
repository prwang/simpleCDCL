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
    __slots__ = ('n_', 'stat', 'rev')
    undef: Set[int]
    rev: Dict[Clause, bool]  # role(+-) of its occurrences in each clause
    # number of negatively and/or positively occurrences
    stat: List[int]
    n_: int

    def __init__(self, n: int):
        self.n_ = n
        self.stat = [0, 0]
        self.rev = {}


class Asg_sideaff:
    __slots__ = ('var', 'cl', 'value', 'role')
    var: int
    cl: Clause
    value: bool
    role: bool

    def __init__(self, _var: int, _cl: Clause, _value: bool, _role: bool):
        self.var = _var
        self.cl = _cl
        self.value = _value
        self.role = _role


class Formula:
    __slots__ = ('raw', 'cnf', 'var', 'var_value', 'model', 'changes', 'frame', 'depth', 'one', 'zero', 'clacnt')
    # the following members are managed by push & pop, used in the recursive process
    raw: List[List[int]]
    cnf: Dict[int, Clause]
    var: List[VarInfo]
    var_value: Dict[int, Tuple[bool,  # value
                               int,  # depth
                               Optional[Set[int]]]]  # any edge table
    model: Optional[List[int]]
    changes: List[Union[int, Asg_sideaff]]
    frame: List[int]
    depth: int
    clacnt : int

    one: Set[Clause]  # guaranteed to be size 0 after bcp exits
    zero: Optional[List[int]]  # not None during the inflating process(backjumping)

    def get_var(self, x) -> VarInfo:
        return self.var[abs(x) - 1]

    def assign(self, _var: int, value: bool,
               cause: Optional[Set[int]] = None) -> None:
        self.var_value[_var] = (value, self.depth,
                                None if cause is None else copy(cause))
        self.changes.append(_var)
        for cl, role in self.get_var(_var).rev.items():
            x = cl.def_(_var * (-1 + 2 * role))
            if role == value:
                self.before_unmount(cl)
                del self.cnf[cl.i_]
            else:
                if x == 0:
                    self.one.discard(cl)
                    self.zero = list(cl.defined)
                elif x == 1:
                    self.one.add(cl)
            self.changes.append(Asg_sideaff(_var, cl, value, role))

    def push(self) -> None:
        self.depth += 1
        print('push called, depth = %d'% self.depth)
        self.frame.append(len(self.changes))

    def pop(self) -> None:
        last = self.frame.pop()
        while len(self.changes) > last:
            p = self.changes.pop()# FIXME really ? throws IndexError indicating unsat
            if type(p) == Asg_sideaff:
                if p.value == p.role:
                    self.cnf[p.cl.i_] = p.cl
                    self.after_mounted(p.cl)
                p.cl.undef_(p.var * (-1 + 2 * p.role))
            elif type(p) == int:
                del self.var_value[p]
            else:
                assert False
        self.depth -= 1
        print('pop called, depth = %d'% self.depth)

    def after_mounted(self, cl: Clause) -> None:
        for x in cl.undef:
            self.get_var(x).rev[cl] = x > 0
            self.get_var(x).stat[x > 0] += 1
            assert self.get_var(x).stat[x > 0]

    def before_unmount(self, cl: Clause) -> None:

        for x in cl.undef:
            self.get_var(x).stat[x > 0] -= 1
            assert self.get_var(x).stat[x > 0] >= 0
            del self.get_var(x).rev[cl]
    def bcp(self) -> bool:
        self.one = { i for k, i in self.cnf.items() if len(i.undef) == 1 }
        while (self.zero is not None) or len(self.one):
            if self.zero is not None:
                print('bcp returned false!')
                return False
            y = self.one.pop()
            assert (len(y.undef) == 1)
            m = next(iter(y.undef))
            self.assign(abs(m), m > 0, y.defined)
        return True

    def add_clause(self, cl) -> None:
        tp = self.cnf[self.clacnt] = Clause(cl, self.clacnt)
        self.after_mounted(tp)
        self.clacnt += 1

    def __init__(self, n: int, cnf1: List[List[int]]):
        self.var = [VarInfo(1 + i) for i in range(n)]
        self.raw = cnf1
        self.clacnt = self.depth = 0
        self.cnf = {}
        self.var_value = {}
        self.model = None
        self.changes = []
        self.frame = []
        self.one = set()
        self.zero = None
        for cl in cnf1: self.add_clause(cl)

    def validate(self) -> None:
        n = len(self.var)
        self.model = {(i + 1): False for i in range(n)}
        for x, (y, p1, p2) in self.var_value.items():
            self.model[x] = y
        assert all([any([self.model[abs(j)] == (j > 0) for j in i]) for i in self.raw])

    def inflate_cause(self, cause: Iterable[int]):
        for i in cause:  # 找到低阶项或者同阶自由变量，特别的是同阶决定变量要yieldfrom 边表
            i1 = abs(i)
            val, dep, edg = self.var_value[i1]
            if val: i1 = -i1
            # if it's been an positive assignment before,
            # now it's to be forced false, and vice versa
            if dep < self.depth or edg is None:
                yield (i1, edg is None)
            else:
                yield from self.inflate_cause(edg)

    def decide(self) -> bool:  # True if already satisfied
        assert not self.one and not self.zero
        for q, cl in self.cnf.items():
            if len(cl.undef) == 0:
                assert False
        dc = (0, 0, False)
        for p in self.var:
            if p.n_ not in self.var_value and (p.stat[0] + p.stat[1]):
                if not p.stat[0]:  # pure
                    self.assign(p.n_, True, None)
                    return False
                elif not p.stat[1]:
                    self.assign(p.n_, False, None)
                    return False
                elif p.stat[0] > dc[0]:
                    dc = (p.stat[0], p.n_, False)
                elif p.stat[1] > dc[0]:
                    dc = (p.stat[1], p.n_, True)
        if dc[0] == 0:
            assert len(self.cnf) == 0;
            return True
        x, y, w = dc
        self.assign(y, w, None)
        return False

    def step(self) -> bool:  # throws IndexError
        if self.bcp():
            self.push()
            if self.decide():  #FIXME 异常
                return True
            elif self.zero is None:
                return False
        assert self.zero
        self.one.clear()
        newlst: List[Tuple[int, bool]] = list(self.inflate_cause(self.zero))
        self.zero = { x[0] for x in newlst }
        if any(x[1] for x in newlst):
            self.add_clause(self.zero)
            self.zero = None
        self.pop()
        return False

    def solve(self) -> bool:
        try:
            while not self.step(): pass
            self.validate()
            return True
        except IndexError:
            return False

