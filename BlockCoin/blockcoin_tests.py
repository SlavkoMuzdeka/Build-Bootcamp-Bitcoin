import pytest, ecdsa
from models import Block, Bank
from identities import bank_private_key, user_public_key, user_private_key
from blockcoin import prepare_simple_tx, airdrop_tx


def test_blocks():
    bank = Bank(id=0, private_key=bank_private_key(0))

    # Good block
    block = Block(txns=[])
    block.sign(bank.private_key)
    bank.handle_block(block)
    assert len(bank.blocks) == 1

    # Wrong bank signs
    block = Block(txns=[])
    wrong_private_key = bank_private_key(1000)
    block.sign(wrong_private_key)
    with pytest.raises(ecdsa.keys.BadSignatureError):
        bank.handle_block(block)


def test_bad_tx():
    bank = Bank(id=0, private_key=bank_private_key(0))
    tx = airdrop_tx()
    bank.airdrop(tx)

    tx = prepare_simple_tx(
        utxos=bank.fetch_utxos(user_public_key("alice")),
        sender_private_key=user_private_key("alice"),
        recipient_public_key=user_public_key("bob"),
        amount=10,
    )
    # Put in a phony signature
    tx.tx_ins[0].signature = user_private_key("alice").sign(b"bad")

    with pytest.raises(ecdsa.keys.BadSignatureError):
        bank.handle_tx(tx)


def test_airdrop():
    bank = Bank(id=0, private_key=bank_private_key(0))
    tx = airdrop_tx()
    bank.airdrop(tx)

    assert 500_000 == bank.fetch_balance(user_public_key("alice"))
    assert 500_000 == bank.fetch_balance(user_public_key("bob"))


def test_utxo():
    bank = Bank(id=0, private_key=bank_private_key(0))
    tx = airdrop_tx()
    bank.airdrop(tx)
    assert len(bank.blocks) == 1

    # Alice sends 10 to Bob
    tx = prepare_simple_tx(
        utxos=bank.fetch_utxos(user_public_key("alice")),
        sender_private_key=user_private_key("alice"),
        recipient_public_key=user_public_key("bob"),
        amount=10,
    )
    block = Block(txns=[tx])
    block.sign(bank_private_key(1))
    bank.handle_block(block)

    assert 500_000 - 10 == bank.fetch_balance(user_public_key("alice"))
    assert 500_000 + 10 == bank.fetch_balance(user_public_key("bob"))
