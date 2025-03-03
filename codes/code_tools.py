## Tools for css codes

from typing import List,Set,Dict

def commutation_test(Sx:List[Set[int]],Sz:List[Set[int]]) -> bool:
    r"""
    function for taking two lists of sets and determining if they satisfy the necessary constraint
    """

    return all([(not len(sx&sz)%2) for sx in Sx for sz in Sz])

def remove_empties(set_list:List[Set[int]]) -> List[Set[int]]:
    r"""
    Function that removes empty sets from the input list of sets and returns the modified list
    """
    
    while set() in set_list:
        set_list.remove(set())
    return set_list

def remove_duplicates(set_list:List[Set[int]]) -> List[Set[int]]:

    new_list = []
    for x in set_list:
        if x not in new_list:
            new_list.append(x)
    
    return new_list

def pivot_finder(set_list:List[Set[int]],piv_list:List[Set[int]]) -> List[Set[int]]:
    r"""
    Function that takes as input a list of sets and returns an equivalent list of generators that have
    unique minimum elements.
    """
    
    set_list = remove_empties(set_list)
    set_list = remove_duplicates(set_list)

    # print(set_list)
    # print(piv_list)
    # print()

    if not len(set_list):
        return piv_list
    
    else:
        ord_list = order_set_list(set_list)

        # print(len(set_list))
        # print(len(piv_list))
        
        if len(ord_list)==1:
            piv_list.append(ord_list[0])
            return piv_list
        
        else:

            new_pivot = ord_list.pop(0)

            q = min(new_pivot)

            # print('q = ' + str(q) + '\n')

            for chk in ord_list:
                if q in chk:
                    chk ^= new_pivot
            piv_list.append(new_pivot)

            return pivot_finder(ord_list,piv_list)

def order_set_list(set_list:List[Set[int]]) -> List[Set[int]]:
    r"""
    Order a list of sets using a merge-sort algorithm and the set ordering is determined by the comparing 
    the minimum unique element for two sets.
    """

    set_list = remove_empties(set_list)
    set_list = remove_duplicates(set_list)

    if len(set_list) < 2:
        return set_list
    
    elif len(set_list) == 2:
        ## There is an issue is one set is a subset of the other
        # print(set_list)
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
    
def generate_check_dict(set_list:List[Set[int]]) -> Dict[int,Set[int]]:
    r"""
    Takes a list of sets and labels them according to the ordering in order_set_list

    """

    check_dict = dict()

    set_list_ordered = order_set_list(set_list)

    for i in range(len(set_list_ordered)):
        check_dict[i] = set_list_ordered[i]

    return check_dict

def generate_qubit_nbrs_dict(set_list:List[Set[int]]) -> Dict[int,Set[int]]:
    r"""
    A function to generate a dictionary that maps qubit labels to a labeling of the sets containing them.
    The labeling is assigned by the generate_check_dict function.

    INPUT: List of sets of qubit labels
    OUTPUT: Dictionary mapping qubit labels to a set of the integer labels for the input sets
    """

    qubits = set.union(*set_list)

    qubit_dict: Dict[int,Set[int]] = { q: set() for q in list(qubits)}

    i2c = generate_check_dict(set_list)
    c2i = {tuple(sorted(list(v))):k for k,v in i2c.items()}

    for q in list(qubits):
        for chk in set_list:
            if q in chk:
                qubit_dict[q].add(c2i[tuple(sorted(list(chk)))])

    return qubit_dict

def pcm_to_sets(H:List[List[int]]) -> List[Set[int]]:
    r"""
    Takes in a parity check matrix and returns the supports as sets of qubit labels for each row, i.e., check operator
    """

    gens = []

    for row in range(len(H)):
        row_set = set()
        for col in range(len(H[0])):
            if H[row][col]:
                row_set.add(col)
        gens.append(row_set)

    return gens

def max_elem(S:List[Set[int]]) -> int:
    r"""
    Takes in a list of sets of non-negative integers and outputs the maximum element over all sets
    """

    full_set = set.union(*S)

    return max(full_set)
    

def min_elem(S:List[Set[int]]) -> int:
    r"""
    Takes in a list of sets of non-negative integers and outputs the minimum element over all sets
    """
    full_set = set.union(*S)
    
    return min(full_set)