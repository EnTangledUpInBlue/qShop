## A class for a css code
## The code itself is specified by subsets of the set of qubits subject to certain consistency constraints
## We will initialize based on parity check matrices

import math
import numpy as np

from networkx import Graph
from typing import Dict, Set, List
from code_tools import commutation_test, order_set_list, generate_label_dict

class cssCode:

    def __init__(self,Sx:List[Set[int]],Sz:List[Set[int]]) -> None:
        r"""
        Initialize a CSS code instance
        """

        assert commutation_test(Sx,Sz)

        self.code = {False:Sx,True:Sz}
        self.qubits = set.union(*(Sx+Sz))
        self.check_labels = {False:generate_label_dict(Sx), True:generate_label_dict(Sz)}

        
    ## Include methods for producing check matrices and Tanner graphs
    ## Can also change the presentation of a given linear code

    def to_check_matrices(self) -> List[List[List[int]]]:
        check_matrices = []
        
        for sector in [False,True]:
            labeler = self.check_labels[sector]
            chk_mat = np.zeros(shape=[len(labeler),len(self.qubits)],dtype=int)
            for row_label in labeler:
                for col_label in list(labeler[row_label]):
                    chk_mat[row_label,col_label] = 1
            check_matrices.append(chk_mat)

        return check_matrices
    
    def check_connectivity_graph(self) -> Graph:

        ccg = Graph()

        for xlabel in self.check_labels[False]:
            ccg.add_node((False,xlabel))

            xcheck = self.check_labels[False][xlabel]

            for zlabel in self.check_labels[True]:
                zcheck = self.check_labels[True][zlabel]
                if not xcheck.isdisjoint(zcheck):
                    ccg.add_edge((False,xlabel),(True,zlabel))

        return ccg




