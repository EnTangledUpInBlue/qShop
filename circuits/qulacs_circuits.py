import numpy as np
from qulacs import QuantumState, QuantumCircuit
from qulacs.state import tensor_product, drop_qubit
from qulacs.gate import CNOT, H, RY, S, Sdag, P0

# from qulacs.gate import X, Y, Z, P0
from qulacs.gate import DepolarizingNoise, TwoQubitDepolarizingNoise

__all__ = [
    "controlled_hadamard",
    "controlled_y",
    "magic_state_initialization",
    "repetition_encoder",
    "steane_encoder",
    "noisy_controlled_hadamard",
    "noisy_controlled_y",
    "noisy_magic_state_initialization",
    "noisy_repetition_encoder",
    "noisy_steane_encoder",
]


def controlled_hadamard(
    state: QuantumState, control_block: list[int], target_block: list[int]
) -> QuantumState:
    r"""
    Updates the state performing an encoded controlled-Hadamard gate

    :param state: QuantumState representing the input state to the hadamard test
    :param target_block: List of integers specifying the target block which is Steane-encoded
    :param control_block: List of integers specifying the control block of the logical controlled operation.

    :returns: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
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


def controlled_y(
    state: QuantumState, control_block: list[int], target_block: list[int]
) -> QuantumState:
    r"""
    Updates the state performing an encoded controlled-Y gate

    :param state: QuantumState representing the input state to the hadamard test
    :param target_block: List of integers specifying the target block which is Steane-encoded
    :param control_block: List of integers specifying the control block of the logical controlled operation.

    :returns: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
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

    H(qubit).update_quantum_state(state)
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

    :returns: A QuantumState representing the updated state where qubit block[0] has been
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
        print(first_half[-1], second_half[-1])

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

    :returns: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the qubits of block.
    """

    for qub in range(1, 4):
        H(block[qub]).update_quantum_state(state)

    # Following the convention in FIG. 3.

    CNOT(0, 6).update_quantum_state(state)
    CNOT(3, 4).update_quantum_state(state)

    CNOT(0, 5).update_quantum_state(state)
    CNOT(1, 4).update_quantum_state(state)
    CNOT(3, 6).update_quantum_state(state)

    CNOT(1, 0).update_quantum_state(state)
    CNOT(2, 4).update_quantum_state(state)
    CNOT(3, 5).update_quantum_state(state)

    CNOT(2, 0).update_quantum_state(state)
    CNOT(1, 5).update_quantum_state(state)

    CNOT(2, 6).update_quantum_state(state)

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

    :returns: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
    """

    n = state.get_qubit_count()
    angle = np.pi / 4.0

    for ii in range(len(target_block)):
        circuit = QuantumCircuit(n)
        circuit.add_RY_gate(target_block[ii], -angle)
        circuit.update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    for ii in range(len(target_block)):
        qtarget = target_block[ii]
        qcontrol = control_block[ii]
        CNOT(qcontrol, qtarget).update_quantum_state(state)

        TwoQubitDepolarizingNoise(qtarget, qcontrol, perr).update_quantum_state(state)

    for ii in range(len(target_block)):
        circuit = QuantumCircuit(n)
        circuit.add_RY_gate(target_block[ii], angle)
        circuit.update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    circuit.update_quantum_state(state)

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

    :returns: An update of the input state with the ancilla now adjoined and controlled-Hadamard gate implemented.
    """

    for ii in range(len(target_block)):

        Sdag(target_block[ii]).update_quantum_state(state)

        # single-qubit gate noise
        DepolarizingNoise(target_block[ii], perr).update_quantum_state(state)

        # idling noise on control block
        DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

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
        DepolarizingNoise(control_block[ii], perr).update_quantum_state(state)

    return state


def noisy_magic_state_initialization(
    state: QuantumState, qubit: int, perr: float, angle=np.pi / 4.0
) -> QuantumState:

    n = state.get_qubit_count()

    circuit = QuantumCircuit(n)

    circuit.add_H_gate(qubit)
    circuit.add_RY_gate(qubit, angle)

    circuit.update_quantum_state(state)

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

    :returns: A QuantumState representing the updated state where qubit block[0] has been
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


def noisy_steane_encoder(
    state: QuantumState, block: list[int], perr: float
) -> QuantumState:
    r"""
    Encode the input state, assumed to be on the qubit at block[0], into the
    the Steane code supported on the seven qubits in the list block.

    :param state: A QuantumState representing the qubit state to be encoded.
    :param block: A list of integers indicating the locations of the qubits in the block.

    :returns: A QuantumState representing the updated state where qubit block[0] has been
            encoded into the qubits of block.
    """

    n = state.get_qubit_count()

    circuit = QuantumCircuit(n)

    for qub in range(1, 4):
        circuit.add_H_gate(block[qub])

    # Following the convention in FIG. 3.
    # Still needs ****NOISE****

    circuit.add_CNOT_gate(0, 6)
    circuit.add_CNOT_gate(3, 4)

    circuit.add_CNOT_gate(0, 5)
    circuit.add_CNOT_gate(1, 4)
    circuit.add_CNOT_gate(3, 6)

    circuit.add_CNOT_gate(1, 0)
    circuit.add_CNOT_gate(2, 4)
    circuit.add_CNOT_gate(3, 5)

    circuit.add_CNOT_gate(2, 0)
    circuit.add_CNOT_gate(1, 5)

    circuit.add_CNOT_gate(2, 6)

    circuit.update_quantum_state(state)

    return state
