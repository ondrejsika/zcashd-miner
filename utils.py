import binascii
import hashlib


def hex_to_bin(data_hex):
    return binascii.unhexlify(data_hex)


def bin_to_hex(data_bin):
    return binascii.hexlify(data_bin)


def double_sha256_digest(data):
    return hashlib.sha256(hashlib.sha256(data).digest()).digest()


def bin_le_to_int(val):
    val_hex = bin_to_hex(val[::-1])
    return int(val_hex, 16)


def sha256_digest_to_int(val):
    return bin_le_to_int(val)

