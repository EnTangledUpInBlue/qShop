from typing import List,Set,Dict,Tuple

def rsurf_qubit_coords(L1:int,L2:int) -> Set[Tuple[int,int]]:
    r"""
    Coordinates for the qubit locations in the rotated surface code. A factor of 2 is included to allow for 
    checks to be located at integer coordinates.

    :param L: The dimensions of the square lattice for the rotated surface code.

    """

    if L1==1:
        Lset = set([(0,2*coord2) for coord2 in range(L2)])
    
    else:
        Lset = rsurf_qubit_coords(L1-1,L2)
        for coord1 in range(L2):
            Lset.add(((2*(L1-1)),2*coord1))
        
    return Lset

def rsurf_check_coords(L1:int,L2:int) -> List[Set[Tuple[int,int]]]:
    r"""
    Coordinates for the check locations in the rotated surface code

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """

    if L1==3:
        xcheck_coords = {(-1,1), (1,3), (3,1), (5,3)}

        zcheck_coords = {(1,1),(1,5),(3,-1), (3,3)}

        return [xcheck_coords,zcheck_coords]
    
    else:
        xcheck_coords,zcheck_coords = rsurf_check_coords(L-2)

        z1 = (1,2*L-1)
        z2 = (2*L-3,-1)
        dy = [-2,2]

        zcheck_coords.add(z1)
        zcheck_coords.add(z2)

        for ii in range(L-2):
            z1 = (z1[0]+2,z1[1]+dy[ii%2])
            z2 = (z2[0]+dy[ii%2],z2[1]+2)

            zcheck_coords.add(z1)
            zcheck_coords.add(z2)            

        x1 = (-1,2*L-5)
        x2 = (2*L-3,1)
        dx = [2,-2]

        xcheck_coords.add(x1)
        xcheck_coords.add(x2)

        for ii in range(L-2):
            x1 = (x1[0]+2, x1[1]+dx[ii%2])
            x2 = (x2[0]+dx[ii%2],x2[1]+2)
            xcheck_coords.add(x1)
            xcheck_coords.add(x2)

        return xcheck_coords,zcheck_coords

def rsurf_q2i(L:int) -> Dict[Tuple[int,int],int]:
    r"""
    Creates a dictionary mapping qubit coordinates to integer labels. Note that this mapping is based on the lowest integer label and 
    is different than might be expected based on geometry of the lattice.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    qcoords = rsurf_qubit_coords(L)

    q2i:Dict[Tuple[int,int],int] = {q: i for i,q in enumerate(sorted(qcoords, key=lambda v:(v[0],v[1])))}

    return q2i

def rsurf_c2i(L:int) -> Dict[bool,Dict[Tuple[int,int],int]]:
    r"""
    Creates a dictionary mapping check coordinates to integer labels.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    xcoords,zcoords = rsurf_check_coords(L)

    x2i:Dict[Tuple[int,int],int] = {x: i for i,x in enumerate(sorted(xcoords,key = lambda v:(v[0],v[1])))}

    z2i:Dict[Tuple[int,int],int] = {z: i for i,z in enumerate(sorted(zcoords,key = lambda v:(v[0],v[1])))}

    return {False:x2i,True:z2i}

def rsurf_stabilizer_generators(L:int) -> List[List[Set[int]]]:
    r"""
    Function to use specify the set of generating operators for the rotated surface code.
    Qubits are labeled according to the function q2i.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    q2i = rsurf_q2i(L)
    c2i = rsurf_c2i(L)

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
        for y in deltas:
            nbrs.append((r[0]+x,r[1]+y))

    return nbrs
