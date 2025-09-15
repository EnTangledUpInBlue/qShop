from circuits.circuit_tools import file_tagger
from noisy_circuits_stim import construct_steane_3rep_circuit
from circuits.decoders import steane_transversal_decoder, repetition_transversal_xdecoder
from random import randint

if __name__ == '__main__':

    r"""
    Experiment C:
    
    Magic state preparation in Steane encoding.

    Three-qubit repetition-encoded ancilla without a flag qubit
    in the preparation.

    A simulation of magic state distillation circuit for preparing a 
    Steane encoded qubit and a three-qubit repetition encoded ancilla
    prepared WITHOUT a flag qubit.

    """


    error_rates = [0,
                1.0*10**(-5), 2.5*10**(-5),5.0*10**(-5),7.5*10**(-5),
                1.0*10**(-4), 2.5*10**(-4),5.0*10**(-4),7.5*10**(-4),
                1.0*10**(-3), 2.5*10**(-3),5.0*10**(-3),7.5*10**(-3),
                1.0*10**(-2)]

    nkshots = 1_000
    shots = int(nkshots*10**3)

    flag = False

    filename = file_tagger('ExpC_'+str(nkshots) + 'k')+'.txt'

    for perr in error_rates:

        print('perr = ' + str(perr))

        # set seed
        seed = randint(0,1_000)

        # reset counters
        selected = 0
        errors = 0
        
        # construct noisy circuit and sampler then sample
        noisy_circ = construct_steane_3rep_circuit(perr,flag)
        sampler = noisy_circ.compile_sampler(seed = seed)
        sample = sampler.sample(shots)

        # process each outcome
        for rec in sample:

            mx = repetition_transversal_xdecoder(rec[:3])

            if mx: # post-select on expected observable for Y_L =+1
                selected +=1

                # decode the steane measurement
                my = steane_transversal_decoder(rec[3:])

                # add error if the measurements do not agree
                errors += not(mx==my)

        with open(filename,'a') as f:
            f.write(str([perr,selected,errors])+"\n"+str(seed)+"\n")
            f.close()