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

    def step(self) -> None:
        if self.bcp():
            self.push()
            # decide例程，同时处理成功的情况，以及pure的情况
            pass
        else:
            #  在下面判断，否则如果出现同阶自由变量则表示应该直接加入，并且删掉changes
            assert(self.zero)
            newlst: List[Tuple[int, bool]] = list(self.inflate_cause(self.zero))
            # 这里会出现x or -x吗 ?
            self.zero = [x[0] for x in newlst]
            if any(x[1] for x in newlst):
                self.add_clause(self.zero)
                self.zero = None
            self.pop()
            #pop两次当且仅当所有的返回项都是低阶项，TODO 反复思考这里的正确性



    #TODO 哪一步调push(), 哪一步pop()
    # 向下走，push(), 向上走pop()，走向sibling: pop() & push()
    #最开始做了0次假设，每push一次代表多做了一次假设
    #
