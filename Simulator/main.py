import puf_challenge_response
import blockchain_validation
import numpy as np
import random
import hashlib
from collections import defaultdict
from rich.console import Console
from rich.table import Table



def enrollment(smart_contract, num_crp, puf):

    identifier = get_id(puf)

    challenges, responses = puf_challenge_response.get_crp(puf, num_crp)

    crp_dict = dict(zip(map(tuple, challenges), responses))

    estado = "Registrado"

    smart_contract.store_puf(identifier, crp_dict, estado)

    print(f"Identificador: {identifier}")
    print(f"Estado: {estado}")

    
def authentication(smart_contract, num_crp, puf, permitido):

    identifier = get_id(puf)
    
    if not permitido:
        smart_contract.set_state(identifier, "Bloqueado")
        return 2
    num_responses = 64
    random_indices = []
    random_responses = []

    for _ in range(num_responses):
        random_index = random.randint(0, num_crp - 1)
        response = smart_contract.get_response_by_index(identifier, random_index)
        random_indices.append(random_index)
        random_responses.append(response)

    challenges = np.array(smart_contract.get_challenges(identifier))

    generated_responses = puf.eval(challenges)

    probabilidad_Fallo_Autenticacion = 0.3
    fallo = random.random() < probabilidad_Fallo_Autenticacion
    if fallo:
        generated_responses = np.where(generated_responses == 1, -1, 1)

    authentication_success = False
    for i in range(num_responses):
        if generated_responses[random_indices[i]] == random_responses[i]:
            authentication_success = True
            break

    if authentication_success:
        print("Successful authentication")
        smart_contract.set_state(identifier, "Autenticado")
        return 0
    else:
        print("Authentication failed")
        smart_contract.set_state(identifier, "Autenticación fallida")
        return 1


def get_id(puf):
    memory_address = id(puf)   
    return hashlib.sha256(str(memory_address).encode()).hexdigest()


def enroll_and_authenticate(smart_contract, blockchain, puf, num_crp, states_tracker, intentos_maximos):
    print("Enrollement phase:")
    enrollment(smart_contract, num_crp, puf)

    blockchain.add_smart_contract(smart_contract)
    blockchain_validation.validate_blockchain(blockchain)
    
    print()
    print("Authentication phase:")

    smart_contract = blockchain.get_latest_smart_contract()
    
    intentos = 0
    
    permitido = True
    probabilidad_no_Permitido = 0.2
    permitido = not random.random() < probabilidad_no_Permitido

    while True:
        autenticado = authentication(smart_contract, num_crp, puf, permitido)
        if autenticado == 0:
            if intentos == 0:
                break
            else:
                smart_contract.set_state(get_id(puf), "En Observacaión")
                break
        elif autenticado == 1:
            intentos += 1

            if intentos >= intentos_maximos:
                print("Authentication failed due to exceeded failures")
                smart_contract.set_state(get_id(puf), "Denied for exceeded judgements")
                break
        else:
            break

    blockchain.add_smart_contract(smart_contract)
    blockchain_validation.validate_blockchain(blockchain)        

    smart_contract = blockchain.get_latest_smart_contract()
    state = smart_contract.get_state(get_id(puf))['estado']
    print()
    print("State: " + str(state))

    if state not in states_tracker:
        states_tracker[state] = {
            'count': 0,
            'ids': []
        }
    
    states_tracker[state]['ids'].append(get_id(puf))
    states_tracker[state]['count'] += 1

def print_states_tracker(states_tracker):
    for state, info in states_tracker.items():
        print(f"{state}: {info['count']}")
        for puf_id in info['ids']:
            print(f"- {puf_id}")

def main ():
    num_crp = 256
    num_blocks = 10
    num_PUFs = 20
    intentos_maximos = 3

    smart_contract = blockchain_validation.SmartContract()
    blockchain = blockchain_validation.Blockchain(num_blocks)

    console = Console()

    states_tracker = {}

    puf_types = {
            "1": "ArbiterPUF",
            "2": "XORArbiterPUF",
            "3": "XORFeedForwardArbiterPUF",
            "4": "BistableRingPUF",
            "5": "InterposePUF",
            "6": "LightweightSecurePUF",
            "7": "PermutationPUF",
            "8": "XORBistableRingPUF"
        }
    
    selected_puf_types = random.choices(list(puf_types.values()), k=num_PUFs)

    puf_count = defaultdict(int)

    # Crear y procesar PUFs aleatorios
    for puf_name in selected_puf_types:
        puf = puf_challenge_response.get_puf(puf_name)
        console.print("\n[bold cyan]-------------------------------------------------------------------------------[/bold cyan]")
        console.print(f"[bold #FFA500]{puf_name}[/bold #FFA500]")
        console.print("[bold cyan]-------------------------------------------------------------------------------[/bold cyan]")

        enroll_and_authenticate(smart_contract, blockchain, puf, num_crp, states_tracker, intentos_maximos)
        puf_count[puf_name] += 1

    print("------------------------------------------------------------------")
    print()
    print("PUFs generated:")
    for puf_name, count in puf_count.items():
        print(f"{puf_name}: {count}")

    print()
    print_states_tracker(states_tracker)
    print()
    print("------------------------------------------------------------------")
    print()


    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Metric", style="dim", justify="center")
    table.add_column("Value", justify="center")

  
    table.add_row("Total Hashes", str(blockchain.get_total_hashes()))
    table.add_row("Total time", f"{blockchain.get_total_time()} seconds")
    table.add_row("Average Hash rate", f"{blockchain.get_medium_hash_rate()} hashes/second")

    console.print(table)

if __name__ == "__main__":
    main()

