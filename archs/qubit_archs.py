import networkx as nx
from networkx import Graph

def rotated_qubit_architecture(L1:int,L2:int) -> Graph:
    r"""
    Function producing a newtorkx Graph representing the connectivity
    of a rotated planar architecture.

    :param L1: An integer
    :param L2: An integer
    """

    qubit_architecture = Graph()

    qubit_coords = set()

    for ii in range(2*L1-1):
        for jj in range(2*L2-1):
            if ii%2 == jj%2:
                qubit_coords.add((ii,jj))

    q2i = {q:ii for ii,q in enumerate(sorted(qubit_coords,key=lambda v:(v[0],v[1])))}
    i2q = {v:k for k,v in q2i.items()}
        
    qubit_architecture.add_nodes_from(q2i.values())

    nx.set_node_attributes(qubit_architecture,i2q,"coords")

    for qac in qubit_coords:
        for qbc in rotated_nbhd(qac[0],qac[1]):
            if qbc in qubit_coords:
                qubit_architecture.add_edge(q2i[qac],q2i[qbc])
    
    return qubit_architecture

def planar_qubit_architecture(L1:int,L2:int) -> Graph:
    r"""
    Function producing a newtorkx Graph representing the connectivity
    of a rotated planar qubit architecture.

    :param L1: An integer
    :param L2: An integer
    """

    qubit_architecture = Graph()

    qubit_coords = set([(ii,jj) for ii in range(L1) for jj in range(L2)])
    q2i = {q:ii for ii,q in enumerate(sorted(qubit_coords,key=lambda v:(v[0],v[1])))}
    i2q = {v:k for k,v in q2i.items()}

    qubit_architecture.add_nodes_from(q2i.values())

    nx.set_node_attributes(qubit_architecture,i2q,"coords")

    for qac in qubit_coords:
        for qbc in planar_nbhd(qac[0],qac[1]):
            if qbc in qubit_coords:
                qubit_architecture.add_edge(q2i[qac],q2i[qbc])
    
    return qubit_architecture


def planar_nbhd(xcoord:int,ycoord:int) -> list[tuple[int,int]]:
    r"""
    Function for producing the coordinates of potential neighbors in
    the planar architecture layout.

    :param xcoord:
    :param ycoord:

    :returns: List of tuples representing the coordinates of possible
    neighbors.
    """

    nbhd = [(xcoord+1,ycoord),
            (xcoord-1, ycoord),
            (xcoord,ycoord-1),
            (xcoord,ycoord+1)
    ]

    return nbhd

def rotated_nbhd(xcoord:int,ycoord:int) -> list[tuple[int,int]]:
    r"""
    Function for producing the coordinates of potential neighbors in
    the rotated planar architecture layout.

    :param xcoord:
    :param ycoord:

    :returns: List of tuples representing the coordinates of possible
    neighbors.
    """
    nbhd = [(xcoord+1,ycoord+1),
            (xcoord-1, ycoord+1),
            (xcoord+1,ycoord-1),
            (xcoord-1,ycoord-1)
    ]

    return nbhd