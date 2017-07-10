from typing import *
from formula import Formula

#FIXME 检查所有的abs
#FIXME 检查所有的not 注意空表是falsey，不像javascript

'''
        def SAT(Formula):
            while true:
                Formula1 = BCP(Formula)
                Formula2 = SET_PURE_TRUE(Formula1)
                if Formula2 == Formula1:
                    break
            if Formula == true:
                return true
            elif Formula == false:
                return false
            else:
                x = CHOOSE_VAR(Formula)
                return Formula[true/x] or Formula[false/x]
    '''

class CdclEngine(Formula):
    def __init__(self, n: int, cnf1: List[List[int]]):
        super().__init__(n, cnf1)

    def inflate_cause(self, cause: Iterable[int]):
        for i in cause: # 找到低阶项或者同阶自由变量，特别的是同阶决定变量要yieldfrom 边表
            i1 = abs(i)
            val, dep, edg = self.assignment[i1]
            if val: i1 = -i1
            # if it's been an positive assignment before,
            # now it's to be forced false, and vice versa
            if dep < self.depth or edg is None:
                yield (i1, edg is None)
            else: yield from self.inflate_cause(edg)
#TODO 这里先乱写一个能用的，调通了再改
    def decide(self) -> bool: #True if already satisfied
        dc = (0, 0, False)
        for p in self.var:
            if p.n_ not in self.assignment and (p.stat[0] + p.stat[1]):
                if not p.stat[0]: # pure
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
    def step(self) -> bool: #throws IndexError
        if self.bcp():
            self.push()
            if self.decide(): return True
            elif self.zero is None: return False
        assert(self.zero)
        newlst: List[Tuple[int, bool]] = list(self.inflate_cause(self.zero))
        # 这里会出现x or -x吗 ?
        self.zero = [x[0] for x in newlst]
        if any(x[1] for x in newlst):
            self.add_clause(self.zero)
            self.zero = None
        self.pop()
        return False
    def solve(self) -> bool:
        try:
            while not self.step(): pass

            return True
        except IndexError:
            return False
            #pop两次当且仅当所有的返回项都是低阶项，TODO 反复思考这里的正确性

    # 哪一步调push(), 哪一步pop()
    # 向下走，push(), 向上走pop()，走向sibling: pop() & push()
    #最开始做了0次假设，每push一次代表多做了一次假设
