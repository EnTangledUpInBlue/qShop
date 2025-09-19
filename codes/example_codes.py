# parity check matrices for a growing set of CSS codes

from typing import List, Set
from codes.rotated_surface_code_coordinates import rsurf_stabilizer_generators
from codes.toric_code_coordinates import toric_stabilizer_generators
from codes.standard_surface_code_coordinates import surf_stabilizer_generators

__all__ = [
    "bf_rep_code",
    "pf_rep_code",
    "qpc",
    "rsurf_code",
    "steane_code",
    "surf_code",
    "toric_code",
]


def bf_rep_code(n: int) -> List[List[Set[int]]]:
    r"""
    Bit-flip repetition code

    """

    Sx = []
    Sz = []

    for i in range(n):
        Sz.append(set([i, i + 1]))

    return Sx, Sz


def pf_rep_code(n: int) -> List[List[Set[int]]]:
    r"""
    Phase-flip repetition code
    """
    Sx = []
    Sz = []

    for i in range(n):
        Sx.append(set([i, i + 1]))

    return Sx, Sz


def qpc(m: int, n: int) -> List[List[Set[int]]]:
    r"""
    Rotated variation of the Shor familty of quantum parity check codes with X (Z) type logical operators
    expressed in terms of single qubit X (Z) operators.

    :param m: size of blocks of consecutive qubit labels
    :param n: the number of blocks of qubits
    """

    Sx = []
    Sz = []

    # n blocks, each with m consecutive qubits

    for i in range(n):
        for j in range(m - 1):
            Sz.append({j + i * m, j + 1 + i * m})
        if i != n - 1:
            Sx.append(set([i * m + k for k in range(2 * n)]))

    return Sx, Sz


def rsurf_code(L1: int, L2: int) -> List[List[Set[int]]]:
    r"""
    Rotated surface code with dimensions L1 x L2
    """

    Sx, Sz = rsurf_stabilizer_generators(L1, L2)

    return Sx, Sz


def steane_code() -> List[List[Set[int]]]:
    r"""
    Steane code with the high-weight central qubit presentation of the stabilizer generators
    """

    S = [{0, 1, 2, 3}, {1, 2, 4, 5}, {2, 3, 5, 6}]

    return S, S


def surf_code(L1: int, L2: int) -> List[List[Set[int]]]:
    r"""
    Standard, or 'planar', surface code with minimum distances L1 and L2
    """

    Sx, Sz = surf_stabilizer_generators(L1, L2)

    return Sx, Sz


def toric_code(Lx: int, Ly: int) -> List[List[Set[int]]]:
    r"""
    Toric code with minimum distances Lx and Ly
    """

    Sx, Sz = toric_stabilizer_generators(Lx, Ly)

    return Sx, Sz
