## A class for a css code
## The code itself is specified by subsets of the set of qubits subject to certain consistency constraints
## We will initialize based on parity check matrices

import math
import numpy as np

from networkx import Graph
from typing import Dict, Set, List
from code_tools import commutation_test, order_set_list, generate_check_dict, generate_qubit_nbrs_dict

class cssCode:

    def __init__(self,Sx:List[Set[int]],Sz:List[Set[int]]) -> None:
        r"""
        Initialize a CSS code instance
        """

        assert commutation_test(Sx,Sz)

        self.code = {False:Sx,True:Sz}
        self.qubits = set.union(*(Sx+Sz))
        self.check_dict = {False:generate_check_dict(Sx), True:generate_check_dict(Sz)}
        self.qubit_dict = {q:[generate_qubit_nbrs_dict(Sx)[q],generate_qubit_nbrs_dict(Sz)[q]] for q in list(self.qubits)}
        
    ## Include methods for producing check matrices and Tanner graphs
    ## Can also change the presentation of a given linear code

    def to_check_matrices(self) -> List[List[List[int]]]:
        check_matrices = []
        
        for sector in [False,True]:
            labeler = self.check_dict[sector]
            chk_mat = np.zeros(shape=[len(labeler),len(self.qubits)],dtype=int)
            for row_label in labeler:
                for col_label in list(labeler[row_label]):
                    chk_mat[row_label,col_label] = 1
            check_matrices.append(chk_mat)

        return check_matrices
    
    def check_chain_graph(self) -> Graph:

        ccg = Graph()

        for xlabel in self.check_dict[False]:
            ccg.add_node((False,xlabel))

            xcheck = self.check_dict[False][xlabel]

            for zlabel in self.check_dict[True]:
                zcheck = self.check_dict[True][zlabel]
                if not xcheck.isdisjoint(zcheck):
                    ccg.add_edge((False,xlabel),(True,zlabel))

        return ccg


    def check_connectivity_graphs(self) -> Dict[bool,Graph]:

        z_ccg = Graph()
        x_ccg = Graph()

        for ii in range(len(self.check_dict[False])):
            xcheck1 = self.check_dict[False][ii]
            
            for jj in range(ii+1,len(self.check_dict[False])):
                xcheck2 = self.check_dict[False][jj]
                if not xcheck1.isdisjoint(xcheck2):
                    x_ccg.add_edge((False,ii),(False,jj))
                
        for ii in range(len(self.check_dict[True])):
            zcheck1 = self.check_dict[True][ii]
            
            for jj in range(ii+1,len(self.check_dict[True])):
                zcheck2 = self.check_dict[True][jj]
                if not zcheck1.isdisjoint(zcheck2):
                    z_ccg.add_edge((True,ii),(True,jj))

        return {False:x_ccg,True:z_ccg}


