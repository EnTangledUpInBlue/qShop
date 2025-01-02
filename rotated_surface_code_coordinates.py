from typing import List,Set,Dict,Tuple

def rsurf_qubit_coords(L:int) -> Set[Tuple[int,int]]:

    if L==1:
        return set([(0,0)])
    
    else:
        Lset = rsurf_qubit_coords(L-1)
        for coord1 in range(L-2,L):
            Lset.add((2*coord1,2*coord1))

            for coord2 in range(coord1):
                Lset.add((2*coord1,2*coord2))
                Lset.add((2*coord2,2*coord1))
        
        return Lset

