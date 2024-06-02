from hashlib import sha256
import json
import time

class Block:
    """
    Clase que representa un bloque en la cadena de bloques.
    """

    def __init__(self, index, timestamp, data, previous_hash=''):
        """
        Inicializa un bloque con los siguientes parámetros:
        - index: El índice del bloque en la cadena.
        - timestamp: La marca de tiempo del bloque.
        - data: datos del bloque (puede ser cualquier información relevante).
        - previous_hash: El hash del bloque anterior en la cadena (opcional).
        """
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        """
        Calcula el hash del bloque.
        """
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "data": self.data
        }
        
        # Serializar los datos del bloque y calcular el hash
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

class SmartContract:
    """
    Clase que representa un smart contract para almacenar parejas challenge-response.
    """

    def __init__(self):
        """Inicializa el contrato inteligente con un diccionario vacío de desafíos y respuestas."""
        self.challenge_response_pairs = {}
        self.state = {}

    def store_puf(self, identifier, challenges_responses_dict, estado):
        """Almacena las parejas challenge-response validadas en el contrato inteligente."""
        self.challenge_response_pairs[identifier] = challenges_responses_dict
        self.state[identifier] = {"estado": estado}

    def get_challenges(self, identifier):
        """Devuelve todos los desafíos almacenados para un identificador dado."""
        return list(self.challenge_response_pairs.get(identifier, {}).keys())

    def get_response_by_index(self, identifier, index):
        """Devuelve la respuesta correspondiente a un desafío específico en un identificador dado."""
        challenges = self.get_challenges(identifier)
        if 0 <= index < len(challenges):
            return self.challenge_response_pairs[identifier][challenges[index]]
        else:
            return None
        
    def get_state(self, identifier):
        """Devuelve el estado almacenado para un identificador dado."""
        return self.state.get(identifier, {})

    def set_state(self, identifier, new_state):
        """Actualiza el estado para un identificador dado."""
        if identifier in self.state:
            self.state[identifier]["estado"] = new_state

    @staticmethod
    def from_dict(data):
        smart_contract = SmartContract()
        for key, value in data.items():
            setattr(smart_contract, key, value)
        return smart_contract
    

class Blockchain:
    def __init__(self, num_blocks=10):
        self.chain = [self.create_genesis_block()]
        self.pending_smart_contracts = []
        self.num_blocks = num_blocks
        self.difficulty = 4
        self.block_validation_times = []
        self.total_hashes = 0
        self.total_validation_time = 0.0
        self.num_blocks_validated = 0
        self.current_validation_time = 0.0
        self.current_hashes = 0

    def create_genesis_block(self):
        """Crea el bloque génesis."""
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        """Obtiene el último bloque de la cadena."""
        return self.chain[-1]

    def add_block(self, new_block):
        """
        Añade un nuevo bloque a la cadena después de minarlo.
        """
        
        new_block.previous_hash = self.get_latest_block().hash
        self.current_hashes = 0
        current_validation_time = 0
        start_time = time.time()
        new_block.hash = self.mine_block(new_block)

        self.current_validation_time = time.time() - start_time
        
        self.chain.append(new_block)

        self.num_blocks_validated += 1
        self.total_validation_time += self.current_validation_time

        self.calculate_hash_rate()

    def mine_block(self, block):
        """
        Mina el bloque (calcula el hash que cumple con la dificultad).
        """
        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.calculate_hash()

            self.current_hashes += 1
            self.total_hashes += 1
        return block.hash

    def is_chain_valid(self):
        """Verifica la validez de la cadena de bloques."""

        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            
        return True

    def add_smart_contract(self, smart_contract):
        """Añade un contrato inteligente a la cadena de bloques."""
        self.pending_smart_contracts.append(smart_contract)

        def convert_keys_to_strings(d):
            """Convierte todas las claves del diccionario a cadenas."""
            if isinstance(d, dict):
                return {str(k): convert_keys_to_strings(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [convert_keys_to_strings(i) for i in d]
            else:
                return d
        
        # Convertir las claves del diccionario a cadenas
        converted_dict = convert_keys_to_strings(smart_contract.challenge_response_pairs)
        
        # Crear una copia del contrato inteligente con las claves convertidas
        smart_contract_data = {
            'challenge_response_pairs': converted_dict,
            'state': smart_contract.state
        }
        
        data = json.dumps(smart_contract_data, sort_keys=True)
        new_block = Block(len(self.chain), time.time(), data, self.get_latest_block().hash)
        self.add_block(new_block)
        if len(self.chain) > self.num_blocks:
            self.chain = self.chain[-self.num_blocks:]


    def get_latest_smart_contract(self):
        """Obtiene y deserializa el último contrato inteligente añadido a la cadena."""
        if not self.chain:
            return None

        latest_block = self.get_latest_block()
        smart_contract_data = json.loads(latest_block.data)

        def convert_keys_back(d):
            """Convierte las claves de los diccionarios a tuplas si es necesario."""
            if isinstance(d, dict):
                new_dict = {}
                for k, v in d.items():
                    try:
                        new_key = tuple(map(int, k.strip("()").split(", ")))
                    except:
                        new_key = k
                    new_dict[new_key] = convert_keys_back(v)
                return new_dict
            elif isinstance(d, list):
                return [convert_keys_back(i) for i in d]
            else:
                return d

        # Convertir las claves del diccionario de vuelta a su formato original
        smart_contract_data['challenge_response_pairs'] = convert_keys_back(smart_contract_data['challenge_response_pairs'])

        smart_contract = SmartContract()
        smart_contract.challenge_response_pairs = smart_contract_data['challenge_response_pairs']
        smart_contract.state = smart_contract_data['state']

        return smart_contract

    def calculate_hash_rate(self):
        if self.current_validation_time > 0:
            return self.current_hashes / self.current_validation_time
        else:
            return 0

    def get_avg_block_validation_time(self):
        if self.num_blocks_validated > 0:
            return self.total_validation_time / self.num_blocks_validated
        return 0

    def get_total_hashes(self):
        return self.total_hashes
    
    def get_total_time(self):
        return self.total_validation_time
    
    def get_medium_hash_rate(self):
        if self.num_blocks_validated > 0:
            return self.total_hashes / self.total_validation_time
        return 0

def generate_blockchain(blockchain):

    for block_index in range(1, blockchain.num_blocks + 1):
        new_block = Block(block_index, time.time(), f"Block {block_index} data")
        
        blockchain.add_block(new_block)


def validate_blockchain(blockchain):
    print()
    if blockchain.is_chain_valid():
        print("Validación de los bloques correcta.")
    else:
        print("Error en la validación de los bloques.")

    avg_time = blockchain.get_avg_block_validation_time()
    hash_rate = blockchain.calculate_hash_rate()
    print(f"Tiempo promedio de validación de bloques: {avg_time:.6f} segundos")
    print(f"Tasa de hash: {hash_rate:.6f} hashes/segundo")

    blockchain.total_validation_time += avg_time
