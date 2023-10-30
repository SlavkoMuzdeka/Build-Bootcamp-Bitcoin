import pickle, socket, random, threading


def serialize(coin):
    return pickle.dumps(coin)


def deserialize(serialized):
    return pickle.loads(serialized)


def spend_message(tx, index):
    outpoint = tx.tx_ins[index].outpoint
    return serialize(outpoint) + serialize(tx.tx_outs)


def prepare_message(command, data):
    message = {
        "command": command,
        "data": data,
    }
    serialized_message = serialize(message)
    length = len(serialized_message).to_bytes(4, "big")
    return length + serialized_message


def read_message(s):
    message = b""
    # Our protocol is: first 4 bytes signify message length
    raw_message_length = s.recv(4) or b"\x00"
    message_length = int.from_bytes(raw_message_length, "big")

    while message_length > 0:
        chunk = s.recv(1024)
        message += chunk
        message_length -= len(chunk)

    return deserialize(message)


def send_message(address, command, data, response=False):
    message = prepare_message(command, data)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.connect(address)
        s.sendall(message)
        if response:
            return read_message(s)


def total_work(blocks):
    return sum([2**block.bits for block in blocks])


def tx_in_to_tx_out(tx_in, blocks):
    for block in blocks:
        for tx in block.txns:
            if tx.id == tx_in.tx_id:
                return tx.tx_outs[tx_in.index]


def disrupt(func, args):
    # Simulate packet loss
    if random.randint(0, 10) != 0:
        # Simulate network latency
        threading.Timer(random.random(), func, args).start()
