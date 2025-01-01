## parity check matrices for the repetition code
from typing import List, Set, Dict

def bf_rep_code(n:int) -> Dict[bool,List[Set[int]]]:

    Sx = []
    Sz = []

    for i in range(n):
        Sz.append(set([i,i+1]))
    
    code = {False:Sx, True:Sz}

    return code

def pf_rep_code(n:int) -> Dict[bool,List[Set[int]]]:

    Sx = []
    Sz = []

    for i in range(n):
        Sx.append(set([i,i+1]))
    
    code = {False:Sx, True:Sz}

    return code

def steane_code() -> Dict[bool,List[Set[int]]]:

    r"""
    Steane code with the high-weight central qubit presentation of the stabilizer generators
    """

    plaquettes = [{0,1,2,3},{1,2,4,5},{2,3,5,6}]

    return {False:plaquettes,True:plaquettes}

def qpc(m:int,n:int) -> Dict[bool,List[Set[int]]]:

    r"""
    Rotated variation of the quantum parity check codes, with logical X
    in terms of physical X operators and same for Z
    """

    Sx = []
    Sz = []

    nqubits = int(n*m)

    ## n blocks, each with length m

    for i in range(n):        
        for j in range(m-1):
            Sz.append({j+i*m,j+1+i*m})
        if i != n-1:
            Sx.append(set([i*m+k for k in range(2*n)]))

    return {False:Sx,True:Sz}

