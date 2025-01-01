## Tools for css codes

from typing import List,Set,Dict

def commutation_test(Sx:List[Set[int]],Sz:List[Set[int]]) -> bool:
    r"""
    function for taking two lists of sets and determining if they satisfy the necessary constraint
    """

    return all([(not len(sx&sz)%2) for sx in Sx for sz in Sz])
