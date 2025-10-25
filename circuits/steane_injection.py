import numpy as np
from qulacs import QuantumState
from qulacs.gate import H, RY, X, Z, DepolarizingNoise
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
    "repn_chad_test",
    "noisy_magic_circuit_A",
    "noisy_magic_circuit_B",
    "state_processing_A",
    "state_processing_B",
    "one_double_run",
    "one_single_run",
]


def repn_chad_test(
    state: QuantumState,
    steaneBlock: list[int],
    repnBlock: list[int],
    perr: float,
    idling=False,
) -> QuantumState:

    rep_anc = QuantumState(7)
    state = tensor_product(rep_anc, state)

    state = noisy_plus_state_init(state, repnBlock[0], perr)
    state = noisy_repetition_encoder(state, repnBlock, perr, flag=True, idling=idling)
    state = noisy_encoded_chad(state, repnBlock, steaneBlock, perr, idling=idling)

    for qub in repnBlock:
        H(qub).update_quantum_state(state)
        DepolarizingNoise(qub, perr).update_quantum_state(state)

    return state


def noisy_magic_circuit_A(
    steaneBlock: list[int], repnBlock: list[int], perr: float, flag=True
) -> QuantumState:

    angle = np.pi / 4.0

    num_qubits = len(steaneBlock + repnBlock)

    state = QuantumState(num_qubits)
    state.set_zero_state()

    state = noisy_magic_state_init(state, steaneBlock[0], perr, angle)
    state = noisy_plus_state_init(state, repnBlock[0], perr)
    state = noisy_steane_encoder(state, steaneBlock, perr)

    state = steane_decoder(state, steaneBlock)

    for qub in repnBlock:
        H(qub).update_quantum_state(state)

    return state


def state_processing_A(
    state: QuantumState, steaneBlock: list[int], repnBlock: list[int]
) -> tuple[float]:

    bs7 = [x for x in bit_strings(7) if not sum(x) % 2]
    bs6 = bit_strings(6)

    angle = np.pi / 4.0

    net_prob = 0
    err_prob = 0
    err = 0

    for bs_rep in bs7:

        if drop_qubit(state, repnBlock, list(bs_rep)).get_squared_norm() > 1e-10:

            for bs_steane in bs6:

                bs_state = drop_qubit(
                    state, steaneBlock[1:] + repnBlock, list(bs_steane + bs_rep)
                )

                pbs = bs_state.get_squared_norm()

                if pbs > 1e-10:
                    net_prob += pbs

                    xsynd = bs_steane[:3]
                    zsynd = bs_steane[3:]

                    if sum(xsynd) == 2:
                        Z(0).update_quantum_state(bs_state)

                    if sum(zsynd) == 2:
                        X(0).update_quantum_state(bs_state)

                    RY(steaneBlock[0], -angle).update_quantum_state(bs_state)
                    H(steaneBlock[0]).update_quantum_state(bs_state)

                    X(steaneBlock[0]).update_quantum_state(bs_state)

                    err_prob += bs_state.get_zero_probability(steaneBlock[0])

                    if bs_state.get_zero_probability(steaneBlock[0]) / pbs > 0.1:
                        err += pbs

    return net_prob, err_prob, err


def noisy_magic_circuit_B(
    steaneBlock: list[int],
    repnBlock1: list[int],
    repnBlock2: list[int],
    perr: float,
    flag=True,
) -> QuantumState:

    angle = np.pi / 4.0

    state = QuantumState(len(steaneBlock))
    state.set_zero_state()

    state = noisy_magic_state_init(state, steaneBlock[0], perr, angle)
    state = noisy_steane_encoder(state, steaneBlock, perr)

    state = repn_chad_test(state, steaneBlock, repnBlock1, perr)
    state = repn_chad_test(state, steaneBlock, repnBlock2, perr)

    state = steane_decoder(state, steaneBlock)

    return state


def state_processing_B(
    state: QuantumState,
    steaneBlock: list[int],
    repnBlock1: list[int],
    repnBlock2: list[int],
) -> tuple[float]:

    bs7 = [x for x in bit_strings(7) if not sum(x) % 2]
    bs6 = bit_strings(6)

    angle = np.pi / 4.0

    net_prob = 0
    err_prob = 0
    err = 0

    for bs_rep1 in bs7:
        if drop_qubit(state, repnBlock1, list(bs_rep1)).get_squared_norm() > 1e-10:
            for bs_rep2 in bs7:
                if (
                    drop_qubit(
                        state, repnBlock1 + repnBlock2, list(bs_rep1 + bs_rep2)
                    ).get_squared_norm()
                    > 1e-10
                ):

                    for bs_steane in bs6:

                        bs_state = drop_qubit(
                            state,
                            steaneBlock[1:] + repnBlock1 + repnBlock2,
                            list(bs_steane + bs_rep1 + bs_rep2),
                        )

                        pbs = bs_state.get_squared_norm()

                        if pbs > 1e-10:
                            net_prob += pbs

                            xsynd = bs_steane[:3]
                            zsynd = bs_steane[3:]

                            if sum(xsynd) == 2:
                                Z(0).update_quantum_state(bs_state)

                            if sum(zsynd) == 2:
                                X(0).update_quantum_state(bs_state)

                            RY(steaneBlock[0], -angle).update_quantum_state(bs_state)
                            H(steaneBlock[0]).update_quantum_state(bs_state)

                            X(steaneBlock[0]).update_quantum_state(bs_state)

                            err_prob += bs_state.get_zero_probability(steaneBlock[0])

                            if (
                                bs_state.get_zero_probability(steaneBlock[0]) / pbs
                                > 0.1
                            ):
                                err += pbs

    return net_prob, err_prob, err


def one_single_run(perr: float) -> tuple[float]:

    steaneBlock = [0, 1, 2, 3, 4, 5, 6]
    repnBlock = [7, 8, 9, 10, 11, 12, 13]

    idling = False

    bs7 = [x for x in bit_strings(7) if not sum(x) % 2]
    bs6 = [x for x in bit_strings(6)]

    angle = np.pi / 4.0

    # net_prob = 0
    ps_prob = 0
    err_prob = 0

    state = QuantumState(len(steaneBlock))
    state.set_zero_state()

    state = noisy_magic_state_init(state, steaneBlock[0], perr, angle)
    state = noisy_steane_encoder(state, steaneBlock, perr, idling=idling)

    state = repn_chad_test(state, steaneBlock, repnBlock, perr, idling=idling)

    for bs in bs7:
        bs_state = drop_qubit(state, repnBlock, list(bs))
        pbs = bs_state.get_squared_norm()

        if pbs > 1e-10:

            ps_prob += pbs

            bs_state = steane_decoder(bs_state, steaneBlock)

            for steanebs in bs6:
                qubit_state = drop_qubit(bs_state, steaneBlock[1:], list(steanebs))

                if qubit_state.get_squared_norm() > 1e-8:

                    xsynd = steanebs[:3]
                    zsynd = steanebs[3:]

                    if sum(xsynd) == 2:
                        Z(steaneBlock[0]).update_quantum_state(qubit_state)

                    if sum(zsynd) == 2:
                        X(steaneBlock[0]).update_quantum_state(qubit_state)

                    RY(steaneBlock[0], -angle).update_quantum_state(qubit_state)
                    H(steaneBlock[0]).update_quantum_state(qubit_state)

                    X(steaneBlock[0]).update_quantum_state(qubit_state)

                    err_prob += qubit_state.get_zero_probability(steaneBlock[0])

    return ps_prob, err_prob


def one_double_run(perr: float) -> tuple[float]:

    steaneBlock = [0, 1, 2, 3, 4, 5, 6]
    repnBlock = [7, 8, 9, 10, 11, 12, 13]

    bs7 = [x for x in bit_strings(7) if not sum(x) % 2]
    bs6 = [x for x in bit_strings(6)]

    angle = np.pi / 4.0
    idling = False

    # net_prob = 0
    ps_prob = 0
    err_prob = 0

    state = QuantumState(len(steaneBlock))
    state.set_zero_state()

    state = noisy_magic_state_init(state, steaneBlock[0], perr, angle)
    state = noisy_steane_encoder(state, steaneBlock, perr, idling=idling)

    state = repn_chad_test(state, steaneBlock, repnBlock, perr, idling=idling)

    for firstbs in bs7:
        bs_state = drop_qubit(state, repnBlock, list(firstbs))
        pbs = bs_state.get_squared_norm()

        if pbs > 1e-10:
            bs_state = repn_chad_test(
                bs_state, steaneBlock, repnBlock, perr, idling=idling
            )

            for secondbs in bs7:
                sbs_state = drop_qubit(bs_state, repnBlock, list(secondbs))
                psbs = sbs_state.get_squared_norm()

                if psbs > 1e-10:

                    ps_prob += psbs

                    sbs_state = steane_decoder(sbs_state, steaneBlock)

                    for thirdbs in bs6:
                        qubit_state = drop_qubit(
                            sbs_state, steaneBlock[1:], list(thirdbs)
                        )
                        psts = qubit_state.get_squared_norm()

                        if psts > 1e-10:
                            # net_prob += psts

                            xsynd = thirdbs[:3]
                            zsynd = thirdbs[3:]

                            if sum(xsynd) == 2:
                                Z(steaneBlock[0]).update_quantum_state(qubit_state)

                            if sum(zsynd) == 2:
                                X(steaneBlock[0]).update_quantum_state(qubit_state)

                            RY(steaneBlock[0], -angle).update_quantum_state(qubit_state)
                            H(steaneBlock[0]).update_quantum_state(qubit_state)

                            X(steaneBlock[0]).update_quantum_state(qubit_state)

                            err_prob += qubit_state.get_zero_probability(steaneBlock[0])

    return ps_prob, err_prob
