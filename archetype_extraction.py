#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import sys
import functools
import difflib
import re
import itertools

# testing
import unittest
import cProfile
from pstats import Stats

__author__ = "Dmitry Luciv"
__copyright__ = "Copyright 2018+, The DocLine Project"
__credits__ = ["Dmitry Luciv"]
__license__ = "LGPL"
__version__ = "1.0.1"
__maintainer__ = "Dmitry Luciv"
__email__ = "dluciv@dluciv.name"  # Victor Dolotov
__status__ = "Alpha"


def permutations_first_volatile(rank: 'int', n_cover: 'int' = 3):
    """
    Generate subset of all possible permutations with first values changing more frequently
    :param rank: Permutations are tuples of [0, ..., rank)
    :param n_cover: number of first permutation elements to take all possible values
    :return: iterable of permutations
    """
    if n_cover > rank:
        n_cover = rank

    initial = list(reversed(range(rank)))
    initial_s = set(initial)

    for c in itertools.combinations(initial, n_cover):
        pf = tuple(reversed(c))
        yield pf + tuple(initial_s.difference(pf))

@functools.lru_cache(maxsize=None)
def two_tuples_lcs(w1: 'tuple[str]', w2: 'tuple[str]') -> 'tuple[str]':
    sm = difflib.SequenceMatcher(None, w1, w2, False)
    matches = sm.get_matching_blocks()
    return tuple(itertools.chain(*[ w1[match.a: match.a + match.size] for match in matches ]))


@functools.lru_cache(maxsize=None)
def possible_n_tuples_lcs(ws: 'iterable[tuple[str]]') -> 'tuple[str]':
    # operator.reduce is a kind of foldl
    return functools.reduce(two_tuples_lcs, ws)

@functools.lru_cache(maxsize=None)
def best_n_tuples_lcs(strings: 'tuple[tuple[str]]') -> 'tuple[str]':
    strings = tuple(set(strings))
    best_archetype = ()
    best_archetype_len = 0
    for p in permutations_first_volatile(len(strings)):
        permuted_strings = tuple(strings[i] for i in p)
        archetype = possible_n_tuples_lcs(permuted_strings)
        archetype_len = len(' '.join(archetype))
        if archetype_len > best_archetype_len:
            best_archetype = archetype
            best_archetype_len = archetype_len
    return best_archetype



if __name__ == '__main__':
    unittest.main()
    # raise Exception("This is not an entry point")
