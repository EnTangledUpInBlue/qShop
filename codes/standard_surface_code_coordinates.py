from typing import List, Set, Dict, Tuple


def surf_qubit_coords(L1: int, L2: int) -> Set[Tuple[int, int]]:
    r"""
    Coordinates for the qubits in the standard surface code.

    :param L1:
    :param L2:

    :return:
    """

    if L1 == 1:
        return set([(0, 2 * ii) for ii in range(L2)])

    else:
        Lset = surf_qubit_coords(L1 - 1, L2)
        xcoord = 2 * L1 - 2
        for jj in range(L2 - 1):
            ycoord = 2 * jj
            Lset.add((xcoord, ycoord))
            Lset.add((xcoord - 1, ycoord + 1))
        Lset.add((xcoord, 2 * (L2 - 1)))

        return Lset


def surf_check_coords(L1: int, L2: int) -> List[Set[Tuple[int, int]]]:
    r"""
    Coordinates for the check locations in the standard surface code

    :param L1: The dimensions of the square lattice for the standard surface code.
    :param L2:

    :return:
    """

    if L1 == 1:
        xcheck_coords = set([(0, 2 * jj + 1) for jj in range(L2 - 1)])

        zcheck_coords = set()

    else:
        xcheck_coords, zcheck_coords = surf_check_coords(L1 - 1, L2)

        xcoord = 2 * L1 - 2

        for jj in range(L2 - 1):
            zcheck_coords.add((xcoord - 1, 2 * jj))
            xcheck_coords.add((xcoord, 2 * jj + 1))

        zcheck_coords.add((xcoord - 1, 2 * (L2 - 1)))

    return [xcheck_coords, zcheck_coords]


def surf_q2i(L1: int, L2: int) -> Dict[Tuple[int, int], int]:
    r"""
    Creates a dictionary mapping qubit coordinates to integer labels.
    Note that this mapping is based on the lowest integer label and
    is different than might be expected based on geometry of the lattice.

    :param L1: The dimensions of the square lattice for the rotated surface code.
    :param L2:

    :return:
    """
    qcoords = surf_qubit_coords(L1, L2)

    q2i: Dict[Tuple[int, int], int] = {
        q: i for i, q in enumerate(sorted(qcoords, key=lambda v: (v[0], v[1])))
    }

    return q2i


def surf_c2i(L1: int, L2: int) -> Dict[bool, Dict[Tuple[int, int], int]]:
    r"""
    Creates a dictionary mapping check coordinates to integer labels.

    :param L1: The dimensions of the square lattice for the rotated surface code.
    :param L2:

    :return:
    """
    xcoords, zcoords = surf_check_coords(L1, L2)

    x2i: Dict[Tuple[int, int], int] = {
        x: i for i, x in enumerate(sorted(xcoords, key=lambda v: (v[0], v[1])))
    }

    z2i: Dict[Tuple[int, int], int] = {
        z: i for i, z in enumerate(sorted(zcoords, key=lambda v: (v[0], v[1])))
    }

    return {False: x2i, True: z2i}


def surf_stabilizer_generators(L1: int, L2: int) -> List[List[Set[int]]]:
    r"""
    Function to use specify the set of generating operators for the rotated surface code.
    Qubits are labeled according to the function q2i.

    :param L1: The dimensions of the square lattice for the rotated surface code.
    :param L2:

    :return:
    """
    q2i = surf_q2i(L1, L2)
    c2i = surf_c2i(L1, L2)

    stabs = []

    for sector in [False, True]:
        sect_stabs = []
        for check in c2i[sector]:
            chk = set()
            for pot_q in potential_nbrhd(check):
                if pot_q in q2i:
                    chk.add(q2i[pot_q])
            sect_stabs.append(chk)
        stabs.append(sect_stabs)

    return stabs


def potential_nbrhd(r: Tuple[int, int]) -> List[Tuple[int, int]]:
    r"""
    Function for producing a set of coordinates neighboring the input tuple r

    :param r:

    :return:
    """

    nbrs = []

    deltas = [1, -1]

    for x in deltas:
        nbrs.append((r[0] + x, r[1]))
        nbrs.append((r[0], r[1] + x))

    return nbrs
