from typing import List,Set,Dict,Tuple

def rsurf_qubit_coords(L1:int,L2:int) -> Set[Tuple[int,int]]:
    r"""
    Coordinates for the qubit locations in the rotated surface code. A factor of 2 is included to allow for 
    checks to be located at integer coordinates.

    :param L: The dimensions of the square lattice for the rotated surface code.

    :return:

    """

    qubit_coords = set()

    for ii in range(L1):
        for jj in range(L2):
                qubit_coords.add((2*ii,2*jj))
        
    return qubit_coords

def rsurf_check_coords(L1:int,L2:int) -> Tuple[Set[Tuple[int,int]]]:
    r"""
    Coordinates for the check locations in the rotated surface code.

    :param L1: The horizontal dimension of the rectangular lattice for the rotated surface code.
    :param L2: The vertical dimension of the rectangular lattice for the rotated surface code.

    :return: A list with two sets of coordinates. The first element consists of the 
    coordinates of the xchecks with the second element consisting of those for the 
    zchecks.
    """

    xcheck_coords = set()
    zcheck_coords = set()

    for ii in range(-1,L1):
        xcoord = 2*ii + 1
        for jj in range(-1,L2):
            ycoord = 2*jj+1

            if (ii+jj)%2 and (jj>-1 and jj<L2-1):
                xcheck_coords.add((xcoord,ycoord))

            elif (not (ii+jj)%2) and (ii>-1 and ii<L1-1):
                zcheck_coords.add((xcoord,ycoord))
    
    return (xcheck_coords,zcheck_coords)



def rsurf_q2i(L1:int,L2:int) -> Dict[Tuple[int,int],int]:
    r"""
    Creates a dictionary mapping qubit coordinates to integer labels. Note that this mapping is based on the lowest integer label and 
    is different than might be expected based on geometry of the lattice.

    :param L1: The dimensions of the square lattice for the rotated surface code.
    :param L2: The dimensions of the square lattice for the rotated surface code.
    
    :return:
    """
    qcoords = rsurf_qubit_coords(L1,L2)

    q2i:Dict[Tuple[int,int],int] = {q: i for i,q in enumerate(sorted(qcoords, key=lambda v:(v[0],v[1])))}

    return q2i

def rsurf_c2i(L1:int,L2:int) -> Dict[bool,Dict[Tuple[int,int],int]]:
    r"""
    Creates a dictionary mapping check coordinates to integer labels.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    :return:
    """
    xcoords,zcoords = rsurf_check_coords(L1,L2)

    x2i:Dict[Tuple[int,int],int] = {x: i for i,x in enumerate(sorted(xcoords,key = lambda v:(v[0],v[1])))}

    z2i:Dict[Tuple[int,int],int] = {z: i for i,z in enumerate(sorted(zcoords,key = lambda v:(v[0],v[1])))}

    return {False:x2i,True:z2i}

def rsurf_stabilizer_generators(L1:int,L2:int) -> List[List[Set[int]]]:
    r"""
    Function to use specify the set of generating operators for the rotated surface code.
    Qubits are labeled according to the function q2i.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    q2i = rsurf_q2i(L1,L2)
    c2i = rsurf_c2i(L1,L2)

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

def potential_nbrhd(r:Tuple[int,int]) -> Set[Tuple[int,int]]:
    r"""
    Function for producing a set of coordinates neighboring the input tuple r

    :param r: Tuple of integers representing the coordinates on a square grid.

    :return: A list of tuples of integers represeting the neighboring coordinates on the square grid.

    """

    nbrs = set()
    deltas = [1,-1]

    for dx in deltas:
        for dy in deltas:
            nbrs.add((r[0]+dx,r[1]+dy))

    return nbrs
