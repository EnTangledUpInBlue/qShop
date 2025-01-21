## A class for a css code
## The code itself is specified by subsets of the set of qubits subject to certain consistency constraints
## We will initialize based on parity check matrices

from networkx import Graph
from typing import Dict, Set, List, Tuple
from code_tools import commutation_test, generate_check_dict, generate_qubit_nbrs_dict

class cssCode:

    def __init__(self,Sx:List[Set[int]],Sz:List[Set[int]]) -> None:
        r"""
        Initialize a CSS code instance from a presentation of the X and Z stabilizer generators.

        Properties of a cssCode object:

        :property code: A dictionary mapping the boolean False (True) to the list of X (Z) stabilizer generators.

        :property qubits: The set of all qubit labels from the input generators.

        :property check_dict: A dictionary mapping the boolean False (True) to a dictionary assigning integer labels to the input X (Z) stabilizer generators.

        :property qubit_dict: A dictionary mapping the qubit labels to a dictionary mapping the boolean False (True) to the list of X (Z) stabilizer generators containing that label
        """

        assert commutation_test(Sx,Sz)

        self.code = {False:Sx,True:Sz}
        self.qubits = set.union(*(Sx+Sz))
        self.check_dict = {False:generate_check_dict(Sx), True:generate_check_dict(Sz)}

        xdict = generate_qubit_nbrs_dict(Sx)
        zdict = generate_qubit_nbrs_dict(Sz)

        self.qubit_dict = {q:{False:xdict[q], True:zdict[q]} for q in list(self.qubits)}
        
    ## Include methods for producing check matrices and Tanner graphs
    ## Also methods for changing the presentation of a given linear code, i.e., updating the code properties

    def to_check_matrices(self) -> Dict[bool,List[Tuple[int]]]:
        r"""
        Produces a dictionary mapping the boolean False (True) to the Hx (Hz) parity check matrices given in sparse coordinate list format
        of tuples (row_label, col_label, value) where the non-zero values are always one.
        """
        check_matrices = dict()
        
        for sector in [False,True]:
            labeler = self.check_dict[sector]
            entries = []
            for row_label in labeler:
                for col_label in list(labeler[row_label]):
                    entries.append((row_label,col_label,1))

            check_matrices[sector] = entries

        return check_matrices
    
    def check_chain_graph(self) -> Graph:

        r"""
        Produces a graph describing nontrivial intersections between stabilizer generators of opposite types.
        """

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

        r"""
        Produces a dictionary mapping the boolean False (True) to a graph describing the nontrivial intersections
        of the X (Z) type stabilizer generators of the code.
        """

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
    
    def boundary_qubits(self) -> Dict[bool,Set[int]]:
        r"""
        Function returning a dictionary mapping the boolean False (True) to a set of qubit labels for which is supported on only one
        stabilizer generator of X (Z) type. 
        """

        bdries = dict()
        for sector in [False,True]:
            sector_bdry = set()
            for q in self.qubits:
                if len(self.qubit_dict[sector][q])==1:
                    sector_bdry.add(q)
            bdries[sector] = sector_bdry
        
        return bdries

    def classical_bits(self) -> Dict[bool,Set[int]]:
        r"""
        A function that identifies any classical bits which are any qubits that are supported only on a single type of stabilizer.
        These are returned in a dictionary that maps the boolean False (True) to the set of qubits that are solely supported on 
        X (Z) type stabilizers.
        """

        class_bits = dict()
        for sector in [False,True]:
            sector_bits = set()
            for q in self.qubits:
                if not len(self.qubit_dict[sector][q]):
                    sector_bits.add(q)
            class_bits[not sector] = sector_bits
        
        return class_bits