from typing import *
import sys
import itertools as It
from search import CdclEngine


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
                cc = list(set(cc))
                if len(cc):
                    cc.sort(key=abs)
                    N = len(cc) - 1; i = 0
                    while i < N:
                        if abs(cc[i]) == abs(cc[i + 1]): break
                        i += 1
                    if i == N:
                        clauses.append(cc)
                    cc = []
            else: cc.append(num)
        if len(cc): clauses.append(cc)
        assert(len(clauses) == m)
        return n, clauses
    except (ValueError, AssertionError) as e:
        print("invalid cnf format")
        raise e


def main() -> None:
    n, M = parse()
    fm = CdclEngine(n, M)
    if fm.solve():
        print('sat')
        for i in range(1, n + 1):
            print("var_%d = %d"%(i, fm.model[i]))
    else:
        print('unsat')



if __name__ == "__main__":
    sys.stdin = open('in.cnf', 'r')
    main()

