from typing import *
import itertools as It
from formula import Formula


def parse() -> Tuple[int, List]:

    tokens = iter([])
    try:
        while True:
            line1 = list(filter(None, input().strip().split()))
            if len(line1) and line1[0] != 'c' :
                tokens = It.chain(tokens, input().split())
    except EOFError:
        pass
    clauses = []
    try:
        tokens = list(tokens)
        if (len(tokens) < 4 or tokens[0] != 'p'
            or tokens[1] != 'cnf'):  raise ValueError
        n, m = map(int, tokens[2:4])
        cc = []
        for num in map(int, tokens[4:]):
            if num == 0:
                if len(cc): clauses.append(cc);  cc = []
            else: cc.append(num)
        if len(cc): clauses.append(cc)
        if (len(cc) < m) : raise ValueError;
    except ValueError:
        print('invalid cnf file')
        raise ValueError
    return n, clauses


def main() -> None:
    n, M = parse()
    fm = Formula(n, M)


if __name__ == "__main__":
    main()
