from flask import Flask, jsonify, request, render_template
import simpy
from simulation import BlockchainNetworkSimulator
from blockchain import Block, Transaction, Blockchain
from threading import Thread
import csv
import time

app = Flask(__name__)

# Global simulator instance
sim_env = simpy.Environment()
network_simulator = BlockchainNetworkSimulator(sim_env, num_nodes=6, malicious_node_indices=[5])

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/transactions')
def transactions():
    return render_template('transactions.html')

@app.route('/mining')
def mining():
    return render_template('mining.html')

@app.route('/attacks')
def attacks():
    return render_template('attacks.html')

@app.route('/chainex')
def chain_explorer():
    return render_template('chain.html')

@app.route('/chain', methods=['GET'])
def get_chain():
    blockchain = network_simulator.nodes[0].blockchain
    response = {
        'chain': [{
            'index': block.index,
            'transactions': [tx.to_dict() for tx in block.transactions],
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'hash': block.hash,
            'nonce': block.nonce
        } for block in blockchain.chain],
        'length': len(blockchain.chain)
    }
    return jsonify(response)

@app.route('/nodes', methods=['GET'])
def get_nodes():
    nodes = [{
        'node_id': node.node_id,
        'is_malicious': node.is_malicious,
        'hash_rate': node.hash_rate
    } for node in network_simulator.nodes]
    return jsonify({'nodes': nodes, 'total_nodes': len(nodes)})

@app.route('/balances', methods=['GET'])
def get_balances():
    blockchain = network_simulator.nodes[0].blockchain
    return jsonify({'balances': blockchain.accounts})

@app.route('/transaction/new', methods=['POST'])
def new_transaction():
    values = request.get_json()
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    try:
        amount = float(values['amount'])
        transaction = Transaction(values['sender'], values['receiver'], amount)
        success = network_simulator.add_transaction(transaction)
        if success:
            with open('transaction_logs.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                writer.writerow([time.time(), transaction.sender, transaction.receiver, transaction.amount])
            return jsonify({'message': 'Transaction added and broadcasted'}), 201
        return jsonify({'message': 'Invalid transaction'}), 400
    except ValueError:
        return jsonify({'message': 'Invalid amount format'}), 400

@app.route('/mine', methods=['POST'])
def mine():
    miner_address = request.get_json().get('miner_address', 'Node0')
    node_index = 0
    block = network_simulator.mine_block(node_index, miner_address)
    return jsonify({
        'message': 'New block mined',
        'block': {
            'index': block.index,
            'transactions': [tx.to_dict() for tx in block.transactions],
            'timestamp': block.timestamp,
            'previous_hash': block.previous_hash,
            'hash': block.hash,
            'nonce': block.nonce
        }
    }), 200

@app.route('/attack', methods=['POST'])
def perform_attack():
    values = request.get_json()
    required = ['sender', 'receiver', 'amount']
    if not all(k in values for k in required):
        return jsonify({'message': 'Missing values'}), 400
    try:
        amount = float(values['amount'])
        success, success_rate = network_simulator.perform_double_spending_attack(values['sender'], values['receiver'], amount)
        return jsonify({
            'message': 'Double-spending attack attempted',
            'success': success,
            'success_rate': success_rate
        }), 200
    except ValueError:
        return jsonify({'message': 'Invalid amount format'}), 400

@app.route('/stats', methods=['GET'])
def get_stats():
    stats = network_simulator.get_attack_stats()
    return jsonify(stats)

if __name__ == '__main__':
    simulation_thread = Thread(target=network_simulator.run_simulation)
    simulation_thread.start()
    app.run(host='0.0.0.0', port=5000)