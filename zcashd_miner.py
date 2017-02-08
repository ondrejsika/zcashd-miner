import struct
import time
import argparse

from jsonrpc_requests import Server

from pyzceqsolver.solver import Solver
from utils import hex_to_bin, bin_to_hex, double_sha256_digest, sha256_digest_to_int, pack_varint
from merkletree import MerkleTree


parser = argparse.ArgumentParser()
parser.add_argument('zcashd_url', help='Url to Zcashd')
parser.add_argument('block_count', type=int, help='Count of mined blocks')


args = parser.parse_args()


solver = Solver()
server = Server(args.zcashd_url)


def get_block_template():
    return server.getblocktemplate()


def txs_hashes(txs):
    return map(double_sha256_digest, txs)


def get_txs(t):
    return [hex_to_bin(tx['data']) for tx in t['transactions']]


def get_header_from_templete(t, nonce):
    version = t['version']
    previous_block_hash = hex_to_bin(t['previousblockhash'])
    cb_hash = hex_to_bin(t['coinbasetxn']['hash'])[::-1]
    hashes = [cb_hash, ] + txs_hashes(get_txs(t))
    hash_merkle_root = MerkleTree(hashes).tree_digest()
    time = t['curtime']
    bits = t['bits']

    return ''.join((
        struct.pack("<i", version),
        previous_block_hash[::-1],
        hash_merkle_root,
        '\x00' * 32,
        struct.pack("<I", time),
        hex_to_bin(bits)[::-1],
        nonce,
    ))


def submit_block(template, header_with_solution_bin):
    txs = get_txs(template)
    block_bin = ''.join((
        header_with_solution_bin,
        pack_varint(len(txs) + 1),
        hex_to_bin(template['coinbasetxn']['data']),
        ''.join(txs),
    ))
    block_hex = bin_to_hex(block_bin)
    server.submitblock(block_hex)


def mine(template):
    target = long(template['target'], 16)

    nonce_counter = 0
    while True:
        nonce_counter += 1
        nonce_bin = '%32x' % nonce_counter
        header_bin = get_header_from_templete(template, nonce_bin)
        sol_num = solver.find_solutions(header_bin)
        for i in range(sol_num):
            solution_bin = solver.get_solution(i)
            header_with_solution_bin = header_bin + '\xfd\x40\x05' + solution_bin
            hash_bin = double_sha256_digest(header_with_solution_bin)
            hash_int = sha256_digest_to_int(hash_bin)
            if hash_int < target:
                submit_block(template, header_with_solution_bin)
                return


if __name__ == '__main__':
    for _ in range(args.block_count):
        mine(get_block_template())
        time.sleep(2)
