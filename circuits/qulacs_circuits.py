import numpy as np
from qulacs import QuantumState
from qulacs.state import tensor_product, drop_qubit
from qulacs.gate import CNOT, H, RY, S, Sdag, P0

# from qulacs.gate import X, Y, Z, P0
from qulacs.gate import DepolarizingNoise, TwoQubitDepolarizingNoise

__all__ = [
    "encoded_controlled_hadamard",
    "encoded_controlled_y",
    "magic_state_initialization",
    "repetition_encoder",
    "steane_encoder",
    "noisy_controlled_hadamard",
    "noisy_controlled_y",
    "noisy_magic_state_initialization",
    "noisy_repetition_encoder",
    "noisy_steane_encoder",
]


def encoded_controlled_hadamard(
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


def encoded_controlled_y(
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


def magic_state_initialization(
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

    n = state.get_qubit_count()

    # NOTE: The flagged version of the circuit is not working as expected.
    if flag:
        anc = QuantumState(1)
        state = tensor_product(state, anc)
        block.append(n)

    block_length = len(block)

    first_half = block[: int(block_length / 2)]
    second_half = block[int(block_length / 2) :]

    CNOT(first_half[0], second_half[0]).update_quantum_state(state)

    for ii in range(len(first_half) - 1):

        CNOT(first_half[ii], first_half[ii + 1]).update_quantum_state(state)
        CNOT(second_half[ii], second_half[ii + 1]).update_quantum_state(state)

    if block_length % 2:
        CNOT(second_half[-2], second_half[-1]).update_quantum_state(state)

    if flag:
        CNOT(first_half[-1], second_half[-1]).update_quantum_state(state)
        # print(first_half[-1], second_half[-1])

    if flag:
        state = drop_qubit(state, [block[-1]], [0])
        block.remove(n)

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


def noisy_controlled_hadamard(
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


def noisy_controlled_y(
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


def noisy_magic_state_initialization(
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

    n = state.get_qubit_count()

    # print(n)

    if flag:
        anc = QuantumState(1)
        state = tensor_product(state, anc)
        block.append(n)

    # noise on initialized registers
    for q in block[1:]:
        DepolarizingNoise(q, perr).update_quantum_state(state)

    # break repetition block in half
    block_length = len(block)
    first_half = block[: int(block_length / 2)]
    second_half = block[int(block_length / 2) :]

    CNOT(first_half[0], second_half[0]).update_quantum_state(state)

    TwoQubitDepolarizingNoise(first_half[0], second_half[0], perr).update_quantum_state(
        state
    )

    for q in first_half[1:] + second_half[1:]:
        DepolarizingNoise(q, perr).update_quantum_state(state)

    for ii in range(len(first_half) - 1):

        CNOT(first_half[ii], first_half[ii + 1]).update_quantum_state(state)
        CNOT(second_half[ii], second_half[ii + 1]).update_quantum_state(state)

        for jj in range(len(second_half)):
            if jj not in [ii, ii + 1]:
                DepolarizingNoise(second_half[jj], perr).update_quantum_state(state)
                if jj < len(first_half):
                    DepolarizingNoise(first_half[jj], perr).update_quantum_state(state)

    if block_length % 2:
        CNOT(second_half[-2], second_half[-1]).update_quantum_state(state)
        TwoQubitDepolarizingNoise(
            second_half[-2], second_half[-1], perr
        ).update_quantum_state(state)

        for q in first_half + second_half[:-2]:
            DepolarizingNoise(q, perr).update_quantum_state(state)

    if flag:
        CNOT(first_half[-1], second_half[-1]).update_quantum_state(state)
        TwoQubitDepolarizingNoise(
            first_half[-1], second_half[-1], perr
        ).update_quantum_state(state)

        for q in first_half[:-1] + second_half[:-1]:
            DepolarizingNoise(q, perr).update_quantum_state(state)

    if flag:
        # noisy flag qubit measurement
        DepolarizingNoise(n, perr).update_quantum_state(state)
        # state = drop_qubit(state,[n],[0]) # post-select on trivial outcome
        block.remove(n)
        P0(n).update_quantum_state(state)

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
