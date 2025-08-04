# qShop

A place for code and calculations related to quantum information processing.
The main motivator was an interest in a point set topological interpretation of quantum codes (esp. CSS codes), so the basic data structures are sets and there are many tools for playing with these sets.

Checks in a classical linear code are represented by the subsets of bits they sum up.
Quantum codes are given by two classical codes, Sx and Sz, with the constraint that any check from Sx has even overlap with any check from Sz.

### Current layout of the code (as of May 16, 2025):

In the folder /codes/ are basic tools and files for constructing certain families of error-correcting codes (standard and rotated surface codes, toric code, bivariant bicycle codes).

The file example_codes.py pulls all of the examples into a single file for initialization (this is expected to change in the future).

The class cssCode is initialized by two sets of subsets of the qubits, denoted Sx and Sz, and then offers some tools for playing with these sets.

### Update (June 13, 2025):

A jupyter notebook has been added to demonstrate some of the functionality of the tools.
