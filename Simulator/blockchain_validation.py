from hashlib import sha256
import json
import time

class Block:
    def __init__(self, index, timestamp, data, previous_hash=''):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_data = {
            "index": self.index,
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce,
            "data": self.data
        }
        block_string = json.dumps(block_data, sort_keys=True).encode()
        return sha256(block_string).hexdigest()

class SmartContract:
    def __init__(self):
        self.challenge_response_pairs = {}
        self.state = {}

    def store_puf(self, identifier, challenges_responses_dict, estado):
        self.challenge_response_pairs[identifier] = challenges_responses_dict
        self.state[identifier] = {"estado": estado}

    def get_challenges(self, identifier):
        return list(self.challenge_response_pairs.get(identifier, {}).keys())

    def get_response_by_index(self, identifier, index):
        challenges = self.get_challenges(identifier)
        if 0 <= index < len(challenges):
            return self.challenge_response_pairs[identifier][challenges[index]]
        else:
            return None
        
    def get_state(self, identifier):
        return self.state.get(identifier, {})

    def set_state(self, identifier, new_state):
        if identifier in self.state:
            self.state[identifier]["estado"] = new_state
 
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
        return Block(0, time.time(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, new_block):
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
        while block.hash[:self.difficulty] != "0" * self.difficulty:
            block.nonce += 1
            block.hash = block.calculate_hash()

            self.current_hashes += 1
            self.total_hashes += 1
        return block.hash

    def is_chain_valid(self):
        for i in range(1, len(self.chain)):
            current_block = self.chain[i]
            previous_block = self.chain[i - 1]
            if current_block.hash != current_block.calculate_hash():
                return False
            if current_block.previous_hash != previous_block.hash:
                return False
            
        return True

    def add_smart_contract(self, smart_contract):
        self.pending_smart_contracts.append(smart_contract)

        def convert_keys_to_strings(d):
            """Convierte todas las claves del diccionario a cadenas."""
            if isinstance(d, dict):
                return {str(k): convert_keys_to_strings(v) for k, v in d.items()}
            elif isinstance(d, list):
                return [convert_keys_to_strings(i) for i in d]
            else:
                return d
    
        converted_dict = convert_keys_to_strings(smart_contract.challenge_response_pairs)
        
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
        if not self.chain:
            return None

        latest_block = self.get_latest_block()
        smart_contract_data = json.loads(latest_block.data)

        def convert_keys_back(d):
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

def validate_blockchain(blockchain):
    print()
    if blockchain.is_chain_valid():
        print("Validation of the blocks: successful.")
    else:
        print("Error in the validation of the blocks.")

    avg_time = blockchain.get_avg_block_validation_time()
    hash_rate = blockchain.calculate_hash_rate()
    print(f"Average block validation time: {avg_time:.6f} seconds")
    print(f"Hash rate: {hash_rate:.6f} hashes/seconds")

    blockchain.total_validation_time += avg_time
