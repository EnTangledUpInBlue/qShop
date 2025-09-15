from circuits.circuit_tools import file_tagger
from noisy_circuits_stim import construct_steane_7rep_circuit
from circuits.decoders import steane_transversal_decoder, repetition_transversal_xdecoder
from random import randint


if __name__ == '__main__':
    r"""
    Experiment A:
    
    Magic state preparation in Steane encoding.

    Seven-qubit repetition-encoded ancilla with a flag qubit
    in the preparation.

    A simulation of magic state distillation circuit for preparing a 
    Steane encoded qubit and a seven-qubit repetition encoded ancilla.


    """


    error_rates = [0,
                1.0*10**(-5), 2.5*10**(-5),5.0*10**(-5),7.5*10**(-5),
                1.0*10**(-4), 2.5*10**(-4),5.0*10**(-4),7.5*10**(-4),
                1.0*10**(-3), 2.5*10**(-3),5.0*10**(-3),7.5*10**(-3),
                1.0*10**(-2)]

    nkshots = 1_000
    shots = int(nkshots*10**3)

    flag = True

    filename = file_tagger('ExpA_'+str(nkshots) + 'k')+'.txt'

    for perr in error_rates:

        print('perr = ' + str(perr))

        seed = randint(0,1_000)

        selected = 0
        errors = 0
        
        noisy_circ = construct_steane_7rep_circuit(perr,flag)
        sampler = noisy_circ.compile_sampler(seed=seed)
        sample = sampler.sample(shots)

        for rec in sample:
            if not rec[0]: # post-select on False flag qubit
                mx = repetition_transversal_xdecoder(rec[1:8])

                # post-select on expected observable for Y_L =+1
                # (compensate for encoding, see decoder comments)
                if mx: 
                    selected +=1

                    # decode the steane measurement
                    my = steane_transversal_decoder(rec[8:])

                    # add error if the measurements do not agree
                    errors += not(mx==my)

        with open(filename,'a') as f:
            f.write(str([perr,selected,errors])+"\n"+str(seed) +"\n" )
            f.close()