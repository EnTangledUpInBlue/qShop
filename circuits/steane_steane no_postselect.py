from circuits.circuit_tools import file_tagger
from noisy_circuits_stim import construct_steane_steane_circuit
from circuits.decoders import steane_transversal_decoder
from random import randint


if __name__ == '__main__':

    error_rates = [0,
                1.0*10**(-5), 2.5*10**(-5),5.0*10**(-5),7.5*10**(-5),
                1.0*10**(-4), 2.5*10**(-4),5.0*10**(-4),7.5*10**(-4),
                1.0*10**(-3), 2.5*10**(-3),5.0*10**(-3),7.5*10**(-3),
                1.0*10**(-2)]

    nkshots = 1_000
    shots = int(nkshots*10**3)

    filename = file_tagger('stn_stn_no_post_'+str(nkshots) + 'k')+'.txt'

    for perr in error_rates:

        print('perr = ' + str(perr))

        selected = 0
        errors = 0

        seed = randint(0,1_000)
        
        noisy_circ = construct_steane_steane_circuit(perr)
        sampler = noisy_circ.compile_sampler(seed=seed)
        sample = sampler.sample(shots)

        for rec in sample:
            selected +=1

            mx = steane_transversal_decoder(rec[:7])

            # decode the steane measurement
            my = steane_transversal_decoder(rec[7:])

            # add error if the measurements do not agree
            errors += not(mx==my)

        with open(filename,'a') as f:
            f.write(str([perr,selected,errors])+"\n"+str(seed)+"\n")
            f.close()