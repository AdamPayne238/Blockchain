import hashlib
import json
from time import time
from uuid import uuid4
import miner
from flask import Flask, jsonify, request

my_coins = 0


class Blockchain(object):
    def __init__(self):
        self.chain = []
        self.current_transactions = []

        # Genesis Block
        self.new_block(previous_hash=1, proof=100)

    def new_block(self, proof, previous_hash=None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': time(),
            'transactions': self.current_transactions,
            'proof': proof,
            'previous_hash': previous_hash or self.hash(self.last_block)
        }

        # Reset the current list of transactions
        self.current_transactions = []
        # Append the chain to the block
        self.chain.append(block)
        # Return the new block
        return block

    def hash(self, block):
        string_block = json.dumps(block, sort_keys=True)

        raw_hash = hashlib.sha256(string_block.encode())

        hex_hash = raw_hash.hexdigest()

        return hex_hash

    @property
    def last_block(self):
        return self.chain[-1]

    @staticmethod
    def valid_proof(block_string, proof):
        guess = f'{block_string}{proof}'.encode()
        guess_hash = hashlib.sha256(guess).hexdigest()
        # return True or False
        return guess_hash[:6] == "000000"


# Instantiate our Node
app = Flask(__name__)

# Generate a globally unique address for this node
node_identifier = str(uuid4()).replace('-', '')

# Instantiate the Blockchain
blockchain = Blockchain()


@app.route('/mine', methods=['POST'])
def mine():
    global my_coins
    data = request.get_json()
    # Run the proof of work algorithm to get the next proof
    # proof = blockchain.proof_of_work(blockchain.last_block)

    block_string = json.dumps(blockchain.last_block)
    previous_hash = blockchain.hash(blockchain.last_block)
    proof = miner.proof_of_work(block_string)

    if 'proof' in data and 'id' in data:
        print(proof)
        if blockchain.valid_proof(block_string, proof):
            block = blockchain.new_block(proof, previous_hash)
            my_coins += 1
            response = {
                'new_block': block,
                'message': f'You generated a new block! Coins: {my_coins}'
            }
            return jsonify(response), 200

    response = {
        'message': f'Proof is not valid! Coins: {my_coins}'
    }
    return jsonify(response), 400


@app.route('/chain', methods=['GET'])
def full_chain():
    response = {
        # TODO: Return the chain and its current length
        'chain': blockchain.chain,
        'length': len(blockchain.chain)
    }
    return jsonify(response), 200


@app.route('/last', methods=['GET'])
def last_block():
    response = {
        'last': blockchain.last_block
    }
    return jsonify(response), 200


# Run the program on port 5000
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)


