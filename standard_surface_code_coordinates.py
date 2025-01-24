from typing import List,Set,Dict,Tuple

def surf_qubit_coords(L:int) -> Set[Tuple[int,int]]:

    if L == 2:
        return set([(0,0), (1,1), (0,2), (2,0), (2,2)])
    
    else:
        Lset = surf_qubit_coords(L-1)
        for coord1 in range(2*L-1):

            Lset.add((coord1,2*(L-1)-coord1%2))
            Lset.add((2*(L-1)-coord1%2,coord1))
        
        return Lset
            


def surf_check_coords(L:int) -> List[Set[Tuple[int,int]]]:
    r"""
    Coordinates for the check locations in the standard surface code

    :param L: The dimensions of the square lattice for the standard surface code.
    
    """

    if L==2:
        xcheck_coords = {(0,1), (2,1)}

        zcheck_coords = {(1,0),(1,3)}

        return [xcheck_coords,zcheck_coords]
    
    else:
        xcheck_coords,zcheck_coords = surf_check_coords(L-1)

        z1 = (1,2*(L-1))
        z2 = (2*(L-1)-1,0)

        dy = 2

        zcheck_coords.add(z1)
        zcheck_coords.add(z2)

        x1 = (0,2*(L-1)-1)
        x2 = (2*(L-1),1)

        dx = 2

        xcheck_coords.add(x1)
        xcheck_coords.add(x2)


        for ii in range(L-2):

            z1 = (z1[0]+dy,z1[1])
            z2 = (z2[0],z2[1]+dy)

            zcheck_coords.add(z1)
            zcheck_coords.add(z2)            

            x1 = (x1[0]+dx, x1[1])
            x2 = (x2[0],x2[1]+dx)
        
            xcheck_coords.add(x1)
            xcheck_coords.add(x2)

        return [xcheck_coords,zcheck_coords]

def surf_q2i(L:int) -> Dict[Tuple[int,int],int]:
    r"""
    Creates a dictionary mapping qubit coordinates to integer labels. Note that this mapping is based on the lowest integer label and 
    is different than might be expected based on geometry of the lattice.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    qcoords = surf_qubit_coords(L)

    q2i:Dict[Tuple[int,int],int] = {q: i for i,q in enumerate(sorted(qcoords, key=lambda v:(v[0],v[1])))}

    return q2i

def surf_c2i(L:int) -> Dict[bool,Dict[Tuple[int,int],int]]:
    r"""
    Creates a dictionary mapping check coordinates to integer labels.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    xcoords,zcoords = surf_check_coords(L)

    x2i:Dict[Tuple[int,int],int] = {x: i for i,x in enumerate(sorted(xcoords,key = lambda v:(v[0],v[1])))}

    z2i:Dict[Tuple[int,int],int] = {z: i for i,z in enumerate(sorted(zcoords,key = lambda v:(v[0],v[1])))}

    return {False:x2i,True:z2i}


def surf_stabilizer_generators(L:int) -> List[List[Set[int]]]:
    r"""
    Function to use specify the set of generating operators for the rotated surface code.
    Qubits are labeled according to the function q2i.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    q2i = surf_q2i(L)
    c2i = surf_c2i(L)

    stabs = []

    for sector in [False,True]:
        sect_stabs = []
        for check in c2i[sector]:
            chk = set()
            for pot_q in potential_nbrhd(check):
                if pot_q in q2i:
                    chk.add(q2i[pot_q])
            sect_stabs.append(chk)
        stabs.append(sect_stabs)

    return stabs


def potential_nbrhd(r:Tuple[int,int]) -> List[Tuple[int,int]]:
    r"""
    Function for producing a set of coordinates neighboring the input tuple r

    """

    nbrs = []

    deltas = [1,-1]

    for x in deltas:
        nbrs.append((r[0]+x,r[1]))
        nbrs.append((r[0],r[1]+x))

    return nbrs