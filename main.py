from typing import *
import sys
import itertools as It
from formula import Formula

def parse() -> Tuple[int, List]:
    tokens = iter([])
    try:
        while True:
            line1 = list(filter(None, input().strip().split()))
            if len(line1) and line1[0] != 'c':
                tokens = It.chain(tokens, line1)
    except EOFError:
        pass
    clauses = []
    try:
        tokens = list(tokens)
        assert len(tokens) >= 4 and tokens[0] == 'p' and tokens[1] == 'cnf'
        n, m = map(int, tokens[2:4])
        cc = []
        for num in map(int, tokens[4:]):
            if num == 0:
                if len(cc):
                    clauses.append(cc)
                    cc = []
            else: cc.append(num)
        if len(cc): clauses.append(cc)
        assert(len(clauses) == m) #FIXME
        return n, clauses
    except (ValueError, AssertionError) as e:
        print("invalid cnf format")
        raise e


def main() -> None:
    n, M = parse()
    fm = Formula(n, M)
    if fm.solve():
        print('sat')
        for i in range(1, n + 1):
            print("var_%d = %d"%(i, fm.model[i]))
    else:
        print('unsat')



if __name__ == "__main__":
    sys.stdin = open('./testfiles/aim/aim-50-1_6-no-1.cnf', 'r')
    main()

