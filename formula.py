from typing import *
from enum import IntEnum


class Changes(IntEnum):
    VAR = 1 # remove a variable(being assigned false) from a clause
    CLA = 2 # remove a whole clause(being satisfied)
    ASG = 4 # variable assignment, the cause of VAR & CLA


class Success(Exception): pass


class Conflict(Exception): pass


class Formula:
    cnf: Dict[int, List[int]] = []
    var: List[Tuple[Dict[int, bool], Tuple[int, int]]] = None
    assign : Dict[int, int] = [] #
    # Tuple: number of negatively and/or positively occurrences
    depth = 0
    # TODO dict for unit clauses
    changes : List[Tuple[Changes, Any]] = []


    #TODO 两种类型的修改：
    #  [ ] 分别是删除从句中的一个变量，当决定这个变量为假的时候（其逆是加回来这个变量），和
    #  [x] 删除整个从句（其逆是加回这个从句）
    frame : List[int]
    history : List

    def push(self) -> None:
        self.depth += 1
        self.frame.append(len(self.history))
        pass

    def pop(self) -> None:
        last = self.frame.pop()
        while len(self.changes) > last:
            modi = self.changes.pop()
            #TODO 判断类型并恢复相应更改

        self.depth -= 1
        pass

    def add_cl(self, cl: List, i: int) -> None:
        self.cnf[i] = cl
        for x in cl:
            self.var[abs(x)][0][i] = x > 0
            self.var[abs(x)][1][x > 0] += 1 # 正/负出现的次数

    def stash_cl(self, i: int) -> None:
        cl = self.cnf[i]
        for x in cl:
            a = self.var[abs(x)][0][i]
            self.var[abs(x)][1][a] -= 1
            del self.var[abs(x)][0][i]
        self.history.append((Changes.CLA, cl))
        del self.cnf[i]

    def remove_var(self, i: int, var: int):
        #TODO 处理变量的删除

        pass

    def __init__(self, n: int, cnf1: List):
        self.var = [ ([], (0, 0)) for i in range(n)]
        for x in cnf1 : self.add_cl(x, len(self.cnf))


# TODO 把搜索算法放到subclass里面
    def dpll(self) -> bool:  # false = CONFLICT
        try:
            while True:
                self.bcp()
                if not self.pure(): break;
        except Success:
            return True
        except Conflict:
            return False
        self.push()





    def cdcl(self) -> Tuple[bool, int]:
        raise ValueError("Not Implemented")

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

