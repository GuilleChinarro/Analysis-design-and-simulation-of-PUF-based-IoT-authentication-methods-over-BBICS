import pypuf.simulation as simulation
from pypuf.io import random_inputs
from numpy.random import default_rng

def get_puf(puf_name):
    """
    Crea una instancia de un PUF especificado.

    Parámetros:
        puf_name (str): El nombre del PUF que se desea instanciar.

    Devoluciones:
        Objeto con el puf instanciado
    """

    def get_ArbiterPUF():
        # Se le puede añadir un argumento noisiness.
        puf = simulation.ArbiterPUF(n=64, seed=1)
        return puf

    def get_XORArbiterPUF():
        # Se le puede añadir un argumento noisiness.
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

        # Definir el diccionario que mapea los nombres de PUF a las funciones que devuelven sus instancias
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
    
    # Obtener la función correspondiente al nombre del PUF
    puf_function = puf_functions.get(puf_name)

    # Llamar a la función para obtener la instancia del PUF
    if puf_function:
        return puf_function()
    else:
        # Si el nombre del PUF no es válido, devolver None
        print("Nombre no válido")
        return None
    

def get_crp(puf, num_crp):
    """
    Genera un par de challenges-responses para un PUF dado.

    Este método genera aleatoriamente un conjunto de desafíos (challenges) y evalúa el PUF con estos desafíos,
    obteniendo las respuestas correspondientes. Luego, convierte los desafíos y las respuestas de matrices numpy
    a listas y los devuelve como una tupla.

    Parámetros:
        puf (objeto): El PUF para el cual se generarán los challenges-responses.

    Devoluciones:
        challenges (list): Una lista de desafíos generados aleatoriamente.
        responses (list): Una lista de respuestas generadas por el PUF correspondientes a los desafíos.
    """
    challenges = random_inputs(n=64, N=num_crp, seed=2)
    
    # Evaluar el PUF con los desafíos generados
    responses = puf.eval(challenges)

    # Convertir las matrices numpy en listas
    challenges = challenges.tolist()
    responses = responses.tolist()

    return challenges, responses

