from stim import Circuit
from circuits.circuit_tools import (
    repetition_measurement_schedule,
    repetition_encoding_schedule,
)

__all__ = [
    "noisy_repetition_measurement",
    "noisy_repetition_transversal_mx",
    "noisy_repetition_encoder",
    "noisy_steane_encoder",
    "noisy_steane_plus",
    "noisy_steane_zero",
    "noisy_encoded_cy",
]


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


def noisy_repetition_transversal_mx(
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

    circuit.append("DEPOLARIZE1", block, perr)
    circuit.append("MX", block, perr)

    return circuit


def noisy_repetition_encoder(
    circuit: Circuit, block: list[int], perr: float, flag=False
) -> Circuit:
    r"""
    Method for appending a circuit that encodes the incoming state
    on block[0] into the repetition code on the full block, with an
    optional flag qubit

    :param circuit: a stim Circuit
    :param block: list of qubits to encode the state into
    :param flag: A boolean indicating if an error-detecting flag
        qubit should be used

    :return: a stim Circuit

    """

    schedule = repetition_encoding_schedule(block)

    if flag:
        mark = int(len(block) / 2)

        flag_label = int(max(block)) + 1

        if len(block) % 2:
            schedule[-1].append((block[mark - 1], flag_label))
        else:
            schedule.append([(block[mark - 1], flag_label)])

        schedule.append([(block[-1], flag_label)])

    # set of active qubits in the circuit
    active_set = set([block[0]])

    for round in schedule:
        # set of qubits active in this round
        round_set = set()
        for pair in round:
            round_set = round_set.union(set(pair))

            # First determine if qubits need initialization
            for qubit in pair:
                if qubit not in active_set:
                    circuit.append("R", qubit)
                    circuit.append("DEPOLARIZE1", qubit, perr)

                    active_set.add(qubit)

            # Apply noisy CNOT to pair
            circuit.append("CNOT", pair)
            circuit.append("DEPOLARIZE2", pair, perr)

        # Apply noise to idle qubits in this round
        idle_set = active_set - round_set
        circuit.append("DEPOLARIZE1", idle_set, perr)

    if flag:
        # Measure the flag qubit
        circuit.append("DEPOLARIZE1", flag_label, perr)
        circuit.append("MR", flag_label)

    return circuit


def noisy_steane_plus(
    circuit: Circuit, block: list[int], perr: float, verify=False
) -> Circuit:
    r"""
    Specialized circuit for preparing the logical |+> state of the
    Steane code, adapted from Paetznick and Reichardt arXiv:1106.2190

    :param circuit:
    :param block:
    :param perr:
    :param verify:

    :return:
    """

    schedule = [
        [(0, 1), (5, 3), (6, 2)],
        [(4, 1), (0, 2), (6, 3)],
        [(5, 1), (4, 6)],
    ]

    if verify:
        flag = max(block) + 1
        block.append(flag)
        schedule.extend([[(7, 0)], [(7, 5)], [(7, 6)]])

    circuit.append("RX", [block[0]] + block[4:])
    circuit.append("RZ", block[1:4])

    # set of active qubits in the circuit
    active_set = set()

    for round in schedule:
        # set of qubits active in this round
        round_set = set()
        for pair in round:
            control = block[pair[0]]
            target = block[pair[1]]

            round_set = round_set.union(set(pair))

            # First determine if qubits need initialization noise
            for qubit in pair:
                if qubit not in active_set:
                    circuit.append("DEPOLARIZE1", block[qubit], perr)
                    active_set.add(qubit)

            # Apply noisy CNOT to pair
            circuit.append("CNOT", [control, target])
            circuit.append("DEPOLARIZE2", [control, target], perr)

        # Apply noise to idle qubits in this round
        idle_set = active_set - round_set
        idle_list = [block[q] for q in idle_set]
        circuit.append("DEPOLARIZE1", idle_list, perr)

    if verify:
        circuit.append("DEPOLARIZE1", flag, perr)
        circuit.append("MX", flag)
        block.remove(flag)

    return circuit


def noisy_steane_zero(
    circuit: Circuit, block: list[int], perr: float, verify=False
) -> Circuit:
    r"""
    Specialized circuit for preparing the logical |0> state of the
    Steane code, adapted from Paetznick and Reichardt arXiv:1106.2190

    :param circuit:
    :param block:
    :param perr:
    :param verify:

    :return:
    """

    schedule = [
        [(1, 0), (3, 5), (2, 6)],
        [(4, 1), (2, 0), (3, 6)],
        [(1, 5), (6, 4)],
    ]

    if verify:
        flag = max(block) + 1
        block.append(flag)
        schedule.extend([[(0, 7)], [(5, 7)], [(6, 7)]])

    circuit.append("RZ", [block[0]] + block[4:])
    circuit.append("RX", block[1:4])

    # set of active qubits in the circuit
    active_set = set()

    for round in schedule:
        # set of qubits active in this round
        round_set = set()
        for pair in round:
            round_set = round_set.union(set(pair))

            # First determine if qubits need initialization noise
            for qubit in pair:
                if qubit not in active_set:
                    circuit.append("DEPOLARIZE1", qubit, perr)
                    active_set.add(qubit)

            # Apply noisy CNOT to pair
            circuit.append("CNOT", pair)
            circuit.append("DEPOLARIZE2", pair, perr)

        # Apply noise to idle qubits in this round
        idle_set = active_set - round_set
        circuit.append("DEPOLARIZE1", idle_set, perr)

    if verify:
        circuit.append("DEPOLARIZE1", flag, perr)
        circuit.append("MZ", flag)
        block.remove(flag)

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


def noisy_encoded_cy(
    circuit: Circuit, target_block: list[int], control_block: list[int], perr: float
):
    r"""
    Implementation of the transversal controlled-Y gate on Stene encoding
    using the S gate to diagonalize

    Y = S X S^dag

    :param circuit:
    :param target_block:
    :param control_block:
    :param perr:

    :return:
    """
    assert len(target_block) == len(control_block)

    n = len(target_block)

    for ii in range(n):
        circuit.append("S_DAG", target_block[ii])
        # circuit.append("DEPOLARIZE1", [target_block[ii], control_block[ii]], perr)
        circuit.append("DEPOLARIZE1", [target_block[ii]], perr)

    # Noise model assumes that all controlled-operations are performed in parallel
    for ii in range(n):
        circuit.append("CNOT", [control_block[ii], target_block[ii]])
        circuit.append("DEPOLARIZE2", [control_block[ii], target_block[ii]], perr)

    for ii in range(n):
        circuit.append("S", target_block[ii])
        # circuit.append("DEPOLARIZE1", [target_block[ii], control_block[ii]], perr)
        circuit.append("DEPOLARIZE1", [target_block[ii]], perr)

    return circuit
