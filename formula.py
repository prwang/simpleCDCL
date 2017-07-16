from typing import *
from itertools import *
from copy import copy
import logging


class Clause:
    __slots__ = ('undef', 'defined', 'i_')
    # undef: Set[int]
    # defined: Set[int]
    # i_: int

    def __init__(self, undef: Iterable[int], defined: Iterable[int], i_: int):
        self.undef = set(undef)
        self.defined = set(defined)
        self.i_ = i_

    def def_(self, other: int) -> int:
        self.undef.remove(other) #FIXME keyError:
        self.defined.add(other)
        return len(self.undef)

    def undef_(self, other: int) -> None:
        self.defined.remove(other)
        self.undef.add(other)


class VarInfo:
    __slots__ = ('n_', 'stat', 'rev')
    # undef: Set[int]
    # rev: Dict[Clause, bool]  # role(+-) of its occurrences in each clause
    # # number of negatively and/or positively occurrences
    # stat: List[int]
    # n_: int

    def __init__(self, n: int):
        self.n_ = n
        self.stat = [0, 0]
        self.rev = {}


class Formula:
    __slots__ = ('raw', 'cnf', 'var', 'var_value',
                 'model', 'changes', 'frame', 'depth',
                 'one', 'zero', 'clacnt', 'curstep')
    # # the following members are managed by push & pop, used in the recursive process
    # raw: List[List[int]]
    # cnf: Dict[int, Clause]
    # var: List[VarInfo]
    # var_value: Dict[int, Tuple[bool,  # value
    #                            int,  # depth
    #                            Optional[Set[int]]]]  # any edge table
    # model: Optional[List[int]]
    # changes: List[int]
    # frame: List[int]
    # depth: int
    # clacnt: int

    # one: Set[Clause]  # guaranteed to be size 0 after bcp exits
    # zero: Optional[List[int]]  # not None during the inflating process(backjumping)
    # curstep : int
    def get_var(self, x: int) -> VarInfo:
        return self.var[abs(x) - 1]

    def assign(self, _var: int, value: bool,
               cause: Optional[Set[int]] = None) -> None:
        assert(_var > 0)
        self.var_value[_var] = (value, self.depth,
                                None if cause is None else copy(cause))
        self.changes.append(_var)
        for cl, role in self.get_var(_var).rev.items():
            x = cl.def_(_var * (-1 + 2 * role))
            if role == value:
                self.before_unmount(cl, _var) # privatize these clauses
                self.one.discard(cl)
                del self.cnf[cl.i_]
            else:
                if x == 0:
                    self.one.discard(cl)
                    self.zero = list(cl.defined)
                elif x == 1:
                    self.one.add(cl)

    def after_mounted(self, cl: Clause, father: int) -> None:
        for x in chain(cl.undef, cl.defined):
            if x == father or -x == father: continue
            self.get_var(x).rev[cl] = x > 0
            self.get_var(x).stat[x > 0] += 1
            assert self.get_var(x).stat[x > 0]

    def before_unmount(self, cl: Clause, father: int) -> None:
        for x in chain(cl.undef, cl.defined):
            if x == father or -x == father: continue
            self.get_var(x).stat[x > 0] -= 1
            assert self.get_var(x).stat[x > 0] >= 0
            del self.get_var(x).rev[cl]

    def push(self) -> None:
        self.depth += 1
        #logging.debug('push called, depth = %d' % self.depth)
        self.frame.append(len(self.changes))

    def unassign(self, _var: int) -> None:
        assert(_var > 0)
        value = self.var_value[_var][0]
        for cl, role in self.get_var(_var).rev.items():
            if role == value:
                self.cnf[cl.i_] = cl
                self.after_mounted(cl, _var)
            cl.undef_(_var * (-1 + 2 * role))
        del self.var_value[_var]

    def pop(self) -> None:
        last = self.frame.pop()
        while len(self.changes) > last:
            p = self.changes.pop()  # throws IndexError indicating unsat
            if type(p) == int:
                self.unassign(p)
            else:
                assert False
        self.depth -= 1
        #logging.debug('pop called, depth = %d' % self.depth)

    def bcp(self) -> bool:
        self.one = {i for k, i in self.cnf.items() if len(i.undef) == 1}
        while (self.zero is not None) or len(self.one):
            if self.zero is not None:
                #logging.debug('bcp returned false!')
                return False
            y = self.one.pop()
            assert (len(y.undef) == 1)
            m = next(iter(y.undef))
            self.assign(abs(m), m > 0, y.defined)
            #logging.debug('--must assign %d to var_%d because %s' % ( m > 0, abs(m), str(y.defined)))
        return True

    def add_clause(self, cl: Iterable[int]) -> None:
        ud, dd = (set(), set())
        cl = sorted(list(set(cl)), key=abs)
        if any(abs(cl[i]) == abs(cl[i + 1]) for i in range(len(cl) - 1)):
            logging.info('useless clause: %s'%str(cl))
            return
        for x in cl:
            x1 = abs(x)
            if x1 in self.var_value:
                assert self.var_value[x1][0] != (x > 0)
                dd.add(x)
            else:
                ud.add(x)
        assert (not dd or len(ud) == 1)
        tp = self.cnf[self.clacnt] = Clause(ud, dd, self.clacnt)
        self.after_mounted(tp, 0)
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
        self.curstep = 0
        for cl in cnf1: self.add_clause(cl)

    def validate(self) -> None:
        n = len(self.var)
        self.model = {(i + 1): False for i in range(n)}
        for x, (y, p1, p2) in self.var_value.items():
            self.model[x] = y
        assert all([any([self.model[abs(j)] == (j > 0) for j in i]) for i in self.raw])

    def decide(self) -> bool:  # True if already satisfied
        assert not self.one and not self.zero
        for q, cl in self.cnf.items():
            if len(cl.undef) == 0:
                assert False
        dc = (0, 0, False)
        for p in self.var:
            assert(p.n_ > 0)
            if p.n_ not in self.var_value and (p.stat[0] + p.stat[1]):
                if not p.stat[0]:  # pure
                    dc = (p.stat[1], p.n_, True)
                    break
                elif not p.stat[1]:
                    dc = (p.stat[0], p.n_, False)
                    break
                elif p.stat[0] > dc[0]:
                    dc = (p.stat[0], p.n_, False)
                elif p.stat[1] > dc[0]:
                    dc = (p.stat[1], p.n_, True)
        if dc[0] == 0:
            assert len(self.cnf) == 0;
            return True  # SAT
        x, y, w = dc
        self.assign(y, w, None)
        #logging.debug('--decided to assign %d to var_%d' % (w, y))
        return False

    def step(self) -> bool:  # throws IndexError
        def inflate_cause(cause: Iterable[int]):
            for i in cause:  # 找到低阶项或者同阶自由变量，特别的是同阶决定变量要yieldfrom 边表
                i1 = abs(i)
                val, dep, edg = self.var_value[i1]
                if val: i1 = -i1
                # if it's been an positive assignment before,
                # now it's to be forced false, and vice versa
                if dep < self.depth or edg is None:
                    yield (i1, dep == self.depth and edg is None)
                else:
                    yield from inflate_cause(edg)
        self.curstep += 1
        logging.info('current step is: %d, depth = %d'%(self.curstep, self.depth))
        if self.bcp():
            self.push()
            if self.decide():
                return True
            elif self.zero is None:
                return False
        assert self.zero
        self.one.clear()
        #logging.debug('::zero = ' + str(self.zero))
        newlst = list(inflate_cause(self.zero))
        self.zero = {x[0] for x in newlst}
        self.pop()  # must pop at first, or getting wrong number of undecided vars
        if any(x[1] for x in newlst):
            self.add_clause(self.zero)
            self.zero = None
        return False

    def solve(self) -> bool:
        try:
            while not self.step(): pass
            self.validate()
            return True
        except IndexError:
            return False
