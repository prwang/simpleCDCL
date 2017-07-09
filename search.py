from typing import *
from formula import Formula

class Success(Exception): pass


class Conflict(Exception): pass


class DpllEngine(Formula):
    def search(self) -> bool:  # false = CONFLICT
        try:
            while True:
                self.bcp()
                if not self.pure(): break;
        except Success:
            return True
        except Conflict:
            return False
        self.push()
        #TODO 实现DPLL引擎




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
    pass
    #TODO 实现cdcl，注意只用做一边决策，
    #TODO 因为另一边会由于附加了矛盾式子而直接被deduce出来
