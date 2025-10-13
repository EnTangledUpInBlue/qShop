import numpy as np
from qulacs import QuantumState
from qulacs.state import tensor_product, drop_qubit
from qulacs.gate import CNOT, H, RY, S, Sdag, P0

# from qulacs.gate import X, Y, Z, P0
from qulacs.gate import DepolarizingNoise, TwoQubitDepolarizingNoise
from circuits.circuit_tools import repetition_encoding_schedule
from codes.decoders import bit_strings

__all__ = [
    "encoded_chad",
    "encoded_cy",
    "magic_state_init",
    "repetition_encoder",
    "steane_encoder",
    "noisy_encoded_chad",
    "noisy_encoded_cy",
    "noisy_magic_state_init",
    "noisy_repetition_encoder",
    "noisy_steane_decoder",
    "noisy_steane_encoder",
]


def print_nonzeros(state: QuantumState):
    outs = bit_strings(state.get_qubit_count())
    for s in outs:
        if state.get_marginal_probability(s) > 1e-5:
            print(s)


def encoded_chad(
    state: QuantumState, control_block: list[int], target_block: list[int]
) -> QuantumState:
    r"""
    Updates the state performing an encoded controlled-Hadamard gate

    :param state: QuantumState representing the input state to the hadamard test
    :param target_block: List of integers specifying the target block which is Steane-encoded
    :param control_block: List of integers specifying the control block of the logical controlled operation.

    :return: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
    """

    angle = np.pi / 4.0

    for ii in range(len(target_block)):
        RY(target_block[ii], -angle).update_quantum_state(state)

    for ii in range(len(target_block)):
        qtarget = target_block[ii]
        qcontrol = control_block[ii]

        CNOT(qcontrol, qtarget).update_quantum_state(state)

    for ii in range(len(target_block)):
        RY(target_block[ii], angle).update_quantum_state(state)

    return state


def encoded_cy(
    state: QuantumState, control_block: list[int], target_block: list[int]
) -> QuantumState:
    r"""
    Updates the state performing an encoded controlled-Y gate

    :param state: QuantumState representing the input state to the hadamard test
    :param target_block: List of integers specifying the target block which is Steane-encoded
    :param control_block: List of integers specifying the control block of the logical controlled operation.

    :return: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
    """

    for ii in range(len(target_block)):
        Sdag(target_block[ii]).update_quantum_state(state)

    for ii in range(len(target_block)):
        qtarget = target_block[ii]
        qcontrol = control_block[ii]

        CNOT(qcontrol, qtarget).update_quantum_state(state)

    for ii in range(len(target_block)):
        S(target_block[ii]).update_quantum_state(state)

    return state


def magic_state_init(
    state: QuantumState, qubit: int, angle=np.pi / 4.0
) -> QuantumState:
    r"""
    Function that updates a QuantumState by initializing a given qubit into
    the Hadamard eigenstate

    |H_+> = cos(angle/2) |0> + sin(angle/2) |1>

    """

    # Initialize register in the |+> state
    P0(qubit).update_quantum_state(state)
    H(qubit).update_quantum_state(state)

    # Rotate the state about the Y-axis
    RY(qubit, angle).update_quantum_state(state)

    return state


def plus_state_init(state: QuantumState, qubit: int) -> QuantumState:
    r"""
    Function that updates a QuantumState by initializing a given qubit into
    the Hadamard eigenstate

    |H_+> = cos(angle/2) |0> + sin(angle/2) |1>

    """

    # Initialize register in the |+> state
    P0(qubit).update_quantum_state(state)
    H(qubit).update_quantum_state(state)

    return state


def repetition_encoder(
    state: QuantumState, block: list[int], flag=False
) -> QuantumState:
    r"""
    Encode the input state, assumed to be on the qubit at block[0], into the
    the repetition code supported on the qubits in the list block.

    :param state: A QuantumState representing the qubit state to be encoded.
    :param block: A list of integers indicating the locations of the qubits in the block.
    :param flag: A Boolean indicating if a flag qubit will be used for the encoding.

    :return: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the qubits of block.
    """

    schedule = repetition_encoding_schedule(block)

    if flag:
        anc = QuantumState(1)
        anc.set_zero_state()
        state = tensor_product(anc, state)

        # modifications to the cnot schedule for including the flag qubit with
        # considerations for circuit-level noise

        mark = int(len(block) / 2)
        flag_label = int(state.get_qubit_count()) - 1

        print(flag_label)

        if len(block) % 2:
            schedule[-1].append((block[mark - 1], flag_label))
        else:
            schedule.append([(block[mark - 1], flag_label)])

        schedule.append([(block[-1], flag_label)])

    for round in schedule:
        for pair in round:
            control = pair[0]
            target = pair[1]

            CNOT(control, target).update_quantum_state(state)

    if flag:
        # Post-select on trivial outcome
        state = drop_qubit(state, [flag_label], [0])

    return state


def steane_encoder(state: QuantumState, block: list[int]) -> QuantumState:
    r"""
    Encode the input state, assumed to be on the qubit at block[0], into the
    the Steane code supported on the seven qubits in the list block.

    :param state: A QuantumState representing the qubit state to be encoded.
    :param block: A list of integers indicating the locations of the qubits in the block.

    :return: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the qubits of block.
    """

    schedule = [
        [(0, 6), (3, 4)],
        [(0, 5), (1, 4), (3, 6)],
        [(1, 0), (2, 4), (3, 5)],
        [(2, 0), (1, 5)],
        [(2, 6)],
    ]

    for qub in range(1, 4):
        H(block[qub]).update_quantum_state(state)

    # Following the convention in FIG. 3.

    for round in schedule:
        for pair in round:
            CNOT(pair[0], pair[1]).update_quantum_state(state)

    return state


def noisy_encoded_chad(
    state: QuantumState, control_block: list[int], target_block: list[int], perr: float
) -> QuantumState:
    r"""
    Updates the state with implementation of the hadamard test with a probabilistic projection, returning the outcome.
    This assumes the target block is encoded in a Steane code and the ancilla is repetition encoded.

    :param state: QuantumState representing the input state to the hadamard test
    :param target_block: List of integers specifying the target block which is Steane-encoded
    :param control_block: List of integers specifying the control block of the logical controlled operation.

    :return: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
    """

    angle = np.pi / 4.0

    for ii in range(len(target_block)):

        RY(target_block[ii], -angle).update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        # DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    for ii in range(len(target_block)):
        qtarget = target_block[ii]
        qcontrol = control_block[ii]
        CNOT(qcontrol, qtarget).update_quantum_state(state)

        TwoQubitDepolarizingNoise(qtarget, qcontrol, perr).update_quantum_state(state)

    for ii in range(len(target_block)):

        RY(target_block[ii], angle).update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    return state


def noisy_encoded_cy(
    state: QuantumState, control_block: list[int], target_block: list[int], perr: float
) -> QuantumState:
    r"""
    Updates the state with implementation of the hadamard test with a probabilistic projection, returning the outcome.
    This assumes the target block is encoded in a Steane code and the ancilla is repetition encoded.

    :param state: QuantumState representing the input state to the hadamard test
    :param target_block: List of integers specifying the target block which is Steane-encoded
    :param control_block: List of integers specifying the control block of the logical controlled operation.

    :return: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
    """

    for ii in range(len(target_block)):

        Sdag(target_block[ii]).update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        # DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    for ii in range(len(target_block)):
        qtarget = target_block[ii]
        qcontrol = control_block[ii]

        CNOT(qcontrol, qtarget).update_quantum_state(state)
        TwoQubitDepolarizingNoise(qtarget, qcontrol, perr).update_quantum_state(state)

    for ii in range(len(target_block)):
        S(target_block[ii]).update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        # DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    return state


def noisy_magic_state_init(
    state: QuantumState, qubit: int, perr: float, angle=np.pi / 4.0
) -> QuantumState:
    r"""
    A method that takes a QuantumState and initializes the register
    qubit RY(angle)|+>

    :param state: a QuantumState object on which to act
    :param qubit: the qubit register to initialize
    :param perr: the single-qubit depolarizing noise strength
    :param angle: the angle about the Y-axis that |+> is to be
        rotated

    :return: a QuantumState object
    """

    H(qubit).update_quantum_state(state)
    RY(qubit, angle).update_quantum_state(state)

    DepolarizingNoise(qubit, perr).update_quantum_state(state)

    return state


def noisy_repetition_encoder(
    state: QuantumState, block: list[int], perr: float, flag=False
) -> QuantumState:
    r"""
    Encode the input state, assumed to be on the qubit at block[0], into the
    the repetition code supported on the qubits in the list block.

    :param state: A QuantumState representing the qubit state to be encoded.
    :param block: A list of integers indicating the locations of the qubits in the block.
    :param flag: A Boolean indicating if a flag qubit will be used for the encoding.

    :return: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the logical state of the block.
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
                    DepolarizingNoise(qubit, perr).update_quantum_state(state)
                    active_set.add(qubit)

            # Apply noisy CNOT to pair
            control = pair[0]
            target = pair[1]

            CNOT(control, target).update_quantum_state(state)

        # Apply noise to idle qubits in this round
        idle_set = active_set - round_set

        for idler in idle_set:
            DepolarizingNoise(idler, perr).update_quantum_state(state)

    if flag:
        # Measure the flag qubit
        DepolarizingNoise(flag_label, perr)
        state = drop_qubit(state, [flag_label], [0])

    return state


def noisy_steane_decoder(
    state: QuantumState, block: list[int], perr: float
) -> QuantumState:
    r"""
    Decoder circuit for the Steane code. Leaves the last six
    qubit registers of block in the following
    Steane code stabilizers

    X0 X1 X4 X5
    X0 X2 X4 X6
    X3 X4 X5 X6
    Z1 Z2 Z3 Z4
    Z0 Z2 Z3 Z5
    Z0 Z1 Z3 Z6

    The logical state is in the first qubit register of block.

    :param state: A QuantumState representing the qubit state to be encoded.
    :param block: A list of integers indicating the locations of the qubits in the block.
    :param perr: a float representing the noise strength in a circuit-level noise model.

    :return: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the qubits of block.
    """

    schedule = [
        [(1, 5), (2, 6)],
        [(2, 0), (3, 5)],
        [(1, 0), (2, 4), (3, 6)],
        [(1, 4), (0, 5)],
        [(0, 6), (3, 4)],
    ]

    # Still needs ****NOISE****
    for round in schedule:
        for pair in round:
            CNOT(pair[0], pair[1]).update_quantum_state(state)

    # Rotate everything to the Z-basis
    for qub in range(1, 4):
        H(block[qub]).update_quantum_state(state)

    return state


def noisy_steane_encoder(
    state: QuantumState, block: list[int], perr: float
) -> QuantumState:
    r"""
    Encode the input state, assumed to be on the qubit at block[0], into the
    the Steane code supported on the seven qubits in the list block.

    :param state: A QuantumState representing the qubit state to be encoded.
    :param block: A list of integers indicating the locations of the qubits in the block.
    :param perr: a float representing the noise strength in a circuit-level noise model.

    :return: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the qubits of block.
    """

    schedule = [
        [(0, 6), (3, 4)],
        [(0, 5), (1, 4), (3, 6)],
        [(1, 0), (2, 4), (3, 5)],
        [(2, 0), (1, 5)],
        [(2, 6)],
    ]

    for qub in range(1, 4):
        H(block[qub]).update_quantum_state(state)

    # Following the convention in FIG. 3.
    # Still needs ****NOISE****
    for round in schedule:
        for pair in round:
            CNOT(pair[0], pair[1]).update_quantum_state(state)

    return state
