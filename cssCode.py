## A class for a css code
## The code itself is specified by subsets of the set of qubits subject to certain consistency constraints
## We will initialize based on parity check matrices

import math
import numpy as np
from typing import Dict, Set, List
from code_tools import commutation_test, order_set_list

class cssCode:

    def __init__(self,Sx:List[Set[int]],Sz:List[Set[int]]) -> None:
        r"""
        Initialize a CSS code instance
        """

        assert commutation_test(Sx,Sz)

        self.code = {False:Sx,True:Sz}
        self.qubits = set.union(*(Sx+Sz))

        


    def to_check_matrices(self) -> List[List[List[int]]]:


        Hx = []
        Hz = []


        return Hx,Hz




