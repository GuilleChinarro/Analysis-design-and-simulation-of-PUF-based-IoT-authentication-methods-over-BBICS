import pypuf.simulation as simulation
import numpy as np
import time
from pypuf.io import random_inputs
from numpy.random import default_rng
import pandas as pd
import matplotlib.pyplot as plt

def calculate_entropy(responses):
    value, counts = np.unique(responses, return_counts=True)
    probs = counts / len(responses)
    entropy = -np.sum(probs * np.log2(probs))
    return entropy

def evaluate_puf(puf_name, noise, num_challenges=1000):
    puf = get_puf(puf_name, noise)
    if puf is None:
        return None

    challenges = random_inputs(n=64, N=num_challenges, seed=2)

    start_time = time.time()
    responses = puf.eval(challenges)
    end_time = time.time()
    response_time = end_time - start_time

    response_entropy = calculate_entropy(responses)
    
    repeated_challenges = np.tile(challenges, (2, 1))
    repeated_responses = puf.eval(repeated_challenges)
    ber = np.mean(repeated_responses[:num_challenges] != repeated_responses[num_challenges:])

    return {
        "puf_name": puf_name,
        "noise": noise,
        "response_time": response_time,
        "entropy": response_entropy,
        "ber": ber
    }

def get_puf(puf_name, noise):
    def get_ArbiterPUF():
        return simulation.ArbiterPUF(n=64, noisiness=noise, seed=1)

    def get_XORArbiterPUF():
        return simulation.XORArbiterPUF(n=64, k=2, noisiness=noise, seed=1)

    def get_XORFeedForwardArbiterPUF():
        return simulation.XORFeedForwardArbiterPUF(n=64, k=4, ff=[(32, 63)], noisiness=noise, seed=1)
    
    def get_BistableRingPUF():
        n = 64
        weights = default_rng(1).normal(size=(n+1))
        return simulation.BistableRingPUF(n=64, weights=weights)
    
    def get_XORBistableRingPUF():
        k, n = 8, 64
        weights = default_rng(1).normal(size=(k, n+1))
        return simulation.XORBistableRingPUF(n=64, k=8, weights=weights)

    def get_InterposePUF():
        return simulation.InterposePUF(n=64, k_up=8, k_down=8, noisiness=noise, seed=1)

    def get_LightweightSecurePUF():
        return simulation.LightweightSecurePUF(n=64, k=8, noisiness=noise, seed=1)

    def get_PermutationPUF():
        return simulation.PermutationPUF(n=64, k=8, noisiness=noise, seed=1)

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

# Evaluate PUFs for different noise levels
puf_names = ["ArbiterPUF", "XORArbiterPUF", "XORFeedForwardArbiterPUF", "BistableRingPUF", "XORBistableRingPUF", "InterposePUF", "LightweightSecurePUF", "PermutationPUF"]
noise_levels = np.arange(0.0, 1.0, 0.05)
results = []

for puf_name in puf_names:
    for noise in noise_levels:
        result = evaluate_puf(puf_name, noise)
        if result:
            results.append(result)

df_results = pd.DataFrame(results)
print(df_results)

# Save the DataFrame to an Excel file
df_results.to_csv("PUF_Evaluation_Results.csv", index=False)

# Plotting Entropy for all PUFs
plt.figure(figsize=(14, 8))
for puf_name in puf_names:
    subset = df_results[df_results['puf_name'] == puf_name]
    plt.plot(subset['noise'], subset['entropy'], label=puf_name, marker='o')

plt.title('Entropy vs Noise Level for All PUFs')
plt.xlabel('Noise Level')
plt.ylabel('Entropy')
plt.legend()
plt.grid(True)
plt.show()

# Plotting BER for each PUF
for puf_name in puf_names:
    subset = df_results[df_results['puf_name'] == puf_name]
    plt.figure(figsize=(10, 6))
    plt.plot(subset['noise'], subset['ber'], label='BER', marker='x')
    plt.title(f'{puf_name} - BER vs Noise Level')
    plt.xlabel('Noise Level')
    plt.ylabel('BER')
    plt.legend()
    plt.grid(True)
    plt.show()
