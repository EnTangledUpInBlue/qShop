## Tools for css codes

from typing import List,Set,Dict

def commutation_test(Sx:List[Set[int]],Sz:List[Set[int]]) -> bool:
    r"""
    function for taking two lists of sets and determining if they satisfy the necessary constraint
    """

    return all([(not len(sx&sz)%2) for sx in Sx for sz in Sz])


def order_set_list(set_list:List[Set[int]]) -> List[Set[int]]:
    r"""
    Order a list of sets using a merge-sort algorithm and the set ordering is determined by the comparing 
    the minimum unique element for two sets.
    """

    if len(set_list) < 2:
        return set_list
    elif len(set_list) ==2:
        if min(set_list[0]-set_list[1])<min(set_list[1]-set_list[0]):
            return set_list
        else:
            return [set_list[1],set_list[0]]
        
    else:
        num_sets = len(set_list)
        opening_set = order_set_list(set_list[:int(num_sets/2)])
        closing_set = order_set_list(set_list[int(num_sets/2):])

        full_set_list = []

        while(len(opening_set)>0 and len(closing_set) > 0):

            if min(opening_set[0]-closing_set[0]) < min(closing_set[0] - opening_set[0]):
                full_set_list.append(opening_set.pop(0))            
            else:
                full_set_list.append(closing_set.pop(0))

        if len(opening_set)>0:
            full_set_list.extend(opening_set)
        else:
            full_set_list.extend(closing_set)
        
        return full_set_list


def max_elem(S:List[Set[int]]) -> int:
    
    max_elem = 0

    for subset in S:
        if max(subset)>max_elem:
            max_elem = max(subset)
    
    return max_elem

def min_elem(S:List[Set[int]]) -> int:

    assert len(S)>0

    min_elem = min(S[0])

    for subset in S[1:]:
        if min(subset)<min_elem:
            min_elem = min(subset)
    
    return min_elem
