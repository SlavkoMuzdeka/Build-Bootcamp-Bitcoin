"""
BlockCoin

Usage:
  blockcoin.py serve
  blockcoin.py ping [--node <node>]
  blockcoin.py tx <from> <to> <amount> [--node <node>]
  blockcoin.py balance <name> [--node <node>]

Options:
  -h --help      Show this screen.
  --node=<node>  Hostname of node [default: node0]
"""

import logging, os, socketserver
from docopt import docopt
from models import Bank, Tx, TxIn, TxOut
from uuid import uuid4
from identities import bank_private_key, user_public_key, user_private_key
from utils import (
    prepare_message,
    serialize,
    deserialize,
    external_address,
    send_message,
)

PORT = 10000
BLOCK_TIME = 5  # in seconds
bank = None

logging.basicConfig(
    level="INFO",
    format="%(asctime)-15s %(levelname)s %(message)s",
)
logger = logging.getLogger(__name__)


class TCPHandler(socketserver.BaseRequestHandler):
    def respond(self, command, data):
        response = prepare_message(command, data)
        return self.request.sendall(serialize(response))

    def handle(self):
        message_bytes = self.request.recv(1024 * 4).strip()
        message = deserialize(message_bytes)
        command = message["command"]
        data = message["data"]

        logger.info(f"received {command}")

        if command == "ping":
            self.respond(command="pong", data="")

        if command == "block":
            bank.handle_block(data)

        if command == "tx":
            bank.handle_tx(data)

        if command == "balance":
            balance = bank.fetch_balance(data)
            self.respond(command="balance-response", data=balance)

        if command == "utxos":
            utxos = bank.fetch_utxos(data)
            self.respond(command="utxos-response", data=utxos)


def serve():
    server = socketserver.TCPServer(("localhost", PORT), TCPHandler)
    server.serve_forever()


def airdrop_tx():
    id = "1"
    tx = Tx(
        id=id,
        tx_ins=[],
        tx_outs=[
            TxOut(tx_id=id, index=0, amount=500_000, public_key=user_public_key("bob")),
            TxOut(
                tx_id=id, index=1, amount=500_000, public_key=user_public_key("alice")
            ),
        ],
    )
    return tx


def prepare_simple_tx(utxos, sender_private_key, recipient_public_key, amount):
    sender_public_key = sender_private_key.get_verifying_key()

    # Construct tx.tx_outs
    tx_ins = []
    tx_in_sum = 0
    for tx_out in utxos:
        tx_ins.append(TxIn(tx_id=tx_out.tx_id, index=tx_out.index, signature=None))
        tx_in_sum += tx_out.amount
        if tx_in_sum > amount:
            break

    # Make sure sender can afford it
    assert tx_in_sum >= amount

    # Construct tx.tx_outs
    tx_id = uuid4()
    change = tx_in_sum - amount
    tx_outs = [
        TxOut(tx_id=tx_id, index=0, amount=amount, public_key=recipient_public_key),
        TxOut(tx_id=tx_id, index=1, amount=change, public_key=sender_public_key),
    ]

    # Construct tx and sign inputs
    tx = Tx(id=tx_id, tx_ins=tx_ins, tx_outs=tx_outs)
    for i in range(len(tx.tx_ins)):
        tx.sign_input(i, sender_private_key)

    return tx


def main(args):
    if args["serve"]:
        global bank
        bank_id = int(os.environ["ID"])
        bank = Bank(id=bank_id, private_key=bank_private_key(bank_id))
        # Airdrop starting balances
        bank.airdrop(airdrop_tx())
        # Start producing blocks
        bank.schedule_next_block()
        serve()
    elif args["ping"]:
        address = external_address(args["--node"])
        send_message(address, "ping", "")
    elif args["balance"]:
        public_key = user_public_key(args["<name>"])
        address = external_address(args["--node"])
        response = send_message(address, "balance", public_key, response=True)
        print(response["data"])
    elif args["tx"]:
        # Grab parameters
        sender_private_key = user_private_key(args["<from>"])
        sender_public_key = sender_private_key.get_verifying_key()

        recipient_private_key = user_private_key(args["<to>"])
        recipient_public_key = recipient_private_key.get_verifying_key()

        amount = int(args["<amount>"])
        address = external_address(args["--node"])

        # Fetch utxos available to spend
        response = send_message(address, "utxos", sender_public_key, response=True)
        utxos = response["data"]

        # Prepare transaction
        tx = prepare_simple_tx(utxos, sender_private_key, recipient_public_key, amount)

        # send to bank
        send_message(address, "tx", tx)
    else:
        print("Invalid command")


if __name__ == "__main__":
    main(docopt(__doc__))
