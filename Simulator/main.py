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

    # Generar CRP
    challenges, responses = puf_challenge_response.get_crp(puf, num_crp)

    # Preparar el diccionario de CRP
    crp_dict = dict(zip(map(tuple, challenges), responses))

    estado = "Registrado"

    # Almacenar los pares de CRP y el estado en el contrato inteligente
    smart_contract.store_puf(identifier, crp_dict, estado)

    # Mostrar el identificador y el estado
    print(f"Identificador: {identifier}")
    print(f"Estado: {estado}")

    
def authentication(smart_contract, num_crp, puf, permitido):

    identifier = get_id(puf)
    
    # TODO: Si existieser una lista de identificadores no permitidos, se comprobaria el id y si no esta permitido se transiciona a estado bloqueado, ruptura de método
    if not permitido:
        smart_contract.set_state(identifier, "Bloqueado")
        return 2
    # Número de responses a evaluar
    num_responses = 64
    # Arrays para los valores aleatorios y las respuestas
    random_indices = []
    random_responses = []

    # Obtiene "num_responses" responses aleatorios y guarda los índices
    for _ in range(num_responses):
        random_index = random.randint(0, num_crp - 1)
        response = smart_contract.get_response_by_index(identifier, random_index)
        random_indices.append(random_index)
        random_responses.append(response)

    # Obtiene TODOS los challenges
    challenges = np.array(smart_contract.get_challenges(identifier))

    # Genera TODOS los responses de los challenges obtenidos
    generated_responses = puf.eval(challenges)

    probabilidad_Fallo_Autenticacion = 0.3
    fallo = random.random() < probabilidad_Fallo_Autenticacion
    if fallo:
        generated_responses = np.where(generated_responses == 1, -1, 1)

    # Valida la autenticación
    authentication_success = False
    for i in range(num_responses):
        if generated_responses[random_indices[i]] == random_responses[i]:
            authentication_success = True
            break

    if authentication_success:
        print("Autenticación correcta")
        smart_contract.set_state(identifier, "Autenticado")
        return 0
    else:
        print("Autenticación fallida")
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
    
    smart_contract = blockchain.get_latest_smart_contract()
    
    print()
    print("Authentication phase:")

    intentos = 0
    permitido = True
    probabilidad_no_Permitido = 0.2
    permitido = not random.random() < probabilidad_no_Permitido

    while True:
        autenticado = authentication(smart_contract, num_crp, puf, permitido)
        if autenticado == 0:
            if intentos == 0:
                # Autenticado a la primera, pasa al estado "Autenticado"
                break
            else:
                smart_contract.set_state(get_id(puf), "En Observacaión")
                break
        elif autenticado == 1:
            intentos += 1

            # Mientras lo intenta está en el estado "Autenticación fallida"
            if intentos >= intentos_maximos:
                print("Autenticación fallida por fallos excedidos")
                smart_contract.set_state(get_id(puf), "Bloqueado por fallos excedidos")
                break
        else:
            break

    blockchain.add_smart_contract(smart_contract)
    blockchain_validation.validate_blockchain(blockchain)        

    smart_contract = blockchain.get_latest_smart_contract()
    state = smart_contract.get_state(get_id(puf))['estado']
    print()
    print("Estado: " + str(state))

    if state not in states_tracker:
        states_tracker[state] = {
            'count': 0,
            'ids': []
        }
    
    # Añade el ID del puf a la lista correspondiente al estado
    states_tracker[state]['ids'].append(get_id(puf))
    # Incrementa el contador del estado
    states_tracker[state]['count'] += 1

def print_states_tracker(states_tracker):
    for state, info in states_tracker.items():
        print(f"{state}: {info['count']}")
        for puf_id in info['ids']:
            print(f"- {puf_id}")

def main ():
    num_crp = 10
    num_blocks = 10
    num_PUFs = 10   
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

    # Diccionario para contar el número de PUFs generados de cada tipo
    puf_count = defaultdict(int)

    # Crear y procesar PUFs aleatorios
    for puf_name in selected_puf_types:
        puf = puf_challenge_response.get_puf(puf_name)
        console.print("\n[bold cyan]-------------------------------------------------------------------------------[/bold cyan]")
        console.print(f"[bold #FFA500]{puf_name}[/bold #FFA500]")
        console.print("[bold cyan]-------------------------------------------------------------------------------[/bold cyan]")

        enroll_and_authenticate(smart_contract, blockchain, puf, num_crp, states_tracker, intentos_maximos)
        puf_count[puf_name] += 1

    # Imprimir el conteo de PUFs generados de cada tipo
    print("------------------------------------------------------------------")
    print()
    print("PUFs generados:")
    for puf_name, count in puf_count.items():
        print(f"{puf_name}: {count}")

    print()
    print_states_tracker(states_tracker)
    print()
    print("------------------------------------------------------------------")
    print()

   

    # Tabla de métricas
    table = Table(show_header=True, header_style="bold magenta")
    table.add_column("Métrica", style="dim", justify="center")
    table.add_column("Valor", justify="center")

  
    table.add_row("Hash totales", str(blockchain.get_total_hashes()))
    table.add_row("Tiempo total", f"{blockchain.get_total_time()} segundos")
    table.add_row("Tasa media de Hash", f"{blockchain.get_medium_hash_rate()} hashes/segundo")

    console.print(table)

if __name__ == "__main__":
    main()

