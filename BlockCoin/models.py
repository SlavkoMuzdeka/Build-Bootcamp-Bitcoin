from utils import spend_message, serialize, send_message
import time, os, threading
from identities import bank_public_key
from copy import deepcopy

PORT = 10000
NUM_BANKS = 3

###########
# CLASSES #
###########


class Tx:
    def __init__(self, id, tx_ins, tx_outs):
        self.id = id
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs

    def sign_input(self, index, private_key):
        message = spend_message(self, index)
        signature = private_key.sign(message)
        self.tx_ins[index].signature = signature

    def verify_input(self, index, public_key):
        return public_key.verify(
            self.tx_ins[index].signature, spend_message(self, index)
        )


class TxIn:
    def __init__(self, tx_id, index, signature=None):
        self.tx_id = tx_id
        self.index = index
        self.signature = signature

    @property
    def outpoint(self):
        return (self.tx_id, self.index)


class TxOut:
    def __init__(self, tx_id, index, amount, public_key):
        self.tx_id = tx_id
        self.index = index
        self.amount = amount
        self.public_key = public_key

    @property
    def outpoint(self):
        return (self.tx_id, self.index)


class Block:
    def __init__(self, txns, timestamp=None, signature=None):
        if timestamp == None:
            timestamp = time.time()
        self.timestamp = timestamp
        self.signature = signature
        self.txns = txns

    @property
    def message(self):
        return serialize([self.timestamp, self.txns])

    def sign(self, private_key):
        self.signature = private_key.sign(self.message)


class Bank:
    def __init__(self, id, private_key):
        self.id = id
        self.blocks = []
        self.utxo_set = {}
        self.mempool = []
        self.private_key = private_key
        self.peer_addresses = {
            (p, PORT) for p in os.environ.get("PEERS", "").split(",") if p
        }

    @property
    def next_id(self):
        return len(self.blocks) % NUM_BANKS

    @property
    def our_turn(self):
        return self.id == self.next_id

    @property
    def mempool_outpoints(self):
        return [tx_in.outpoint for tx in self.mempool for tx_in in tx.tx_ins]

    def fetch_utxos(self, public_key):
        return [
            tx_out
            for tx_out in self.utxo_set.values()
            if tx_out.public_key == public_key
        ]

    def update_utxo_set(self, tx):
        # Remove utxos that were just spent
        for tx_in in tx.tx_ins:
            del self.utxo_set[tx_in.outpoint]
        # Save utxos which were just created
        for tx_out in tx.tx_outs:
            self.utxo_set[tx_out.outpoint] = tx_out

    def fetch_balance(self, public_key):
        # Fetch utxos associated with this public key
        utxos = self.fetch_utxos(public_key)
        # Sum the amounts
        return sum([tx_out.amount for tx_out in utxos])

    def validate_tx(self, tx):
        in_sum = 0
        out_sum = 0
        for index, tx_in in enumerate(tx.tx_ins):
            # TxIn spending an unspent output
            assert tx_in.outpoint in self.utxo_set

            # No pending transactions spending this same output
            assert tx_in.outpoint not in self.mempool_outpoints

            # Grab the tx_out
            tx_out = self.utxo_set[tx_in.outpoint]

            # Verify signature using public key of TxOut we're spending
            public_key = tx_out.public_key
            tx.verify_input(index, public_key)

            # Sum up the total inputs
            amount = tx_out.amount
            in_sum += amount

        for tx_out in tx.tx_outs:
            # Sum up the total outpouts
            out_sum += tx_out.amount

        # Check no value created or destroyed
        assert in_sum == out_sum

    def handle_tx(self, tx):
        self.validate_tx(tx)
        self.mempool.append(tx)

    def handle_block(self, block):
        # Genesis block has no signature
        if len(self.blocks) > 0:
            public_key = bank_public_key(self.next_id)
            public_key.verify(block.signature, block.message)

        # Check the transactions are valid
        for tx in block.txns:
            self.validate_tx(tx)

        # If they're all good, update self.blocks and self.utxo_set
        for tx in block.txns:
            self.update_utxo_set(tx)

        # Add the block and increment the id of bank who will report next block
        self.blocks.append(block)

        # Schedule submisison of next block
        self.schedule_next_block()

    def make_block(self):
        # Reset mempool
        txns = deepcopy(self.mempool)
        self.mempool = []
        block = Block(txns=txns)
        block.sign(self.private_key)
        return block

    def submit_block(self):
        # Make the block
        block = self.make_block()

        # Save locally
        self.handle_block(block)

        # Tell peers
        for address in self.peer_addresses:
            send_message(address, "block", block)

    def schedule_next_block(self):
        if self.our_turn:
            threading.Timer(5, self.submit_block, []).start()

    def airdrop(self, tx):
        assert len(self.blocks) == 0

        # Update utxo set
        self.update_utxo_set(tx)

        # Update blockchain
        block = Block(txns=[tx])
        self.blocks.append(block)
