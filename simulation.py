import simpy
import random
import time
from blockchain import Block, Transaction, Blockchain
import csv
import json
import os   


class Node:
    def __init__(self, env, node_id, blockchain, is_malicious=False, hash_rate=1.0):
        self.env = env
        self.node_id = node_id
        self.blockchain = blockchain
        self.is_malicious = is_malicious
        self.hash_rate = hash_rate
        self.transaction_queue = []
        self.attack_success_count = 0
        self.attack_attempts = 0
        self.action = env.process(self.run())
        self.mining_process = env.process(self.mine_continuously())

    def run(self):
        while True:
            yield self.env.timeout(random.uniform(0.1, 0.5))
            if self.transaction_queue:
                tx = self.transaction_queue.pop(0)
                if self.blockchain.add_transaction(tx):
                    for node in self.network.nodes:
                        if node.node_id != self.node_id:
                            self.env.process(self.broadcast_transaction(node, tx))

    def broadcast_transaction(self, target_node, transaction):
        yield self.env.timeout(random.uniform(0.1, 0.5))
        target_node.transaction_queue.append(transaction)

    def mine_continuously(self):
        while True:
            if self.blockchain.pending_transactions:
                mining_time = random.expovariate(self.hash_rate)
                yield self.env.timeout(mining_time)
                block = self.mine_block(self.node_id)
                for other in self.network.nodes:
                    if other != self and not self.is_malicious:
                        self.env.process(self.broadcast_block(other, block))

    def mine_block(self, miner_address):
        transactions = self.blockchain.pending_transactions[:]
        block = Block(len(self.blockchain.chain), transactions, time.time(), self.blockchain.get_latest_block().hash)
        block.mine_block(self.blockchain.difficulty)
        self.blockchain.add_block(block)
        return block

    def broadcast_block(self, target, block):
        yield self.env.timeout(random.uniform(0.1, 0.5))
        if target.blockchain.validate_block(block):
            target.blockchain.add_block(block)

    def perform_double_spending_attack(self, sender, receiver, amount):
        if not self.is_malicious:
            return False, 0.0

        self.attack_attempts += 1

        total_other_hash_rate = sum(node.hash_rate for node in self.network.nodes if not node.is_malicious)
        if self.hash_rate <= total_other_hash_rate:
            success_rate = self.attack_success_count / self.attack_attempts if self.attack_attempts > 0 else 0.0
            return False, success_rate

        transaction = Transaction(sender, receiver, amount)
        malicious_transaction = Transaction(sender, sender, amount)

        print("Public transaction initiated:", transaction.to_dict())
        print("Private transaction initiated:", malicious_transaction.to_dict())

        success = True
        success_rate = self.attack_success_count / self.attack_attempts if self.attack_attempts > 0 else 0.0
        return success, success_rate


class BlockchainNetworkSimulator:
    def __init__(self, env, num_nodes=6, malicious_node_indices=None, difficulty=4):
        self.env = env
        self.nodes = []
        self.difficulty = difficulty
        self.attack_stats = {'attempts': 0, 'successes': 0, 'success_rate': 0.0}

        for i in range(num_nodes):
            node_id = f"Node{i}"
            is_malicious = i in (malicious_node_indices or [])
            hash_rate = 6.0 if is_malicious else 1.0
            blockchain = Blockchain(difficulty=difficulty)
            node = Node(env, node_id, blockchain, is_malicious, hash_rate)
            self.nodes.append(node)

        for node in self.nodes:
            node.network = self

    def add_transaction(self, transaction):
        success = True
        for node in self.nodes:
            if not node.blockchain.add_transaction(transaction):
                success = False
        if success:
            for node in self.nodes:
                node.transaction_queue.append(transaction)
        return success

    def mine_block(self, node_index, miner_address):
        return self.nodes[node_index].mine_block(miner_address)

    def perform_double_spending_attack(self, sender, receiver, amount):
        malicious_node = next((node for node in self.nodes if node.is_malicious), None)
        if malicious_node:
            amount = float(amount)
            public_tx = Transaction(sender, receiver, amount)
            private_tx = Transaction(sender, sender, amount)

            print("Public transaction initiated:", public_tx.to_dict())
            print("Private transaction initiated:", private_tx.to_dict())

            #  transaction_logs.csv with header
            file_exists = os.path.isfile('transaction_logs.csv')
            with open('transaction_logs.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists or os.path.getsize('transaction_logs.csv') == 0:
                    writer.writerow(['Type', 'Timestamp', 'Sender', 'Receiver', 'Amount'])
                writer.writerow(['Public', time.time(), sender, receiver, amount])
                writer.writerow(['Private', time.time(), sender, sender, amount])

            # Add public TX to honest nodes
            public_success = True
            for node in self.nodes:
                if not node.is_malicious:
                    if not node.blockchain.add_transaction(public_tx):
                        public_success = False
                    else:
                        node.transaction_queue.append(public_tx)

            #  Add private TX to malicious node and mine
            malicious_node.blockchain.add_transaction(private_tx)
            private_block = malicious_node.mine_block(sender)

            total_other_hash_rate = sum(node.hash_rate for node in self.nodes if not node.is_malicious)
            success = malicious_node.hash_rate > total_other_hash_rate

            # attack_logs.csv with header
            file_exists = os.path.isfile('attack_logs.csv')
            with open('attack_logs.csv', 'a', newline='') as csvfile:
                writer = csv.writer(csvfile)
                if not file_exists or os.path.getsize('attack_logs.csv') == 0:
                    writer.writerow([
                        'Transaction ID',
                        'Timestamp',
                        'Sender',
                        'Receiver',
                        'Amount',
                        'Public Transaction Details',
                        'Private Transaction Details',
                        'Attack Result'
                    ])
                writer.writerow([
                    public_tx.id,
                    time.time(),
                    sender,
                    receiver,
                    amount,
                    json.dumps(public_tx.to_dict()),
                    json.dumps(private_tx.to_dict()),
                    success
                ])

            if success:
                for node in self.nodes:
                    if not node.is_malicious:
                        node.blockchain.chain = malicious_node.blockchain.chain.copy()
                        node.blockchain.pending_transactions = malicious_node.blockchain.pending_transactions.copy()
                        node.blockchain.accounts = malicious_node.blockchain.accounts.copy()
            else:
                if public_success:
                    honest_node = self.nodes[0]
                    block = honest_node.mine_block(sender)
                    for node in self.nodes:
                        if node != honest_node:
                            node.blockchain.chain = honest_node.blockchain.chain.copy()
                            node.blockchain.pending_transactions = honest_node.blockchain.pending_transactions.copy()
                            node.blockchain.accounts = honest_node.blockchain.accounts.copy()

            malicious_node.attack_attempts += 1
            if success:
                malicious_node.attack_success_count += 1
            success_rate = malicious_node.attack_success_count / malicious_node.attack_attempts if malicious_node.attack_attempts > 0 else 0.0

            return success, success_rate
        return False, 0.0

    def get_attack_stats(self):
        return self.attack_stats

    def run_simulation(self):
        self.env.run(until=1000)
