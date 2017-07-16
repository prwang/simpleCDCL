from typing import *
import sys
import itertools as It
from formula import Formula
import logging
from datetime import datetime
import re

def parse() -> Tuple[int, List]:
    tokens = iter([])
    try:
        while True:
            line1 = list(filter(None, input().strip().split()))
            if len(line1) and line1[0] != 'c':
                tokens = It.chain(tokens, line1)
                logging.info(line1)
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
        assert(len(clauses) == m)
        return n, clauses
    except (ValueError, AssertionError) as e:
        print("invalid cnf format")
        raise e

def main() -> None:
    try:
        logging.basicConfig(filename='logs/run%s.log'%
                                     re.sub('\W+','_', str(datetime.now()))
                            , level=logging.DEBUG)
    except FileNotFoundError:
        logging.disable(2333)
    logging.info('original file is:')
    n, M = parse()
    fm = Formula(n, M)
    if fm.solve():
        print('s SATISFIABLE')
        #logging.debug(str(fm.model))
    else:
        print('s UNSATISFIABLE')



if __name__ == "__main__":
    sys.stdin = open(sys.argv[1], 'r', encoding='utf-8')
    main()

