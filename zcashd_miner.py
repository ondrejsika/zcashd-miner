from __future__ import print_function

import struct
import time
import argparse

from jsonrpc_requests import Server

from pyzceqsolver.solver import Solver
from utils import hex_to_bin, bin_to_hex, double_sha256_digest, sha256_digest_to_int, pack_varint, replace_output
from merkletree import MerkleTree


parser = argparse.ArgumentParser()
parser.add_argument('zcashd_url', help='Url to Zcashd')
parser.add_argument('block_count', type=int, help='Count of mined blocks')
parser.add_argument('-a', '--address', default=None, help='Mining address')


args = parser.parse_args()


solver = Solver()
server = Server(args.zcashd_url)


def get_block_template():
    return server.getblocktemplate()


def txs_hashes(txs):
    return map(double_sha256_digest, txs)


def get_txs(t):
    return [hex_to_bin(tx['data']) for tx in t['transactions']]


def get_cb_tx(template, mining_address=None):
    orig = hex_to_bin(template['coinbasetxn']['data'])
    if not mining_address:
        return orig

    orig_decoded = server.decoderawtransaction(template['coinbasetxn']['data'])

    founder_tax_address = orig_decoded['vout'][1]['scriptPubKey']['addresses'][0]
    founder_tax_amount = orig_decoded['vout'][1]['value']
    reward = orig_decoded['vout'][0]['value']

    new_out_tx = hex_to_bin(server.createrawtransaction([], {mining_address: reward,
                                                             founder_tax_address: founder_tax_amount}))
    return replace_output(orig, new_out_tx)


def get_header_from_templete(t, cb_tx, nonce):
    version = t['version']
    previous_block_hash = hex_to_bin(t['previousblockhash'])

    cb_hash = double_sha256_digest(cb_tx)#[::-1]
    # cb_hash = hex_to_bin(t['coinbasetxn']['hash'])[::-1]
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


def submit_block(template, cb_tx, header_with_solution_bin):
    txs = get_txs(template)
    block_bin = ''.join((
        header_with_solution_bin,
        pack_varint(len(txs) + 1),
        # hex_to_bin(template['coinbasetxn']['data']),
        cb_tx,
        ''.join(txs),
    ))
    block_hex = bin_to_hex(block_bin)
    result = server.submitblock(block_hex)
    if not result:
        print('OK')
    else:
        print('ERR %s' % result)


def mine(template, mining_address=None):
    target = long(template['target'], 16)

    nonce_counter = 0
    while True:
        nonce_counter += 1
        nonce_bin = '%32x' % nonce_counter
        cb_tx = get_cb_tx(template, mining_address)
        header_bin = get_header_from_templete(template, cb_tx, nonce_bin)
        sol_num = solver.find_solutions(header_bin)
        for i in range(sol_num):
            solution_bin = solver.get_solution(i)
            header_with_solution_bin = header_bin + '\xfd\x40\x05' + solution_bin
            hash_bin = double_sha256_digest(header_with_solution_bin)
            hash_int = sha256_digest_to_int(hash_bin)
            if hash_int < target:
                submit_block(template, cb_tx, header_with_solution_bin)
                return


if __name__ == '__main__':
    for _ in range(args.block_count):
        mine(get_block_template(), args.address)
        time.sleep(2)
