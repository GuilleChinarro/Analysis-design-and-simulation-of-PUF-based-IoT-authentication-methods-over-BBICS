import pypuf.simulation as simulation
from pypuf.io import random_inputs
from numpy.random import default_rng

def get_puf(puf_name):

    def get_ArbiterPUF():
        puf = simulation.ArbiterPUF(n=64, seed=1)
        return puf

    def get_XORArbiterPUF():
        return simulation.XORArbiterPUF(n=64, k=2, seed=1)

    def get_XORFeedForwardArbiterPUF():
        return simulation.XORFeedForwardArbiterPUF(n=64, k=4, ff=[(32, 63)], seed=1)
    
    def get_BistableRingPUF():
        n = 64
        weights = default_rng(1).normal(size=(n+1))
        return simulation.BistableRingPUF(n=64, weights=weights)
    
    def get_XORBistableRingPUF():
        k, n = 8, 64
        weights = default_rng(1).normal(size=(k, n+1))
        return simulation.XORBistableRingPUF(n=64, k=8, weights=weights)

    def get_InterposePUF():
        return simulation.InterposePUF(n=64, k_up=8, k_down=8, seed=1, noisiness=.05)

    def get_LightweightSecurePUF():
        return simulation.LightweightSecurePUF(n=64, k=8, seed=1, noisiness=.05)

    def get_PermutationPUF():
        return simulation.PermutationPUF(n=64, k=8, seed=1, noisiness=.05)

    puf_functions = {
        "ArbiterPUF": get_ArbiterPUF,
        "XORArbiterPUF": get_XORArbiterPUF,
        "XORFeedForwardArbiterPUF": get_XORFeedForwardArbiterPUF,
        "BistableRingPUF": get_BistableRingPUF,
        "InterposePUF": get_InterposePUF,
        "LightweightSecurePUF": get_LightweightSecurePUF,
        "PermutationPUF": get_PermutationPUF,
        "XORBistableRingPUF": get_XORBistableRingPUF
}
    
    puf_function = puf_functions.get(puf_name)

    if puf_function:
        return puf_function()
    else:
        print("Invalid name")
        return None
    

def get_crp(puf, num_crp):
    challenges = random_inputs(n=64, N=num_crp, seed=2)
    
    responses = puf.eval(challenges)

    challenges = challenges.tolist()
    responses = responses.tolist()

    return challenges, responses

