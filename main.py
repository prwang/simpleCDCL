from typing import *
import itertools as It
from formula import Formula

def parse() -> Tuple[int, List]:
    tokens = iter([])
    try:
        while True:
            line1 = list(filter(None, input().strip().split()))
            if len(line1) and line1[0] != 'c':
                tokens = It.chain(tokens, input().split())
    except EOFError:
        pass
    clauses = []
    try:
        tokens = list(tokens)
        assert(not (len(tokens) < 4 or tokens[0] != 'p' or tokens[1] != 'cnf'))
        n, m = map(int, tokens[2:4])
        cc = []
        for num in map(int, tokens[4:]):
            if num == 0:
                if len(cc):
                    # (not x or x) = true
                    cc.sort(key = abs)
                    x = len(cc) - 1; i = 0
                    while i < x:
                        if abs(cc[x]) == abs(cc[x + 1]): break
                    if i != x: clauses.append(cc)
                    cc = []
            else: cc.append(num)
        if len(cc): clauses.append(cc)
        assert(len(cc) == m)
        return n, clauses
    except (ValueError, AssertionError):
        print("invalid cnf format")
        exit(1)


def main() -> None:
    n, M = parse()
    fm = Formula(n, M)


if __name__ == "__main__":
    main()
