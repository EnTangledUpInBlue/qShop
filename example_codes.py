## parity check matrices for the repetition code
from typing import List, Set, Dict
from rotated_surface_code_coordinates import rsurf_stabilizer_generators
from toric_code_coordinates import toric_stabilizer_generators
from standard_surface_code_coordinates import surf_stabilizer_generators
from bivariate_bicycle_checks import pcm




def surf_code(L:int) -> List[List[Set[int]]]:

    Sx,Sz = surf_stabilizer_generators(L)

    return Sx,Sz

def toric_code(Lx:int,Ly:int) -> List[List[Set[int]]]:

    Sx,Sz = toric_stabilizer_generators(Lx,Ly)

    return Sx,Sz

def rsurf_code(L:int) -> List[List[Set[int]]]:

    Sx,Sz = rsurf_stabilizer_generators(L)

    return Sx,Sz

def bf_rep_code(n:int) -> List[List[Set[int]]]:

    Sx = []
    Sz = []

    for i in range(n):
        Sz.append(set([i,i+1]))

    return Sx,Sz

def pf_rep_code(n:int) -> List[List[Set[int]]]:

    Sx = []
    Sz = []

    for i in range(n):
        Sx.append(set([i,i+1]))
    
    return Sx,Sz

def steane_code() -> List[List[Set[int]]]:

    r"""
    Steane code with the high-weight central qubit presentation of the stabilizer generators
    """

    S = [{0,1,2,3},{1,2,4,5},{2,3,5,6}]

    return S,S

def qpc(m:int,n:int) -> List[List[Set[int]]]:

    r"""
    Rotated variation of the Shor familty of quantum parity check codes with X (Z) type logical operators
    expressed in terms of single qubit X (Z) operators.

    :param m: size of blocks of consecutive qubit labels
    :param n: the number of blocks of qubits
    """

    Sx = []
    Sz = []

    nqubits = int(n*m)

    ## n blocks, each with m consecutive qubits

    for i in range(n):        
        for j in range(m-1):
            Sz.append({j+i*m,j+1+i*m})
        if i != n-1:
            Sx.append(set([i*m+k for k in range(2*n)]))

    return Sx,Sz

