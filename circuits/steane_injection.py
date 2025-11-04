import numpy as np
from qulacs import QuantumState
from qulacs.gate import H, RY, X, DepolarizingNoise
from qulacs.state import drop_qubit, tensor_product
from codes.decoders import bit_strings

from circuits.qulacs_circuits import (
    noisy_encoded_chad,
    noisy_repetition_encoder,
    noisy_plus_state_init,
    noisy_magic_state_init,
    noisy_steane_encoder,
    steane_decoder,
)


__all__ = [
    "repn_had_test",
    "one_double_run",
    "one_single_run",
]


def repn_had_test(
    state: QuantumState,
    steaneBlock: list[int],
    repnBlock: list[int],
    perr: float,
    idling=True,
) -> QuantumState:
    r"""
    Implementation of an encoded Hadamard test with repetition-repetition
    encoded ancilla under circuit-level noise, with optional idling noise.

    """

    # Initialize ancilla qubits and tensor with the input state
    rep_anc = QuantumState(7)
    state = tensor_product(rep_anc, state)

    # Initialize the ancilla in the |+> state:
    state = noisy_plus_state_init(state, repnBlock[0], perr)

    # Encode the ancilla block into 7-qubit repetition code
    state = noisy_repetition_encoder(state, repnBlock, perr, flag=True, idling=idling)

    # Implement the noisy encoded controlled Hadamard between the two blocks
    # with the steaneBlock as target and repnBlock as control
    state = noisy_encoded_chad(state, repnBlock, steaneBlock, perr, idling=idling)

    # Rotate ancilla qubits into the X-basis for readout. Noise applied first.
    for qub in repnBlock:
        DepolarizingNoise(qub, perr).update_quantum_state(state)
        H(qub).update_quantum_state(state)

    return state


def one_single_run(perr: float) -> tuple[float]:
    r"""
    A function for implementing one run of the single post-selected
    Hadamard-test protocol.
    First a state is generated from a distribution of circuits under
    circuit-level noise of strength perr.
    Then the state is then projected onto the different postselectable


    """

    steaneBlock = [0, 1, 2, 3, 4, 5, 6]
    repnBlock = [7, 8, 9, 10, 11, 12, 13]

    # Option to include idling errors or not:
    idling = True

    # All even parity bit strings of length 7:
    bs7 = [x for x in bit_strings(7) if not sum(x) % 2]

    angle = np.pi / 4.0

    # post-selection probability
    ps_prob = 0

    # logical error probability for post-selected states
    err_prob = 0

    # Initialize the state on the steaneBlock to all zeros
    state = QuantumState(len(steaneBlock))
    state.set_zero_state()

    # Rotate first qubit into the |A> state then apply the
    # Steane encoding map:
    state = noisy_magic_state_init(state, steaneBlock[0], perr, angle)
    state = noisy_steane_encoder(state, steaneBlock, perr, idling=idling)

    # Perform the encoded Hadamard test:
    state = repn_had_test(state, steaneBlock, repnBlock, perr, idling=idling)

    # Apply the steane-decoder circuit, with logical qubit mapped to the
    # first position of the steaneBlock:
    state = steane_decoder(state, steaneBlock)

    # Rotate the qubit to diagonalize the Hadamard gate
    RY(steaneBlock[0], -angle).update_quantum_state(state)
    H(steaneBlock[0]).update_quantum_state(state)

    # Add the probability of an error, corresponding to the
    # probability of observing |1> in the output:
    X(steaneBlock[0]).update_quantum_state(state)

    # Look over all post-selected patterns (even bitstrings)
    for bs in bs7:
        qubit_state = drop_qubit(
            state, steaneBlock[1:] + repnBlock, [0, 0, 0, 0, 0, 0] + list(bs)
        )

        # Add probability of this outcome to the post-selection probability:
        ps_prob += qubit_state.get_squared_norm()
        err_prob += qubit_state.get_zero_probability(steaneBlock[0])

    return ps_prob, err_prob


def one_double_run(perr: float) -> tuple[float]:
    r"""
    A function for implementing one run of the double post-selected
    Hadamard-test protocol.
    First a state is generated from a distribution of circuits under
    circuit-level noise of strength perr.
    Then the state is then projected onto the different postselectable
    measurement patterns.


    """
    steaneBlock = [0, 1, 2, 3, 4, 5, 6]
    repnBlock = [7, 8, 9, 10, 11, 12, 13]

    bs7 = [x for x in bit_strings(7) if not sum(x) % 2]

    angle = np.pi / 4.0
    idling = True

    ps_prob = 0
    err_prob = 0

    # Initialize the steaneBlock to the all zeros state:
    state = QuantumState(len(steaneBlock))
    state.set_zero_state()

    # Rotate first qubit in the steaneBlock to the magic state then
    # encode the steaneBlock into the Steane codespace:
    state = noisy_magic_state_init(state, steaneBlock[0], perr, angle)
    state = noisy_steane_encoder(state, steaneBlock, perr, idling=idling)

    # Perform first encoded Hadamard test:
    state = repn_had_test(state, steaneBlock, repnBlock, perr, idling=idling)

    # Scan over measurement patterns to post-select over:
    for firstbs in bs7:

        # For each pattern project out the repnBlock and take the norm
        # of the state to determine if a second Hadamard test will be
        # performed:

        bs_state = drop_qubit(state, repnBlock, list(firstbs))
        pbs = bs_state.get_squared_norm()

        if pbs > 1e-10:
            # Perform second Hadamard test:
            bs_state = repn_had_test(
                bs_state, steaneBlock, repnBlock, perr, idling=idling
            )

            # Decode the Steane-encoded state
            bs_state = steane_decoder(bs_state, steaneBlock)

            # Logical qubit now at first position in steaneBlock
            # rotate into Hadamard eigenbasis:
            RY(steaneBlock[0], -angle).update_quantum_state(bs_state)
            H(steaneBlock[0]).update_quantum_state(bs_state)

            # Flip the logical qubit so that |0> indicates error:
            X(steaneBlock[0]).update_quantum_state(bs_state)

            # Scan over measurement patterns to post-select over for the
            # second Hadamard test:
            for secondbs in bs7:
                qubit_state = drop_qubit(
                    bs_state,
                    steaneBlock[1:] + repnBlock,
                    [0, 0, 0, 0, 0, 0] + list(secondbs),
                )
                ps_prob += qubit_state.get_squared_norm()
                err_prob += qubit_state.get_zero_probability(steaneBlock[0])

    return ps_prob, err_prob
