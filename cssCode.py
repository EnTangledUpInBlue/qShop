## A class for a css code
## The code itself is specified by subsets of the set of qubits subject to certain consistency constraints
## We will initialize based on parity check matrices

import math
import numpy as np
from typing import Dict, Set, List

class cssCode:

    def __init__(self,Sx:List[Set[int]],Sz:List[Set[int]]) -> None:
        r"""
        Initialize a CSS code instance
        """

        self.code = {False:Sx,True:Sz}

        assert commutation_test(Sx,Sz)

        self.qubits = set.union(*(Sx+Sz))


