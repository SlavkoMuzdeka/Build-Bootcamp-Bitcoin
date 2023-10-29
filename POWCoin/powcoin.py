"""
POWCoin

Usage:
  powcoin.py serve
  powcoin.py ping [--node <node>]
  powcoin.py tx <from> <to> <amount> [--node <node>]
  powcoin.py balance <name> [--node <node>]

Options:
  -h --help      Show this screen.
  --node=<node>  Hostname of node [default: node0]
"""

import uuid, socketserver, socket, time, os, logging, threading, random, re
import utils as u
import models as m

from docopt import docopt
from ecdsa import SigningKey, SECP256k1


PORT = 10000
GET_BLOCKS_CHUNK = 10
BLOCK_SUBSIDY = 50
node = None
lock = threading.Lock()

logging.basicConfig(level="INFO", format="%(threadName)-6s | %(message)s")
logger = logging.getLogger(__name__)


def prepare_simple_tx(utxos, sender_private_key, recipient_public_key, amount):
    sender_public_key = sender_private_key.get_verifying_key()

    # Construct tx.tx_outs
    tx_ins = []
    tx_in_sum = 0
    for tx_out in utxos:
        tx_ins.append(m.TxIn(tx_id=tx_out.tx_id, index=tx_out.index, signature=None))
        tx_in_sum += tx_out.amount
        if tx_in_sum > amount:
            break

    # Make sure sender can afford it
    assert tx_in_sum >= amount

    # Construct tx.tx_outs
    tx_id = uuid.uuid4()
    change = tx_in_sum - amount
    tx_outs = [
        m.TxOut(tx_id=tx_id, index=0, amount=amount, public_key=recipient_public_key),
        m.TxOut(tx_id=tx_id, index=1, amount=change, public_key=sender_public_key),
    ]

    # Construct tx and sign inputs
    tx = m.Tx(id=tx_id, tx_ins=tx_ins, tx_outs=tx_outs)
    for i in range(len(tx.tx_ins)):
        tx.sign_input(i, sender_private_key)

    return tx


def prepare_coinbase(public_key, tx_id=None):
    if tx_id is None:
        tx_id = uuid.uuid4()
    return m.Tx(
        id=tx_id,
        tx_ins=[
            m.TxIn(None, None, None),
        ],
        tx_outs=[
            m.TxOut(tx_id=tx_id, index=0, amount=BLOCK_SUBSIDY, public_key=public_key),
        ],
    )


##########
# Mining #
##########

DIFFICULTY_BITS = 2
POW_TARGET = 2 ** (256 - DIFFICULTY_BITS)
mining_interrupt = threading.Event()


def mine_block(block):
    while block.proof >= POW_TARGET:
        if mining_interrupt.is_set():
            logger.info("Mining interrupted")
            mining_interrupt.clear()
            return
        block.nonce += 1
    return block


def mine_forever(public_key):
    logging.info("Starting miner")
    while True:
        coinbase = prepare_coinbase(public_key)
        unmined_block = m.Block(
            txns=[coinbase] + node.mempool,
            prev_id=node.blocks[-1].id,
            nonce=random.randint(0, 1000000000),
        )
        mined_block = mine_block(unmined_block)

        if mined_block:
            logger.info("")
            logger.info("Mined a block")
            with lock:
                node.handle_block(mined_block)


def mine_genesis_block(node, public_key):
    coinbase = prepare_coinbase(public_key, tx_id="abc123")
    unmined_block = m.Block(txns=[coinbase], prev_id=None, nonce=0)
    mined_block = mine_block(unmined_block)
    node.blocks.append(mined_block)
    node.connect_tx(coinbase)
    return mined_block


##############
# Networking #
##############


class TCPHandler(socketserver.BaseRequestHandler):
    def get_canonical_peer_address(self):
        ip = self.client_address[0]
        try:
            hostname = socket.gethostbyaddr(ip)
            hostname = re.search(r"_(.*?)_", hostname[0]).group(1)
        except:
            hostname = ip
        return (hostname, PORT)

    def respond(self, command, data):
        response = u.prepare_message(command, data)
        return self.request.sendall(response)

    def handle(self):
        message = u.read_message(self.request)
        command = message["command"]
        data = message["data"]

        peer = self.get_canonical_peer_address()

        # Handshake / Authentication
        if command == "connect":
            if peer not in node.pending_peers and peer not in node.peers:
                node.pending_peers.append(peer)
                logger.info(f'(handshake) Accepted "connect" request from "{peer[0]}"')
                u.send_message(peer, "connect-response", None)
        elif command == "connect-response":
            if peer in node.pending_peers and peer not in node.peers:
                node.pending_peers.remove(peer)
                node.peers.append(peer)
                logger.info(f'(handshake) Connected to "{peer[0]}"')
                u.send_message(peer, "connect-response", None)

                # Request their peers
                u.send_message(peer, "peers", None)

        # else:
        # assert peer in node.peers, \
        # f"Rejecting {command} from unconnected {peer[0]}"

        # Business Logic
        if command == "peers":
            u.send_message(peer, "peers-response", node.peers)

        if command == "peers-response":
            for peer in data:
                node.connect(peer)

        if command == "ping":
            self.respond(command="pong", data="")

        if command == "sync":
            # Find our most recent block peer doesn't know about,
            # But which build off a block they do know about.
            peer_block_ids = data
            for block in node.blocks[::-1]:
                if block.id not in peer_block_ids and block.prev_id in peer_block_ids:
                    height = node.blocks.index(block)
                    blocks = node.blocks[height : height + GET_BLOCKS_CHUNK]
                    u.send_message(peer, "blocks", blocks)
                    logger.info('Served "sync" request')
                    return

            logger.info('Could not serve "sync" request')

        if command == "blocks":
            for block in data:
                try:
                    with lock:
                        node.handle_block(block)
                    mining_interrupt.set()
                except:
                    logger.info("Rejected block")

            if len(data) == GET_BLOCKS_CHUNK:
                node.sync()

        if command == "tx":
            node.handle_tx(data)

        if command == "balance":
            balance = node.fetch_balance(data)
            self.respond(command="balance-response", data=balance)

        if command == "utxos":
            utxos = node.fetch_utxos(data)
            self.respond(command="utxos-response", data=utxos)


def external_address(node):
    i = int(node[-1])
    port = PORT + i
    return ("localhost", port)


def serve():
    logger.info("Starting server")
    server = socketserver.TCPServer(("0.0.0.0", PORT), TCPHandler)
    server.serve_forever()


#######
# CLI #
#######


def lookup_private_key(name):
    exponent = {"alice": 1, "bob": 2, "node0": 3, "node1": 4, "node2": 5}[name]
    return SigningKey.from_secret_exponent(exponent, curve=SECP256k1)


def lookup_public_key(name):
    return lookup_private_key(name).get_verifying_key()


def main(args):
    if args["serve"]:
        threading.current_thread().name = "main"
        name = os.environ["NAME"]

        duration = 10 * ["node0", "node1", "node2"].index(name)
        time.sleep(duration)

        global node
        node = m.Node(address=(name, PORT))

        # Alice is Satoshi!
        mine_genesis_block(node, lookup_public_key("alice"))

        # Start server thread
        server_thread = threading.Thread(target=serve, name="server")
        server_thread.start()

        # Join the network
        peers = [(p, PORT) for p in os.environ["PEERS"].split(",")]
        for peer in peers:
            node.connect(peer)

        # Wait for peer connections
        time.sleep(1)

        # Do initial block download
        node.sync()

        # Wait for IBD to finish
        time.sleep(1)

        # Start miner thread
        miner_public_key = lookup_public_key(name)
        miner_thread = threading.Thread(
            target=mine_forever, args=[miner_public_key], name="miner"
        )
        miner_thread.start()

    elif args["ping"]:
        address = external_address(args["--node"])
        u.send_message(address, "ping", "")
    elif args["balance"]:
        public_key = lookup_public_key(args["<name>"])
        address = external_address(args["--node"])
        response = u.send_message(address, "balance", public_key, response=True)
        print(response["data"])
    elif args["tx"]:
        # Grab parameters
        sender_private_key = lookup_private_key(args["<from>"])
        sender_public_key = sender_private_key.get_verifying_key()
        recipient_private_key = lookup_private_key(args["<to>"])
        recipient_public_key = recipient_private_key.get_verifying_key()
        amount = int(args["<amount>"])
        address = external_address(args["--node"])

        # Fetch utxos available to spend
        response = u.send_message(address, "utxos", sender_public_key, response=True)
        utxos = response["data"]

        # Prepare transaction
        tx = prepare_simple_tx(utxos, sender_private_key, recipient_public_key, amount)

        # send to node
        u.send_message(address, "tx", tx)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main(docopt(__doc__))
