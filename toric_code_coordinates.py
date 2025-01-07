from typing import List,Set,Dict,Tuple

def toric_code_coords(Lx:int,Ly:int) -> List[Set[Tuple[int,int]]]:
    
    qubit_coords = set()
    xcheck_coords = set()
    zcheck_coords = set()

    for x in range(2*Lx):
        for y in range(2*Ly):
            if x%2:
                if y%2:
                    zcheck_coords.add((x,y))
                else:
                    qubit_coords.add((x,y))
            else:
                if y%2:
                    qubit_coords.add((x,y))
                else:
                    xcheck_coords.add((x,y))
    return [qubit_coords,xcheck_coords,zcheck_coords]


def toric_q2i(Lx:int,Ly:int) -> Dict[Tuple[int,int],int]:
    r"""
    Creates a dictionary mapping qubit coordinates to integer labels

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    qcoords = toric_code_coords(Lx,Ly)[0]

    q2i:Dict[Tuple[int,int],int] = {q: i for i,q in enumerate(sorted(qcoords, key=lambda v:(v[0],v[1])))}

    return q2i

def toric_c2i(Lx:int,Ly:int) -> Dict[bool,Dict[Tuple[int,int],int]]:
    r"""
    Creates a dictionary mapping check coordinates to integer labels.

    :param L: The dimensions of the square lattice for the rotated surface code.
    
    """
    xcoords,zcoords = toric_code_coords(Lx,Ly)[1:]

    x2i:Dict[Tuple[int,int],int] = {x: i for i,x in enumerate(sorted(xcoords,key = lambda v:(v[0],v[1])))}

    z2i:Dict[Tuple[int,int],int] = {z: i for i,z in enumerate(sorted(zcoords,key = lambda v:(v[0],v[1])))}

    return {False:x2i,True:z2i}

def toric_stabilizer_generators(Lx:int,Ly:int) -> List[List[Set[int]]]:

    q2i = toric_q2i(Lx,Ly)
    c2i = toric_c2i(Lx,Ly)

    stabs = []

    for sector in [False,True]:
        sect_stabs = []
        for check in c2i[sector]:
            chk = set()
            for pot_q in potential_nbrhd(Lx,Ly,check):
                if pot_q in q2i:
                    chk.add(q2i[pot_q])
            sect_stabs.append(chk)
        stabs.append(sect_stabs)

    return stabs

def potential_nbrhd(Lx:int,Ly:int,r:Tuple[int,int]) -> List[Tuple[int,int]]:
    r"""
    Function for producing a set of coordinates neighboring the input tuple r

    """

    nbrs = []
    deltas = [1,-1]

    for x in deltas:
        nbrs.append(((r[0]+x)%(2*Lx),r[1]))
        nbrs.append((r[0],(r[1]+x)%(2*Ly)))

    return nbrs