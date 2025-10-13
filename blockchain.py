import hashlib
import time
import json
import uuid

class Transaction:
    def __init__(self, sender, receiver, amount, timestamp=None):
        self.sender = sender
        self.receiver = receiver
        self.amount = float(amount)  # Convert amount to float
        self.timestamp = timestamp or time.time()
        self.id = str(uuid.uuid4())

    def to_dict(self):
        return {
            "id": self.id,
            "sender": self.sender,
            "receiver": self.receiver,
            "amount": self.amount,
            "timestamp": self.timestamp
        }

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = 0
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

    def mine_block(self, difficulty):
        target = "0" * difficulty
        while self.hash[:difficulty] != target:
            self.nonce += 1
            self.hash = self.calculate_hash()

class Blockchain:
    def __init__(self, difficulty=4):
        self.difficulty = difficulty
        self.accounts = {f"Node{j}": 100.0 for j in range(6)}  # Hardcoded initial balances
        self.chain = [self.create_genesis_block()]
        self.pending_transactions = []

    def create_genesis_block(self):
        genesis = Block(0, [], time.time(), "0")
        genesis.hash = genesis.calculate_hash()  # No mining for genesis
        return genesis

    def get_latest_block(self):
        return self.chain[-1]

    def add_block(self, block):
        self.chain.append(block)
        self.update_balances(block.transactions)
        self.pending_transactions = []

    def add_transaction(self, transaction):
        if self.verify_transaction(transaction):
            self.pending_transactions.append(transaction)
            return True
        return False

    def verify_transaction(self, transaction):
        if transaction.sender in ["coinbase", "genesis"]:
            print(f"Node verifying transaction: {transaction.sender} → {transaction.receiver}, Amount: {transaction.amount} (Coinbase/Genesis, auto-verified)")
            return True
        spent_in_pending = sum(tx.amount for tx in self.pending_transactions if tx.sender == transaction.sender)
        balance = self.accounts.get(transaction.sender, 0)
        print(f"Node verifying transaction: {transaction.sender} → {transaction.receiver}, Amount: {transaction.amount}, Balance: {balance}, Spent in pending: {spent_in_pending}")
        if balance - spent_in_pending < transaction.amount:
            print(f"Transaction rejected for {transaction.sender}: Insufficient funds")
            return False
        print(f"Transaction verified for {transaction.sender}")
        return all(key in transaction.to_dict() for key in ["id", "sender", "receiver", "amount", "timestamp"])

    def update_balances(self, transactions):
        for tx in transactions:
            if tx.sender not in ["coinbase", "genesis"]:
                self.accounts[tx.sender] -= tx.amount
            if tx.receiver not in self.accounts:
                self.accounts[tx.receiver] = 0
            self.accounts[tx.receiver] += tx.amount

    def validate_block(self, block):
        if block.previous_hash != self.get_latest_block().hash:
            return False
        if block.hash != block.calculate_hash():
            return False
        if block.hash[:self.difficulty] != "0" * self.difficulty:
            return False
        for tx in block.transactions:
            if not self.verify_transaction(tx):
                return False
        return True