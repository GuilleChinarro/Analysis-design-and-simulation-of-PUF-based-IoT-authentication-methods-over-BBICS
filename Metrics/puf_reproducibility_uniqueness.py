import pypuf.simulation as simulation
import numpy as np
import time
from pypuf.io import random_inputs
from numpy.random import default_rng
import pandas as pd
import matplotlib.pyplot as plt
import os

def calculate_entropy(responses):
    value, counts = np.unique(responses, return_counts=True)
    probs = counts / len(responses)
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

def evaluate_reproducibility(puf_name, noise_level, num_challenges=1000, num_repeats=10):
    puf = get_puf(puf_name, noise_level=noise_level)
    if puf is None:
        return None

    # Generar desafíos aleatorios
    challenges = random_inputs(n=64, N=num_challenges, seed=2)

    responses_list = []
    for _ in range(num_repeats):
        responses = puf.eval(challenges)
        responses_list.append(responses)

    responses_array = np.array(responses_list)
    variability = np.mean(np.std(responses_array, axis=0))

    return {
        "puf_name": puf_name,
        "noise_level": noise_level,
        "variability": variability
    }

def evaluate_uniqueness(puf_name, noise_level, num_challenges=1000, num_instances=10):
    pufs = [get_puf(puf_name, noise_level=noise_level, seed=i) for i in range(num_instances)]
    if None in pufs:
        return None

    # Generar desafíos aleatorios
    challenges = random_inputs(n=64, N=num_challenges, seed=2)

    responses_list = []
    for puf in pufs:
        responses = puf.eval(challenges)
        responses_list.append(responses)

    responses_array = np.array(responses_list)
    hamming_distances = np.mean([
        np.mean(np.abs(responses_array[i] - responses_array[j]))
        for i in range(num_instances) for j in range(i + 1, num_instances)
    ])

    return {
        "puf_name": puf_name,
        "noise_level": noise_level,
        "hamming_distance": hamming_distances
    }

def get_puf(puf_name, noise_level, seed=None):
    if seed is None:
        seed = int(time.time() * 1e6)
    
    def get_ArbiterPUF():
        return simulation.ArbiterPUF(n=64, seed=seed, noisiness=noise_level)

    def get_XORArbiterPUF():
        return simulation.XORArbiterPUF(n=64, k=2, seed=seed, noisiness=noise_level)

    def get_XORFeedForwardArbiterPUF():
        return simulation.XORFeedForwardArbiterPUF(n=64, k=4, ff=[(32, 63)], seed=seed, noisiness=noise_level)
    
    def get_BistableRingPUF():
        n = 64
        weights = default_rng(1).normal(size=(n+1))
        return simulation.BistableRingPUF(n=64, weights=weights)
    
    def get_XORBistableRingPUF():
        k, n = 8, 64
        weights = default_rng(1).normal(size=(k, n+1))
        return simulation.XORBistableRingPUF(n=64, k=8, weights=weights)

    def get_InterposePUF():
        return simulation.InterposePUF(n=64, k_up=8, k_down=8, seed=seed, noisiness=noise_level)

    def get_LightweightSecurePUF():
        return simulation.LightweightSecurePUF(n=64, k=8, seed=seed, noisiness=noise_level)

    def get_PermutationPUF():
        return simulation.PermutationPUF(n=64, k=8, seed=seed, noisiness=noise_level)

    puf_functions = {
        "ArbiterPUF": get_ArbiterPUF,
        "XORArbiterPUF": get_XORArbiterPUF,
        "XORFeedForwardArbiterPUF": get_XORFeedForwardArbiterPUF,
        "BistableRingPUF": get_BistableRingPUF,
        "XORBistableRingPUF": get_XORBistableRingPUF,
        "InterposePUF": get_InterposePUF,
        "LightweightSecurePUF": get_LightweightSecurePUF,
        "PermutationPUF": get_PermutationPUF
    }
    
    puf_function = puf_functions.get(puf_name)
    if puf_function:
        return puf_function()
    else:
        print(f"PUF name {puf_name} is not valid.")
        return None

# Crear directorio para guardar las gráficas
output_dir = "PUF_Evaluation_Plots"
os.makedirs(output_dir, exist_ok=True)

# Evaluar la reproducibilidad y unicidad para cada PUF disponible en diferentes niveles de ruido
puf_names = ["ArbiterPUF", "XORArbiterPUF", "XORFeedForwardArbiterPUF", "InterposePUF", "LightweightSecurePUF", "PermutationPUF"]
noise_levels = np.arange(0.0, 1.0, 0.05)

reproducibility_results = []
uniqueness_results = []

for puf_name in puf_names:
    for noise_level in noise_levels:
        reproducibility_results.append(evaluate_reproducibility(puf_name, noise_level))
        uniqueness_results.append(evaluate_uniqueness(puf_name, noise_level))

df_reproducibility_results = pd.DataFrame(reproducibility_results)
df_uniqueness_results = pd.DataFrame(uniqueness_results)

# Guardar los resultados en archivos CSV
df_reproducibility_results.to_csv('reproducibility_results.csv', index=False)
df_uniqueness_results.to_csv('uniqueness_results.csv', index=False)

# Graficar y guardar los resultados de reproducibilidad en una sola gráfica
plt.figure(figsize=(14, 8))
for puf_name in puf_names:
    df_reproducibility = df_reproducibility_results[df_reproducibility_results['puf_name'] == puf_name]
    plt.plot(df_reproducibility['noise_level'], df_reproducibility['variability'], label=puf_name, marker='o')

plt.xlabel('Noise Level')
plt.ylabel('Variability')
plt.title('Variability vs Noise Level for All PUFs')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(output_dir, 'Variability_vs_Noise_Level_All_PUFs.png'))
plt.show()

# Graficar y guardar los resultados de unicidad (Hamming Distance)
plt.figure(figsize=(12, 6))
for puf_name in puf_names:
    df_uniqueness = df_uniqueness_results[df_uniqueness_results['puf_name'] == puf_name]
    plt.plot(df_uniqueness['noise_level'], df_uniqueness['hamming_distance'], label=puf_name, marker='o')
plt.xlabel('Noise Level')
plt.ylabel('Hamming Distance')
plt.title('Hamming Distance for all PUFs')
plt.legend()
plt.grid(True)
plt.savefig(os.path.join(output_dir, 'Hamming_Distance_vs_Noise_Level_All_PUFs.png'))
plt.show()
