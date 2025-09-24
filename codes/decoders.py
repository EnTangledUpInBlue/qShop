__all__ = [
    "bit_strings",
    "steane_transversal_syndrome",
    "steane_transversal_decoder",
    "repetition_transversal_xdecoder",
    "repetition_transversal_zdecoder",
]


def bit_strings(n: int) -> list[tuple[int]]:
    r"""
    Function for generating a list of all bit strings of length n

    :param n:

    :return:

    """
    if n == 0:
        return []
    elif n == 1:
        return [[0], [1]]
    else:
        nstrings = []
        nm1strings = bit_strings(n - 1)
        for bs in nm1strings:
            nstrings.append(bs + [0])
            nstrings.append(bs + [1])
        return nstrings


def steane_transversal_syndrome(rec: list[bool]) -> tuple[bool]:
    r"""
    A function that computes the X (or Z or Y) syndrome of the Steane code
    given the transversal readout of the local operators.
    For example, for the X syndrome we use the traditional Hamming code
    generators:

    S0 = X 0 X 1 X 2
    S1 = X 0 X 3 X 4
    S2 = X 0 X 5 X 6

    such that the syndrome is a binary representation of the label of the qubit
    on which a Z error occurred.

    :param rec:

    :return:

    """

    s1 = sum([rec[3], rec[4], rec[5], rec[6]]) % 2
    s2 = sum([rec[1], rec[2], rec[5], rec[6]]) % 2
    s3 = sum([rec[0], rec[2], rec[4], rec[6]]) % 2

    return (s1, s2, s3)


def steane_transversal_decoder(rec: list[bool]) -> bool:
    r"""
    A function that decodes the output from a transversal measurement of any
    of the logical Paulis X, Y, or Z.

    This computes the syndrome for the Steane code. If the syndrome is trivial
    indicating no detected error, the logical Pauli eigenvalue is returned
    as the parity of all the measurement results.
    If the syndrome is nontrivial, we assume an error to one of the bits
    (since the code can only correct one error), and so flip the
    observed logical value.

    EXAMPLE: Our choice for the logical Pauli-X operator will be:

    X_L = X 0 X 1 X 2 X 3 X 4 X 5 X 6

    This representation flips in parity for a single-qubit error
    on any of the qubits, regardless of the qubit.

    One choice of the stabilizer generators is given by:

    S0 = X 0 X 1 X 2
    S1 = X 0 X 3 X 4
    S2 = X 0 X 5 X 6

    If any of these is non-trivial, then the correction
    is to flip the value of one of the qubits (we don't care which one).

    NOTE: Will need to compensate for the logical Pauli-Y operator:

    Y_L = - Y 0 Y 1 Y 2 Y 3 Y 4 Y 5 Y 6

    :param rec:

    :return:

    """

    # compute the syndromes of the Hamming code
    s = steane_transversal_syndrome(rec)

    # if syndrome is trivial, return parity of msmt
    if not sum(s):
        return sum(rec) % 2

    # if syndrome is nontrivial assume one qubit flip and return not of the parity
    else:
        return not sum(rec) % 2


def repetition_transversal_xdecoder(rec: list[bool]) -> bool:
    r"""
    A method for decoding the transversal measurement of the bit-flip
    repetition encoded X operator.

    """

    # The product of +/- outcomes maps to sum of 0/1 modulo 2:
    mx = sum(rec) % 2

    return mx


def repetition_transversal_zdecoder(rec: list[bool]) -> bool:
    r"""
    A method for taking the transversal measurement of the repetition
    encoded Z operator. Decoding is performed via majority vote.

    """
    n = len(rec)
    score = sum(rec)

    return score > int(n / 2)
