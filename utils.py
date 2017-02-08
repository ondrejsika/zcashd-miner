import binascii
import hashlib
import struct


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


def pack_varint(i):
    r = ''
    if i < 0:
        raise ValueError('varint must be non-negative integer')
    elif i < 0xfd:
        r += chr(i)
    elif i <= 0xffff:
        r += chr(0xfd)
        r += struct.pack(b'<H', i)
    elif i <= 0xffffffff:
        r += chr(0xfe)
        r += struct.pack(b'<I', i)
    else:
        r += chr(0xff)
        r += struct.pack(b'<Q', i)
    return r
