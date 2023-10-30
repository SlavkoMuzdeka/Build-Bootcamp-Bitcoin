import utils as u, hashlib, logging, time

logging.basicConfig(level="INFO", format="%(threadName)-6s | %(message)s")
logger = logging.getLogger(__name__)

# In next iteration import these constants as environment variables
SATOSHIS_PER_COIN = 100_000_000
GET_BLOCKS_CHUNK = 10
HALVENING_INTERVAL = 60 * 24  # daily (assuming 1 minute blocks)
BLOCK_TIME_IN_SECS = 1
BLOCKS_PER_DIFFICULTY_PERIOD = 5
DIFFICULTY_PERIOD_IN_SECS = BLOCK_TIME_IN_SECS * BLOCKS_PER_DIFFICULTY_PERIOD


class Tx:
    def __init__(self, id, tx_ins, tx_outs):
        self.id = id
        self.tx_ins = tx_ins
        self.tx_outs = tx_outs

    def sign_input(self, index, private_key):
        message = u.spend_message(self, index)
        signature = private_key.sign(message)
        self.tx_ins[index].signature = signature

    def verify_input(self, index, public_key):
        tx_in = self.tx_ins[index]
        message = u.spend_message(self, index)
        return public_key.verify(tx_in.signature, message)

    @property
    def is_coinbase(self):
        return self.tx_ins[0].tx_id is None

    def __eq__(self, other):
        return self.id == other.id


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
    def __init__(self, txns, prev_id, nonce, bits, timestamp):
        self.txns = txns
        self.prev_id = prev_id
        self.nonce = nonce
        self.bits = bits
        self.timestamp = timestamp

    @property
    def header(self):
        return u.serialize(self)

    @property
    def id(self):
        return hashlib.sha256(self.header).hexdigest()

    @property
    def proof(self):
        return int(self.id, 16)

    @property
    def target(self):
        return 2 ** (256 - self.bits)

    def __eq__(self, other):
        return self.id == other.id

    def __repr__(self):
        prev_id = self.prev_id[:10] if self.prev_id else None
        return f"Block(prev_id={prev_id}... id={self.id[:10]}...)"


class Node:
    def __init__(self, address):
        self.blocks = []
        self.branches = []
        self.utxo_set = {}
        self.mempool = []
        self.peers = []
        self.pending_peers = []
        self.address = address

    def connect(self, peer):
        if peer not in self.peers and peer != self.address:
            logger.info(f'(handshake) Sent "connect" to {peer[0]}')
            try:
                u.send_message(peer, "connect", None)
                self.pending_peers.append(peer)
            except:
                logger.info(f"(handshake) Node {peer[0]} offline")

    def sync(self):
        blocks = self.blocks[-GET_BLOCKS_CHUNK:]
        block_ids = [block.id for block in blocks]
        for peer in self.peers:
            u.send_message(peer, "sync", block_ids)

    def fetch_utxos(self, public_key):
        return [
            tx_out
            for tx_out in self.utxo_set.values()
            if tx_out.public_key == public_key
        ]

    def connect_tx(self, tx):
        # Remove utxos that were just spent
        if not tx.is_coinbase:
            for tx_in in tx.tx_ins:
                del self.utxo_set[tx_in.outpoint]

        # Save utxos which were just created
        for tx_out in tx.tx_outs:
            self.utxo_set[tx_out.outpoint] = tx_out

        # Clean up mempool
        if tx in self.mempool:
            self.mempool.remove(tx)

    def disconnect_tx(self, tx):
        # Add back UTXOs spent by this transaction
        if not tx.is_coinbase:
            for tx_in in tx.tx_ins:
                tx_out = u.tx_in_to_tx_out(tx_in, self.blocks)
                self.utxo_set[tx_out.outpoint] = tx_out

        # Remove UTXOs created by this transaction
        for tx_out in tx.tx_outs:
            del self.utxo_set[tx_out.outpoint]

        # Put it back in mempool
        if tx not in self.mempool and not tx.is_coinbase:
            self.mempool.append(tx)
            logging.info(f"Added tx to mempool")

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
        assert in_sum >= out_sum

    def validate_coinbase(self, block):
        tx = block.txns[0]
        assert len(tx.tx_ins) == len(tx.tx_outs) == 1
        fees = self.calculate_fees(block.txns[1:])
        assert tx.tx_outs[0].amount == self.get_block_subsidy() + fees

    def handle_tx(self, tx):
        if tx not in self.mempool:
            self.validate_tx(tx)
            self.mempool.append(tx)

            # Propogate transaction
            for peer in self.peers:
                u.send_message(peer, "tx", tx)

    def validate_block(self, block, validate_txns=False):
        assert block.proof < block.target, "Insufficient Proof-of-Work"

        if validate_txns:
            # Check block timestamps cannot be too far in future
            assert (
                block.timestamp - time.time() < DIFFICULTY_PERIOD_IN_SECS
            ), "Block too far in future"

            # Block timestamps must advance every block period
            height = max(len(self.blocks) - BLOCKS_PER_DIFFICULTY_PERIOD, 0)
            assert (
                block.timestamp > self.blocks[height].timestamp
            ), "Block periods cannot go backwards in time"

            # Check difficulty adjustment
            assert block.bits == self.get_next_bits(block.prev_id, log=True)

            # Validate coinbase separately
            self.validate_coinbase(block)

            # Check the transactions are valid
            for tx in block.txns[1:]:
                self.validate_tx(tx)

    def find_in_branch(self, block_id):
        for branch_index, branch in enumerate(self.branches):
            for height, block in enumerate(branch):
                if block.id == block_id:
                    return branch, branch_index, height
        return None, None, None

    def handle_block(self, block):
        # Ignore if we've already seen it
        found_in_chain = block in self.blocks
        found_in_branch = self.find_in_branch(block.id)[0] is not None
        if found_in_chain or found_in_branch:
            raise Exception("Received duplicate block")

        # Look up previous block
        branch, branch_index, height = self.find_in_branch(block.prev_id)

        # Conditions
        extends_chain = block.prev_id == self.blocks[-1].id
        forks_chain = not extends_chain and block.prev_id in [
            block.id for block in self.blocks
        ]
        extends_branch = branch and height == len(branch) - 1
        forks_branch = branch and height != len(branch) - 1

        # Always validate, but only validate transactions if extending chain
        self.validate_block(block, validate_txns=extends_chain)

        # Handle each condition separately
        if extends_chain:
            self.connect_block(block)
            logger.info(f"Extended chain to height {len(self.blocks)-1}")
        elif forks_chain:
            self.branches.append([block])
            logger.info(f"Created branch {len(self.branches)}")
        elif extends_branch:
            branch.append(block)
            logger.info(f"Extended branch {branch_index} to {len(branch)}")

            # Reorg if branch now has more work than main chain

            chain_ids = [block.id for block in self.blocks]
            fork_height = chain_ids.index(branch[0].prev_id)
            chain_since_fork = self.blocks[fork_height + 1 :]
            if u.total_work(branch) > u.total_work(chain_since_fork):
                logger.info(f"Reorging to branch {branch_index}")
                self.reorg(branch, branch_index)
        elif forks_branch:
            self.branches.append(branch[: height + 1] + [block])
            logger.info(
                f"Created branch {len(self.branches)-1} to height {len(self.branches[-1]) - 1}"
            )
        else:
            self.sync()
            raise Exception("Encountered block with unknown parent. Syncing.")

        # Block propogation
        for peer in self.peers:
            u.disrupt(func=u.send_message, args=[peer, "blocks", [block]])

    def reorg(self, branch, branch_index):
        # Disconnect to fork block, preserving as a branch
        disconnected_blocks = []
        while self.blocks[-1].id != branch[0].prev_id:
            block = self.blocks.pop()
            for tx in block.txns:
                self.disconnect_tx(tx)
            disconnected_blocks.insert(0, block)

        # Replace branch with newly disconnected blocks
        self.branches[branch_index] = disconnected_blocks

        # Connect branch, rollback if error encountered
        for block in branch:
            try:
                self.validate_block(block, validate_txns=True)
                self.connect_block(block)
            except:
                self.reorg(disconnected_blocks, branch_index)
                logger.info(f"Reorg failed")
                return

    def connect_block(self, block):
        # Add the block to our chain
        self.blocks.append(block)

        # If they're all good, update UTXO set / mempool
        for tx in block.txns:
            self.connect_tx(tx)

    def get_block_subsidy(self):
        halvings = len(self.blocks) // HALVENING_INTERVAL
        return (50 * SATOSHIS_PER_COIN) // (2**halvings)

    def calculate_fees(self, txns):
        fees = 0
        for txn in txns:
            inputs = outputs = 0
            for tx_in in txn.tx_ins:
                inputs += self.utxo_set[tx_in.outpoint].amount
            for tx_out in txn.tx_outs:
                outputs += tx_out.amount
            fees += inputs - outputs
        return fees

    def get_next_bits(self, block_id, log=False):
        # Find the block
        height = [block.id for block in self.blocks].index(block_id)
        block = self.blocks[height]

        # Will we enter a new difficulty period?
        next_height = height + 1
        next_block_period = next_height // BLOCKS_PER_DIFFICULTY_PERIOD
        next_block_period_height = next_height % BLOCKS_PER_DIFFICULTY_PERIOD

        # Only change bits if we're entering a new difficulty period
        if next_block_period_height != 0:
            return block.bits

        # Calculate how long this difficulty period lasted
        one_period_ago_index = max(height - BLOCKS_PER_DIFFICULTY_PERIOD, 0)
        one_period_ago_block = self.blocks[one_period_ago_index]
        period_duration = block.timestamp - one_period_ago_block.timestamp

        # Calculate next bits
        if period_duration <= DIFFICULTY_PERIOD_IN_SECS:
            next_bits = block.bits + 1
        else:
            next_bits = block.bits - 1

        # Log some information
        if log:
            logger.info(
                "(difficulty adjustment) "
                f"period={next_block_period} "
                f"target={DIFFICULTY_PERIOD_IN_SECS} "
                f"duration={period_duration} "
                f"bits={block.bits}->{next_bits} "
            )

        return next_bits
