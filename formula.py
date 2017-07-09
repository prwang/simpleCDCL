from typing import *
from enum import IntEnum


class Changes(IntEnum):
    VAR = 1 # remove a variable(being assigned false) from a clause
    CLA = 2 # remove a whole clause(being satisfied)
    ASG = 4 # variable assignment, the cause of VAR & CLA



class Formula:
    cnf: Dict[int, Set[int]] = []
    var: List[Tuple[
        Dict[int, bool], # identity(+-) of its occurrences in each clause
        Tuple[int, int] # number of negatively and/or positively occurrences
    ]] = None
    assign : Dict[int, int] = [] # TODO
    depth = 0
    # TODO dict for unit clauses
    changes : List[Tuple[Changes, Union[
            Tuple[List[int], int], #add_cl
            Tuple[int, int], # add_var
            #TODO
    ]]] = []


    frame : List[int]
    history : List

    # 两种类型的修改：
    #  [x] 删除整个从句（其逆是加回这个从句）
    #  [x] 分别是删除从句中的一个变量，当决定这个变量为假的时候（其逆是加回来这个变量），和
    #  [x] 相应的恢复操作
    def push(self) -> None:
        self.depth += 1
        self.frame.append(len(self.history))
        pass

    def pop(self) -> None:
        last = self.frame.pop()
        while len(self.changes) > last:
            modi = self.changes.pop()
            if modi[0] == Changes.CLA:
                self.add_cl(modi[1][0], modi[1][1])
            elif modi[0] == Changes.VAR:
                self.add_var(modi[1][0], modi[1][1])
            elif modi[0] == Changes.ASG: #TODO
                pass
        self.depth -= 1
        pass

    def add_cl(self, cl: List, i: int) -> None:
        self.cnf[i] = set(cl)
        for x in cl:
            self.var[abs(x)][0][i] = x > 0
            self.var[abs(x)][1][x > 0] += 1

    def stash_cl(self, i: int) -> None:
        cl = list(self.cnf[i]) #XXX overhead of transforming between sets & lists
        for x in cl:
            a = self.var[abs(x)][0][i]
            self.var[abs(x)][1][a] -= 1
            del self.var[abs(x)][0][i]
        self.history.append((Changes.CLA, (cl, i)))
        del self.cnf[i]

    def remove_var(self, i: int, var: int) -> None:
        cl = self.cnf[i]; v1 = self.var[abs(var)]
        cl.remove(var) # throws KeyError if var not existing
        v1[0].remove(i)
        v1[1][var > 0] -= 1
        self.history.append((Changes.VAR, (i, var)))

    def add_var(self, i : int, var : int) -> None:
        cl = self.cnf[i]; v1 = self.var[abs(var)]
        assert(var not in cl and -var not in cl);
        cl.add(var)
        v1[0][i] = var > 0
        v1[1][var > 0] += 1

    def bcp(self): # TODO 找到单位子句并确定其值，
        # 什么时候会改变单位从句的列表？以上两种操作
        # 这一步会不会出现矛盾？

        pass
    def __init__(self, n: int, cnf1: List):
        self.var = [ ([], (0, 0)) for i in range(n)]
        for x in cnf1 : self.add_cl(x, len(self.cnf))


