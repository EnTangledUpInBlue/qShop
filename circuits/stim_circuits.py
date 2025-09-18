from stim import Circuit
from circuits.circuit_tools import repetition_measurement_schedule


def noisy_repetition_measurement(
    circuit: Circuit, block: list[int], perr: float
) -> Circuit:
    r"""
    Method for appending a circuit for a measurement of
    a repetition-encoded qubit on the set of qubits
    indicated by block

    :param circuit:
    :param block:
    :param perr:

    :return:
    """

    schedule = repetition_measurement_schedule(block)

    measured_set = set()
    block_set = set(block)

    for round in schedule:
        idle_set = [x for x in block_set - measured_set]

        for pair in round:
            idle_set.remove(pair[0])
            idle_set.remove(pair[1])

            circuit.append("CNOT", pair)
            circuit.append("DEPOLARIZE2", pair, perr)

            circuit.append("DEPOLARIZE1", pair[1], perr)
            circuit.append("MZ", pair[1])

            measured_set.add(pair[1])

        circuit.append("DEPOLARIZE1", list(idle_set), perr)

    circuit.append("DEPOLARIZE1", block[0], perr)
    circuit.append("MX", block[0])

    return circuit


def noisy_repetition_encoder(
    circuit: Circuit, block: list[int], perr: float, flag=False
) -> Circuit:
    r"""
    Method for appending a circuit that encodes the incoming state
    on block[0] into the repetition code on the full block, with an
    optional flag qubit

    :param circuit: object of stim Circuit class
    :param block: list of qubits to encode the state into
    :param flag: A boolean indicating if a flag qubit should be used

    :return: a stim Circuit

    """

    if flag:
        blockmax = int(max(block))
        block.append(blockmax + 1)

    circuit.append("R", block[1:])
    circuit.append("DEPOLARIZE1", block[1:], perr)

    block_length = len(block)

    first_half = block[: int(block_length / 2)]
    second_half = block[int(block_length / 2) :]

    circuit.append("CNOT", [first_half[0], second_half[0]])
    circuit.append("DEPOLARIZE2", [first_half[0], second_half[0]], perr)

    circuit.append("DEPOLARIZE1", first_half[1:] + second_half[1:], perr)

    for ii in range(len(first_half) - 1):
        circuit.append("CNOT", [first_half[ii], first_half[ii + 1]])
        circuit.append("DEPOLARIZE2", [first_half[ii], first_half[ii + 1]], perr)

        circuit.append("CNOT", [second_half[ii], second_half[ii + 1]])
        circuit.append("DEPOLARIZE2", [second_half[ii], second_half[ii + 1]], perr)

        for jj in range(len(second_half)):
            if jj not in [ii, ii + 1]:
                circuit.append("DEPOLARIZE1", [second_half[jj]], perr)
                if jj < len(first_half):
                    circuit.append("DEPOLARIZE1", [first_half[jj]], perr)

    if block_length % 2:
        circuit.append("CNOT", [second_half[-2], second_half[-1]])
        circuit.append("DEPOLARIZE2", [second_half[-2], second_half[-1]], perr)
        circuit.append("DEPOLARIZE1", first_half + second_half[:-2], perr)

    if flag:
        circuit.append("CNOT", [first_half[-1], second_half[-1]])
        circuit.append("DEPOLARIZE2", [first_half[-1], second_half[-1]], perr)
        circuit.append("DEPOLARIZE1", first_half[:-1] + second_half[:-1], perr)

        circuit.append("DEPOLARIZE1", second_half[-1], perr)
        circuit.append("MRZ", second_half[-1])

    return circuit


def noisy_steane_encoder(circuit: Circuit, block: list[int], perr: float) -> Circuit:
    r"""
    Method for encoding an initial state, given as the
    first element of the block. Uses circuit-level depolarizing
    noise with strength p. Following the schedule prescribed in FIG. 3.

    :param circuit:
    :param block:
    :param perr:

    :return: A stim circuit with the Steane encoding circuit appended.

    """

    assert len(block) == 7

    circuit.append("RX", block[1:4])
    circuit.append("RZ", block[4:])

    circuit.append("DEPOLARIZE1", block[1:], perr)

    schedule = [
        [(0, 6), (3, 4)],
        [(0, 5), (1, 4), (3, 6)],
        [(1, 0), (2, 4), (3, 5)],
        [(2, 0), (1, 5)],
        [(2, 6)],
    ]

    for round in schedule:
        qubits = [a for a in block]
        for ctpair in round:
            control = block[ctpair[0]]
            target = block[ctpair[1]]

            circuit.append("CX", [control, target])
            circuit.append("DEPOLARIZE2", [control, target], perr)
            qubits.remove(control)
            qubits.remove(target)

        circuit.append("DEPOLARIZE1", qubits, perr)  # noise for idling qubits

    return circuit


def noisy_encoded_y(
    circuit: Circuit, target_block: list[int], control_block: list[int], perr: float
):
    r"""
    Implementation of the transversal controlled-Y gate on Stene encoding
    using the S gate to diagonalize

    Y = S X S^dag

    :param:

    :return:
    """
    assert len(target_block) == len(control_block)

    n = len(target_block)

    for ii in range(n):
        circuit.append("S_DAG", target_block[ii])
        circuit.append("DEPOLARIZE1", [target_block[ii], control_block[ii]], perr)

    # Noise model assumes that all controlled-operations are performed in parallel
    for ii in range(n):
        circuit.append("CNOT", [control_block[ii], target_block[ii]])
        circuit.append("DEPOLARIZE2", [control_block[ii], target_block[ii]], perr)

    for ii in range(n):
        circuit.append("S", target_block[ii])
        circuit.append("DEPOLARIZE1", [target_block[ii], control_block[ii]], perr)

    return circuit


def construct_steane_7rep_circuit(perr: float, flag=True) -> Circuit:
    r"""
    Method for producing a noisy circuit that in the absence of errors
    will initialize and measure the logical Pauli-Y eigenstate |+i>.
    In this particular circuit, the logical qubit is encoded in a Steane code
    while the logical ancilla is encoded into a seven-qubit repetition code.

    :param perr:
    :param flag:

    :return:
    """

    noisy_circ = Circuit()

    steaneBlock = [0, 1, 2, 3, 4, 5, 6]
    repnBlock = [7, 8, 9, 10, 11, 12, 13]

    # initialize seed Y-eigenstate: S |+> = |+i>

    noisy_circ.append("RX", steaneBlock[0])
    noisy_circ.append("S", steaneBlock[0])

    # initialize seed state for ancilla |+>
    noisy_circ.append("RX", repnBlock[0])

    # apply single-qubit depolarization to initialized states
    noisy_circ.append("DEPOLARIZE1", [steaneBlock[0], repnBlock[0]], perr)

    # add noisy encoding circuits
    noisy_circ = noisy_steane_encoder(noisy_circ, steaneBlock, perr)

    # default repetition encoder includes flag qubit
    noisy_circ = noisy_repetition_encoder(noisy_circ, repnBlock, perr, flag)

    if flag:
        noisy_circ = noisy_encoded_y(noisy_circ, steaneBlock, repnBlock[:-1], perr)
        noisy_circ.append("DEPOLARIZE1", repnBlock[:-1], perr)
        noisy_circ.append("MX", repnBlock[:-1])  # readout transversal logical-X

    else:
        # Apply the encoded controlled-Y circuit
        noisy_circ = noisy_encoded_y(noisy_circ, steaneBlock, repnBlock, perr)

        # noisy readout transversal logical-X
        noisy_circ.append("DEPOLARIZE1", repnBlock, perr)
        noisy_circ.append("MX", repnBlock)

    # ideal readout transversal logical-Y
    noisy_circ.append("MY", steaneBlock)

    return noisy_circ


def construct_steane_3rep_circuit(perr: float, flag=True) -> Circuit:
    r"""
    Method for producing a noisy circuit that in the absence of errors
    will initialize and measure the logical Pauli-Y eigenstate |+i>.
    In this particular circuit, the logical qubit is encoded in a Steane code
    while the logical ancilla is encoded into a seven-qubit repetition code.

    In this case the repetition encoding is only 3 qubits but there is still
    a transversal CNOT to be performed.
    """

    noisy_circ = Circuit()

    steaneBlock = [0, 1, 2, 3, 4, 5, 6]
    repnBlock = [7, 8, 9]

    # initialize the Y-eigenstate: S |+> = |+i>

    noisy_circ.append("RX", steaneBlock[0])
    noisy_circ.append("S", steaneBlock[0])

    noisy_circ.append("RX", repnBlock[0])

    noisy_circ.append("DEPOLARIZE1", [steaneBlock[0], repnBlock[0]], perr)

    noisy_circ = noisy_steane_encoder(noisy_circ, steaneBlock, perr)
    noisy_circ = noisy_repetition_encoder(
        noisy_circ, repnBlock, perr, flag
    )  # include flag qubit in encoder

    if flag:
        noisy_circ = noisy_encoded_y(noisy_circ, [1, 4, 6], repnBlock[:-1], perr)
        # noisy readout transversal logical-X
        noisy_circ.append("DEPOLARIZE1", repnBlock[:-1], perr)
        noisy_circ.append("MX", repnBlock[:-1])

    else:
        noisy_circ = noisy_encoded_y(noisy_circ, [1, 4, 6], repnBlock, perr)
        # noisy readout transversal logical-X
        noisy_circ.append("DEPOLARIZE1", repnBlock, perr)
        noisy_circ.append("MX", repnBlock)

    # ideal readout transversal logical-Y
    noisy_circ.append("MY", steaneBlock)

    return noisy_circ


def construct_steane_steane_circuit(perr: float) -> Circuit:
    r"""
    Method for producing a noisy circuit that in the absence of errors
    will initialize and measure the logical Pauli-Y eigenstate |+i>.
    In this particular circuit, the both the logical qubit and ancilla are
    encoded into the Steane code.
    """

    noisy_circ = Circuit()

    steaneBlockA = [0, 1, 2, 3, 4, 5, 6]
    steaneBlockB = [7, 8, 9, 10, 11, 12, 13]

    # prep initial state to |+i>
    noisy_circ.append("RX", steaneBlockA[0])
    noisy_circ.append("S", steaneBlockA[0])

    # prep unencoded ancilla in |+>
    noisy_circ.append("RX", steaneBlockB[0])

    # apply noise for qubit initialization
    noisy_circ.append("DEPOLARIZE1", [steaneBlockA[0], steaneBlockB[0]], perr)

    # apply noisy encoder circuits for each qubit
    noisy_circ = noisy_steane_encoder(noisy_circ, steaneBlockA, perr)
    noisy_circ = noisy_steane_encoder(noisy_circ, steaneBlockB, perr)

    # apply noisy transversal Y between two steane encoded blocks
    noisy_circ = noisy_encoded_y(noisy_circ, steaneBlockA, steaneBlockB, perr)

    # noisy readout transversal logical-X
    noisy_circ.append("DEPOLARIZE1", steaneBlockB, perr)
    noisy_circ.append("MX", steaneBlockB)

    # ideal readout transversal logical-Y
    noisy_circ.append("MY", steaneBlockA)

    return noisy_circ
