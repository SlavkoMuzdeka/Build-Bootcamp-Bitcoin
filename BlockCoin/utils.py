import pickle, socket

###########
# HELPERS #
###########


def serialize(coin):
    return pickle.dumps(coin)


def deserialize(serialized):
    return pickle.loads(serialized)


def spend_message(tx, index):
    outpoint = tx.tx_ins[index].outpoint
    return serialize(outpoint) + serialize(tx.tx_outs)


def prepare_message(command, data):
    return {
        "command": command,
        "data": data,
    }


def external_address(node, PORT):
    i = int(node[-1])
    port = PORT + i
    return ("localhost", port)


def send_message(address, command, data, response=False):
    message = prepare_message(command, data)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        s.sendall(serialize(message))
        if response:
            return deserialize(s.recv(1024 * 4))
