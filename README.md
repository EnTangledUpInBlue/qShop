# qShop

A place for code and calculations related to quantum information processing.
The main motivator was an interest in a point set topological interpretation of quantum codes (esp. CSS codes), so the basic data structures are sets and there are many tools for playing with these sets.

Checks in a classical linear code are represented by the subsets of bits they sum up.
Quantum codes are given by two classical codes, Sx and Sz, with the constraint that any check from Sx has even overlap with any check from Sz.
